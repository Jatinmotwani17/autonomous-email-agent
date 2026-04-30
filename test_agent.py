from __future__ import annotations

import json

from main import run_full_demo


def main() -> None:
    report = run_full_demo(write_outputs=True)
    print("Email Agent test completed.")
    print(json.dumps(report["final_report"], indent=2))


if __name__ == "__main__":
    main()
