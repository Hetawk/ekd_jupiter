# SafeZone: An Intelligent System for Real-Time Workspace Safety and Compliance Monitoring

## 1. Project Overview

SafeZone is an intelligent, robot-assisted workspace safety and compliance monitoring system designed to use computer vision, multi-object detection, and context-aware decision-making to identify selected objects within a monitored environment and assess their relevance to predefined workspace safety policies.

The project addresses the need for more consistent and continuous observation of workplace conditions. In many operational environments, safety requirements govern the tools, equipment, personal devices, and activities permitted in particular areas. However, relying exclusively on manual supervision or periodic inspections may make it difficult to identify every situation that requires attention.

SafeZone proposes an automated visual monitoring approach in which a camera mounted on a Jupiter robot observes a designated workspace. The captured video frames are processed using a YOLOv5-based multi-object detection model trained to recognize selected workspace-related objects.

The initial implementation focuses on two object categories: **scissors and earbuds**. These categories represent different monitoring scenarios. Scissors are potentially hazardous tools whose placement may need to be controlled, while earbuds are personal electronic devices that may be restricted in environments where awareness of surrounding sounds and communication are important.

However, SafeZone is not intended to generate warnings merely because an object is detected. Instead, detected objects are passed to a separate compliance assessment component, which evaluates their location, persistence, and relevant visual context against predefined workspace rules.

For example, scissors detected in an approved storage location should not automatically trigger an alert. Similarly, the presence of earbuds on a table does not establish that a person is wearing them. The system must distinguish between object presence and the specific condition that a workspace policy prohibits.

When a violation is sufficiently established according to the configured rules, SafeZone is designed to issue an audio warning and record the incident for subsequent review.

The broader objective is to demonstrate how multi-object detection, robotic vision, spatial analysis, and rule-based decision-making can be integrated into an intelligent system for real-time workspace safety and compliance monitoring.

## 2. Background and Motivation

Workplace safety and operational compliance are important considerations in environments where tools, equipment, and personal devices are used regularly. Depending on the nature of the environment, certain objects may need to be stored in designated locations, while particular activities or personal devices may be restricted.

Maintaining these requirements can be challenging when monitoring depends entirely on human observation. Supervisors may not continuously observe every part of a workspace, and periodic inspections may fail to identify situations that occur between inspection periods.

Examples of situations that may require attention include:

- Potentially hazardous tools being left in inappropriate locations.
- Restricted objects being introduced into designated work areas.
- Personal electronic devices being used in environments where their use is prohibited.
- Safety-related conditions remaining unnoticed until someone intervenes.

These situations motivate the development of monitoring systems that can observe workspace conditions and identify situations that may require human attention.

Recent developments in computer vision and deep learning have made automated object detection increasingly practical. Object detection models can identify objects within images and video streams, estimate their locations, and provide confidence scores for their predictions.

When integrated with robotic vision, these capabilities can support automated observation of physical environments. However, recognizing an object is not sufficient to determine whether a safety violation has occurred. The system must also interpret the detection in relation to the object's location, the surrounding environment, and the applicable workspace policies.

SafeZone is proposed as an implementation of this approach, combining YOLOv5-based object detection with workspace analysis and rule-based compliance assessment on a Jupiter robotic platform.

## 3. Problem Statement

Many workspaces operate under safety and compliance requirements governing the placement, presence, and use of particular objects. Maintaining these requirements through manual supervision alone can be difficult, especially in environments where activities occur continuously and multiple objects are present.

Conventional monitoring approaches may not provide continuous observation or immediate identification of every relevant condition. Furthermore, simply detecting an object does not provide sufficient information to determine whether its presence or use represents a violation.

For example, scissors may be permitted in one workspace area but restricted in another. Likewise, earbuds may be allowed in certain situations but prohibited during activities that require personnel to remain attentive to surrounding sounds.

There is therefore a need for a monitoring approach that combines object recognition with contextual analysis and predefined compliance rules.

SafeZone addresses this problem by proposing a robotic vision system that detects selected objects, evaluates their relevance to workspace policies, and provides notifications when configured compliance conditions are met.

## 4. Aim and Objectives

### 4.1 Overall Aim

To design and implement an intelligent robotic vision system capable of detecting selected workspace objects in real time and assessing their relevance to predefined safety and compliance requirements.

### 4.2 Specific Objectives

1. To develop a unified multi-object detection dataset by combining existing scissors and earbuds image datasets.
2. To train and evaluate a YOLOv5-based object detection model capable of recognizing the selected object categories.
3. To integrate the trained detection model with the Jupiter robot's camera system for visual monitoring of a designated workspace.
4. To develop a rule-based monitoring mechanism that evaluates detected objects according to predefined workspace safety and compliance policies.
5. To incorporate spatial and temporal analysis where necessary to improve the reliability of compliance decisions.
6. To implement an audio notification mechanism for communicating confirmed compliance violations.
7. To maintain incident records containing relevant detection and monitoring information.
8. To evaluate the system in terms of detection performance, processing speed, monitoring reliability, and alert effectiveness.

## 5. Proposed Research Questions

The project will be guided by the following research questions:

1. How effectively can a YOLOv5-based multi-class detection model identify scissors and earbuds within a combined detection dataset?
2. How can object detection be integrated with robotic vision to support continuous workspace observation?
3. How can spatial and contextual information be used to distinguish ordinary object presence from potential workspace compliance violations?
4. To what extent can temporal monitoring and rule-based decision-making improve the reliability of automated compliance assessment?
5. What detection and processing performance can be achieved when deploying the system on the Jupiter robot?
6. How reliably can the integrated system identify configured violations and generate appropriate audio notifications?

These questions connect the computer vision component with the broader objective of intelligent workspace monitoring.

## 6. Proposed System Architecture

SafeZone is designed around five interconnected functional components.

### 6.1 Visual Acquisition

The visual acquisition component obtains images or video frames from a camera mounted on the Jupiter robot.

The camera provides the visual information required to monitor the designated workspace. The captured frames are passed to the detection component for analysis.

The camera interface will depend on the actual hardware and software configuration supported by the Jupiter robot.

### 6.2 Multi-Object Detection

The detection component uses a YOLOv5-based model trained on the combined sz-mod dataset.

The initial model recognizes two object categories:

- Class 0: scissors
- Class 1: earbuds

For each detection, the model provides the predicted object class, confidence score, and bounding-box coordinates.

A single multi-class model is used rather than maintaining separate detection models for each category.

### 6.3 Contextual and Workspace Analysis

The contextual analysis component interprets the detection results in relation to the monitored environment.

Its responsibilities may include:

- Determining the location of detected objects.
- Identifying whether an object is inside or outside a designated workspace zone.
- Tracking detections across consecutive frames.
- Assessing whether a relevant condition persists over time.
- Associating detected objects with other visual information where required.

This component is important because object recognition alone cannot establish whether a workspace rule has been violated.

### 6.4 Safety and Compliance Engine

The compliance engine evaluates the contextual information against predefined workspace policies.

Different object categories require different rules.

For example, scissors may be monitored according to their placement, while earbuds may require an additional assessment of whether they are being worn by a person.

The compliance engine determines whether a detected situation is permitted, potentially non-compliant, or sufficiently confirmed to justify an alert.

### 6.5 Response and Incident Management

When a violation is confirmed, the system is designed to:

- Generate an appropriate audio warning.
- Record the incident timestamp.
- Store the detected object category and confidence score.
- Record the relevant workspace zone and violation type.
- Optionally retain an annotated image as supporting evidence.

Alert cooldowns and persistence checks should be used to avoid repeatedly announcing the same incident.

### 6.6 Architectural Design Principle

A central design principle of SafeZone is the separation of object detection from compliance decision-making.

YOLOv5 answers:

**What objects are visible, and where are they located?**

The compliance engine answers:

**Does the detected situation violate a predefined workspace rule?**

This separation allows the system to introduce additional object categories and monitoring policies without requiring a complete redesign of the detection component.

## 7. Dataset Development: sz-mod

### 7.1 Dataset Identity

**Dataset Name:** sz-mod

**Full Name:** SafeZone Multi-Object Detection Dataset

The sz-mod dataset is a unified multi-object detection dataset developed for the SafeZone project. It was created by combining two independently sourced datasets: a scissors detection dataset and an earbuds detection dataset.

The objective of this integration is to provide a single training resource for developing a multi-class object detection model capable of recognizing both categories.

### 7.2 Initial Object Categories

| Class ID | Class Name |
| -------- | ---------- |
| 0        | scissors   |
| 1        | earbuds    |

The class identifiers are standardized across the combined dataset to ensure consistent annotation interpretation during training and evaluation.

### 7.3 Dataset Sources and Preparation

The original scissors and earbuds datasets were exported from Roboflow and retained as separate source datasets.

The combined dataset was prepared using an integration process that:

- Preserves the original source exports.
- Combines images and their corresponding annotations.
- Maps scissors to class ID 0.
- Maps earbuds to class ID 1.
- Converts polygon annotations into enclosing YOLO bounding boxes for object detection.
- Checks for missing labels, invalid coordinates, and exact duplicate images.
- Produces a unified YOLOv5-compatible dataset configuration.

The initial combined dataset contains 889 images.

The source datasets and their recorded export configurations are:

| Source dataset | Images | Recorded preprocessing                                 |
| -------------- | ------ | ------------------------------------------------------ |
| Scissors v2    | 410    | Auto-orientation and resize to 640 × 640 using stretch |
| Earbud v1      | 480    | Resize to 640 × 640 using stretch                      |

The scissors export records horizontal and vertical flipping and random rotation between -15° and +15°. The earbuds export records horizontal and vertical flipping.

These are export-time transformations recorded in the source dataset documentation. They should be distinguished from augmentations performed dynamically during YOLOv5 training.

One exact duplicate scissors image within the training split was removed. No identical image bytes were found across the initial source splits.

### 7.4 Initial Combined Dataset Distribution

The initial combined dataset contains:

| Split      | Images  | Scissors instances | Earbud instances |
| ---------- | ------- | ------------------ | ---------------- |
| Train      | 749     | 445                | 418              |
| Validation | 70      | 31                 | 52               |
| Test       | 70      | 30                 | 56               |
| **Total**  | **889** | **506**            | **526**          |

The two object categories have relatively similar total instance counts in this initial dataset.

### 7.5 Current 70/15/15 Training Split

For the main training experiment, the combined 889-image dataset was repartitioned using a stratified 70/15/15 split with random seed 42.

The resulting distribution is:

| Split      | Images  | Scissors images | Scissors instances | Earbuds images | Earbuds instances | Total instances |
| ---------- | ------- | --------------- | ------------------ | -------------- | ----------------- | --------------- |
| Train      | 622     | 286             | 366                | 335            | 366               | 732             |
| Validation | 133     | 61              | 68                 | 72             | 82                | 150             |
| Test       | 134     | 62              | 72                 | 72             | 78                | 150             |
| **Total**  | **889** | —               | **506**            | —              | **526**           | **1,032**       |

Class-image counts can overlap when an image contains both object categories.

### 7.6 Dataset Integrity and Evaluation Considerations

The source datasets are already processed Roboflow exports rather than untouched original camera images.

The 70/15/15 split was generated by reassigning the existing exported images. It did not first identify and separate all original unaugmented images before applying augmentation.

Consequently, related exported augmentation variants may be distributed across different splits. Some images from the earlier test partition were also used in previous model comparisons.

For this reason, the current test results are exploratory rather than an independent estimate of generalization performance.

A future independent benchmark should use unaugmented source images, split them by original-image identity before augmentation, and apply augmentation only to the training partition. The validation and test partitions should remain free of derived variants from training images.

This dataset-lineage audit is an important remaining research task.

## 8. Model Development and Training

### 8.1 Detection Framework

SafeZone uses the existing YOLOv5 implementation for object detection.

YOLOv5 was selected as the initial detection framework because it provides an established object detection pipeline and supports the training of a single model with multiple object categories.

The project uses YOLOv5s as its initial model candidate.

### 8.2 Multi-Class Training Approach

Instead of training separate models for scissors and earbuds, the two datasets were combined into a single YOLOv5-compatible dataset.

The resulting model is trained to recognize both classes within one detection framework.

The model can produce multiple detections from a single frame, including multiple instances of the same category or instances belonging to different categories.

### 8.3 Current Training Configuration

The main model candidate was trained using the following configuration:

| Setting                    | Value                 |
| -------------------------- | --------------------- |
| Model                      | YOLOv5s               |
| Initialization             | Pretrained yolov5s.pt |
| Dataset                    | sz-mod 70/15/15 split |
| Input image size           | 640 × 640             |
| Epochs                     | 100                   |
| Batch size                 | 8                     |
| Optimizer                  | SGD                   |
| Initial learning rate      | 0.01                  |
| Final learning-rate factor | 0.01                  |
| Momentum                   | 0.937                 |
| Weight decay               | 0.0005                |
| Warmup                     | 3 epochs              |
| Random seed                | 42                    |
| Training hardware          | NVIDIA Tesla T4       |
| Data loader workers        | 2                     |

The YOLOv5 training-time augmentation configuration included HSV transformations, translation, scaling, horizontal flipping, and mosaic augmentation. Vertical flipping and rotation were disabled during this training run.

The selected checkpoint is the best-performing checkpoint produced during the completed training run.

### 8.4 Selected Model Evaluation

The selected best.pt checkpoint produced the following results:

| Split      | Class    | Precision | Recall | mAP\@0.5 | mAP\@0.5:0.95 |
| ---------- | -------- | --------- | ------ | -------- | ------------- |
| Validation | All      | 0.879     | 0.833  | 0.860    | 0.577         |
| Validation | Scissors | 0.943     | 0.971  | 0.957    | 0.727         |
| Validation | Earbuds  | 0.815     | 0.695  | 0.762    | 0.428         |
| Test\*     | All      | 0.900     | 0.851  | 0.893    | 0.618         |
| Test\*     | Scissors | 0.985     | 0.907  | 0.974    | 0.741         |
| Test\*     | Earbuds  | 0.816     | 0.795  | 0.812    | 0.496         |

*The test results are exploratory because the current split reuses images that were examined in earlier experiments.*

The results indicate stronger detection performance for scissors than for earbuds, particularly under the stricter mAP\@0.5:0.95 metric.

The difference between the classes indicates that further investigation may be required to improve earbuds detection. This may involve examining annotation quality, image diversity, challenging examples, and class-specific errors.

The results should be reported separately for both classes rather than relying exclusively on the overall model score.

### 8.5 Inference Performance

During the recorded test evaluation, YOLOv5 reported approximately 8.5 milliseconds of model inference time per image using the NVIDIA Tesla T4 GPU.

This value represents model inference timing under the recorded evaluation configuration. It is not an end-to-end measurement of the Jupiter robot's camera processing, compliance assessment, or audio notification latency.

Real-time deployment performance must be measured separately on the actual robot hardware.

## 9. Object-Specific Workspace Monitoring

### 9.1 Scissors: Workspace Hazard Monitoring

Scissors are potentially hazardous tools, but their presence does not automatically constitute a violation.

SafeZone will evaluate scissors detections according to their location and the applicable workspace policy.

Possible monitoring conditions include:

- Scissors located in an approved storage area.
- Scissors detected within a designated restricted area.
- Scissors remaining in a restricted area beyond a configured duration.

A spatial monitoring component can compare detected object positions with predefined workspace zones.

The system may use the bounding-box centre or bottom-centre point to represent the object's position. The selected method should be validated against the actual camera perspective and workspace geometry.

If the camera moves with the Jupiter robot, zone calibration must account for changes in camera position or orientation.

### 9.2 Earbuds: Personal Device Compliance Monitoring

Earbuds introduce a different type of compliance scenario.

In certain work environments, wearing earbuds may be restricted because personnel need to hear instructions, warnings, machinery, or other environmental sounds.

However, three different conditions must be distinguished:

1. Earbuds are lying on a table.
2. Earbuds are present somewhere within the workspace.
3. A person is actually wearing earbuds.

Only the third condition directly supports a policy that prohibits wearing earbuds.

The existing earbuds detection dataset may teach the model to identify earbuds as objects. It does not automatically provide the ability to determine whether a person is wearing them.

An extended wearing-detection implementation would require suitable images showing people wearing earbuds, appropriate annotations, and a reliable method for associating the detected earbuds with a person's head or ears.

A person detection class or an additional wearing-state analysis component may also be necessary.

Until that functionality has been implemented and evaluated, the project should describe earbuds as an object-detection category rather than claim that the system can recognize prohibited earbud use.

### 9.3 Initial Compliance Policy Examples

| Object or condition          | Monitoring rule              | Possible response                        |
| ---------------------------- | ---------------------------- | ---------------------------------------- |
| Scissors in approved area    | Permitted placement          | No alert                                 |
| Scissors in restricted area  | Restricted placement         | Warning after confirmation               |
| Earbuds in prohibited area   | Prohibited object presence   | Warning if policy requires it            |
| Person wearing earbuds       | Prohibited wearing condition | Warning after wearing state is confirmed |
| Brief or uncertain detection | Insufficient evidence        | Continue monitoring                      |

These are proposed rules and must be configured according to the actual workspace requirements.

## 10. Real-Time Deployment on the Jupiter Robot

The intended deployment platform is a Jupiter robot running Linux.

The training and deployment environments will be separated.

### 10.1 Development and Training Environment

The existing YOLOv5 codebase and the sz-mod dataset are used on the development computer or an appropriate GPU training environment.

The training process produces a best.pt checkpoint that will be selected after model evaluation.

### 10.2 Robot Deployment Environment

The trained checkpoint will be transferred to the Jupiter robot.

The deployment process will involve:

1. Inspecting the robot's Linux distribution and hardware specifications.
2. Identifying its processor architecture, memory, and available acceleration hardware.
3. Establishing the appropriate Python and PyTorch runtime environment.
4. Transferring the trained checkpoint.
5. Loading the model within the existing YOLOv5 implementation.
6. Connecting the inference process to the robot's camera.
7. Testing detection using actual camera frames.
8. Measuring processing speed and operational stability.

The robot does not need the full training dataset to perform inference. It requires the compatible model checkpoint, the relevant application code, configuration, and runtime dependencies.

The existing YOLOv5 project will remain the foundation for implementation. No separate replacement codebase is required.

Model optimization through ONNX or hardware-specific acceleration may be investigated if the initial deployment does not achieve acceptable performance.

## 11. Audio Notification and Incident Management

Audio notifications are intended to communicate confirmed workspace compliance violations.

The system should avoid generating warnings merely because an object is detected. Instead, the compliance engine should first establish that the relevant condition meets the configured violation criteria.

The notification component should incorporate:

- Detection confidence thresholds.
- Persistence checks across consecutive frames.
- Violation confirmation.
- Alert cooldown periods.
- Appropriate warning messages.
- Incident timestamps.
- Object category and confidence.
- Violation type and relevant workspace zone.

Example warning messages include:

- "Warning: Scissors detected in a restricted workspace area."
- "Warning: A prohibited workspace condition has been detected."

The exact messages will depend on the rules implemented.

Incident records can be maintained using a structured file or database. Each record may include the timestamp, detected category, confidence, location, violation type, and optional annotated image evidence.

These records will also support the evaluation of the integrated monitoring system.

## 12. Experimental Evaluation Plan

The project should be evaluated in stages to establish the performance of individual components and the complete system.

### Experiment 1: Multi-Object Detection

**Purpose:** Evaluate the ability of the YOLOv5 model to recognize scissors and earbuds.

Measurements:

- Per-class precision.
- Per-class recall.
- F1-score.
- mAP\@0.5.
- mAP\@0.5:0.95.
- False-positive and false-negative detections.

### Experiment 2: Workspace-Zone Monitoring

**Purpose:** Evaluate whether detected objects are correctly classified as being inside or outside designated workspace areas.

Measurements:

- Zone classification accuracy.
- Incorrect zone assignments.
- Violation detection rate.
- False violation rate.

### Experiment 3: Contextual and Temporal Monitoring

**Purpose:** Evaluate whether the system can distinguish persistent compliance conditions from temporary or uncertain detections.

Measurements:

- Detection persistence.
- Tracking reliability.
- Violation confirmation accuracy.
- Time required to confirm a violation.
- Repeated or unnecessary alerts.

### Experiment 4: Integrated Robotic Monitoring

**Purpose:** Evaluate the complete system on the Jupiter robot.

Measurements:

- End-to-end processing latency.
- Average inference time.
- Frames per second.
- Alert response time.
- False alert rate.
- Missed violation rate.
- Operational stability during extended monitoring.

If earbud-wearing recognition is implemented, it should receive a separate evaluation. Ordinary earbuds object-detection accuracy cannot be used as evidence of wearing-state recognition accuracy.

## 13. Expected Contributions

The intended contributions of SafeZone include:

1. **Unified multi-object detection dataset:** The integration of independently sourced scissors and earbuds datasets into a single YOLOv5-compatible detection resource.
2. **Multi-class detection model:** A unified YOLOv5 model capable of recognizing the initial workspace-related object categories.
3. **Robotic vision integration:** The deployment of an object detection model within a Jupiter robotic monitoring platform.
4. **Context-aware compliance assessment:** A rule-based mechanism that evaluates detected objects according to their location and relevant workspace conditions.
5. **Automated notification and incident recording:** A mechanism for communicating confirmed violations and retaining records for review.
6. **Integrated system evaluation:** An assessment of object detection, spatial monitoring, alert reliability, and real-time deployment performance.

These are the intended contributions. Their final reporting should reflect the capabilities actually implemented and experimentally demonstrated.

## 14. Scope and Limitations

The initial project scope focuses on:

- Two object categories: scissors and earbuds.
- One combined YOLOv5 multi-class detection model.
- A Jupiter robot with a camera.
- Object-specific workspace monitoring policies.
- Spatial and temporal analysis where required.
- Audio notifications for confirmed violations.
- Incident logging and performance evaluation.

Potential limitations include:

1. **Dataset diversity:** The source datasets may not fully represent the lighting, backgrounds, viewpoints, and object appearances of the actual workspace.
2. **Dataset lineage:** The current exported images have not yet undergone a complete cross-split augmentation-lineage audit.
3. **Class-specific detection performance:** The current evaluation indicates weaker earbuds detection than scissors detection.
4. **Lighting and occlusion:** Poor illumination and partial obstruction may reduce detection reliability.
5. **Camera perspective:** Image coordinates do not necessarily correspond directly to physical workspace positions.
6. **Camera movement:** Changes in robot position or orientation may require workspace recalibration.
7. **Earbud-wearing recognition:** Detecting earbuds as objects does not automatically establish that someone is wearing them.
8. **Hardware limitations:** The Jupiter robot's available processing resources may constrain inference speed.
9. **Policy dependence:** Whether a detected condition represents a violation depends on the workspace's actual rules.

SafeZone should be presented as a prototype monitoring and decision-support system, not as a certified replacement for established workplace safety procedures or human supervision.

## 15. Current Development Status

The following table distinguishes completed work from remaining implementation and evaluation tasks.

| Project component                        | Current status |
| ---------------------------------------- | -------------- |
| Project concept and research direction   | Established    |
| Existing YOLOv5 codebase                 | Available      |
| Scissors dataset export                  | Completed      |
| Earbuds dataset export                   | Completed      |
| Combined sz-mod dataset                  | Prepared       |
| Class mapping and annotation integration | Completed      |
| Initial dataset checks                   | Completed      |
| 70/15/15 repartitioning                  | Completed      |
| YOLOv5s training                         | Completed      |
| Selected best.pt checkpoint              | Available      |
| Validation evaluation                    | Completed      |
| Exploratory test evaluation              | Completed      |
| Independent dataset-lineage audit        | Pending        |
| Independent test benchmark               | Pending        |
| Jupiter hardware inspection              | Pending        |
| SafeZone wake/detection/Qwen/TTS demo flow | Implemented; hardware validation pending |
| Jupiter runtime deployment               | Hardware validation pending |
| Live camera integration                  | Implemented in demo launch; hardware validation pending |
| Workspace-zone enforcement               | Pending        |
| Temporal compliance monitoring           | Pending        |
| Audio warning integration                | Implemented through Jupiter `/voiceWords`; hardware validation pending |
| Basic SafeZone event logging              | Implemented; hardware validation pending |
| Integrated robot evaluation              | Pending        |

### SafeZone robot demo flow

The demo is inference-only and uses the existing checkpoint; it does not train a model. Run `docs/safezone.sh` from one terminal to start the Jupiter camera, local multi-phrase wake-word listener, continuous detector, and Jupiter text-to-speech node. Supported phrases include “Hey EKD,” “Hi EKD,” “Hello EKD,” “Hey SafeZone,” “Okay SafeZone,” “SafeZone,” “SafeZone wake up,” and “Wake up SafeZone.” The listener uses the selected PulseAudio microphone by default and reports quiet input or unmatched speech. The camera preview and local scissors/earbuds detection stay active throughout the run. Frames are processed in memory; no image is saved or sent to Qwen until a wake phrase is recognized. Each wake phrase saves and sends one current frame, whether or not a target is detected, so Qwen can return a concise, respectful spoken message (up to 50 words when useful). It may describe clearly visible details such as object location, a person's posture/position, and an unambiguous clothing color. It must not infer identity, gender, movement from a still image, intent, danger, injury, or policy compliance, or associate an object with a person unless that is unmistakably visible. When no target or person-object association is clear, the message should be appreciative and avoid singling anyone out. No workspace policy is configured, so it asks the operator to check local rules rather than claiming an item is prohibited or threatening a report. SafeZone prints concise timestamped status and publishes its spoken response to `/voiceWords`; camera-driver and TTS logs are routed to ROS log files. Wake events, live target detections, image paths, Qwen response/context or API errors, and final spoken messages are appended to `~/.ros/safezone/events/events.jsonl`; wake-triggered stills are saved alongside it with user-only file permissions. Without `EKD_QWEN_API_KEY` or if the Qwen request fails, an appreciative, non-accusatory local message is still spoken. This event log and event images may contain sensitive workspace information; review and remove them according to local policy.

Qwen is not asked to identify people, infer gender, determine whether earbuds are being worn, or decide policy compliance. Full workspace-zone enforcement and live robot validation remain outside the current demo; basic event logging is implemented. For the one-terminal launch command, see [`safezone.sh`](./safezone.sh).

### Current Model Evidence

The current YOLOv5s model was trained for 100 epochs using an NVIDIA Tesla T4 GPU.

Its reported validation results were:

- Overall precision: 0.879
- Overall recall: 0.833
- Overall mAP\@0.5: 0.860
- Overall mAP\@0.5:0.95: 0.577

The exploratory test results were:

- Overall precision: 0.900
- Overall recall: 0.851
- Overall mAP\@0.5: 0.893
- Overall mAP\@0.5:0.95: 0.618

These results describe the trained detector under the recorded evaluation conditions. They do not establish real-time Jupiter performance, workspace compliance accuracy, or end-to-end alert reliability.

## 16. Future Work

Future development may extend SafeZone in several directions:

- Expanding the dataset with additional workspace-related object categories.
- Improving class-specific detection performance through additional data and targeted experiments.
- Collecting independent images from the intended deployment environment.
- Developing more reliable spatial calibration and object tracking.
- Implementing person-associated earbud-wearing recognition.
- Supporting additional workspace policies and restricted zones.
- Investigating optimized inference through ONNX or hardware-specific acceleration.
- Developing a monitoring interface for reviewing incidents and system activity.
- Evaluating the system across different workspace environments.

These extensions should be introduced incrementally and supported by appropriate experiments.

## 17. Conclusion

SafeZone proposes an intelligent approach to workspace safety and compliance monitoring through the integration of computer vision, multi-object detection, robotic vision, and rule-based decision-making.

The project combines independently sourced scissors and earbuds datasets into the sz-mod multi-object detection dataset and uses the resulting training resource to develop a unified YOLOv5 model.

The current development work has established the combined dataset, completed a YOLOv5s training run, and produced initial validation and exploratory test results.

The next stage is to complete the dataset-lineage audit, obtain independent evaluation data, and integrate the trained model with the Jupiter robot's camera system.

Beyond object recognition, the central objective is to develop a system that can interpret visual detections in relation to workspace conditions, apply object-specific compliance rules, and communicate confirmed violations through audio notifications and incident records.

SafeZone therefore investigates how multi-object detection can be extended beyond conventional object recognition to support context-aware monitoring of physical work environments.

---
