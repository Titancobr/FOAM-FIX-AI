from collections import Counter


MISTAKE_LABELS = {
    "good_form": "good form",
    "elbow_instability": "elbow instability",
    "knee_instability": "knee instability",
    "hip_sag": "hip sag",
    "insufficient_depth": "insufficient depth",
    "too_deep": "too deep",
    "incomplete_contraction": "incomplete contraction",
    "incomplete_lockout": "incomplete lockout",
    "overflexion": "overflexion",
    "overfolding": "over-folding",
}


class WorkoutScorer:
    def __init__(self):
        self.exercise_stats = {}

    def _ensure(self, exercise_name):
        if exercise_name not in self.exercise_stats:
            self.exercise_stats[exercise_name] = {
                "frames": 0,
                "good_frames": 0,
                "reps": 0,
                "mistakes": Counter(),
            }
        return self.exercise_stats[exercise_name]

    def update(self, exercise_name, reps, posture_result):
        stat = self._ensure(exercise_name)
        stat["frames"] += 1
        stat["reps"] = max(stat["reps"], int(reps))

        if posture_result.get("is_good", False):
            stat["good_frames"] += 1
        else:
            code = posture_result.get("mistake_code", "unknown")
            stat["mistakes"][code] += 1

    def build_report(self):
        total_frames = sum(s["frames"] for s in self.exercise_stats.values())
        total_good_frames = sum(s["good_frames"] for s in self.exercise_stats.values())
        total_reps = sum(s["reps"] for s in self.exercise_stats.values())

        global_mistakes = Counter()
        exercise_wise_breakdown = []

        for exercise_name, stat in self.exercise_stats.items():
            accuracy = 0
            if stat["frames"] > 0:
                accuracy = round((stat["good_frames"] / stat["frames"]) * 100)

            top_mistakes = [
                MISTAKE_LABELS.get(code, code)
                for code, _ in stat["mistakes"].most_common(3)
            ]
            global_mistakes.update(stat["mistakes"])

            exercise_wise_breakdown.append(
                {
                    "exercise": exercise_name,
                    "reps": stat["reps"],
                    "accuracy": accuracy,
                    "common_mistakes": top_mistakes,
                }
            )

        overall_accuracy = 0
        if total_frames > 0:
            overall_accuracy = round((total_good_frames / total_frames) * 100)

        return {
            "total_reps": total_reps,
            "accuracy": overall_accuracy,
            "common_mistakes": [
                MISTAKE_LABELS.get(code, code)
                for code, _ in global_mistakes.most_common(5)
            ],
            "exercise_wise_breakdown": exercise_wise_breakdown,
        }
