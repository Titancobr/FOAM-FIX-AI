import json
from pathlib import Path


TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "utils" / "posture_templates.json"


class PostureAnalyzer:
    def __init__(self):
        if TEMPLATE_PATH.exists():
            self.templates = json.loads(TEMPLATE_PATH.read_text(encoding="utf-8"))
        else:
            self.templates = {"default": {"good_message": "Good form", "rules": []}}

    def _result(self, message, mistake_code="good_form", severity=0):
        return {
            "message": message,
            "mistake_code": mistake_code,
            "is_good": mistake_code == "good_form",
            "severity": severity,
        }

    def _metric_value(self, angles, metric):
        if isinstance(metric, list):
            return [float(angles.get(name, 0.0)) for name in metric]
        return float(angles.get(metric, 0.0))

    def _rule_fails(self, angles, rule):
        metric = self._metric_value(angles, rule["metric"])
        op = rule["op"]
        value = float(rule["value"])

        if op == "lt":
            return metric < value
        if op == "gt":
            return metric > value
        if op == "abs_diff_gt":
            if not isinstance(metric, list) or len(metric) != 2:
                return False
            return abs(metric[0] - metric[1]) > value
        return False

    def analyze(self, exercise, angles):
        exercise_template = self.templates.get(exercise.name) or self.templates.get("default", {})
        rules = exercise_template.get("rules", [])
        good_message = exercise_template.get("good_message", "Good form")

        failed_rules = []
        for rule in rules:
            if self._rule_fails(angles, rule):
                failed_rules.append(rule)

        if not failed_rules:
            return self._result(good_message)

        failed_rules.sort(key=lambda r: int(r.get("severity", 1)), reverse=True)
        top = failed_rules[0]
        return self._result(
            top.get("message", "Adjust your form"),
            top.get("mistake_code", "form_issue"),
            int(top.get("severity", 1)),
        )

    def check_form(self, exercise, angles):
        return self.analyze(exercise, angles)["message"]
