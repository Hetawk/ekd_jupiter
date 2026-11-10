# Download a dataset from Roboflow

This helper downloads one fixed Roboflow dataset version as YOLOv5-formatted
images and labels. It does not choose or download a dataset automatically.

## Configure

Edit `.env` in this directory:

- `ROBOFLOW_API_KEY`: your private Roboflow API key. Get it from
  [Roboflow Settings > API Key](https://app.roboflow.com/settings/api).
- `ROBOFLOW_WORKSPACE`: the workspace slug.
- `ROBOFLOW_PROJECT`: the project slug.
- `ROBOFLOW_VERSION`: the dataset version number. Create a version in the
  project's **Versions** page before downloading; a project with uploaded
  images but no generated version cannot be exported yet.
- `ROBOFLOW_FORMAT`: defaults to `yolov5`.

Only `ROBOFLOW_API_KEY` is a secret/API key. Workspace, project, and version
are identifiers. The `.env` file is excluded by the repository's `.gitignore`;
do not paste the key into source code or commit it.

## Install and run

From the SafeZone project root:

```bash
python -m pip install -r datasets/requirements.txt
python datasets/download_roboflow.py --list-versions
python datasets/download_roboflow.py --dry-run
python datasets/download_roboflow.py
```

Roboflow's Python SDK uses `tqdm` progress bars while downloading the ZIP and
extracting it. No separate progress-bar implementation is needed in this
script.

By default, the download goes directly to `datasets/earbud/`. The script
refuses to write outside `datasets/` and does not overwrite a non-empty
destination unless `--overwrite` is supplied. To use another directory within
`datasets/`:

```bash
python datasets/download_roboflow.py --output-dir datasets/my-dataset
```

After downloading, check the exported `data.yaml`, class mapping, split names,
and image/label counts before training. Dataset access and license terms are
set by the Roboflow project owner; confirm that the selected version is
available to your account and permitted for the intended use.

For the Earbud and Scissors datasets' server paths, YOLOv5 YAML configuration,
training commands, and robot inference considerations, see
[SERVER_DATASET_SETUP.md](SERVER_DATASET_SETUP.md).
The project overview and current training/monitoring commands are in the
[SafeZone project guide](../docs/README.md).

Project-level training configs are in `data/earbud.yaml` and
`data/scissors.yaml`. Keep the Roboflow-exported `data.yaml` alongside each
dataset for export metadata; pass the project-level config to `train.py` and
`val.py`.

To build the combined two-class `sz-mod` dataset from the preserved source
exports, run:

```bash
python datasets/prepare_sz_mod.py
```

This validates the source annotations and split contents, remaps scissors to
class 0 and earbuds to class 1, and writes `datasets/sz-mod/` plus
`data/sz-mod.yaml`. Polygon annotations are converted to normalized YOLO
detection boxes.
It refuses to overwrite a non-empty combined dataset unless `--overwrite` is
passed. To intentionally rebuild it from the preserved originals, use
`python datasets/prepare_sz_mod.py --overwrite`. Train the one-checkpoint
model with `python train.py --data data/sz-mod.yaml`.

To create a separate, reproducible 70/15/15 exploratory split without
modifying `datasets/sz-mod/`, use:

```bash
python datasets/split_sz_mod.py --seed 42
```

This creates `datasets/sz-mod-70-15-15/` and its YOLOv5 `data.yaml`. It checks
for exact duplicate image content and stratifies images by class presence.
Because it repartitions the existing dataset, whose test split was already
used for model comparisons, this variant is not an independent final test set.

Official references:

- [Roboflow dataset download guide](https://docs.roboflow.com/datasets/create-and-upload/download-a-dataset)
- [Roboflow Python SDK](https://docs.roboflow.com/reference/platform/python-sdk)
- [Roboflow authentication](https://docs.roboflow.com/reference/authentication/authentication)
