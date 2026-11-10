I agree with this direction. I think the new title is stronger, more professional, and gives the project room to grow beyond scissors and earbuds.

More importantly, it gives us a clear research identity: an intelligent robotic vision system that observes a workspace, recognizes relevant objects, evaluates predefined safety and compliance rules, and responds when a violation is identified.

We will retain the existing YOLOv5 codebase. We are not creating a new codebase, replacing your existing implementation, or changing the underlying project unnecessarily. Our immediate task is to combine the datasets correctly, train one multi-class detection model, and then integrate the resulting checkpoint into your existing application.

Below is the revised project direction and write-up that we can use as our working foundation.

# SafeZone: An Intelligent System for Real-Time Workspace Safety and Compliance Monitoring

Agreed project title

# SafeZone: An Intelligent System for Real-Time Workspace Safety and Compliance Monitoring

Detection dataset: `sz-mod`

Full dataset name: SafeZone Multi-Object Detection Dataset

Initial detection classes:

- `scissors`
- `earbuds`

Detection framework: YOLOv5

Deployment platform: Jupiter robot running Linux

# 1. Project overview

SafeZone is an intelligent workspace safety and compliance monitoring system designed to use computer vision and robotic technology to identify selected objects and assess their presence or use against predefined workspace safety policies.

The system will use a camera mounted on a Jupiter robot to continuously observe a designated workspace. Video frames captured by the robot will be processed using a YOLOv5-based multi-object detection model trained to recognize relevant objects.

For the initial implementation, the system will focus on two object categories: scissors and earbuds. These objects represent different types of workspace monitoring requirements.

Scissors represent potentially hazardous tools whose placement and presence may need to be monitored within designated work areas. Earbuds represent personal electronic devices that may be restricted in certain environments because their use could reduce awareness of surrounding sounds or interfere with communication.

However, recognizing these objects is only the first stage. The system must also interpret detections in relation to the workspace and its predefined policies.

For example, detecting scissors does not automatically mean that a safety violation has occurred. The system must determine whether the scissors are located within an approved or restricted area. Similarly, detecting earbuds does not automatically establish that someone is wearing them. Additional visual analysis is required if the intended policy concerns earbud use by personnel.

Once a potential violation is identified and confirmed according to the configured rules, SafeZone can generate an audio warning and record the incident for subsequent review.

The overall objective is to demonstrate how intelligent object detection, robotic vision, and rule-based decision-making can be integrated to support continuous workspace safety and compliance monitoring.

# 2. The problem we are addressing

Many workspaces have established safety and operational policies governing the tools, equipment, and personal devices that may be used in particular areas.

Maintaining compliance with these policies can be challenging when monitoring depends entirely on human observation. Supervisors may not continuously observe every part of a workspace, and periodic inspections may fail to identify situations that occur between inspection periods.

Some examples include:

- Potentially hazardous tools being left in inappropriate locations.
- Restricted objects being introduced into designated areas.
- Personnel using personal electronic devices in environments where such use is prohibited.
- Safety-related conditions remaining unnoticed until someone intervenes.

These situations demonstrate the need for a monitoring approach capable of observing workspace conditions continuously and identifying situations that may require attention.

Computer vision offers an opportunity to automate part of this process. By combining object detection with spatial analysis and predefined compliance rules, a monitoring system can identify relevant objects and assess whether their presence or use is consistent with established workspace requirements.

SafeZone is proposed as a practical implementation of this approach using a mobile or stationary robotic vision platform.

# 3. Aim and objectives

Overall aim

To design and implement an intelligent robotic vision system capable of detecting selected workspace objects in real time and assessing their relevance to predefined safety and compliance requirements.

Specific objectives

1. To develop a unified multi-object detection dataset by combining existing scissors and earbuds datasets.
2. To train and evaluate a YOLOv5-based object detection model capable of recognizing the selected object categories.
3. To integrate the trained model with the Jupiter robot's camera system for real-time workspace observation.
4. To develop a rule-based monitoring mechanism that evaluates detected objects according to predefined workspace safety and compliance policies.
5. To implement an audio notification mechanism for communicating confirmed compliance violations.
6. To maintain incident records containing relevant detection and monitoring information.
7. To evaluate the system in terms of detection performance, processing speed, monitoring reliability, and alert effectiveness.

# 4. Proposed system architecture

The system should be understood as five interconnected functional components.

## SafeZone functional architecture

1\. Visual acquisition

Jupiter robot camera captures workspace frames.

2\. Multi-object detection

YOLOv5 detects scissors and earbuds using one trained checkpoint.

3\. Context and workspace analysis

Object location, tracking, persistence, and relevant visual context.

4\. Safety and compliance engine

Applies object-specific rules and determines whether a violation is confirmed.

5\. Response and incident management

Audio warning

Incident log

The important design decision is that object detection and compliance decision-making remain separate.

YOLOv5 identifies what is visible. The compliance engine determines whether the detected situation violates a rule.

This separation makes the system easier to extend. New object classes and safety policies can be introduced without redesigning the entire application.

# 5. Dataset development: sz-mod

The first major development task is to create the combined dataset.

# sz-mod

SafeZone Multi-Object Detection Dataset

The `sz-mod` dataset is a unified multi-object detection dataset for SafeZone,
created by combining independently sourced scissors and earbuds datasets.

[Open scissors Images - Free Download on Magnific (formerly Freepik)](https://images.openai.com/static-rsc-4/bUETJRLgFey00xEqKGBobznkkvZ0ngqldykgrkdPZvyF6DlAn8IixSzFHjlEOKDizZ0gft1bpzEu5biMWcuztI9dRYFhc7K8RczJl-Qtv5JWhKmCjydw7lpvAEc2eISgSYLuW3arBFU2cPQy1Q3ec1iFwlwKYLx6i0sa3YUduAI?purpose=inline)

Class 0: scissors

[Écouteurs sans fil : comment ça marche ?](https://images.openai.com/static-rsc-4/XBTO8Wcmomx_s17tesevQ_g2Q_1Nqoaw0ba8LSy9g8zWZciek-RYEIZzys_W1-tLZoy-7UoX3nEJOkQChj5Z0cAh1ElC74iQNCUlvnyskDUWRU7XSrj3LBAHsmyMuZ1SzopNsY4s9OJnmNahkOulyXv4Us5rVZKjR0pNefFHxHY?purpose=inline)

Class 1: earbuds

Dataset construction

- Original scissors dataset.
- Original earbuds dataset.
- Unified annotations.
- Consistent class identifiers.
- Combined training, validation, and testing partitions.

The two datasets will be integrated into a single YOLOv5-compatible dataset.

The class mapping must be consistent across every annotation:

| Class ID | Class    |
| -------- | -------- |
| 0        | scissors |
| 1        | earbuds  |

The combined dataset will support training one model to recognize both categories.

## Prepared dataset status

The initial combined dataset has been prepared as `datasets/sz-mod/`. The
original Roboflow exports remain unchanged. The combined project configuration
is `data/sz-mod.yaml`, with class 0 mapped to `scissors` and class 1 mapped to
`earbuds`.

| Split | Images | Scissors instances | Earbud instances |
|---|---:|---:|---:|
| Train | 749 | 445 | 418 |
| Validation | 70 | 31 | 52 |
| Test | 70 | 30 | 56 |

Both source exports contain valid YOLO bounding-box rows and polygon rows.
Polygon annotations are converted to their enclosing normalized bounding boxes
for this detection dataset; the source exports remain unchanged. One exact
duplicate scissors image within the training split was deduplicated. No
identical image bytes were found across splits.
The source train/validation/test assignments were preserved; near-duplicate or
augmented-image lineage across splits has not yet been independently audited.

Important dataset preparation requirements:

- Verify that both datasets use compatible YOLO annotation formats.
- Remap the class IDs correctly.
- Inspect bounding boxes and remove invalid annotations.
- Identify duplicate images.
- Check image quality and variation.
- Split original images into training, validation, and testing sets before applying augmentation.
- Check the distribution of images and annotated instances across both classes.

We should also be careful about class imbalance. The combined training split currently has 445 scissors instances and 418
earbud instances, so the object-instance counts are similar. We will still
report per-class metrics and reassess balance using training results.

The fact that earbuds are the primary dataset in terms of size does not necessarily mean that scissors will become a secondary class in the final model.

Both classes must be evaluated independently.

# 6. Model development and training strategy

We will use the YOLOv5 implementation you already have.

The main change is that, instead of training separate models for scissors and earbuds, we will prepare one combined dataset and train a single multi-class detector.

## 6.1 Training approach

The proposed workflow is:

1. Export the scissors dataset.
2. Export the earbuds dataset.
3. Combine their images and annotations.
4. Standardize the class identifiers.
5. Prepare the combined dataset configuration.
6. Train YOLOv5 using both classes.
7. Evaluate the model on the validation and test sets.
8. Save the best-performing checkpoint.

The resulting checkpoint will contain the learned parameters for both object categories.

Expected model output

# best.pt

One trained YOLOv5 checkpoint

`scissors`

Class 0

`earbuds`

Class 1

When the robot receives a camera frame, the model can produce multiple detections. Each detection will have a predicted class, confidence score, and bounding-box coordinates.

The application can then process each detection according to its class.

## 6.2 Training and evaluation considerations

We should begin with YOLOv5s as a practical baseline, but we should not assume it will be the best model for the Jupiter robot. We will evaluate the model's accuracy and deployment performance before making a final choice.

The evaluation should include:

| Metric            | Purpose                                             |
| ----------------- | --------------------------------------------------- |
| Precision         | Measures how often predicted objects are correct    |
| Recall            | Measures how many actual objects are detected       |
| F1-score          | Balances precision and recall                       |
| mAP\@0.5          | Measures detection quality at IoU 0.5               |
| mAP\@0.5:0.95     | Measures performance across multiple IoU thresholds |
| Inference latency | Measures the time required to process a frame       |
| FPS               | Measures the processing rate                        |

We must report results separately for scissors and earbuds, not only an overall model score.

For example, a model might perform very well on earbuds but poorly on scissors. An overall score could hide that weakness.

We should also test the model on images from the actual Jupiter robot camera. Dataset performance alone does not guarantee reliable performance in the deployment environment.

# 7. How the system will interpret scissors and earbuds

This is a central part of the project. The two classes have different meanings and therefore require different compliance rules.

## 7.1 Scissors: workspace hazard monitoring

Scissors are potentially hazardous tools, but their presence is not automatically a safety violation.

The system should determine whether their location or handling conflicts with the workspace's defined rules.

For example:

- Scissors in an approved storage area: no alert.
- Scissors in a designated restricted area: potential violation.
- Scissors remaining in a restricted area beyond a configured duration: confirmed violation, if that is the applicable policy.

The system can use bounding-box coordinates, workspace-zone calibration, and temporal tracking to make this assessment.

One technical consideration is that a bounding box does not directly establish the precise physical location of an object. We should therefore define how the object's position is represented, such as using its centre or bottom-centre point, and validate that choice against the camera's perspective.

## 7.2 Earbuds: workspace compliance monitoring

Earbuds introduce a different compliance scenario.

In some work environments, wearing earbuds may be prohibited because personnel need to hear instructions, warnings, machinery, or other environmental sounds.

However, we must distinguish three situations:

1. Earbuds are lying on a table.
2. Earbuds are somewhere inside the workspace.
3. A person is actually wearing earbuds.

Only the third situation directly supports a rule that prohibits wearing earbuds.

This distinction has an important consequence for our implementation:

If your existing earbuds dataset mainly contains product images of individual earbuds, the resulting model will learn to detect earbuds as objects. It will not automatically learn to recognize whether a person is wearing them.

We have two possible development stages:

- Initial implementation: Detect earbuds as objects and monitor their presence in designated areas.
- Extended implementation: Detect whether earbuds are being worn by a person and evaluate that condition against workspace policy.

For the extended implementation, we would need appropriate images showing people wearing earbuds and a reliable way to associate the detected earbuds with a person's head or ears. A person class, additional detection annotations, or a separate wearing-state analysis component may be necessary.

I would not claim earbud-wearing recognition in the research report until that capability has been implemented and evaluated.

## 7.3 Proposed compliance rules

The following table gives us an initial policy framework.

| Object or condition              | Monitoring rule              | System response                          |
| -------------------------------- | ---------------------------- | ---------------------------------------- |
| Scissors in approved area        | Permitted placement          | No alert                                 |
| Scissors in restricted area      | Restricted placement         | Warning after confirmation               |
| Earbuds lying in prohibited area | Prohibited object presence   | Warning if policy requires it            |
| Person wearing earbuds           | Prohibited wearing condition | Warning after wearing state is confirmed |
| Object detected briefly          | Insufficient persistence     | Continue monitoring                      |

These rules are examples. We should define the actual approved and restricted areas and prohibited activities based on the intended workspace policy.

The system should not generate alarms merely because it recognizes an object.

# 8. Real-time operation on the Jupiter robot

After training and evaluating the model outside the robot, we will deploy the resulting checkpoint to the Jupiter robot.

The deployment approach remains the one we previously discussed:

Development environment

1. Prepare the combined `sz-mod` dataset.
2. Train the YOLOv5 model.
3. Evaluate and select the best checkpoint.

best.pt

Jupiter robot

1. Inspect its Linux hardware and software environment.
2. Install compatible inference dependencies.
3. Transfer the checkpoint into your existing project.
4. Load the model and connect it to the robot's camera.
5. Test real-time inference.

We must first establish the robot's processor architecture, available acceleration hardware, memory, and camera interface.

The trained `.pt` file is generally portable between machines when the model architecture and software dependencies are compatible. However, we should test checkpoint loading on the robot before assuming that the training environment and deployment environment will work identically.

If the robot cannot achieve adequate processing speed, we can investigate ONNX or hardware-specific acceleration after the standard model works.

# 9. Audio warnings and incident management

Audio warnings will be an important output of the system, but they must be generated only when the compliance engine determines that a violation has occurred.

The system should not repeatedly announce the same violation every time it processes a video frame.

We should therefore include:

- Detection confidence thresholds.
- Persistence checks across consecutive frames.
- Violation confirmation.
- Alert cooldown periods.
- Incident timestamps.
- Object category and confidence.
- Violation type.
- Relevant workspace zone.
- Optional annotated image evidence.

For example, the system might produce an announcement such as:

- "Warning: Scissors detected in a restricted workspace area."
- "Warning: Earbuds detected in a prohibited workspace condition."

The exact wording will depend on the rules we ultimately implement.

Incident records will also give us evidence for evaluating the system beyond simple object-detection accuracy.

# 10. Experimental evaluation

To make the work academically meaningful, we should evaluate the system in stages rather than only demonstrating that the robot can detect objects.

I recommend four main experiments.

| Experiment                                    | What we evaluate                                                                                   |
| --------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| Experiment 1: Multi-object detection          | How accurately YOLOv5 detects scissors and earbuds                                                 |
| Experiment 2: Workspace-zone monitoring       | How reliably the system identifies objects inside and outside restricted areas                     |
| Experiment 3: Context and temporal monitoring | Whether detections persist and whether the relevant compliance conditions are correctly identified |
| Experiment 4: Integrated robotic monitoring   | End-to-end operation, alert reliability, processing speed, and stability on Jupiter                |

For each experiment, we should record measurable results.

Some useful measures include:

- Per-class precision, recall, F1-score, and mAP.
- False-positive and false-negative detections.
- Workspace violation detection rate.
- False alert rate.
- Time between a confirmed violation and an audio warning.
- Average inference latency and FPS.
- System stability during extended operation.

If we implement earbud-wearing detection, it should have its own evaluation. We should not treat ordinary earbud object-detection accuracy as evidence of wearing-state recognition accuracy.

# 11. Proposed academic report structure

The revised topic supports a conventional and coherent research report.

Chapter One: Introduction

- Background of the study.
- Problem statement.
- Research aim and objectives.
- Research questions.
- Significance of the study.
- Scope and limitations.

Chapter Two: Literature Review

- Computer vision in workspace monitoring.
- Object detection techniques.
- YOLO-based object detection.
- Robotic vision systems.
- Workspace safety and compliance monitoring.
- Rule-based monitoring and alert mechanisms.
- Related research and identified research gap.

Chapter Three: Methodology and System Design

- Overall system methodology.
- Dataset sources and preparation.
- The `sz-mod` dataset.
- YOLOv5 model selection and training.
- Jupiter robot platform.
- Camera acquisition and visual processing.
- Workspace-zone analysis.
- Compliance rule engine.
- Audio warning and incident management.
- Evaluation methodology.

Chapter Four: Implementation

- Dataset integration.
- Model training implementation.
- Model evaluation.
- Deployment on the Jupiter robot.
- Camera integration.
- Multi-object detection.
- Compliance monitoring.
- Audio notification and incident logging.

Chapter Five: Results and Discussion

- Dataset statistics.
- Training and validation results.
- Per-class detection performance.
- Workspace monitoring results.
- Integrated system performance.
- Real-time processing performance.
- Discussion of limitations and challenges.

Chapter Six: Conclusion and Future Work

- Summary of the work.
- Findings in relation to the objectives.
- Contributions.
- Limitations.
- Future improvements.

# 12. Scope and limitations

We should keep the initial project achievable and avoid expanding it beyond what we can implement and evaluate properly.

The initial scope will focus on:

- Two object categories: scissors and earbuds.
- One combined YOLOv5 detection model.
- One Jupiter robot with a camera.
- Object-specific workspace monitoring rules.
- Audio warnings for confirmed violations.
- Incident logging and performance evaluation.

Potential limitations include:

1. Dataset diversity: The original datasets may not fully represent real workspace conditions.
2. Lighting and occlusion: Objects may be difficult to detect under poor lighting or when partially hidden.
3. Class imbalance: One object category may have significantly more training examples than the other.
4. Camera perspective: Object location in an image may not correspond directly to its physical workspace location.
5. Earbud-wearing recognition: Detecting earbuds as objects does not automatically establish that someone is wearing them.
6. Processing limitations: The Jupiter robot's hardware may limit the achievable inference speed.
7. Policy dependence: Whether an object represents a violation depends on the actual workspace rules.

We should also describe SafeZone as a prototype decision-support and monitoring system, not as a certified replacement for workplace safety procedures or human supervision.

# 13. Immediate implementation plan: combining your datasets

Since your YOLOv5 codebase is already available, you can now proceed with dataset integration.

Here is the checklist I recommend following.

## sz-mod dataset preparation checklist

10 of 11 completed

- [x] Export the scissors dataset from Roboflow.
- [x] Export the earbuds dataset from Roboflow.
- [x] Verify image counts and split sizes.
- [x] Check YOLO bounding-box and polygon annotation formats.
- [x] Remap source class IDs consistently.
- [x] Combine images and annotations into `datasets/sz-mod/`.
- [x] Check missing/orphan labels, invalid coordinates, and exact duplicates.
- [ ] Audit near-duplicate/augmentation lineage across inherited splits. Existing
  source partitions were preserved, and no identical image bytes cross splits.
- [x] Verify that both classes are represented in every split.
- [x] Prepare and validate `data/sz-mod.yaml`.
- [x] Visually inspect representative combined annotations before training.

A few important points before you start:

- Keep the two original datasets unchanged as backups.
- Preserve their original annotations so you can trace any errors back to their sources.
- Do not simply copy the annotation files without checking class IDs. Both datasets may use class ID `0` for their original object. In the combined dataset, scissors must consistently use `0` and earbuds `1`.
- If an image contains both classes, its annotation file must contain both classes with the correct IDs.
- Use the same class order in your dataset configuration and throughout training and evaluation.
- Do not allow augmented versions of an image to leak into another evaluation split.

After the two remaining review tasks, train one model with
`python train.py --data data/sz-mod.yaml` and evaluate each class independently.

# 14. The research story we should maintain

I want to emphasize one thing about the direction of this project.

We should not present SafeZone as simply a system that detects two objects. That would make the research contribution rather limited.

The stronger story is:

SafeZone investigates how real-time multi-object detection can be integrated with robotic vision and context-aware rule-based decision-making to support workspace safety and compliance monitoring.

The contribution is not just recognizing scissors or earbuds. It is the integration of:

1. Multi-object visual recognition.
2. Workspace and contextual analysis.
3. Object-specific compliance rules.
4. Temporal monitoring and violation confirmation.
5. Automated audio notification.
6. Incident recording and system evaluation.

That is the direction I recommend maintaining throughout the implementation and academic report.

Our agreed project identity:

# SafeZone

Project title

SafeZone: An Intelligent System for Real-Time Workspace Safety and Compliance Monitoring

Dataset

`sz-mod`

SafeZone Multi-Object Detection Dataset

Initial detection classes

`scissors` · `earbuds`

Model

One YOLOv5 multi-class model and one final checkpoint.

Deployment

Jupiter robot running Linux.

The two datasets have now been combined in the existing YOLOv5 project. Before
training, complete the remaining visual annotation and split-lineage checks,
then use `data/sz-mod.yaml` so the final model learns both classes in one
checkpoint.