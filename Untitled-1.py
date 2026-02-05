 def display_image_on_canvas(self):
        if not self.processor or self.processor.current_image is None:
            return

        img_rgb = cv2.cvtColor(self.processor.current_image, cv2.COLOR_BGR2RGB)
        pil = Image.fromarray(img_rgb)

        cw, ch = self.canvas.winfo_width(), self.canvas.winfo_height()
        if cw > 1 and ch > 1:
            pil.thumbnail((cw - 10, ch - 10))

        self.display_image = ImageTk.PhotoImage(pil)
        self.canvas.delete("all")
        self.canvas.create_image(cw // 2, ch // 2, image=self.display_image)


def main():
    root = TkinterDnD.Tk() if DND_AVAILABLE else tk.Tk()
    ImageApp(root)
    root.mainloop()
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


if __name__ == "__main__":
    main()
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
        }def reset_to_original(self):
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

        if DND_AVAILABLE:self.canvas.drop_target_register(DND_FILES)
            self.canvas.dnd_bind("<<Drop>>", self._on_drop)
        
        right_frame = ttk.Frame(main_container, width=250)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))
        right_frame.pack_propagate(False)

        self._create_control_panel(right_frame)
        self._create_status_bar()
 def _create_control_panel(self, parent):
        title_label = ttk.Label(parent, text="Image Effects", font=("Arial", 12, "bold"))
        title_label.pack(pady=10)

        ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)

        blur_frame = ttk.LabelFrame(parent, text="Blur Intensity", padding=10)
        blur_frame.pack(fill=tk.X, pady=5)

        self.blur_label = ttk.Label(blur_frame, text="Value: 5")
        self.blur_label.pack()