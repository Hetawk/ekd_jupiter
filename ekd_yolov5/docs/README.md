# SafeZone project guide

SafeZone is an intelligent workspace safety and compliance monitoring project.
The current vision model uses YOLOv5 to detect scissors and earbuds; a separate
compliance component will interpret detections against workspace rules.

## Training status

The `sz-mod` training run completed all 100 epochs on `ci2p`, GPU 3, with seed
42, 640-pixel images, and batch size 8. The best checkpoint is
`runs/train/sz-mod/weights/best.pt`; training logs and metrics are in
`runs/train/sz-mod*`.

The best checkpoint was evaluated on the held-out test split (70 images, 86
labels) on GPU 3. Overall metrics: precision 0.815, recall 0.729, mAP@0.5
0.764, and mAP@0.5:0.95 0.475. Per-class mAP@0.5: scissors 0.951; earbuds
0.577. Per-class mAP@0.5:0.95: scissors 0.673; earbuds 0.277. Results are
saved on the server in `runs/val/exp2/`. These were the baseline's initial
held-out results; they were later compared with the 300-epoch run on the same
test set. This set is no longer an untouched final evaluation set.

A local copy of the training, smoke-test, and held-out evaluation artifacts,
including CSVs, plots, configs, logs, TensorBoard events, and checkpoints, is
collected in
[`../analysis/sz-mod-training-2026-11-09/`](../analysis/sz-mod-training-2026-11-09/).
Its README summarizes the metrics and contents.

### 300-epoch follow-up run

A separate 300-epoch comparison run completed on `ci2p`, GPU 3:

- Run name: `sz-mod-300-20261109`
- Initialization: the same pretrained `yolov5s.pt` as the 100-epoch baseline
- Settings: 300 epochs, 640-pixel images, batch size 8, seed 42
- Early stopping: disabled (`--patience 0`) so the requested 300 epochs can run
- Checkpoints and metrics: `runs/train/sz-mod-300-20261109/`
- Console log and PID: `runs/train/sz-mod-300-20261109-launch.log` and
  `runs/train/sz-mod-300-20261109.pid`
- Held-out evaluation: `runs/val/sz-mod-300-test/`

Its best checkpoint improved validation mAP@0.5:0.95 (0.571 vs 0.549 for the
100-epoch run), but the repeated test evaluation did not improve aggregate test
mAP@0.5 (0.724 vs 0.764); test mAP@0.5:0.95 tied at 0.475. Test earbuds AP was
also lower for the 300-epoch checkpoint. Use the 100-epoch `best.pt` as the
current main-model candidate, provisionally. The same 70-image test set was
used to compare both runs, so this is not an unbiased final model-selection
set. Full artifacts and the comparison table are in
[`../analysis/sz-mod-training-2026-11-09/`](../analysis/sz-mod-training-2026-11-09/).

### 200-epoch comparison run

A separate 200-epoch run completed on `ci2p`, GPU 3. Its test metrics did not
exceed the 100-epoch baseline, so the 100-epoch `best.pt` remains the
provisional main-model candidate.

- Run name: `sz-mod-200-20261109`
- Initialization: `yolov5s.pt`
- Settings: 200 epochs, 640-pixel images, batch size 8, seed 42
- Early stopping: disabled (`--patience 0`)
- Checkpoints and metrics: `runs/train/sz-mod-200-20261109/`
- Console log and PID: `runs/train/sz-mod-200-20261109-launch.log` and
  `runs/train/sz-mod-200-20261109.pid`
- Test evaluation: `runs/val/sz-mod-200-test/`
- Local artifacts and comparison: `../analysis/sz-mod-training-2026-11-09/`

The same small 70-image test set was reused for all three runs. These test
comparisons are exploratory, not an unbiased final model selection; a new
independent test set is needed for a final generalization claim.

To conserve space, `last.pt` was removed from the completed 100-, 200-, and
300-epoch runs and the smoke tests after confirming their `best.pt` files.
Only the best checkpoints are retained for these completed runs.

The full run uses `datasets/sz-mod/` and `data/sz-mod.yaml`, with class IDs:

| Class ID | Name |
|---:|---|
| 0 | `scissors` |
| 1 | `earbuds` |

The source datasets are preserved separately under `datasets/scissors/` and
`datasets/earbud/`. The combined dataset has 749 training, 70 validation, and
70 test images. Dataset details and preparation are in
[`../datasets/sz-mod/README.md`](../datasets/sz-mod/README.md) and
[`../datasets/README.md`](../datasets/README.md).

## Connect and prepare the server environment

The YOLOv5 checkout and isolated SafeZone runtime are on `ci2p`:

```bash
ssh ci2p
cd /data2/enoch/ekd_coding_env/jup/yolov5
source /data2/enoch/.virtualenvs/safezone_yolov5/bin/activate
```

The SafeZone environment is separate from the MedDef environment. This YOLOv5
revision also requires `distutils.version` to be imported before its
TensorBoard integration. Define this helper once per shell:

```bash
yolo_run() {
  python -c 'import distutils.version, runpy, sys; script = sys.argv[1]; sys.argv = [script] + sys.argv[2:]; runpy.run_path(script, run_name="__main__")' "$@"
}
```

Check the environment and GPU before training:

```bash
python -c 'import torch, torchvision, PIL; print("torch", torch.__version__, "torchvision", torchvision.__version__, "Pillow", PIL.__version__, "CUDA", torch.cuda.is_available(), torch.version.cuda)'
python -c 'import torch; from torchvision.ops import nms; boxes=torch.tensor([[0.,0.,2.,2.],[1.,1.,3.,3.]],device="cuda:3"); scores=torch.tensor([.9,.8],device="cuda:3"); print("GPU 3 NMS:", nms(boxes,scores,.5).tolist())'
nvidia-smi
```

GPU 2 is reserved. GPU 3 was selected for SafeZone after a checkpointed MedDef
run was paused; recheck it before starting any new run.

## Prepare the combined dataset

When rebuilding from the preserved source exports, run this from the local
SafeZone project root after checking that the target directory will not be
overwritten:

```bash
python datasets/prepare_sz_mod.py
```

The preparation script validates the source annotations and split contents,
maps scissors to class 0 and earbuds to class 1, and writes
`datasets/sz-mod/` and `data/sz-mod.yaml`. To intentionally rebuild an existing
dataset, pass `--overwrite`; this replaces the generated combined dataset.
Check the output paths and class mapping before transferring or training.

## Smoke test and full training

The one-epoch smoke test has completed successfully on GPU 3, including
validation. It produced checkpoints under
`runs/train/sz-mod-smoke-pillowfix/`. One validation image has an empty label
file; verify that this is intentional.

The completed 100-epoch baseline training command was:

```bash
yolo_run train.py --data data/sz-mod.yaml --weights yolov5s.pt \
  --img 640 --batch-size 8 --epochs 100 --device 3 --workers 2 \
  --patience 20 --seed 42 --project runs/train --name sz-mod
```

This command was used for the completed baseline training run; do not run it
again with the same name. It writes to `runs/train/sz-mod/`. YOLOv5 stores
`weights/best.pt` there, along with `results.csv`, plots, and the run
configuration. YOLOv5 writes a temporary `last.pt` while training; after a run
finishes, remove `last.pt` if only the selected `best.pt` is needed.

For a future separate experiment, choose a new `RUN_NAME` so the existing run
is preserved:

```bash
RUN_NAME=sz-mod-next
test ! -e "runs/train/$RUN_NAME" || { echo "Run already exists: $RUN_NAME" >&2; exit 1; }
yolo_run train.py --data data/sz-mod.yaml --weights yolov5s.pt \
  --img 640 --batch-size 8 --epochs 100 --device 3 --workers 2 \
  --patience 20 --seed 42 --project runs/train --name "$RUN_NAME"
```

## Exploratory 70/15/15 split

The current combined dataset uses 749/70/70 images (about 84/8/8). An
exploratory alternative was generated with seed 42, stratified by the classes
present in each image: 622 train, 133 validation, and 134 test images. It is
stored separately under `datasets/sz-mod-70-15-15/`; the original
`datasets/sz-mod/` and its checkpoints are unchanged.

The 70/15/15 test split is not an independent final test: its images are
repartitioned from the existing dataset, whose original test images were
already used in model comparisons. Of the original 70 test images, 46 moved
into new training, 12 into validation, and 12 remain in the new test split.
Use these results only as exploratory evidence. To regenerate this variant
from the original combined dataset:

```bash
python datasets/split_sz_mod.py --seed 42
```

The YOLOv5s experiment completed 100 epochs on GPU 3 as
`sz-mod-s-70-15-15-100-20261110`, using a distinct run name and the alternate
dataset config:

```bash
yolo_run train.py --data datasets/sz-mod-70-15-15/data.yaml \
  --weights yolov5s.pt --img 640 --batch-size 8 --epochs 100 \
  --device 3 --workers 2 --patience 20 --seed 42 \
  --project runs/train --name sz-mod-s-70-15-15-100-20261110
```

This keeps model size and training settings aligned with the existing YOLOv5s
baseline so the split change is the main experimental difference. The larger
validation set selects `best.pt`; do not present this split's test metrics as
an unbiased final generalization estimate.

The run completed all 100 epochs. On its 133-image validation split, the best
checkpoint scored P 0.879, R 0.833, mAP@0.5 0.860, and mAP@0.5:0.95 0.577. On
the 134-image exploratory test split, it scored P 0.900, R 0.851, mAP@0.5
0.893, and mAP@0.5:0.95 0.618. These test results are not directly comparable
to the earlier run because the test images differ and include images already
used in the previous comparisons. The full per-class report and artifacts are
in the [70/15/15 analysis archive](../analysis/sz-mod-training-2026-11-09/split-70-15-15-2026-11-10/README.md).

Monitor this run from the YOLOv5 checkout:

```bash
RUN_NAME=sz-mod-s-70-15-15-100-20261110
ps -p "$(cat "runs/train/$RUN_NAME.pid")" -o pid,etime,stat
nvidia-smi -i 3
tail -n 5 "runs/train/$RUN_NAME/results.csv"
tail -n 20 "runs/train/$RUN_NAME-launch.log"
```

## Check training status

Run these commands from the YOLOv5 checkout on `ci2p`:

```bash
ps -p "$(cat runs/train/sz-mod.pid)" -o pid,etime,stat
nvidia-smi -i 3
tail -n 5 runs/train/sz-mod/results.csv
```

`results.csv` contains completed-epoch metrics. To see the latest batch and
epoch progress from the live log, run:

```bash
tail -f runs/train/sz-mod-launch.log
```

Press Ctrl+C to stop watching the log; this does not stop training. For a
continuously refreshing GPU view, use `watch -n 30 nvidia-smi -i 3`.
For this completed run, `ps` no longer shows the training process. The best
checkpoint and completed-epoch metrics are in `runs/train/sz-mod/`.

## Resume an interrupted run

If training is interrupted and `last.pt` exists, first confirm the old process
has stopped and GPU 3 is available, then resume from the checkpoint:

```bash
yolo_run train.py --resume runs/train/sz-mod/weights/last.pt --device 3
```

Do not delete or replace the run directory before checking its checkpoints and
logs. If the checkpoint is missing or the resume command fails, preserve the
directory and investigate the error rather than starting over in the same path.

## Validate and run inference

The held-out test evaluation for both current runs is complete. The test set
has now been used for comparison, so do not use it to tune further runs; use
new independent test data for the next unbiased final comparison. To reproduce
the recorded test evaluation from the server YOLOv5 directory, with the
environment activated and the `yolo_run` helper defined above, run:

```bash
yolo_run val.py --data data/sz-mod.yaml --weights runs/train/sz-mod/weights/best.pt --img 640 --task test
```

This evaluates the 70-image test split and reports overall and per-class
detection metrics. The baseline result is in `runs/val/exp2/`; the 300-epoch
result is in `runs/val/sz-mod-300-test/`. For routine validation during
training, omit `--task test` to use the validation split.

Run inference on an image, video, camera, or directory with the selected
checkpoint:

```bash
yolo_run detect.py --weights runs/train/sz-mod/weights/best.pt \
  --source /path/to/image-or-video --img 640 --conf-thres 0.25
```

Detection alone does not determine whether a policy was violated; that decision
belongs to the separate compliance component.

## Codebase touchpoints

The current model-training workflow uses these project files and locations:

| Purpose | File or directory | Status |
|---|---|---|
| Build the combined dataset and remap class IDs | `datasets/prepare_sz_mod.py` | Implemented; preserves the two source exports |
| Create the exploratory 70/15/15 split | `datasets/split_sz_mod.py` | Reproducible with seed 42; writes a separate dataset and leaves `sz-mod/` unchanged |
| Combined training, validation, and test images/labels | `datasets/sz-mod/` | Prepared; 749 train, 70 validation, 70 test images |
| Dataset paths and class names/order | `data/sz-mod.yaml`, `datasets/sz-mod-70-15-15/data.yaml` | Configured as class 0 `scissors`, class 1 `earbuds`; alternate split is exploratory |
| Generic model training and evaluation | `train.py`, `val.py` | Existing YOLOv5 scripts; invoked with the corresponding dataset YAML, no SafeZone-specific edits required |
| Run outputs and trained checkpoint | `runs/train/sz-mod/`, `runs/train/sz-mod-200-20261109/`, `runs/train/sz-mod-300-20261109/`, and `runs/train/sz-mod-s-70-15-15-100-20261110/` on `ci2p` | All runs complete; the original 100-epoch `best.pt` remains the provisional candidate; the split experiment is separate and exploratory. |
| Generic image/video inference | `detect.py` | Existing YOLOv5 script; can load the trained checkpoint, but is not yet a Jupiter robot integration |

The object-detection model is only one part of the planned system. The current
codebase does not yet include SafeZone-specific Jupiter camera acquisition,
object tracking or workspace-zone logic, compliance rules, audio alerts, or
incident logging. Those should be implemented as separate application
components after evaluating the trained detector; do not treat a detection by
itself as a confirmed policy violation.

## More project information

- [Project background and research direction](./about.md)
- [Server dataset and pipeline notes](../datasets/SERVER_DATASET_SETUP.md)
- [Combined dataset details](../datasets/sz-mod/README.md)
