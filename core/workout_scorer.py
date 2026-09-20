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
                "mistake_weighted": Counter(),
                "severity_sum": 0.0,
            }
        return self.exercise_stats[exercise_name]

    def update(self, exercise_name, reps, posture_result):
        stat = self._ensure(exercise_name)
        stat["frames"] += 1
        stat["reps"] = max(stat["reps"], int(reps))

        if posture_result.get("is_good", False):
            stat["good_frames"] += 1
        else:
            severity = int(posture_result.get("severity", 1))
            failed_rules = posture_result.get("failed_rules") or []
            if failed_rules:
                for rule in failed_rules:
                    code = rule.get("mistake_code", "unknown")
                    rule_severity = int(rule.get("severity", severity))
                    stat["mistakes"][code] += 1
                    stat["mistake_weighted"][code] += rule_severity
                    stat["severity_sum"] += rule_severity
            else:
                code = posture_result.get("mistake_code", "unknown")
                stat["mistakes"][code] += 1
                stat["mistake_weighted"][code] += severity
                stat["severity_sum"] += severity

    def build_report(self):
        total_frames = sum(s["frames"] for s in self.exercise_stats.values())
        total_good_frames = sum(s["good_frames"] for s in self.exercise_stats.values())
        total_reps = sum(s["reps"] for s in self.exercise_stats.values())

        global_mistakes = Counter()
        exercise_wise_breakdown = []

        for exercise_name, stat in self.exercise_stats.items():
            accuracy = 0
            if stat["frames"] > 0:
                good_ratio = stat["good_frames"] / stat["frames"]
                severity_ratio = min(1.0, stat["severity_sum"] / (stat["frames"] * 2.5))
                accuracy = round(max(0.0, min(1.0, (0.72 * good_ratio) + (0.28 * (1.0 - severity_ratio)))) * 100)

            top_mistakes = [
                MISTAKE_LABELS.get(code, code)
                for code, _ in sorted(
                    stat["mistakes"].items(),
                    key=lambda item: (stat["mistake_weighted"].get(item[0], 0), item[1]),
                    reverse=True,
                )[:3]
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
            total_severity = sum(s["severity_sum"] for s in self.exercise_stats.values())
            total_good_ratio = total_good_frames / total_frames
            severity_ratio = min(1.0, total_severity / (total_frames * 2.5))
            overall_accuracy = round(max(0.0, min(1.0, (0.72 * total_good_ratio) + (0.28 * (1.0 - severity_ratio)))) * 100)

        return {
            "total_reps": total_reps,
            "accuracy": overall_accuracy,
            "common_mistakes": [
                MISTAKE_LABELS.get(code, code)
                for code, _ in global_mistakes.most_common(5)
            ],
            "exercise_wise_breakdown": exercise_wise_breakdown,
        }
