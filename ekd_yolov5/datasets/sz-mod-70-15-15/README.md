# Exploratory SafeZone 70/15/15 dataset split

Reproducibly re-split from `../sz-mod/` with seed `42`.
Class IDs: `0` scissors, `1` earbuds. The original dataset is unchanged.

This is an exploratory split, not an independent final test: the original
validation and test images were used in earlier model comparisons. In
particular, 46 of the original 70 test images were assigned to new training,
12 to new validation, and 12 remain in the new test split. Exact duplicate
image content was checked before assignment.

| Split | Images | Scissors images | Earbuds images |
|---|---:|---:|---:|
| train | 622 | 286 | 335 |
| valid | 133 | 61 | 72 |
| test | 134 | 62 | 72 |

Original split redistribution:

| Original split | New train | New validation | New test |
|---|---:|---:|---:|
| train | 532 | 107 | 110 |
| valid | 44 | 14 | 12 |
| test | 46 | 12 | 12 |

The per-image source split and class IDs are recorded in
`split-manifest.csv`. YOLOv5 config: `data.yaml`.
