import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import cv2
import numpy as np
from PIL import Image, ImageTk
import os
from collections import deque
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except Exception:
    DND_AVAILABLE = False


class ImageProcessor:
    """ img handles using OpenCV"""

    def __init__(self, image_path=None):
        self.original_image = None
        self.current_image = None
        self.image_path = image_path

        if image_path:
            self.load_image(image_path)

    def load_image(self, image_path):
        self.original_image = cv2.imread(image_path)
        if self.original_image is None:
            raise ValueError(f"Could not load image from {image_path}")
        self.current_image = self.original_image.copy()
        self.image_path = image_path

    def save_image(self, file_path):
        if self.current_image is None:
            raise ValueError("No image to save")
        if not cv2.imwrite(file_path, self.current_image):
            raise ValueError("Failed to save image")

    def get_image_info(self):
        if self.current_image is None:
            return None
        h, w = self.current_image.shape[:2]
        filename = os.path.basename(self.image_path) if self.image_path else "Unknown"
        return {
            "filename": filename,
            "width": w,
            "height": h,
            "dimensions": f"{w}x{h}"
        }

    def reset_to_original(self):
        self.current_image = self.original_image.copy()

    def grayscale(self):
        gray = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
        self.current_image = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

    def blur(self, intensity):
        intensity = max(3, int(float(intensity)))  # FIX
        if intensity % 2 == 0:
            intensity += 1
        self.current_image = cv2.GaussianBlur(
            self.current_image, (intensity, intensity), 0)



    def edge_detection(self):
        gray = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        self.current_image = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

    def adjust_brightness(self, factor):
        self.current_image = cv2.convertScaleAbs(self.current_image, alpha=factor)

    def adjust_contrast(self, factor):
        self.current_image = cv2.convertScaleAbs(self.current_image, alpha=factor)

    def rotate_image(self, angle):
        if angle == 90:
            self.current_image = cv2.rotate(self.current_image, cv2.ROTATE_90_CLOCKWISE)
        elif angle == 180:
            self.current_image = cv2.rotate(self.current_image, cv2.ROTATE_180)
        elif angle == 270:
            self.current_image = cv2.rotate(self.current_image, cv2.ROTATE_90_COUNTERCLOCKWISE)

    def flip_image(self, direction):
        if direction == "horizontal":
            self.current_image = cv2.flip(self.current_image, 1)
        else:
            self.current_image = cv2.flip(self.current_image, 0)

    def resize_image(self, width, height):
        self.current_image = cv2.resize(self.current_image, (int(width), int(height)))



class ImageHistory:
    def __init__(self, max_history=20):
        self.undo_stack = deque(maxlen=max_history)
        self.redo_stack = deque(maxlen=max_history)

    def save_state(self, image):
        '''Save image state for undo'''
        self.undo_stack.append(image.copy())
        self.redo_stack.clear()

    def undo(self):
        '''undo the last action'''
        if len(self.undo_stack) > 1:
            self.redo_stack.append(self.undo_stack.pop())
            return self.undo_stack[-1].copy()
        return None

    def redo(self):
        '''Redo the last action'''
        if self.redo_stack:
            img = self.redo_stack.pop()
            self.undo_stack.append(img.copy())
            return img.copy()
        return None

    def can_undo(self):
        return len(self.undo_stack) > 1

    def can_redo(self):
        return len(self.redo_stack) > 0

    def clear(self):
        '''Clear history stacks'''
        self.undo_stack.clear()
        self.redo_stack.clear()


class ImageApp:
    
    def __init__(self, root):
        self.root = root
        self.root.title("Image Processing Application")
        self.root.geometry("1200x800")

        self.processor = None
        self.history = ImageHistory()
        self.display_image = None
        self.preview_base = None  # FIX: preview state

        self._create_menu_bar()
        self._create_main_layout()
        self._update_ui_state()
   
    def _create_menu_bar(self):
        ''' this function creates the menu bar and help to getting image from file system '''
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open", command=self.open_image)
        file_menu.add_command(label="Save", command=self.save_image)
        file_menu.add_command(label="Save As", command=self.save_image_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        """after editing image you can undo or redo the changes or reset to original image """
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.undo_action)
        edit_menu.add_command(label="Redo", command=self.redo_action)
        edit_menu.add_separator()
        edit_menu.add_command(label="Reset to Original", command=self.reset_image)

    def _create_main_layout(self):
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        left_frame = ttk.Frame(main_container)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(left_frame, bg="gray20")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.canvas.bind("<Configure>", lambda e: self.display_image_on_canvas())

        if DND_AVAILABLE:
            self.canvas.drop_target_register(DND_FILES)
            self.canvas.dnd_bind("<<Drop>>", self._on_drop)
        
        right_frame = ttk.Frame(main_container, width=250)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))
        right_frame.pack_propagate(False)

        self._create_control_panel(right_frame)
        self._create_status_bar()
        self.display_image_on_canvas() 

    def _create_control_panel(self, parent):
        title_label = ttk.Label(parent, text="Image Effects", font=("Arial", 10, "bold"))
        title_label.pack(pady=10)

        ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)

        blur_frame = ttk.LabelFrame(parent, text="Blur Intensity", padding=10)
        blur_frame.pack(fill=tk.X, pady=5)

        self.blur_label = ttk.Label(blur_frame, text="Value: 5")
        self.blur_label.pack()

        self.blur_scale = ttk.Scale(
            blur_frame, from_=1, to=31, orient=tk.HORIZONTAL,
            command=self._on_blur_change
        )
        self.blur_scale.pack(fill=tk.X, pady=5)
        self.blur_scale.set(5)


        brightness_frame = ttk.LabelFrame(parent, text="Brightness", padding=10)
        brightness_frame.pack(fill=tk.X, pady=5)

        self.brightness_label = ttk.Label(brightness_frame, text="Value: 1.0")
        self.brightness_label.pack()

        self.brightness_scale = ttk.Scale(
            brightness_frame, from_=0.5, to=3.0, orient=tk.HORIZONTAL,
            command=self._on_brightness_change
        )
        self.brightness_scale.pack(fill=tk.X, pady=5)
        self.brightness_scale.set(1.0)


        contrast_frame = ttk.LabelFrame(parent, text="Contrast", padding=10)
        contrast_frame.pack(fill=tk.X, pady=5)

        self.contrast_label = ttk.Label(contrast_frame, text="Value: 1.0")
        self.contrast_label.pack()

        self.contrast_scale = ttk.Scale(
            contrast_frame, from_=0.5, to=3.0, orient=tk.HORIZONTAL,
            command=self._on_contrast_change
        )
        self.contrast_scale.pack(fill=tk.X, pady=5)
        self.contrast_scale.set(1.0)


        ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)

        ttk.Button(parent, text="Grayscale", command=self._apply_grayscale).pack(fill=tk.X, pady=3)
        ttk.Button(parent, text="Edge Detection", command=self._apply_edge_detection).pack(fill=tk.X, pady=3)

        ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)

        ttk.Button(parent, text="Rotate 90°", command=lambda: self._apply_rotation(90)).pack(fill=tk.X, pady=3)
        ttk.Button(parent, text="Rotate 180°", command=lambda: self._apply_rotation(180)).pack(fill=tk.X, pady=3)
        ttk.Button(parent, text="Rotate 270°", command=lambda: self._apply_rotation(270)).pack(fill=tk.X, pady=3)
        ttk.Button(parent, text="Flip Horizontal", command=lambda: self._apply_flip("horizontal")).pack(fill=tk.X, pady=3)
        ttk.Button(parent, text="Flip Vertical", command=lambda: self._apply_flip("vertical")).pack(fill=tk.X, pady=3)

        ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)

        resize_frame = ttk.LabelFrame(parent, text="Resize", padding=10)
        resize_frame.pack(fill=tk.X, pady=5)

        ttk.Label(resize_frame, text="Width:").pack()
        self.resize_width = ttk.Entry(resize_frame)
        self.resize_width.pack(fill=tk.X)

        ttk.Label(resize_frame, text="Height:").pack()
        self.resize_height = ttk.Entry(resize_frame)
        self.resize_height.pack(fill=tk.X)

        ttk.Button(resize_frame, text="Apply Resize", command=self._apply_resize).pack(fill=tk.X, pady=5)

    def _create_status_bar(self):
        self.status_var = tk.StringVar(value="Ready | No image loaded")
        ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN).pack(side=tk.BOTTOM, fill=tk.X)

    def _update_ui_state(self):
        if self.processor and self.processor.current_image is not None:
            info = self.processor.get_image_info()
            self.status_var.set(f"Image: {info['filename']} | Dimensions: {info['dimensions']}")
        else:
            self.status_var.set("Ready | No image loaded")

    # ---------- FILE ----------
    def open_image(self):
        path = filedialog.askopenfilename()
        if not path:
            return
        self._load_image_from_path(path)



    def _parse_drop_files(self, data):
        try:
            items = self.root.tk.splitlist(data)
        except Exception:
            items = [data]

        paths = []
        for item in items:
            item = str(item).strip()
            if item.startswith("{") and item.endswith("}"):
                item = item[1:-1]
            paths.append(item)
        return paths

    def _load_image_from_path(self, path):
        try:
            self.preview_base = None
            self.processor = ImageProcessor(path)
            self.history.clear()
            self.history.save_state(self.processor.current_image)
            self.display_image_on_canvas()
            self._update_ui_state()
        except Exception as e:
            messagebox.showerror("Open image failed", str(e))

    def _on_drop(self, event):
        paths = self._parse_drop_files(getattr(event, "data", ""))
        if not paths:
            return
        path = paths[0]

        if os.path.isdir(path):
            messagebox.showwarning("Drop an image", "Please drop an image file, not a folder.")
            return
        if not os.path.isfile(path):
            messagebox.showwarning("Drop failed", "Dropped item is not a valid file.")
            return

        ext = os.path.splitext(path)[1].lower()
        if ext not in {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".gif", ".webp"}:
            messagebox.showwarning(
                "Unsupported file",
                "Drop a supported image: png, jpg, jpeg, bmp, tif, tiff, gif, webp."
            )
            return

        self._load_image_from_path(path)

    def save_image(self):
        if not self.processor:
            return
        self.processor.save_image(self.processor.image_path)

    def save_image_as(self):
        if not self.processor:
            return
        path = filedialog.asksaveasfilename(defaultextension=".png")
        if path:
            self.processor.save_image(path)
            self.processor.image_path = path

    # ---------- ACTIONS ----------
    def reset_image(self):
        self.processor.reset_to_original()
        self.history.clear()
        self.history.save_state(self.processor.current_image)
        self.preview_base = None
        self.display_image_on_canvas()

    def undo_action(self):
        img = self.history.undo()
        if img is not None:
            self.processor.current_image = img
            self.preview_base = None
            self.display_image_on_canvas()

    def redo_action(self):
        img = self.history.redo()
        if img is not None:
            self.processor.current_image = img
            self.preview_base = None
            self.display_image_on_canvas()

    def _apply_resize(self):
        w = int(self.resize_width.get())
        h = int(self.resize_height.get())
        self.history.save_state(self.processor.current_image)
        self.processor.resize_image(w, h)
        self.preview_base = None
        self.display_image_on_canvas()
        self._update_ui_state()

    def _apply_rotation(self, angle):
        self.preview_base = None
        self.history.save_state(self.processor.current_image)
        self.processor.rotate_image(angle)
        self.display_image_on_canvas()

    def _apply_flip(self, direction):
        self.history.save_state(self.processor.current_image)
        self.processor.flip_image(direction)
        self.preview_base = None
        self.display_image_on_canvas()

    def _apply_grayscale(self):
        self.history.save_state(self.processor.current_image)
        self.processor.grayscale()
        self.preview_base = None
        self.display_image_on_canvas()

    def _apply_edge_detection(self):
        self.history.save_state(self.processor.current_image)
        self.processor.edge_detection()
        self.preview_base = None
        self.display_image_on_canvas()

    # ---------- SLIDERS (FIXED) ----------
    def _on_blur_change(self, value):
        self.blur_label.config(text=f"Value: {int(float(value))}")
        if self.processor:
            if self.preview_base is None:
                self.preview_base = self.processor.current_image.copy()
            self.processor.current_image = self.preview_base.copy()
            self.processor.blur(value)
            self.display_image_on_canvas()

    def _on_brightness_change(self, value):
        value = float(value)
        self.brightness_label.config(text=f"Value: {value:.2f}")
        if self.processor:
            if self.preview_base is None:
                self.preview_base = self.processor.current_image.copy()
            self.processor.current_image = self.preview_base.copy()
            self.processor.adjust_brightness(value)
            self.display_image_on_canvas()

    def _on_contrast_change(self, value):
        value = float(value)
        self.contrast_label.config(text=f"Value: {value:.2f}")
        if self.processor:
            if self.preview_base is None:
                self.preview_base = self.processor.current_image.copy()
            self.processor.current_image = self.preview_base.copy()
            self.processor.adjust_contrast(value)
            self.display_image_on_canvas()

    # ---------- DISPLAY ----------
    def display_image_on_canvas(self):
        self.canvas.delete("all")
        cw, ch = self.canvas.winfo_width(), self.canvas.winfo_height()

        # show text when no image
        if not self.processor or self.processor.current_image is None:
            self.canvas.create_text(
                cw // 2, ch // 2,
                text="Drag & drop an image here\nor File > Open",
                fill="white",
                font=("Arial", 22, "bold"),
                justify="center"
            )
            return

        img_rgb = cv2.cvtColor(self.processor.current_image, cv2.COLOR_BGR2RGB)
        pil = Image.fromarray(img_rgb)

        if cw > 1 and ch > 1:
            pil.thumbnail((cw - 10, ch - 10))

        self.display_image = ImageTk.PhotoImage(pil)
        self.canvas.create_image(cw // 2, ch // 2, image=self.display_image)



def main():
    root = TkinterDnD.Tk() if DND_AVAILABLE else tk.Tk()
    ImageApp(root)
    root.mainloop()



if __name__ == "__main__":
    main()
