from __future__ import annotations

from datetime import datetime
from typing import Any
from tkinter import messagebox

import cv2
from PIL import Image, ImageTk

from src.services.attendance_service import AttendanceService
from src.views.attendance_view import AttendanceView


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
		self.view: AttendanceView | None = None

		self._camera_job: str | None = None
		self._camera_photo: ImageTk.PhotoImage | None = None

		self._recognized_student_id: int | None = None
		self._recognized_student_name: str = ""
		self._recognized_class_name: str = ""
		self._recognized_avatar_student_id: int | None = None

	def build_view(self) -> AttendanceView:
		self.view = AttendanceView(
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
				setattr(self.view.camera_display, "image", None)

			self._camera_photo = None
			self._recognized_student_id = None
			self._recognized_student_name = ""
			self._recognized_class_name = ""
			self._recognized_avatar_student_id = None
			if self.view is not None:
				self.view.clear_avatar()
			return True, "Đã đóng camera."
		except Exception as e:
			messagebox.showerror("Lỗi đóng camera", f"Có lỗi xảy ra: {str(e)}")
			return False, str(e)

	def _update_recognized_avatar(self, student_id: int) -> None:
		if self.view is None:
			return
		if self._recognized_avatar_student_id == student_id:
			return

		avatar_path = self.service.get_student_avatar_path(student_id)
		self.view.set_avatar_image(avatar_path)
		self._recognized_avatar_student_id = student_id

	def _camera_loop(self) -> None:
		if self.view is None:
			return

		try:
			# 1. Lấy khung hình và kết quả nhận diện từ Service
			frame, result = self.service.read_frame()

			if frame is None:
				# Nếu không đọc được camera, hiển thị thông báo và tiếp tục lặp
				self.view.camera_display.configure(text="[Không đọc được khung hình]", image="")
				self.view.camera_display.image = None
				self._camera_job = self.view.after(self.FRAME_INTERVAL_MS, self._camera_loop)
				return

			# 2. Vẽ khung nhận diện nếu có kết quả (Logic Giai đoạn 4)
			if result is not None:
				x, y, w, h = result.bbox
				if hasattr(self._cv2, "rectangle"):
					# Vẽ hình chữ nhật bao quanh mặt (Màu xanh lá nhẹ)
					self._cv2.rectangle(frame, (x, y), (x + w, y + h), (67, 205, 128), 2)

					# Hiển thị ID và Tên phía trên khung
					text_display = f"ID:{result.student_id} {result.student_name}"
					self._cv2.putText(
						frame,
						text_display,
						(x, max(20, y - 10)),
						getattr(self._cv2, "FONT_HERSHEY_SIMPLEX", 0),
						0.6,
						(67, 205, 128),
						2,
					)

				# Cập nhật thông tin sinh viên sang bảng bên phải (View)
				self._recognized_student_id = result.student_id
				self._recognized_student_name = result.student_name
				self._recognized_class_name = result.class_name
				self._update_recognized_avatar(result.student_id)


				self.view.student_id_var.set(str(result.student_id))
				self.view.student_name_var.set(result.student_name)
				self.view.time_var.set(datetime.now().strftime("%H:%M:%S"))

			# 3. Xử lý hiển thị ảnh lên giao diện
			if hasattr(self._cv2, "cvtColor") and hasattr(self._cv2, "COLOR_BGR2RGB"):
				# Chuyển từ BGR (OpenCV) sang RGB (PIL)
				rgb = self._cv2.cvtColor(frame, self._cv2.COLOR_BGR2RGB)

				target_w = self.view.camera_container.winfo_width()
				target_h = self.view.camera_container.winfo_height()

				# Nếu widget chưa render xong, dùng kích thước mặc định
				if target_w < 10 or target_h < 10:
					target_w, target_h = 640, 480

				# Tính toán tỷ lệ để giữ nguyên Aspect Ratio (Tỷ lệ khung hình)
				h0, w0 = rgb.shape[:2]
				scale = min(target_w / w0, target_h / h0)
				new_w = max(1, int(w0 * scale))
				new_h = max(1, int(h0 * scale))

				# Resize ảnh về kích thước phù hợp với khung giao diện
				if hasattr(self._cv2, "resize"):
					rgb = self._cv2.resize(rgb, (new_w, new_h))

				# Chuyển đổi sang định dạng ảnh Tkinter
				pil_image = Image.fromarray(rgb)
				photo = ImageTk.PhotoImage(image=pil_image)

				# Cập nhật ảnh lên giao diện
				self._camera_photo = photo
				self.view.camera_display.configure(image=photo, text="")

				# Phải giữ một tham chiếu đến PhotoImage trong object của Tkinter
				self.view.camera_display.image = photo

		except Exception as exc:
			if self.view:
				self.view.camera_display.configure(text=f"[Lỗi camera: {exc}]", image="")

		finally:
			if self.view:
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
