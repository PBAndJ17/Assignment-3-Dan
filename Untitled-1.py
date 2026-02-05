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
