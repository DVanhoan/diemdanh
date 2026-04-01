from __future__ import annotations

import sys
from pathlib import Path


def _ensure_project_root_on_path() -> Path:
	project_root = Path(__file__).resolve().parents[1]
	project_root_str = str(project_root)
	if project_root_str not in sys.path:
		sys.path.insert(0, project_root_str)
	return project_root


def main() -> None:
	project_root = _ensure_project_root_on_path()

	from src.services.face_training_service import FaceTrainingService

	trainer = FaceTrainingService(project_root=project_root)
	ok, msg = trainer.train_lbph_model(output_name="classifier.xml")
	print(msg)
	if not ok:
		raise SystemExit(1)


if __name__ == "__main__":
	main()
