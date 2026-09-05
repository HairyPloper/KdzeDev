"""Validate saved workflows without executing nodes or calling model providers.

Usage:
    docker compose exec backend python -m tools.validate_all_yamls
"""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Initialize node registration before importing the configuration checker.
import runtime  # noqa: E402, F401
from check.check import load_config  # noqa: E402


def validate_all() -> int:
    files = sorted((REPO_ROOT / "yaml_instance").rglob("*.yaml"))
    if not files:
        print("No workflow YAML files found.")
        return 1

    failed = 0
    for path in files:
        label = path.relative_to(REPO_ROOT)
        try:
            load_config(path)
        except Exception as exc:
            print(f"FAIL {label}: {exc}")
            failed += 1
        else:
            print(f"PASS {label}")

    print(f"Validated {len(files)} workflow(s): {len(files) - failed} passed, {failed} failed.")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(validate_all())
