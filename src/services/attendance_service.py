from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
import re

import sys
import cv2

from src.db.database import DatabaseConnection


def _resolve_cv2_module():
	if hasattr(cv2, "CascadeClassifier") and hasattr(cv2, "VideoCapture"):
		return cv2

	try:
		from cv2 import cv2 as cv2_native  # type: ignore
		if hasattr(cv2_native, "CascadeClassifier") and hasattr(cv2_native, "VideoCapture"):
			return cv2_native
	except Exception:  # noqa: BLE001
		return cv2

	return cv2


@dataclass(slots=True)
class RecognitionResult:
	student_id: int
	student_name: str
	class_name: str
	confidence: float
	bbox: tuple[int, int, int, int]


class AttendanceService:
	def __init__(self, assets_dir: Path, project_root: Path) -> None:
		self.db = DatabaseConnection().get_connection()
		self.assets_dir = assets_dir
		self.project_root = project_root
		self._cv2 = _resolve_cv2_module()
		self._lesson_display_to_id: dict[str, int] = {}

		self._capture: Any | None = None

		self._cascade = self._load_cascade()
		self._recognizer = self._load_recognizer()

	def _load_cascade(self):
		if not hasattr(self._cv2, "CascadeClassifier"):
			return None

		cascade_path = self.assets_dir / "haarcascade_frontalface_default.xml"
		if not cascade_path.exists():
			print(f"Cascade file not found at: {cascade_path}")
			return None
		print(f"Loading cascade from: {cascade_path}")
		cascade = self._cv2.CascadeClassifier(str(cascade_path))
		if cascade.empty():
			return None
		return cascade

	def _load_recognizer(self):
		if not hasattr(self._cv2, "face"):
			return None
		if not hasattr(self._cv2.face, "LBPHFaceRecognizer_create"):
			return None

		try:
			recognizer = self._cv2.face.LBPHFaceRecognizer_create()
		except Exception:  # noqa: BLE001
			return None

		model_path = None
		for candidate in (
			self.project_root / "models" / "classifier.xml",
			self.project_root / "models" / "trainer.yml",
		):
			if candidate.exists():
				model_path = candidate
				break

		if model_path is None:
			return None

		try:
			recognizer.read(str(model_path))
		except Exception:  # noqa: BLE001
			return None

		return recognizer

	def start_camera(self) -> tuple[bool, str]:
		if not hasattr(self._cv2, "VideoCapture"):
			return False, "OpenCV chưa sẵn sàng trong môi trường hiện tại."

		if self._capture is not None and self._capture.isOpened():
			return True, "Camera đang chạy."

		def _open(index: int):
			if sys.platform.startswith("win") and hasattr(self._cv2, "CAP_DSHOW"):
				return self._cv2.VideoCapture(index, self._cv2.CAP_DSHOW)
			return self._cv2.VideoCapture(index)

		cap = _open(0)
		if not cap.isOpened():
			cap = _open(1)
		if not cap.isOpened():
			cap = _open(2)
		if not cap.isOpened():
			return False, "Không mở được camera (đã thử 0/1/2)."

		# Some webcams/drivers need explicit settings to start streaming.
		try:
			if hasattr(self._cv2, "CAP_PROP_FRAME_WIDTH"):
				cap.set(self._cv2.CAP_PROP_FRAME_WIDTH, 640)
				cap.set(self._cv2.CAP_PROP_FRAME_HEIGHT, 480)
			if hasattr(self._cv2, "CAP_PROP_FPS"):
				cap.set(self._cv2.CAP_PROP_FPS, 30)
		except Exception:  # noqa: BLE001
			pass

		self._capture = cap
		return True, "Đã mở camera."

	def stop_camera(self) -> tuple[bool, str]:
		if self._capture is not None:
			self._capture.release()
			self._capture = None
		return True, "Đã đóng camera."

	def read_frame(self) -> tuple[Any | None, RecognitionResult | None]:
		if self._capture is None or not self._capture.isOpened():
			return None, None

		ok, frame = self._capture.read()
		if not ok:
			return None, None

		result = self._recognize_face(frame)
		return frame, result

	def _recognize_face(self, frame) -> RecognitionResult | None:
		if self._cascade is None or self._recognizer is None:
			return None
		if not hasattr(self._cv2, "cvtColor") or not hasattr(self._cv2, "COLOR_BGR2GRAY"):
			return None

		gray = self._cv2.cvtColor(frame, self._cv2.COLOR_BGR2GRAY)
		faces = self._cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5)
		if len(faces) == 0:
			return None

		x, y, w, h = max(faces, key=lambda box: box[2] * box[3])
		roi = gray[y:y + h, x:x + w]

		try:
			label, confidence = self._recognizer.predict(roi)
		except Exception:  # noqa: BLE001
			return None

		if confidence > 80:
			return None

		student = self.get_student_by_id(int(label))
		if student is None:
			return None

		return RecognitionResult(
			student_id=student["student_id"],
			student_name=student["name"],
			class_name=student["class_name"],
			confidence=float(confidence),
			bbox=(int(x), int(y), int(w), int(h)),
		)

	def get_student_by_id(self, student_id: int) -> dict[str, Any] | None:
		cursor = self.db.cursor(dictionary=True)
		cursor.execute(
			"SELECT Student_id, Name, Class FROM student WHERE Student_id = %s LIMIT 1",
			(student_id,),
		)
		row = cursor.fetchone()
		cursor.close()

		if not row:
			return None

		return {
			"student_id": int(row["Student_id"]),
			"name": str(row.get("Name") or ""),
			"class_name": str(row.get("Class") or ""),
		}

	def get_student_avatar_path(self, student_id: int) -> Path | None:
		dataset_dir = self.project_root / "dataset"
		if not dataset_dir.exists():
			return None

		candidates = list(dataset_dir.glob(f"User.{student_id}.*.jpg"))
		if not candidates:
			return None

		def _sort_key(path: Path) -> tuple[int, str]:
			match = re.match(rf"^User\.{student_id}\.(\d+)\.jpg$", path.name)
			if match:
				return int(match.group(1)), path.name
			return 10**9, path.name

		return sorted(candidates, key=_sort_key)[0]

	def get_lesson_options(self) -> list[str]:
		cursor = self.db.cursor(dictionary=True)
		cursor.execute(
			"""
			SELECT l.Lesson_id, s.Subject_name, s.Class, c.Name AS ClassName
			FROM lesson l
			JOIN subject s ON s.Subject_id = l.Subject_id
			LEFT JOIN class c ON c.Class = s.Class
			ORDER BY l.Lesson_id DESC
			"""
		)
		rows = cursor.fetchall()
		cursor.close()

		self._lesson_display_to_id = {}
		options: list[str] = []
		for row in rows:
			lesson_id_raw = row.get("Lesson_id")
			if lesson_id_raw is None:
				continue
			lesson_id = int(lesson_id_raw)
			subject_name = str(row.get("Subject_name") or "")
			class_name = str(row.get("ClassName") or row.get("Class") or "")
			display = f"{subject_name} - {class_name}"
			options.append(display)
			if display not in self._lesson_display_to_id:
				self._lesson_display_to_id[display] = lesson_id
		return options

	@staticmethod
	def _extract_lesson_id(lesson_raw: str) -> int:
		lesson_text = (lesson_raw or "").strip()
		if not lesson_text:
			raise ValueError("empty")
		return int(lesson_text)

	def get_lesson_info(self, lesson_raw: str) -> tuple[dict[str, Any] | None, str | None]:
		if not (lesson_raw or "").strip():
			return None, "Vui lòng nhập ID buổi học."

		lesson_text = (lesson_raw or "").strip()
		lesson_id = self._lesson_display_to_id.get(lesson_text)
		if lesson_id is None:
			try:
				lesson_id = self._extract_lesson_id(lesson_text)
			except ValueError:
				return None, "ID buổi học không hợp lệ."

		cursor = self.db.cursor(dictionary=True)
		cursor.execute(
			"""
			SELECT l.Lesson_id, l.Time_start, l.Time_end, l.Date,
				   s.Subject_name, s.Class, c.Name AS ClassName
			FROM lesson l
			JOIN subject s ON s.Subject_id = l.Subject_id
			LEFT JOIN class c ON c.Class = s.Class
			WHERE l.Lesson_id = %s
			LIMIT 1
			""",
			(lesson_id,),
		)
		row = cursor.fetchone()
		cursor.close()

		if not row:
			return None, "Không tìm thấy buổi học với ID đã nhập."

		return {
			"lesson_id": int(row["Lesson_id"]),
			"class_name": str(row.get("ClassName") or row.get("Class") or ""),
			"subject_name": str(row.get("Subject_name") or ""),
			"time_start": row.get("Time_start"),
			"time_end": row.get("Time_end"),
			"date": row.get("Date"),
		}, None

	def submit_attendance(
		self,
		student_id: int,
		student_name: str,
		class_name: str,
		lesson_id: int,
		attendance_type: str,
	) -> tuple[bool, str]:
		now = datetime.now()
		day = now.date()
		now_time = now.time().replace(microsecond=0)

		cursor = self.db.cursor(dictionary=True)
		cursor.execute(
			"""
			SELECT IdAttendance, Time_in, Time_out
			FROM attendance
			WHERE Student_id = %s AND Lesson_id = %s AND Date = %s
			LIMIT 1
			""",
			(student_id, lesson_id, day),
		)
		existing = cursor.fetchone()

		check_type = (attendance_type or "Vào").strip()

		try:
			if existing is None:
				if check_type == "Ra":
					cursor.close()
					return False, "Chưa có bản ghi giờ vào để điểm danh giờ ra."

				att_id = f"ATT-{lesson_id}-{student_id}-{day.strftime('%Y%m%d')}"
				cursor.execute(
					"""
					INSERT INTO attendance
					(IdAttendance, Student_id, Name, Class, Time_in, Time_out, Date, Lesson_id, AttendanceStatus)
					VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
					""",
					(att_id, student_id, student_name, class_name, now_time, None, day, lesson_id, "Vào"),
				)
				self.db.commit()
				cursor.close()
				return True, "Điểm danh vào thành công."

			attendance_id = str(existing["IdAttendance"])
			if check_type == "Vào":
				if existing.get("Time_in") is not None:
					cursor.close()
					return False, "Bản ghi này đã có giờ vào."

				cursor.execute(
					"UPDATE attendance SET Time_in = %s, AttendanceStatus = %s WHERE IdAttendance = %s",
					(now_time, "Vào", attendance_id),
				)
				self.db.commit()
				cursor.close()
				return True, "Cập nhật giờ vào thành công."

			if existing.get("Time_out") is not None:
				cursor.close()
				return False, "Bản ghi này đã có giờ ra."

			cursor.execute(
				"UPDATE attendance SET Time_out = %s, AttendanceStatus = %s WHERE IdAttendance = %s",
				(now_time, "Ra", attendance_id),
			)
			self.db.commit()
			cursor.close()
			return True, "Điểm danh ra thành công."
		except Exception as exc:  # noqa: BLE001
			cursor.close()
			return False, f"Lỗi khi lưu điểm danh: {exc}"
