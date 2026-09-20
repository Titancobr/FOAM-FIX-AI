import os
import sys

import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.config import EXERCISE_CONFIGS


st.set_page_config(page_title="AI Trainer Dashboard", layout="wide")
st.title("AI Pose Detection and Correction")
st.caption("Dataset-trained exercise recognition pipeline with real-time form guidance.")

selected_exercise = st.selectbox(
    "Exercise profile",
    options=list(EXERCISE_CONFIGS.keys()),
    format_func=lambda key: EXERCISE_CONFIGS[key].display_name,
)

exercise = EXERCISE_CONFIGS[selected_exercise]

col1, col2 = st.columns(2)

with col1:
    st.subheader("Real-Time Features")
    st.write(f"Exercise: {exercise.display_name}")
    st.write(f"Tracked angle: {exercise.tracked_angle_label}")
    st.write(f"Rep counter logic: up >= {exercise.up_threshold} deg, down <= {exercise.down_threshold} deg")
    st.write(f"Target muscles: {exercise.muscle_groups}")
    st.write(f"Voice coach focus: {exercise.coaching_focus}")

with col2:
    st.subheader("What The User Sees")
    st.markdown(
        """
        - Live webcam with detected pose skeleton
        - Rep count such as `8 reps done` or `12 reps done`
        - Current movement stage like `up` or `down`
        - Real-time correction cue spoken aloud
        - Exercise tips and tracked joint angle
        """
    )

st.subheader("Recommended Workflow")
st.markdown(
    """
    1. Detect the user and draw a live MediaPipe pose skeleton.
    2. Convert exercise videos into landmark sequences.
    3. Train the temporal model on those sequences.
    4. Run the real-time trainer with skeleton tracking, rep counting, and voice correction.
    """
)

st.code(
    "python training/preprocess_dataset.py\n"
    "python training/train_lstm.py\n"
    f"python main.py --exercise {selected_exercise}",
    language="bash",
)
