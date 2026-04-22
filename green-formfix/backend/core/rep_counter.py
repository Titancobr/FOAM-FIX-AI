from collections import deque


class RepCounter:
    EXERCISE_PROFILES = {
        "bicep_curl": {"min_range": 16.0, "up_floor_offset": 28.0, "down_ceil_offset": 32.0},
        "barbell_curl": {"min_range": 16.0, "up_floor_offset": 28.0, "down_ceil_offset": 32.0},
        "push_up": {"min_range": 14.0, "up_floor_offset": 38.0, "down_ceil_offset": 28.0},
        "pull_up": {"min_range": 14.0, "up_floor_offset": 34.0, "down_ceil_offset": 26.0},
        "lateral_raise": {"min_range": 18.0, "up_floor_offset": 20.0, "down_ceil_offset": 20.0},
        "squat": {"min_range": 18.0, "up_floor_offset": 22.0, "down_ceil_offset": 30.0},
        "barbell_squat": {"min_range": 18.0, "up_floor_offset": 22.0, "down_ceil_offset": 30.0},
    }

    def __init__(
        self,
        exercise_config,
        smoothing_window=5,
        min_transition_frames=1,
        min_rep_gap_frames=6,
        min_required_range=18.0,
    ):
        self.exercise_config = exercise_config
        self.stage = "ready"
        self.counter = 0

        self.metric_history = deque(maxlen=smoothing_window)
        self.delta_history = deque(maxlen=4)
        self.last_smoothed = None

        self.pending_stage = None
        self.pending_frames = 0
        self.bottom_reached = False
        self.frames_since_last_rep = min_rep_gap_frames

        self.min_transition_frames = min_transition_frames
        self.min_rep_gap_frames = min_rep_gap_frames
        profile = self.EXERCISE_PROFILES.get(exercise_config.name, {})
        self.min_required_range = float(profile.get("min_range", min_required_range))
        self.up_floor_offset = float(profile.get("up_floor_offset", 15.0))
        self.down_ceil_offset = float(profile.get("down_ceil_offset", 15.0))

        self.observed_min = None
        self.observed_max = None

    def _smooth_angle(self, raw_angle):
        if self.last_smoothed is None:
            smoothed = raw_angle
        else:
            alpha = 0.45
            smoothed = (alpha * raw_angle) + ((1.0 - alpha) * self.last_smoothed)
        self.last_smoothed = smoothed
        self.metric_history.append(smoothed)
        return smoothed

    def _update_observed_range(self, angle):
        if self.observed_min is None or angle < self.observed_min:
            self.observed_min = angle
        if self.observed_max is None or angle > self.observed_max:
            self.observed_max = angle

    def _effective_thresholds(self):
        base_up = float(self.exercise_config.up_threshold)
        base_down = float(self.exercise_config.down_threshold)

        if self.observed_min is None or self.observed_max is None:
            return base_up, base_down

        observed_range = self.observed_max - self.observed_min
        if observed_range < self.min_required_range:
            return base_up, base_down

        dynamic_up = self.observed_min + (0.78 * observed_range)
        dynamic_down = self.observed_min + (0.28 * observed_range)

        up_threshold = max(dynamic_up, base_up - self.up_floor_offset)
        down_threshold = min(dynamic_down, base_down + self.down_ceil_offset)
        return up_threshold, down_threshold

    def update(self, angles):
        metric_name = self.exercise_config.rep_metric
        raw_angle = float(angles[metric_name])
        angle = self._smooth_angle(raw_angle)
        self._update_observed_range(angle)

        up_threshold, down_threshold = self._effective_thresholds()
        self.frames_since_last_rep += 1

        if len(self.metric_history) >= 2:
            prev = list(self.metric_history)[-2]
            self.delta_history.append(angle - prev)
        avg_delta = sum(self.delta_history) / len(self.delta_history) if self.delta_history else 0.0

        if self.stage == "ready":
            if angle >= up_threshold:
                self.stage = "up"
            elif angle <= down_threshold:
                self.stage = "down"
                self.bottom_reached = True
            return self.counter, self.stage, angle

        target_stage = None
        # Move into the bottom phase only when angle is going down.
        if self.stage == "up" and angle <= down_threshold and avg_delta <= -0.2:
            target_stage = "down"
        # Move into the top phase only when angle is going up.
        elif self.stage == "down" and angle >= up_threshold and avg_delta >= 0.2:
            target_stage = "up"

        if target_stage is None:
            self.pending_stage = None
            self.pending_frames = 0
            return self.counter, self.stage, angle

        if self.pending_stage == target_stage:
            self.pending_frames += 1
        else:
            self.pending_stage = target_stage
            self.pending_frames = 1

        if self.pending_frames >= self.min_transition_frames:
            self.stage = target_stage
            self.pending_stage = None
            self.pending_frames = 0

            if self.stage == "down":
                self.bottom_reached = True
            elif (
                self.stage == "up"
                and self.bottom_reached
                and self.frames_since_last_rep >= self.min_rep_gap_frames
                and self.observed_min is not None
                and self.observed_max is not None
                and (self.observed_max - self.observed_min) >= self.min_required_range
            ):
                self.counter += 1
                self.bottom_reached = False
                self.frames_since_last_rep = 0

        return self.counter, self.stage, angle

    def reset(self):
        self.stage = "ready"
        self.counter = 0
        self.metric_history.clear()
        self.delta_history.clear()
        self.last_smoothed = None
        self.pending_stage = None
        self.pending_frames = 0
        self.bottom_reached = False
        self.frames_since_last_rep = self.min_rep_gap_frames
        self.observed_min = None
        self.observed_max = None
