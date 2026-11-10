# Server dataset setup and pipeline notes

## Server dataset layout

The two original datasets are preserved under the YOLOv5 project's `datasets/`
directory:

```text
/data2/enoch/ekd_coding_env/jup/yolov5/datasets/earbud/
/data2/enoch/ekd_coding_env/jup/yolov5/datasets/scissors/
/data2/enoch/ekd_coding_env/jup/yolov5/datasets/sz-mod/
```

The combined dataset is `datasets/sz-mod/`, and its training configuration is
`data/sz-mod.yaml`. `datasets/earbud/` and `datasets/scissors/` remain
unchanged as source data. The local `.env`, YOLOv5 training outputs,
checkpoints, and unrelated datasets are not part of this transfer.

| Dataset | Version | Classes | Train | Validation | Test |
|---|---:|---|---:|---:|---:|
| Earbud | 1 | `Earbud` | 386 | 47 | 47 |
| Scissors | 2 | `scissors` | 364 | 23 | 23 |

Image and label counts match in every source split. One exact duplicate image
within the scissors training split was removed from the combined dataset.
Combined counts:

| Split | Images | Scissors instances | Earbud instances |
|---|---:|---:|---:|
| Train | 749 | 445 | 418 |
| Validation | 70 | 31 | 52 |
| Test | 70 | 30 | 56 |

## Configuration and pipeline touchpoints

1. **Dataset files:** Keep each dataset's images and YOLO-format labels together
   under its own source folder. The combined `datasets/sz-mod/` contains the
   class-remapped copy used for the single multi-class model. Original
   Roboflow `data.yaml` files stay with their source data for provenance.
2. **Dataset YAML:** In the project-level configs, `path` is relative to the
   YOLOv5 project root, and `train`, `val`, and `test` are relative to that
   dataset path. Use `data/sz-mod.yaml` for the one-checkpoint model. Its class
   map is ID 0 `scissors` and ID 1 `earbuds`. The individual configs remain
   available for separate baselines.
3. **Training:** YOLOv5 does not automatically discover these datasets. Pass the
   combined YAML explicitly with `train.py --data`.
4. **Validation and final test:** Use `val.py --data <dataset-yaml>` for
   validation metrics. Use `--task test` only for a final held-out test after
   model choices are complete; avoid using test results to tune training.
5. **Robot/inference integration:** Point `detect.py` or the eventual robot
   inference service at the selected trained checkpoint. The combined
   `sz-mod` checkpoint returns both classes; route each class through its
   corresponding workspace rule. Object detection alone does not establish a
   policy violation.
6. **Existing project notes:** `MASKMONITOR.md` documents the older face-mask
   workflow and refers to legacy dataset paths. It is not the configuration
   source for earbud or scissors; use the commands below for these datasets.

## Server training commands

Run these from `/data2/enoch/ekd_coding_env/jup/yolov5`. The SafeZone runtime is
isolated from the MedDef environment at
`/data2/enoch/.virtualenvs/safezone_yolov5`. It uses Python 3.8 with
PyTorch `1.10.0+cu102`, TorchVision `0.11.1+cu102`, and a compatible Pillow
version. Activate it before running YOLOv5:

```bash
source /data2/enoch/.virtualenvs/safezone_yolov5/bin/activate
python -c 'import torch, torchvision, cv2, yaml, matplotlib; print("torch", torch.__version__, "torchvision", torchvision.__version__, "CUDA", torch.cuda.is_available(), torch.version.cuda)'
nvidia-smi
```

PyTorch 1.10's TensorBoard integration expects `distutils.version` to have
already been imported. Define this helper once in the shell before running
training, validation, or inference, so commands work without modifying the
shared YOLOv5 checkout:

```bash
yolo_run() {
  python -c 'import distutils.version, runpy, sys; script = sys.argv[1]; sys.argv = [script] + sys.argv[2:]; runpy.run_path(script, run_name="__main__")' "$@"
}
```

Check CUDA NMS and GPU availability before training. GPU 2 is reserved and had
an unidentified process holding memory during the earlier check; do not use it.
GPU 3 was freed by pausing the checkpointed MedDef run and is the selected GPU
for SafeZone. Recheck `nvidia-smi` before launching:

```bash
python -c 'import torch; from torchvision.ops import nms; b=torch.tensor([[0.,0.,2.,2.],[1.,1.,3.,3.]],device="cuda:3"); s=torch.tensor([.9,.8],device="cuda:3"); print("GPU 3 NMS:", nms(b,s,.5).tolist())'
nvidia-smi
```

Run a one-epoch smoke test first, using a distinct output directory:

```bash
yolo_run train.py --data data/sz-mod.yaml --weights yolov5s.pt \
  --img 640 --batch-size 4 --epochs 1 --device 3 --workers 0 \
  --project runs/train --name sz-mod-smoke-pillowfix
```

The smoke test completed successfully on GPU 3, including validation on all 70
validation images. An empty validation label file was reported for one image;
confirm that this image intentionally contains no target objects. The successful
test artifacts are in `runs/train/sz-mod-smoke-pillowfix/`. The first smoke
attempt exposed an incompatibility between this YOLOv5 revision and Pillow 10;
the isolated environment was pinned to Pillow 9.5.0. The installed Pillow is
also part of the isolated environment and does not change MedDef dependencies.

After confirming the smoke-test artifacts and GPU memory use, start full
training with the conservative batch size for the 15-GB Tesla T4:

```bash
yolo_run train.py --data data/sz-mod.yaml --weights yolov5s.pt \
  --img 640 --batch-size 8 --epochs 100 --device 3 --workers 2 \
  --project runs/train --name sz-mod
```

The run checkpoints will be in `runs/train/sz-mod/weights/`. YOLOv5 saves
`last.pt` and `best.pt` during training by default. After training completes,
if only the selected best checkpoint is required, remove `last.pt` to save
space while keeping `best.pt`. To monitor progress in a second server terminal:

```bash
nvidia-smi
tail -f runs/train/sz-mod/results.csv
```

Validate the selected checkpoint with the validation split:

```bash
yolo_run val.py --data data/sz-mod.yaml \
  --weights runs/train/sz-mod/weights/best.pt --img 640
```

After training and model selection are complete, evaluate the held-out test
split. This reports overall and per-class metrics on the 70 test images; do not
use these metrics to tune the model:

```bash
yolo_run val.py --data data/sz-mod.yaml --weights runs/train/sz-mod/weights/best.pt --img 640 --task test --device 3
```

For project status commands and a map of the files involved, see the
[SafeZone project guide](../docs/README.md). The completed run's test metrics
and output location are recorded there.

## Before training on the server

- Confirm `train`, `val`, and `test` paths resolve and each split has images and
  matching labels.
- Confirm `data/sz-mod.yaml` reports `nc: 2` with class order `scissors`,
  `earbuds`.
- Visually inspect representative annotations and audit near-duplicate or
  augmentation lineage across the inherited splits before training.
- Check GPU availability and choose a batch size that fits.
- Keep run names/checkpoints separate; do not overwrite existing project runs.
- Confirm the Roboflow license/attribution requirements before redistributing
  or deploying either dataset/model.

## Exploratory 70/15/15 experiment

The original combined dataset remains unchanged at `datasets/sz-mod/`. The
separate `datasets/sz-mod-70-15-15/` variant contains 622/133/134 images in
train/validation/test, generated with seed 42 and class-presence
stratification. Its test images come from the already-used dataset and are not
an independent final test set. Of the original 70 test images, 46 moved into new training, 12 into
validation, and 12 remain in this variant's test split.

To regenerate locally from the original combined dataset, then transfer the
new directory to `ci2p`, run:

```bash
python datasets/split_sz_mod.py --seed 42
scp -r datasets/sz-mod-70-15-15 enoch@ci2p:/data2/enoch/ekd_coding_env/jup/yolov5/datasets/
```

From the YOLOv5 checkout on `ci2p`, after activating the SafeZone runtime and
defining `yolo_run`, run the controlled 100-epoch YOLOv5s experiment:

```bash
yolo_run train.py --data datasets/sz-mod-70-15-15/data.yaml \
  --weights yolov5s.pt --img 640 --batch-size 8 --epochs 100 \
  --device 3 --workers 2 --patience 20 --seed 42 \
  --project runs/train --name sz-mod-s-70-15-15-100-20261110
```

The separate run at `runs/train/sz-mod-s-70-15-15-100-20261110/` completed all
100 epochs and preserves prior checkpoints and metrics. Compare its validation
metrics to the original run; interpret its test metrics as exploratory only.
See the [project guide](../docs/README.md) for status commands.

The isolated runtime passed CUDA NMS on GPU 3, and the YOLOv5 data loader found
749 train, 70 validation, and 70 test images with no missing or corrupt images.
A one-epoch smoke training and validation run completed successfully. The
100-epoch `sz-mod` run has since been launched on GPU 3. See the
[SafeZone project guide](../docs/README.md) for current run details and status
commands.
