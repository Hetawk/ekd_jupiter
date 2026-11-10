# MaskMonitor: Intelligent Health Safety Robot

## Introduction
The MaskMonitor is an intelligent robotic system designed to enhance health safety and compliance in public and professional environments. Built on computer vision and machine learning, the robot detects whether individuals are wearing face masks and responds in real time. Inspired by the need for automated monitoring during global health crises, MaskMonitor promotes safety awareness while delivering friendly, informative interactions.

By combining mask detection with a robotic platform, MaskMonitor bridges human-robot interaction and public health automation, delivering safety without sacrificing comfort or engagement.

## Purpose
- **Enhance Safety:** Detect and flag individuals without masks inside the monitored area to reduce health risks and maintain institutional standards.
- **Real-Time Interaction:** Provide instant, context-aware feedback via audio or visual cues, reinforcing desired behavior.
- **Improve Compliance:** Encourage cooperation with positive reinforcement and friendly reminders rather than punitive alerts.
- **Reduce Human Effort:** Automate mask monitoring so staff can focus on higher-priority tasks.

## Features
1. **Mask Detection Module**
   - Deep learning-based face detection and mask classification.
   - Training data includes masked and unmasked faces for high accuracy.
   - Real-time frame processing from the robot's camera.
2. **Interactive Communication**
   - Text-to-speech or pre-recorded audio feedback.
   - Positive reinforcement for compliant users and gentle reminders for non-compliance.
   - Optional displays or LEDs augment spoken responses.
3. **Customizable Behavior**
   - Adjustable responses, languages, tones, and detection sensitivity.
4. **Autonomous Operation**
   - Compatible with mobile platforms (e.g., Raspberry Pi-based bases) for patrol or proximity-based interactions.
   - Optional navigation sensors such as ultrasonic or infrared modules.
5. **Data Logging and Analytics (Optional)**
   - Record detections and compliance rates for reporting and trend analysis.

## Applications
1. **Healthcare Facilities**
   - Hospitals and clinics maintain compliance without burdening staff.
   - Can provide additional reminders on hygiene or distancing.
2. **Public and Commercial Spaces**
   - Airports, malls, and schools gain automated compliance assistants.
3. **Corporate Environments**
   - Entry-point screening to maintain workplace safety.
4. **Educational Institutions**
   - Engages students with informative, safety-focused messaging.

## Interaction Flow
1. **Detection Phase:** Continuous scanning to find faces and classify mask usage.
2. **Decision Phase:** Categorize detections into compliant (masked) or non-compliant (unmasked).
3. **Response Phase:**
   - *Compliant:* "Thank you for wearing your mask!" and optional green visual signals.
   - *Non-compliant:* "Please wear your mask to keep everyone safe." with caution visual cues.
4. **Follow-Up Phase (Optional):** Log the event or notify a monitoring system; reposition for clearer communication.

## Future Enhancements
- Emotion recognition for more empathetic engagement.
- Voice command integration.
- Better adaptation to challenging lighting or crowded scenes.
- Additional health monitoring inputs such as temperature or air quality sensors.

## Conclusion
MaskMonitor showcases intelligent, health-conscious automation. By combining real-time vision, machine learning, and robotics, it elevates safety and awareness in public and healthcare settings while laying groundwork for future AI-driven public health systems.

---

## YOLOv5 Facemask Training Workflow

### Repository Setup
```bash
# Optional: ensure pip is current
python -m pip install --upgrade pip

# Install project dependencies inside the active virtual environment
pip install -r requirements.txt
```

### Dataset Check
```bash
# Quick sanity check: load dataset once, build cache, but skip saving checkpoints
python train.py --data dataset/facemask/data.yaml --weights yolov5s.pt --img 640 --batch 8 --epochs 1 --nosave --cache
```

### Full Training Run
```bash
python train.py --data dataset/facemask/data.yaml --weights yolov5s.pt --img 640 --batch 16 --epochs 100 --project runs/train --name facemask

python train.py --data dataset/mask/data.yaml --weights yolov5s.pt --img 640 --batch 16 --epochs 100 --project runs/train --name mask
```
- Outputs live in `runs/train/facemask/`.
- Checkpoints sit in `runs/train/facemask/weights/last.pt` and `runs/train/facemask/weights/best.pt`.

### Validation (Post-Training)
```bash
python val.py --data dataset/facemask/data.yaml --weights runs/train/facemask/weights/best.pt --img 640

python val.py --data dataset/mask/data.yaml --weights runs/train/mask/weights/best.pt --img 640

python val.py --data dataset/mask/data.yaml --weights runs/train/mask3/weights/best.pt --img 640


python val.py --data dataset/mask/data.yaml --weights runs/train/mask100/weights/best.pt --img 640

python val.py --data dataset/mask/data.yaml --weights runs/train/mask200/weights/best.pt --img 640

```

### Inference on Test Images
```bash
python detect.py --weights runs/train/facemask/weights/best.pt --source dataset/facemask/test/images --img 640

python detect.py --weights runs/train/mask100/weights/best.pt --source dataset/mask/test/images --img 640

python detect.py --weights runs/train/mask200/weights/best.pt --source dataset/mask/test/images --img 640
```
- Annotated results save under `runs/detect/` with timestamped subfolders.

### Optional: Export Trained Weights
```bash
python export.py --weights runs/train/facemask/weights/best.pt --include onnx --img 640

python export.py --weights runs/train/mask100/weights/best.pt --include onnx --img 640

python export.py --weights runs/train/mask200/weights/best.pt --include onnx --img 640
```
- Generated export files appear in the same `runs/train/facemask/weights/` directory.

### Housekeeping
- View metrics: `tensorboard --logdir runs/train`.
- Resume training: add `--resume runs/train/facemask/` to the training command.
- Clean checkpoints: remove unwanted runs from `runs/` when storage is tight.
