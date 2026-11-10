#!/usr/bin/env python3
"""Combine the Earbud and Scissors datasets into the SafeZone sz-mod dataset."""

from __future__ import annotations

import argparse
import hashlib
import math
import shutil
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASETS_DIR = PROJECT_ROOT / "datasets"
OUTPUT_DIR = DATASETS_DIR / "sz-mod"
SPLITS = ("train", "valid", "test")
SOURCES = (
    ("scissors", 0, "scissors"),
    ("earbud", 1, "earbuds"),
)
IMAGE_EXTENSIONS = {".bmp", ".jpeg", ".jpg", ".png", ".tif", ".tiff", ".webp"}


@dataclass(frozen=True)
class SourceImage:
    dataset: str
    image: Path
    labels: tuple[tuple[str, ...], ...]
    digest: str


def parse_labels(path: Path) -> tuple[tuple[str, ...], ...]:
    rows = []
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        fields = raw_line.split()
        if not fields:
            continue
        try:
            class_id = int(fields[0])
            coordinates = [float(value) for value in fields[1:]]
        except ValueError as error:
            raise ValueError(f"{path}:{line_number}: invalid YOLO annotation") from error

        valid_box = len(coordinates) == 4
        valid_polygon = len(coordinates) >= 6 and len(coordinates) % 2 == 0
        if class_id != 0:
            raise ValueError(f"{path}:{line_number}: expected source class ID 0, got {class_id}")
        if not (valid_box or valid_polygon):
            raise ValueError(f"{path}:{line_number}: expected a box or polygon annotation")
        if not all(math.isfinite(value) and 0 <= value <= 1 for value in coordinates):
            raise ValueError(f"{path}:{line_number}: coordinates must be finite and normalized")
        if valid_box:
            x_center, y_center, width, height = coordinates
            if width <= 0 or height <= 0:
                raise ValueError(f"{path}:{line_number}: bounding box has zero area")
            if (
                x_center - width / 2 < 0
                or x_center + width / 2 > 1
                or y_center - height / 2 < 0
                or y_center + height / 2 > 1
            ):
                raise ValueError(f"{path}:{line_number}: bounding box extends outside the image")
        else:
            x_values = coordinates[::2]
            y_values = coordinates[1::2]
            x_min, x_max = min(x_values), max(x_values)
            y_min, y_max = min(y_values), max(y_values)
            width, height = x_max - x_min, y_max - y_min
            if width <= 0 or height <= 0:
                raise ValueError(f"{path}:{line_number}: polygon has zero area")
            x_center, y_center = (x_min + x_max) / 2, (y_min + y_max) / 2
            coordinates = [x_center, y_center, width, height]
        rows.append((str(class_id), *(f"{value:.8g}" for value in coordinates)))
    return tuple(rows)


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_sources() -> dict[str, dict[str, list[SourceImage]]]:
    sources: dict[str, dict[str, list[SourceImage]]] = {
        split: defaultdict(list) for split in SPLITS
    }
    for dataset, _, _ in SOURCES:
        source_root = DATASETS_DIR / dataset
        if not source_root.is_dir():
            raise FileNotFoundError(f"Dataset directory not found: {source_root}")
        for split in SPLITS:
            image_dir = source_root / split / "images"
            label_dir = source_root / split / "labels"
            if not image_dir.is_dir() or not label_dir.is_dir():
                raise FileNotFoundError(f"Expected images and labels under {source_root / split}")
            images = sorted(
                path for path in image_dir.iterdir()
                if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
            )
            labels = {path.stem: path for path in label_dir.glob("*.txt")}
            image_stems = {path.stem for path in images}
            if image_stems != set(labels):
                raise ValueError(
                    f"{dataset}/{split}: image/label mismatch; "
                    f"missing labels={sorted(image_stems - set(labels))[:5]}, "
                    f"orphan labels={sorted(set(labels) - image_stems)[:5]}"
                )
            for image in images:
                sources[split][dataset].append(
                    SourceImage(
                        dataset=dataset,
                        image=image,
                        labels=parse_labels(labels[image.stem]),
                        digest=file_digest(image),
                    )
                )
    return sources


def build_groups(
    sources: dict[str, dict[str, list[SourceImage]]],
) -> tuple[dict[str, list[list[SourceImage]]], int]:
    by_digest: dict[str, list[tuple[str, SourceImage]]] = defaultdict(list)
    for split, dataset_sources in sources.items():
        for images in dataset_sources.values():
            for image in images:
                by_digest[image.digest].append((split, image))

    cross_split = [
        entries for entries in by_digest.values()
        if len({split for split, _ in entries}) > 1
    ]
    if cross_split:
        examples = ", ".join(
            f"{image.image.name} ({split})"
            for split, image in cross_split[0]
        )
        raise ValueError(f"Identical image content occurs across splits: {examples}")

    grouped: dict[str, dict[str, list[SourceImage]]] = {
        split: defaultdict(list) for split in SPLITS
    }
    for entries in by_digest.values():
        split = entries[0][0]
        grouped[split][entries[0][1].digest].extend(image for _, image in entries)

    duplicate_count = sum(
        len(images) - 1
        for digest_groups in grouped.values()
        for images in digest_groups.values()
    )
    return (
        {
            split: [sorted(images, key=lambda item: (item.dataset, item.image.name))
                    for images in digest_groups.values()]
            for split, digest_groups in grouped.items()
        },
        duplicate_count,
    )


def write_configs() -> None:
    config = """# SafeZone Multi-Object Detection Dataset (sz-mod)
path: datasets/sz-mod
train: train/images
val: valid/images
test: test/images

nc: 2
names: ['scissors', 'earbuds']
"""
    (OUTPUT_DIR / "data.yaml").write_text(config, encoding="utf-8")
    (PROJECT_ROOT / "data" / "sz-mod.yaml").write_text(config, encoding="utf-8")


def combine(overwrite: bool) -> None:
    sources = load_sources()
    groups, duplicate_count = build_groups(sources)
    if OUTPUT_DIR.is_symlink():
        raise ValueError(f"Refusing to replace a symlink: {OUTPUT_DIR}")
    if OUTPUT_DIR.exists() and not OUTPUT_DIR.is_dir():
        raise FileExistsError(f"Output path exists and is not a directory: {OUTPUT_DIR}")
    if OUTPUT_DIR.is_dir() and any(OUTPUT_DIR.iterdir()):
        if not overwrite:
            raise FileExistsError(
                f"Output directory is not empty: {OUTPUT_DIR}\n"
                "Pass --overwrite to rebuild only this generated combined dataset."
            )
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    stats: dict[str, Counter[str]] = {split: Counter() for split in SPLITS}

    class_ids = {dataset: class_id for dataset, class_id, _ in SOURCES}
    for split, digest_groups in groups.items():
        image_dir = OUTPUT_DIR / split / "images"
        label_dir = OUTPUT_DIR / split / "labels"
        image_dir.mkdir(parents=True, exist_ok=True)
        label_dir.mkdir(parents=True, exist_ok=True)

        for group in sorted(digest_groups, key=lambda items: (items[0].dataset, items[0].image.name)):
            primary = group[0]
            destination_name = f"{primary.dataset}__{primary.image.name}"
            shutil.copy2(primary.image, image_dir / destination_name)

            rows_by_dataset: dict[str, tuple[tuple[str, ...], ...]] = {}
            for source in group:
                rows_by_dataset.setdefault(source.dataset, source.labels)
            remapped_rows = []
            for dataset, rows in rows_by_dataset.items():
                new_class_id = class_ids[dataset]
                remapped_rows.extend(
                    (str(new_class_id), *row[1:]) for row in rows
                )
            with (label_dir / f"{Path(destination_name).stem}.txt").open(
                "w", encoding="utf-8"
            ) as label_file:
                for row in remapped_rows:
                    label_file.write(" ".join(row) + "\n")

            stats[split]["images"] += 1
            stats[split]["instances"] += len(remapped_rows)
            stats[split]["scissors"] += sum(row[0] == "0" for row in remapped_rows)
            stats[split]["earbuds"] += sum(row[0] == "1" for row in remapped_rows)

    write_configs()
    readme = [
        "# SafeZone Multi-Object Detection Dataset (sz-mod)",
        "",
        "Combined YOLOv5 detection dataset. Source datasets remain unchanged.",
        "",
        "Class mapping:",
        "- `0`: scissors (Roboflow scissors dataset, version 2)",
        "- `1`: earbuds (Roboflow Earbud dataset, version 1)",
        "",
        "All labels are standard YOLO bounding boxes. Source polygon annotations",
        "are converted to their enclosing normalized boxes, matching YOLOv5's",
        "detection-training behavior; source datasets remain unchanged.",
        "",
        f"Removed {duplicate_count} exact duplicate image file(s) within the same split.",
        "No identical image content was found across different splits.",
        "",
        "| Split | Images | Scissors instances | Earbud instances |",
        "|---|---:|---:|---:|",
    ]
    for split in SPLITS:
        values = stats[split]
        readme.append(
            f"| {split} | {values['images']} | {values['scissors']} | {values['earbuds']} |"
        )
    readme.extend(
        [
            "",
            "Training configuration: `data/sz-mod.yaml` from the YOLOv5 project root.",
            "Roboflow source licenses and attribution requirements still apply.",
        ]
    )
    (OUTPUT_DIR / "README.md").write_text("\n".join(readme) + "\n", encoding="utf-8")

    print(f"Combined dataset created: {OUTPUT_DIR}")
    print(f"Removed exact same-split duplicates: {duplicate_count}")
    for split, values in stats.items():
        print(
            f"{split}: {values['images']} images, "
            f"{values['scissors']} scissors, {values['earbuds']} earbuds"
        )
    print(f"Training config: {PROJECT_ROOT / 'data' / 'sz-mod.yaml'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="replace only the generated datasets/sz-mod directory",
    )
    args = parser.parse_args()
    try:
        combine(overwrite=args.overwrite)
    except (FileExistsError, FileNotFoundError, OSError, ValueError) as error:
        print(f"Dataset preparation failed: {error}", file=sys.stderr)
        raise SystemExit(2)
