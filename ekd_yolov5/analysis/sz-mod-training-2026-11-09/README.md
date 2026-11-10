# SafeZone `sz-mod` training and evaluation

This folder contains a local copy of the training, validation, and held-out test
artifacts from the `ci2p` YOLOv5 run completed on 2026-11-09. It is intended for
further analysis; the server remains the source copy.

## Run details

- Dataset: `sz-mod`, 749 train / 70 validation / 70 test images.
- Classes: class 0 `scissors`; class 1 `earbuds`.
- Model initialization: `yolov5s.pt`.
- Training: 100 epochs, 640-pixel images, batch size 8, seed 42, GPU 3 (Tesla T4).
- Best checkpoint: `training/weights/best.pt`.
- Test split: 70 images and 86 object labels.

The training run's validation metrics for the selected best checkpoint were:

| Class | Images | Labels | Precision | Recall | mAP@0.5 | mAP@0.5:0.95 |
|---|---:|---:|---:|---:|---:|---:|
| All | 70 | 83 | 0.903 | 0.817 | 0.850 | 0.549 |
| Scissors | 70 | 31 | 0.994 | 1.000 | 0.995 | 0.718 |
| Earbuds | 70 | 52 | 0.813 | 0.635 | 0.705 | 0.381 |

Final held-out test results for `best.pt`:

| Class | Images | Labels | Precision | Recall | mAP@0.5 | mAP@0.5:0.95 |
|---|---:|---:|---:|---:|---:|---:|
| All | 70 | 86 | 0.815 | 0.729 | 0.764 | 0.475 |
| Scissors | 70 | 30 | 0.940 | 0.900 | 0.951 | 0.673 |
| Earbuds | 70 | 56 | 0.691 | 0.559 | 0.577 | 0.277 |

Metrics are proportions (for example, mAP@0.5 0.764 is 76.4%). The held-out
test set is small, so treat these as an initial estimate rather than a precise
generalization guarantee. Scissors detection is substantially stronger than
earbuds detection; inspect the saved predictions and confusion matrix and
review class-specific data coverage before drawing conclusions or changing the
model. This test split was reused during earlier model comparisons; use fresh,
independent data for any final performance claim.

## Exploratory 70/15/15 dataset split

A separate YOLOv5s run completed 100 epochs using 622/133/134 train/validation/
test images. The results and artifacts are in
[`split-70-15-15-2026-11-10/`](./split-70-15-15-2026-11-10/), and the complete
dataset split is in [`../../datasets/sz-mod-70-15-15/`](../../datasets/sz-mod-70-15-15/).
Its test metrics are exploratory only because the new split reuses images
whose old validation/test results were already examined. Do not compare its
test scores directly to the original runs' scores. Of the original 70 test
images, 46 moved into new training, 12 into validation, and 12 remain in the
new test split.

## Local results retained

- `training/`: complete YOLOv5 run artifacts, including `results.csv`, plots,
  configuration YAMLs, TensorBoard event data, validation prediction images,
  and the selected `weights/best.pt` checkpoint.
- `test-evaluation/`: plots and prediction/label visualizations from the final
  held-out test evaluation (`runs/val/exp2` on the server), plus
  `metrics.csv` transcribed from the completed evaluation output and the exact
  command/device in `evaluation.txt`.
- `config/sz-mod.yaml`: dataset configuration used by YOLOv5.
- `logs/sz-mod-launch.log`: full training console log.
- `split-70-15-15-2026-11-10/`: second 100-epoch run, with its dataset
  manifest/config, best checkpoint, metrics, logs, and evaluation figures.
- `../../datasets/sz-mod-70-15-15/`: generated alternate dataset and split
  manifest.
- `run-comparison.csv`: per-class validation and test metrics for the two
  retained runs. The test splits differ, so their scores are not directly
  comparable.

The local archive now retains only the original 100-epoch run and the
70/15/15 100-epoch run. Smoke-test, 200-epoch, and 300-epoch result directories
were removed to save space. The original 100-epoch `best.pt` remains the
provisional main-model candidate; the alternate split run's `best.pt` is
preserved separately for analysis.

The local run metrics and configurations can be opened in a spreadsheet or
plotted with Python. TensorBoard event data is also included for scalar and
training-curve inspection. Do not treat generated run outputs as source code.

## Reproduce evaluation on `ci2p`

From the YOLOv5 checkout, activate the isolated SafeZone Python environment and
define the `yolo_run` helper from [`../../docs/README.md`](../../docs/README.md).
Then run the final test evaluation with the saved best checkpoint:

```bash
yolo_run val.py --data data/sz-mod.yaml --weights runs/train/sz-mod/weights/best.pt --img 640 --task test --device 3
```

This writes evaluation plots and prediction images to a new `runs/val/exp*`
directory on the server. It does not retrain the model.
