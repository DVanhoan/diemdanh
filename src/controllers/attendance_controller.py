from __future__ import annotations

from datetime import datetime
from typing import Any
import tkinter as tk
from tkinter import messagebox

import cv2
from PIL import Image, ImageTk

from src.services.attendance_service import AttendanceService
from src.views.attendance_view import AttendanceView as AttendanceActionView


def _resolve_cv2_module():
	if hasattr(cv2, "cvtColor") and hasattr(cv2, "COLOR_BGR2RGB"):
		return cv2

	try:
		from cv2 import cv2 as cv2_native  # type: ignore
		if hasattr(cv2_native, "cvtColor") and hasattr(cv2_native, "COLOR_BGR2RGB"):
			return cv2_native
	except Exception:
		return cv2

	return cv2


class AttendanceController:
	FRAME_INTERVAL_MS = 30

	def __init__(self, app: Any, router: Any) -> None:
		self.app = app
		self.router = router
		self._cv2 = _resolve_cv2_module()
		self.service = AttendanceService(self.app.assets_dir, self.app.project_root)
		self.view: AttendanceActionView | None = None

		self._camera_job: str | None = None
		self._camera_photo: ImageTk.PhotoImage | None = None

		self._recognized_student_id: int | None = None
		self._recognized_student_name: str = ""
		self._recognized_class_name: str = ""

	def build_view(self) -> AttendanceActionView:
		self.view = AttendanceActionView(
			self.app.root,
			on_start_camera=self.on_start_camera,
			on_stop_camera=self.on_stop_camera,
			on_submit_check=self.on_submit_check,
			on_lesson_change=self.on_lesson_change,
			on_back=self.on_back,
			assets_dir=self.app.assets_dir,
		)
		return self.view

	def on_show(self, **_: object) -> None:
		try:
			if self.view is None:
				return

			lesson_options = self.service.get_lesson_options()
			self.view.set_lesson_options(lesson_options)
			if not lesson_options:
				self.view.subject_var.set("")
				self.view.session_time_var.set("Không có buổi học trong cơ sở dữ liệu.")
				return

			self.on_lesson_change(self.view.class_var.get())
			
			# Tự động mở camera khi vào trang
			self.on_start_camera()
		except Exception as e:
			messagebox.showerror("Lỗi khi tải dữ liệu", f"Không thể tải danh sách buổi học: {str(e)}")

	def on_lesson_change(self, lesson_raw: str) -> tuple[bool, str]:
		try:
			if self.view is None:
				return False, "View chưa sẵn sàng."

			lesson_info, err = self.service.get_lesson_info(lesson_raw)
			if lesson_info is None:
				self.view.subject_var.set("")
				self.view.lesson_info_var.set(lesson_raw)
				self.view.session_time_var.set(err or "Không tìm thấy thông tin buổi học.")
				return False, err or "Không tìm thấy thông tin buổi học."

			self.view.subject_var.set(str(lesson_info.get("class_name") or ""))
			subject_name = str(lesson_info.get("subject_name") or "")
			lesson_id = str(lesson_info.get("lesson_id") or "")
			self.view.session_time_var.set(self._format_lesson_time(lesson_info))

			lesson_display = f"{subject_name} - {self.view.subject_var.get()}" if subject_name else lesson_raw
			if lesson_id:
				lesson_display = f"{lesson_display} (ID: {lesson_id})"
			self.view.lesson_info_var.set(lesson_display)
			return True, "Đã cập nhật thông tin buổi học."
		except Exception as e:
			messagebox.showerror("Lỗi cập nhật thông tin buổi học", f"Có lỗi xảy ra: {str(e)}")
			return False, str(e)

	@staticmethod
	def _format_lesson_time(lesson_info: dict[str, Any]) -> str:
		date_val = lesson_info.get("date")
		start_val = lesson_info.get("time_start")
		end_val = lesson_info.get("time_end")

		date_text = str(date_val) if date_val is not None else ""
		start_text = str(start_val) if start_val is not None else ""
		end_text = str(end_val) if end_val is not None else ""

		if date_text and (start_text or end_text):
			return f"{date_text} | {start_text} - {end_text}".strip()
		if start_text or end_text:
			return f"{start_text} - {end_text}".strip(" -")
		if date_text:
			return date_text
		return "Chưa có thời gian buổi học."

	def on_back(self) -> None:
		self.on_stop_camera()
		self.router.show("dashboard")

	def on_start_camera(self) -> tuple[bool, str]:
		try:
			ok, msg = self.service.start_camera()
			if not ok:
				return ok, msg

			if self._camera_job is None:
				self._camera_loop()
			return True, "Camera đang chạy."
		except Exception as e:
			messagebox.showerror("Lỗi mở camera", f"Có lỗi xảy ra: {str(e)}")
			return False, str(e)

	def on_stop_camera(self) -> tuple[bool, str]:
		try:
			if self.view is not None and self._camera_job is not None:
				self.view.after_cancel(self._camera_job)
				self._camera_job = None

			self.service.stop_camera()

			if self.view is not None:
				self.view.camera_display.configure(image="", text="[Camera streaming]")

			self._camera_photo = None
			return True, "Đã đóng camera."
		except Exception as e:
			messagebox.showerror("Lỗi đóng camera", f"Có lỗi xảy ra: {str(e)}")
			return False, str(e)

	def _camera_loop(self) -> None:
		if self.view is None:
			return

		frame, result = self.service.read_frame()
		if frame is not None:
			if result is not None:
				x, y, w, h = result.bbox
				if hasattr(self._cv2, "rectangle") and hasattr(self._cv2, "putText"):
					self._cv2.rectangle(frame, (x, y), (x + w, y + h), (67, 205, 128), 2)
					self._cv2.putText(
						frame,
						f"ID:{result.student_id} {result.student_name}",
						(x, max(20, y - 10)),
						getattr(self._cv2, "FONT_HERSHEY_SIMPLEX", 0),
						0.65,
						(67, 205, 128),
						2,
					)

				self._recognized_student_id = result.student_id
				self._recognized_student_name = result.student_name
				self._recognized_class_name = result.class_name

				self.view.student_id_var.set(str(result.student_id))
				self.view.student_name_var.set(result.student_name)
				self.view.time_var.set(datetime.now().strftime("%H:%M:%S"))

				lesson_info, err = self.service.get_lesson_info(self.view.class_var.get())
				if lesson_info is not None:
					self.view.subject_var.set(str(lesson_info.get("class_name") or ""))
					time_start = lesson_info.get("time_start")
					time_end = lesson_info.get("time_end")
					subject_name = str(lesson_info.get("subject_name") or "")
					self.view.session_time_var.set(f"{subject_name}: {time_start} - {time_end}")
				elif err:
					self.view.subject_var.set("")
					self.view.session_time_var.set(err)

			if hasattr(self._cv2, "cvtColor") and hasattr(self._cv2, "COLOR_BGR2RGB"):
				rgb = self._cv2.cvtColor(frame, self._cv2.COLOR_BGR2RGB)
				
				# Resize frame to fit label (keep aspect ratio)
				h, w = rgb.shape[:2]
				max_width = 400
				if w > max_width and hasattr(self._cv2, "resize"):
					ratio = max_width / w
					new_h = int(h * ratio)
					rgb = self._cv2.resize(rgb, (max_width, new_h))
				
				pil_image = Image.fromarray(rgb)
				self._camera_photo = ImageTk.PhotoImage(image=pil_image)
				self.view.camera_display.configure(image=self._camera_photo, text="")

		self._camera_job = self.view.after(self.FRAME_INTERVAL_MS, self._camera_loop)

	def on_submit_check(self, lesson_raw: str, attendance_type: str) -> tuple[bool, str]:
		try:
			if self._recognized_student_id is None:
				return False, "Chưa nhận diện được học sinh nào."

			lesson_info, err = self.service.get_lesson_info(lesson_raw)
			if err is not None or lesson_info is None:
				return False, err or "Không thể đọc thông tin buổi học."

			ok, msg = self.service.submit_attendance(
				student_id=self._recognized_student_id,
				student_name=self._recognized_student_name,
				class_name=self._recognized_class_name,
				lesson_id=int(lesson_info["lesson_id"]),
				attendance_type=attendance_type,
			)
			if ok and self.view is not None:
				self.view.subject_var.set(str(lesson_info.get("class_name") or ""))
				self.view.session_time_var.set(str(lesson_info.get("subject_name") or ""))
				self.view.time_var.set(datetime.now().strftime("%H:%M:%S"))
			return ok, msg
		except Exception as e:
			return False, f"Có lỗi xảy ra: {str(e)}"
