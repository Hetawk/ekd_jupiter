#!/usr/bin/env python3
"""Create a reproducible exploratory split of the combined SafeZone dataset."""

from __future__ import annotations

import argparse
import csv
import hashlib
import math
import random
import shutil
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASETS_DIR = PROJECT_ROOT / "datasets"
SOURCE_DIR = DATASETS_DIR / "sz-mod"
OUTPUT_DIR = DATASETS_DIR / "sz-mod-70-15-15"
SPLITS = ("train", "valid", "test")
RATIOS = {"train": Fraction(7, 10), "valid": Fraction(3, 20), "test": Fraction(3, 20)}
IMAGE_EXTENSIONS = {".bmp", ".jpeg", ".jpg", ".png", ".tif", ".tiff", ".webp"}


@dataclass(frozen=True)
class ImageRecord:
    path: Path
    source_split: str
    classes: tuple[str, ...]
    digest: str


def digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_images() -> list[ImageRecord]:
    records = []
    seen_digests: dict[str, Path] = {}
    for source_split in SPLITS:
        image_dir = SOURCE_DIR / source_split / "images"
        label_dir = SOURCE_DIR / source_split / "labels"
        if not image_dir.is_dir() or not label_dir.is_dir():
            raise FileNotFoundError(f"Expected images and labels under {SOURCE_DIR / source_split}")
        images = sorted(
            path for path in image_dir.iterdir()
            if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
        )
        labels = {path.stem: path for path in label_dir.glob("*.txt")}
        image_stems = {path.stem for path in images}
        if image_stems != set(labels):
            raise ValueError(
                f"{source_split}: image/label mismatch; "
                f"missing labels={sorted(image_stems - set(labels))[:5]}, "
                f"orphan labels={sorted(set(labels) - image_stems)[:5]}"
            )
        for image in images:
            label_path = labels[image.stem]
            classes = set()
            for line_number, line in enumerate(label_path.read_text(encoding="utf-8").splitlines(), 1):
                fields = line.split()
                if not fields:
                    continue
                if fields[0] not in {"0", "1"}:
                    raise ValueError(f"{label_path}:{line_number}: expected class ID 0 or 1")
                classes.add(fields[0])

            digest = digest_file(image)
            if digest in seen_digests:
                raise ValueError(
                    f"Duplicate image content would leak across splits: "
                    f"{seen_digests[digest]} and {image}"
                )
            seen_digests[digest] = image
            records.append(
                ImageRecord(image, source_split, tuple(sorted(classes)), digest)
            )
    return records


def assign_splits(records: list[ImageRecord], seed: int) -> dict[str, list[ImageRecord]]:
    total = len(records)
    targets = {
        "train": math.floor(total * RATIOS["train"]),
        "valid": math.floor(total * RATIOS["valid"]),
    }
    targets["test"] = total - targets["train"] - targets["valid"]

    strata: dict[tuple[str, ...], list[ImageRecord]] = defaultdict(list)
    for record in records:
        strata[record.classes].append(record)

    rng = random.Random(seed)
    assigned: dict[str, list[ImageRecord]] = {split: [] for split in SPLITS}
    assigned_by_stratum: dict[tuple[str, ...], Counter[str]] = {}
    desired_by_stratum: dict[tuple[str, ...], dict[str, float]] = {}
    for signature in sorted(strata):
        group = strata[signature]
        rng.shuffle(group)
        quotas = {split: len(group) * RATIOS[split] for split in SPLITS}
        counts = {split: math.floor(quotas[split]) for split in SPLITS}
        remaining = len(group) - sum(counts.values())
        ranked_splits = sorted(
            SPLITS,
            key=lambda split: (-(quotas[split] - counts[split]), SPLITS.index(split)),
        )
        for split in ranked_splits:
            if remaining == 0:
                break
            counts[split] += 1
            remaining -= 1

        offset = 0
        for split in SPLITS:
            assigned[split].extend(group[offset:offset + counts[split]])
            offset += counts[split]
        assigned_by_stratum[signature] = Counter(counts)
        desired_by_stratum[signature] = quotas

    actual = {split: len(items) for split, items in assigned.items()}
    while actual != targets:
        source = next(
            split for split in SPLITS if actual[split] > targets[split]
        )
        destination = next(
            split for split in SPLITS if actual[split] < targets[split]
        )
        candidates = [
            signature for signature in sorted(strata)
            if assigned_by_stratum[signature][source] > 0
        ]
        if not candidates:
            raise ValueError(f"Unable to balance exact split targets: {targets}")
        signature = max(
            candidates,
            key=lambda key: (
                desired_by_stratum[key][destination]
                - assigned_by_stratum[key][destination]
                + assigned_by_stratum[key][source]
                - desired_by_stratum[key][source],
                key,
            ),
        )
        item = next(
            record for record in assigned[source]
            if record.classes == signature
        )
        assigned[source].remove(item)
        assigned[destination].append(item)
        assigned_by_stratum[signature][source] -= 1
        assigned_by_stratum[signature][destination] += 1
        actual[source] -= 1
        actual[destination] += 1

    if {split: len(items) for split, items in assigned.items()} != targets:
        raise ValueError(
            "Stratified split could not meet exact targets: "
            f"expected {targets}, got "
            f"{ {split: len(items) for split, items in assigned.items()} }"
        )
    return assigned


def write_dataset(assigned: dict[str, list[ImageRecord]], seed: int) -> None:
    if OUTPUT_DIR.exists() or OUTPUT_DIR.is_symlink():
        raise FileExistsError(f"Output already exists; refusing to replace: {OUTPUT_DIR}")

    stats: dict[str, Counter[str]] = {split: Counter() for split in SPLITS}
    source_assignments: Counter[tuple[str, str]] = Counter()
    manifest_path = OUTPUT_DIR / "split-manifest.csv"
    try:
        for split, records in assigned.items():
            image_dir = OUTPUT_DIR / split / "images"
            label_dir = OUTPUT_DIR / split / "labels"
            image_dir.mkdir(parents=True, exist_ok=True)
            label_dir.mkdir(parents=True, exist_ok=True)
            for record in records:
                shutil.copy2(record.path, image_dir / record.path.name)
                shutil.copy2(
                    SOURCE_DIR / record.source_split / "labels" / f"{record.path.stem}.txt",
                    label_dir / f"{record.path.stem}.txt",
                )
                stats[split]["images"] += 1
                source_assignments[(record.source_split, split)] += 1
                for class_id in record.classes:
                    stats[split][class_id] += 1

        config = """# Exploratory SafeZone 70/15/15 split
path: datasets/sz-mod-70-15-15
train: train/images
val: valid/images
test: test/images

nc: 2
names: ['scissors', 'earbuds']
"""
        (OUTPUT_DIR / "data.yaml").write_text(config, encoding="utf-8")
        with manifest_path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(("image", "split", "source_split", "class_ids"))
            for split, records in assigned.items():
                for record in sorted(records, key=lambda item: item.path.name):
                    writer.writerow(
                        (record.path.name, split, record.source_split, " ".join(record.classes))
                    )

        lines = [
            "# Exploratory SafeZone 70/15/15 dataset split",
            "",
            f"Reproducibly re-split from `../sz-mod/` with seed `{seed}`.",
            "Class IDs: `0` scissors, `1` earbuds. The original dataset is unchanged.",
            "",
            "This is an exploratory split, not an independent final test: the original",
            "validation and test images were used in earlier model comparisons. Exact",
            "duplicate image content was checked before assignment.",
            "",
            "| Split | Images | Scissors images | Earbuds images |",
            "|---|---:|---:|---:|",
        ]
        for split in SPLITS:
            lines.append(
                f"| {split} | {stats[split]['images']} | "
                f"{stats[split]['0']} | {stats[split]['1']} |"
            )
        lines.extend(
            [
                "",
                "Original split redistribution (these source images were previously",
                "used for training, validation, and test; this is not an independent",
                "re-split for final evaluation):",
                "",
                "| Original split | New train | New validation | New test |",
                "|---|---:|---:|---:|",
            ]
        )
        for source_split in SPLITS:
            lines.append(
                f"| {source_split} | "
                f"{source_assignments[(source_split, 'train')]} | "
                f"{source_assignments[(source_split, 'valid')]} | "
                f"{source_assignments[(source_split, 'test')]} |"
            )
        lines.extend(
            [
                "",
                "The per-image source split and class IDs are recorded in",
                "`split-manifest.csv`. YOLOv5 config: `data.yaml`.",
            ]
        )
        (OUTPUT_DIR / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    except (OSError, ValueError, csv.Error):
        shutil.rmtree(OUTPUT_DIR, ignore_errors=True)
        raise

    print(f"Created exploratory dataset: {OUTPUT_DIR}")
    for split in SPLITS:
        values = stats[split]
        print(
            f"{split}: {values['images']} images, "
            f"{values['0']} scissors images, {values['1']} earbuds images"
        )
    print(f"Configuration: {OUTPUT_DIR / 'data.yaml'}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    try:
        records = load_images()
        if not records:
            raise ValueError(f"No images found under {SOURCE_DIR}")
        assigned = assign_splits(records, args.seed)
        write_dataset(assigned, args.seed)
    except (FileExistsError, FileNotFoundError, OSError, ValueError) as error:
        print(f"Dataset split failed: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
