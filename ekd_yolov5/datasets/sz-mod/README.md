# SafeZone Multi-Object Detection Dataset (sz-mod)

Combined YOLOv5 detection dataset. Source datasets remain unchanged.

Class mapping:
- `0`: scissors (Roboflow scissors dataset, version 2)
- `1`: earbuds (Roboflow Earbud dataset, version 1)

All labels are standard YOLO bounding boxes. Source polygon annotations
are converted to their enclosing normalized boxes, matching YOLOv5's
detection-training behavior; source datasets remain unchanged.

Removed 1 exact duplicate image file(s) within the same split.
No identical image content was found across different splits.

| Split | Images | Scissors instances | Earbud instances |
|---|---:|---:|---:|
| train | 749 | 445 | 418 |
| valid | 70 | 31 | 52 |
| test | 70 | 30 | 56 |

Training configuration: `data/sz-mod.yaml` from the YOLOv5 project root.
Roboflow source licenses and attribution requirements still apply.
