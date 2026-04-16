import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PLAN_PATH = PROJECT_ROOT / "dataset" / "annotations" / "exercise_dataset_plan.json"
RAW_ROOT = PROJECT_ROOT / "dataset" / "raw_videos"


def main():
    plan = json.loads(PLAN_PATH.read_text())
    created = []

    RAW_ROOT.mkdir(parents=True, exist_ok=True)

    for family in plan["exercise_families"]:
        for exercise_name in family["app_exercises"]:
            target_dir = RAW_ROOT / exercise_name
            target_dir.mkdir(parents=True, exist_ok=True)
            created.append(target_dir)

    print("Created dataset folders:")
    for path in created:
        print(path.relative_to(PROJECT_ROOT))


if __name__ == "__main__":
    main()
