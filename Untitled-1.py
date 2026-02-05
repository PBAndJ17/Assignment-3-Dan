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