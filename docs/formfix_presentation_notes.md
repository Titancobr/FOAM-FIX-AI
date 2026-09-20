# FormFix AI Presentation Notes

## 1. Problem Statement
Say:
"The core problem is that many people work out without supervision, so they either use poor form or do not know whether their reps are correct. My project solves this by detecting the exercise, counting repetitions, checking posture, and giving live feedback."

## 2. Why This Project Matters
Say:
"Most existing systems solve only one piece, like recognition or pose estimation. My project combines recognition, correction, reporting, and progress tracking in one end-to-end system."

## 3. Research Papers
Say:
"I studied papers that use MediaPipe, OpenPose, LSTM, BiLSTM, attention, and angle-based correction. From these papers, I adopted landmark extraction, temporal modeling, and posture-rule analysis. I then extended them with rep counting, database tracking, and a full web interface."

If asked why some paper metrics are not exact:
"Some papers clearly reported headline accuracy, while some were more methodology-focused. Wherever a metric was not clearly extractable from the paper text, I marked it honestly instead of inventing a number."

## 4. Dataset
Say:
"The model is trained on pose sequences, not directly on raw videos. Each processed sample is a 30-frame window with 132 features per frame. That is why 19 videos can become 78 processed sequences."

If asked about squat:
"Squat quality depends heavily on viewpoint and dataset balance. In my dataset, squat has fewer samples than push-up, so improving squat means adding better-balanced squat videos and retraining."

## 5. Architecture
Say:
"The system first extracts pose landmarks using MediaPipe. Then it converts them into joint angles and temporal feature sequences. These are passed into sequence models like LSTM, BiLSTM, or Transformer for exercise classification. Once the exercise is known, rep counting and posture correction use exercise-specific logic."

## 6. Why Three Models
Say:
"I used three models for comparison and deployment flexibility. LSTM is the baseline, BiLSTM captures richer time context, and Transformer models full-sequence attention. In live mode, I also added a hybrid strategy so the system can favor the stronger model while still keeping responsiveness."

## 7. Accuracy Slide
Say:
"I measured Top-1 accuracy, Top-3 accuracy, precision, recall, F1-score, and confusion matrix. Top-1 means the model's highest-confidence class must be correct. Top-3 means the true class appears within the top three predictions."

If asked why BiLSTM validation and evaluation differ:
"The 87.72 percent value was a validation accuracy observed during training, while the later evaluation script computed metrics on the processed dataset. So they answer slightly different questions."

If asked why Transformer looks strongest:
"That is the current measured result in the evaluation path. However, I would still validate it on a strict unseen holdout before making a final deployment claim, because very high evaluation accuracy can also indicate that the split needs to be examined carefully."

## 8. Current Contributions
Say:
"My project contribution is not only the classifier. The bigger contribution is the full system: exercise detection, rep counting, posture correction, voice guidance, web UI, and database-backed workout tracking."

## 9. Future Improvements
Say:
"The most important next improvements are better dataset balance, a stricter test split, more exercise classes, and more personalized correction."

## 10. Strong Closing Line
Say:
"So overall, this project turns pose estimation and sequence modeling research into a practical AI trainer that works in real time and can be used as an actual application, not just a research demo."
