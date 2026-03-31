
from __future__ import annotations

import sys
from pathlib import Path
from src.app import App

def _ensure_project_root_on_path() -> None:
    project_root = Path(__file__).resolve().parents[1]
    project_root_str = str(project_root)
    if project_root_str not in sys.path:
        sys.path.insert(0, project_root_str)


def main() -> None:
    _ensure_project_root_on_path()

    app = App()
    app.run()


if __name__ == "__main__":
    main()
