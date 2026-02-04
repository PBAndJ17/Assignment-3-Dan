import os
import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk


# ----------------------------
# Class 1: History (Undo/Redo)
# ----------------------------
class HistoryManager:
    def __init__(self, max_states=30):
        self.undo_stack = []
        self.redo_stack = []
        self.max_states = max_states

    def push(self, image: np.ndarray):
        """Save current state for undo; clear redo stack."""
        if image is None:
            return
        self.undo_stack.append(image.copy())
        if len(self.undo_stack) > self.max_states:
            self.undo_stack.pop(0)
        self.redo_stack.clear()

    def undo(self, current: np.ndarray):
        if not self.undo_stack or current is None:
            return current
        self.redo_stack.append(current.copy())
        return self.undo_stack.pop()

    def redo(self, current: np.ndarray):
        if not self.redo_stack or current is None:
            return current
        self.undo_stack.append(current.copy())
        return self.redo_stack.pop()


# ---------------------------------
# Class 2: Image Processing (OpenCV)
# ---------------------------------
class ImageProcessor:
    def __init__(self):
        self._image = None  # encapsulated image

    def set_image(self, img: np.ndarray):
        self._image = img

    def get_image(self):
        return self._image

    def load(self, path: str) -> np.ndarray:
        img = cv2.imread(path)
        if img is None:
            raise ValueError("Unsupported file or image could not be read.")
        self._image = img
        return img

    def to_grayscale(self) -> np.ndarray:
        return cv2.cvtColor(self._image, cv2.COLOR_BGR2GRAY)

    def gaussian_blur(self, k: int) -> np.ndarray:
        # kernel must be odd and >= 1
        if k < 1:
            k = 1
        if k % 2 == 0:
            k += 1
        return cv2.GaussianBlur(self._image, (k, k), 0)

    def canny_edges(self, low=100, high=200) -> np.ndarray:
        gray = cv2.cvtColor(self._image, cv2.COLOR_BGR2GRAY)
        return cv2.Canny(gray, low, high)

    def adjust_brightness(self, beta: int) -> np.ndarray:
        # beta: -100..100 typical
        return cv2.convertScaleAbs(self._image, alpha=1.0, beta=beta)

    def adjust_contrast(self, alpha: float) -> np.ndarray:
        # alpha: 0.5..3.0 typical
        return cv2.convertScaleAbs(self._image, alpha=alpha, beta=0)

    def rotate(self, angle: int) -> np.ndarray:
        if angle == 90:
            return cv2.rotate(self._image, cv2.ROTATE_90_CLOCKWISE)
        if angle == 180:
            return cv2.rotate(self._image, cv2.ROTATE_180)
        if angle == 270:
            return cv2.rotate(self._image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        raise ValueError("Angle must be 90, 180, or 270.")

    def flip(self, direction: str) -> np.ndarray:
        # horizontal -> 1, vertical -> 0
        if direction == "horizontal":
            return cv2.flip(self._image, 1)
        if direction == "vertical":
            return cv2.flip(self._image, 0)
        raise ValueError("Direction must be 'horizontal' or 'vertical'.")

    def scale(self, factor: float) -> np.ndarray:
        if factor <= 0:
            factor = 1.0
        h, w = self._image.shape[:2]
        new_w = max(1, int(w * factor))
        new_h = max(1, int(h * factor))
        return cv2.resize(self._image, (new_w, new_h), interpolation=cv2.INTER_AREA)


# -----------------------------------
# Class 3: GUI (Tkinter + Interaction)
# -----------------------------------
class ImageEditorGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("HIT137 Image Editor")
        self.root.geometry("1000x650")

        # class interaction
        self.processor = ImageProcessor()
        self.history = HistoryManager()

        self.current_image = None
        self.current_path = None

        self._build_menu()
        self._build_layout()
        self._update_status("No image loaded")

    # ---------- UI BUILD ----------
    def _build_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open", command=self.open_image)
        file_menu.add_command(label="Save", command=self.save_image)
        file_menu.add_command(label="Save As", command=self.save_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.undo)
        edit_menu.add_command(label="Redo", command=self.redo)

    def _build_layout(self):
        # left image display
        self.display_frame = tk.Frame(self.root, padx=10, pady=10)
        self.display_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.image_label = tk.Label(self.display_frame, bg="#222", width=70, height=30)
        self.image_label.pack(fill=tk.BOTH, expand=True)

        # right control panel
        self.panel = tk.Frame(self.root, padx=10, pady=10)
        self.panel.pack(side=tk.RIGHT, fill=tk.Y)

        tk.Label(self.panel, text="Controls", font=("Arial", 14, "bold")).pack(pady=(0, 10))

        tk.Button(self.panel, text="Grayscale", command=self.apply_grayscale).pack(fill=tk.X, pady=2)
        tk.Button(self.panel, text="Edge Detection (Canny)", command=self.apply_edges).pack(fill=tk.X, pady=2)

        tk.Label(self.panel, text="Blur (kernel size)").pack(pady=(10, 0))
        self.blur_slider = tk.Scale(self.panel, from_=1, to=31, orient=tk.HORIZONTAL, command=self.apply_blur)
        self.blur_slider.set(1)
        self.blur_slider.pack(fill=tk.X)

        tk.Label(self.panel, text="Brightness (-100 to 100)").pack(pady=(10, 0))
        self.brightness_slider = tk.Scale(self.panel, from_=-100, to=100, orient=tk.HORIZONTAL, command=self.apply_brightness)
        self.brightness_slider.set(0)
        self.brightness_slider.pack(fill=tk.X)

        tk.Label(self.panel, text="Contrast (0.5 to 3.0)").pack(pady=(10, 0))
        self.contrast_slider = tk.Scale(self.panel, from_=0.5, to=3.0, resolution=0.1,
                                        orient=tk.HORIZONTAL, command=self.apply_contrast)
        self.contrast_slider.set(1.0)
        self.contrast_slider.pack(fill=tk.X)

        tk.Label(self.panel, text="Rotate").pack(pady=(10, 0))
        tk.Button(self.panel, text="Rotate 90°", command=lambda: self.apply_rotate(90)).pack(fill=tk.X, pady=2)
        tk.Button(self.panel, text="Rotate 180°", command=lambda: self.apply_rotate(180)).pack(fill=tk.X, pady=2)
        tk.Button(self.panel, text="Rotate 270°", command=lambda: self.apply_rotate(270)).pack(fill=tk.X, pady=2)

        tk.Label(self.panel, text="Flip").pack(pady=(10, 0))
        tk.Button(self.panel, text="Flip Horizontal", command=lambda: self.apply_flip("horizontal")).pack(fill=tk.X, pady=2)
        tk.Button(self.panel, text="Flip Vertical", command=lambda: self.apply_flip("vertical")).pack(fill=tk.X, pady=2)

        tk.Label(self.panel, text="Resize/Scale").pack(pady=(10, 0))
        tk.Button(self.panel, text="Scale 50%", command=lambda: self.apply_scale(0.5)).pack(fill=tk.X, pady=2)
        tk.Button(self.panel, text="Scale 150%", command=lambda: self.apply_scale(1.5)).pack(fill=tk.X, pady=2)

        # status bar
        self.status = tk.Label(self.root, text="", anchor="w")
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

    # ---------- HELPERS ----------
    def _ensure_image_loaded(self):
        if self.current_image is None:
            messagebox.showerror("Error", "No image loaded. Please open an image first.")
            return False
        return True

    def _update_status(self, text: str):
        self.status.config(text=text)

    def _set_image(self, img: np.ndarray):
        """Update current image + processor image + display + status."""
        self.current_image = img
        self.processor.set_image(img)
        self._display_image(img)
        self._update_image_info()

    def _update_image_info(self):
        if self.current_image is None:
            self._update_status("No image loaded")
            return
        h, w = self.current_image.shape[:2]
        name = os.path.basename(self.current_path) if self.current_path else "Unsaved image"
        self._update_status(f"{name} | {w} x {h}")

    def _display_image(self, img: np.ndarray):
        # Convert OpenCV image to PIL then to Tkinter image
        if img is None:
            return

        if len(img.shape) == 2:
            rgb = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        else:
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        pil_img = Image.fromarray(rgb)

        # Resize to fit label area (simple approach)
        label_w = 700
        label_h = 550
        pil_img.thumbnail((label_w, label_h))

        self.tk_img = ImageTk.PhotoImage(pil_img)
        self.image_label.config(image=self.tk_img)

    # ---------- FILE MENU ----------
    def open_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp")]
        )
        if not path:
            return

        try:
            img = self.processor.load(path)
            self.current_path = path
            self.history = HistoryManager()  # reset history for new image
            self.history.push(img)
            self._set_image(img)
        except Exception as e:
            messagebox.showerror("Open Error", str(e))

    def save_image(self):
        if not self._ensure_image_loaded():
            return

        if not self.current_path:
            self.save_as()
            return

        try:
            cv2.imwrite(self.current_path, self.current_image)
            messagebox.showinfo("Saved", "Image saved successfully.")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    def save_as(self):
        if not self._ensure_image_loaded():
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPG", "*.jpg"), ("BMP", "*.bmp")]
        )
        if not path:
            return

        try:
            cv2.imwrite(path, self.current_image)
            self.current_path = path
            messagebox.showinfo("Saved", "Image saved successfully.")
            self._update_image_info()
        except Exception as e:
            messagebox.showerror("Save As Error", str(e))

    # ---------- EDIT MENU ----------
    def undo(self):
        if not self._ensure_image_loaded():
            return
        new_img = self.history.undo(self.current_image)
        self._set_image(new_img)

    def redo(self):
        if not self._ensure_image_loaded():
            return
        new_img = self.history.redo(self.current_image)
        self._set_image(new_img)

    # ---------- IMAGE FEATURES ----------
    def apply_grayscale(self):
        if not self._ensure_image_loaded():
            return
        self.history.push(self.current_image)
        img = self.processor.to_grayscale()
        self._set_image(img)

    def apply_edges(self):
        if not self._ensure_image_loaded():
            return
        self.history.push(self.current_image)
        img = self.processor.canny_edges()
        self._set_image(img)

    def apply_blur(self, val):
        if not self._ensure_image_loaded():
            return
        self.history.push(self.current_image)
        img = self.processor.gaussian_blur(int(val))
        self._set_image(img)

    def apply_brightness(self, val):
        if not self._ensure_image_loaded():
            return
        self.history.push(self.current_image)
        img = self.processor.adjust_brightness(int(val))
        self._set_image(img)

    def apply_contrast(self, val):
        if not self._ensure_image_loaded():
            return
        self.history.push(self.current_image)
        img = self.processor.adjust_contrast(float(val))
        self._set_image(img)

    def apply_rotate(self, angle):
        if not self._ensure_image_loaded():
            return
        self.history.push(self.current_image)
        img = self.processor.rotate(angle)
        self._set_image(img)

    def apply_flip(self, direction):
        if not self._ensure_image_loaded():
            return
        self.history.push(self.current_image)
        img = self.processor.flip(direction)
        self._set_image(img)

    def apply_scale(self, factor):
        if not self._ensure_image_loaded():
            return
        self.history.push(self.current_image)
        img = self.processor.scale(factor)
        self._set_image(img)


def main():
    root = tk.Tk()
    app = ImageEditorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
