#!/usr/bin/env python3
"""Download one versioned Roboflow dataset into this datasets directory."""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path


DATASETS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = DATASETS_DIR.parent
DEFAULT_ENV_FILE = DATASETS_DIR / ".env"


def read_env_file(path: Path) -> dict[str, str]:
    """Read simple KEY=VALUE entries without executing the file as shell code."""
    values: dict[str, str] = {}
    if not path.is_file():
        return values

    for line_number, raw_line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ValueError(f"{path}:{line_number}: expected KEY=VALUE")
        key, value = line.split("=", maxsplit=1)
        key = key.strip()
        value = value.strip()
        if not key or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
            raise ValueError(f"{path}:{line_number}: invalid environment key")
        if value[:1] in {"'", '"'}:
            if len(value) < 2 or value[-1] != value[0]:
                raise ValueError(f"{path}:{line_number}: unmatched quote")
            value = value[1:-1]
        else:
            value = value.split(" #", maxsplit=1)[0].strip()
        values[key] = value
    return values


def get_setting(name: str, file_values: dict[str, str], default: str = "") -> str:
    return os.environ.get(name, file_values.get(name, default)).strip()


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-.")
    return slug or "dataset"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Download a Roboflow project version in YOLOv5 format. "
            "Settings come from datasets/.env; process environment values "
            "take precedence."
        )
    )
    parser.add_argument(
        "--env-file",
        type=Path,
        default=DEFAULT_ENV_FILE,
        help=f"configuration file (default: {DEFAULT_ENV_FILE})",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="optional output directory, which must remain inside datasets/",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="allow Roboflow to download into an existing output directory",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="validate configuration and show the destination without downloading",
    )
    parser.add_argument(
        "--list-versions",
        action="store_true",
        help="show the dataset versions available in this Roboflow project",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        file_values = read_env_file(args.env_file.expanduser())
    except (OSError, ValueError) as error:
        print(f"Configuration error: {error}", file=sys.stderr)
        return 2

    api_key = get_setting("ROBOFLOW_API_KEY", file_values)
    workspace = get_setting("ROBOFLOW_WORKSPACE", file_values)
    project_slug = get_setting("ROBOFLOW_PROJECT", file_values)
    version_text = get_setting("ROBOFLOW_VERSION", file_values)
    model_format = get_setting("ROBOFLOW_FORMAT", file_values, "yolov5")

    required = {
        "ROBOFLOW_API_KEY": api_key,
        "ROBOFLOW_WORKSPACE": workspace,
        "ROBOFLOW_PROJECT": project_slug,
    }
    missing = [
        name
        for name, value in required.items()
        if not value or value.startswith("PASTE_") or value.startswith("your-")
    ]
    if missing:
        print(
            "Set these values in datasets/.env or in the process environment: "
            + ", ".join(missing),
            file=sys.stderr,
        )
        return 2
    if version_text and (not version_text.isdecimal() or int(version_text) < 1):
        print("ROBOFLOW_VERSION must be empty or a positive integer.", file=sys.stderr)
        return 2
    if not version_text and not args.list_versions:
        print(
            "No dataset version is set. Roboflow requires a generated version "
            "to export and download a dataset.\n"
            "Create one in the project's Versions page, enter its number in "
            "datasets/.env, then run this script again.\n"
            "To check available versions, run: "
            "python datasets/download_roboflow.py --list-versions",
            file=sys.stderr,
        )
        return 2
    if not model_format:
        print("ROBOFLOW_FORMAT must not be empty.", file=sys.stderr)
        return 2

    if args.list_versions:
        try:
            import roboflow
        except ImportError:
            print(
                "Roboflow SDK is not installed. Install it with:\n"
                "  python -m pip install -r datasets/requirements.txt",
                file=sys.stderr,
            )
            return 2
        client = roboflow.Roboflow(api_key=api_key)
        project = client.workspace(workspace).project(project_slug)
        versions = project.versions()
        if not versions:
            print(
                "No dataset versions have been created for this Roboflow "
                "project yet. Create one in the project's Versions page."
            )
            return 0
        print(f"Available versions for {workspace}/{project_slug}:")
        for version in versions:
            print(f"  {version.version} ({version.images} images)")
        return 0

    version_number = int(version_text)
    target = args.output_dir or (DATASETS_DIR / "earbud")
    if not target.is_absolute():
        target = PROJECT_ROOT / target
    target = target.expanduser().resolve()
    datasets_root = DATASETS_DIR.resolve()
    if not target.is_relative_to(datasets_root):
        print(
            f"Output directory must be inside {datasets_root}: {target}",
            file=sys.stderr,
        )
        return 2
    if target.exists() and not target.is_dir():
        print(f"Output path exists and is not a directory: {target}", file=sys.stderr)
        return 2
    if target.is_dir() and any(target.iterdir()) and not args.overwrite:
        print(
            f"Output directory is not empty: {target}\n"
            "Choose another --output-dir or pass --overwrite to replace its dataset.",
            file=sys.stderr,
        )
        return 2

    print(f"Roboflow project: {workspace}/{project_slug}/{version_number}")
    print(f"Export format: {model_format}")
    print(f"Destination: {target}")
    if args.dry_run:
        print("Dry run only; no download was started.")
        return 0

    try:
        import roboflow
    except ImportError:
        print(
            "Roboflow SDK is not installed. Install it with:\n"
            "  python -m pip install -r datasets/requirements.txt",
            file=sys.stderr,
        )
        return 2

    client = roboflow.Roboflow(api_key=api_key)
    project = client.workspace(workspace).project(project_slug)
    try:
        version = project.version(version_number)
    except RuntimeError as error:
        print(
            f"Roboflow could not find dataset version {version_number}: {error}\n"
            "Create a version in the project's Versions page or run with "
            "--list-versions to see available versions.",
            file=sys.stderr,
        )
        return 2

    dataset = version.download(
        model_format=model_format,
        location=str(target),
        overwrite=args.overwrite,
    )
    print(f"Download complete: {dataset.location}")
    print(
        "Review the downloaded data.yaml before training; confirm the paths, "
        "class names, and train/validation/test splits."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
