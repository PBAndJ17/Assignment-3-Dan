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



if __name__ == "__main__":
    main()
