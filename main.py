import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk
import threading
import queue

TARGET_SIZE = (640, 640)

class GifCombinerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GIF Combiner for Kraken LCD")
        self.folder_path = ""
        self.repeat = tk.IntVar(value=1)
        self.mode = tk.StringVar(value='fill')
        self.size_x = tk.IntVar(value=640)
        self.size_y = tk.IntVar(value=640)
        self.trigger = tk.IntVar(value=0)
        self.frames = []
        self.cached_frames = []
        self.is_preloaded = False
        self.frame_mode_cache = {}  # Cache the frames for each mode
        self.current_frame_index = 0
        self.frame_update_queue = queue.Queue()

        self.build_ui()

    def build_ui(self):
        frame = tk.Frame(self.root, padx=10, pady=10)
        frame.pack()

        # Folder selection
        tk.Button(frame, text="Select Folder", command=self.select_folder).grid(row=0, column=0, pady=5)
        self.folder_label = tk.Label(frame, text="No folder selected", width=40, anchor='w')
        self.folder_label.grid(row=0, column=1, pady=5)

        # Repeat
        tk.Label(frame, text="Repeat each frame:").grid(row=1, column=0, pady=5)
        tk.Entry(frame, textvariable=self.repeat, width=5).grid(row=1, column=1, pady=5, sticky='w')

        # Mode
        tk.Label(frame, text="Mode:").grid(row=2, column=0, pady=5)
        mode_menu = ttk.Combobox(frame, textvariable=self.mode, values=['fit', 'fill', 'stretch'], width=10, state="readonly")
        mode_menu.grid(row=2, column=1, pady=5, sticky='w')
        mode_menu.bind("<Enter>", self.show_tooltip)  # Hover for tooltips
        mode_menu.bind("<Leave>", self.hide_tooltip)  # Hide tooltips

        # Size
        tk.Label(frame, text="Width:").grid(row=3, column=0, pady=5)
        tk.Entry(frame, textvariable=self.size_x, width=5).grid(row=3, column=1, pady=5, sticky='w')
        tk.Label(frame, text="Height:").grid(row=4, column=0, pady=5)
        tk.Entry(frame, textvariable=self.size_y, width=5).grid(row=4, column=1, pady=5, sticky='w')

        # Canvas for preview
        self.preview_canvas = tk.Label(self.root)
        self.preview_canvas.pack(pady=10)

        # Tooltip Label for explanation
        self.tooltip_label = tk.Label(self.root, text="", bg="yellow", width=50, height=2, anchor='w')
        self.tooltip_label.pack(pady=5)

        # Save GIF Button
        tk.Button(self.root, text="Save GIF", command=self.save_combined).pack(pady=10)

        # Compression Option
        self.compression_var = tk.IntVar(value=1)
        tk.Checkbutton(self.root, text="Enable Compression", variable=self.compression_var).pack(pady=5)

        # Trigger the preview on mode change
        trigger_vars = [self.repeat, self.mode, self.size_x, self.size_y, self.trigger]
        for var in trigger_vars:
            var.trace_add("write", lambda *args: self.preview_combined())


    def select_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.folder_path = path
            self.folder_label.config(text=os.path.basename(path))
            self.is_preloaded = False
            self.frames = []
            self.cached_frames = []
            self.frame_update_queue = queue.Queue()  # Clear the queue to avoid stale data
            self.load_and_cache_gifs()
            self.root.after(100, self.wait_for_loading)  # Wait for the loading to complete before triggering preview

    def wait_for_loading(self):
        """Wait for the GIF loading thread to complete before triggering the preview."""
        if not self.frame_update_queue.empty():
            self.cached_frames = self.frame_update_queue.get()
            self.is_preloaded = True
            self.trigger.set(1 - self.trigger.get())  # Trigger the preview after loading
        else:
            self.root.after(100, self.wait_for_loading)  # Check again after 100ms

    def process_frame(self, frame, mode):
        target_size = (self.size_x.get(), self.size_y.get())
        frame = frame.convert('RGBA')
        x, y = frame.size

        if mode == 'fit':
            max_side = max(x, y)
            new_im = Image.new('RGBA', (max_side, max_side), (0, 0, 0, 0))
            new_im.paste(frame, ((max_side - x) // 2, (max_side - y) // 2))
            frame = new_im.resize(target_size, Image.LANCZOS)
        elif mode == 'fill':
            if x > y:
                delta = (x - y) // 2
                frame = frame.crop((delta, 0, delta + y, y))
            elif y > x:
                delta = (y - x) // 2
                frame = frame.crop((0, delta, x, delta + x))
            frame = frame.resize(target_size, Image.LANCZOS)
        elif mode == 'stretch':
            frame = frame.resize(target_size, Image.LANCZOS)

        return frame.convert('P', palette=Image.ADAPTIVE, colors=128)

    def load_and_cache_gifs(self):
        gif_files = [f for f in os.listdir(self.folder_path) if f.lower().endswith('.gif')]
        gif_files.sort()
        frames = []

        if not gif_files:
            return frames

        # Run in a separate thread to speed up
        self.is_preloaded = True
        thread = threading.Thread(target=self._load_gifs, args=(gif_files,))
        thread.daemon = True
        thread.start()

    def _load_gifs(self, gif_files):
        frames = []
        for gif_file in gif_files:
            gif_path = os.path.join(self.folder_path, gif_file)
            gif = Image.open(gif_path)

            try:
                while True:
                    frame = gif.copy()
                    for mode in ['fit', 'fill', 'stretch']:
                        if mode not in self.frame_mode_cache:
                            self.frame_mode_cache[mode] = []
                        processed_frame = self.process_frame(frame, mode)
                        self.frame_mode_cache[mode].append(processed_frame)
                    for _ in range(self.repeat.get()):
                        frames.append(frame)
                    gif.seek(gif.tell() + 1)
            except EOFError:
                pass

        self.frames = frames
        self.frame_update_queue.put(self.frame_mode_cache['fit'])  # Default to fit for initial preview

    def preview_combined(self):
        if not self.folder_path:
            messagebox.showwarning("No Folder", "Please select a folder first.")
            return

        if not self.is_preloaded:
            return

        mode = self.mode.get()
        self.cached_frames = self.frame_mode_cache.get(mode, [])

        if not self.cached_frames:
            messagebox.showerror("Error", "No frames available.")
            return

        # Show first frame in preview
        img = self.cached_frames[self.current_frame_index].copy().convert('RGBA')
        img = img.resize((300, 300))  # Resize for UI preview
        tk_img = ImageTk.PhotoImage(img)
        self.preview_canvas.config(image=tk_img)
        self.preview_canvas.image = tk_img

        # Cycle through frames for preview
        self.current_frame_index = (self.current_frame_index + 1) % len(self.cached_frames)
        self.root.after(100, self.preview_combined)  # Update every 100ms for smooth preview

    def show_tooltip(self, event):
        mode = self.mode.get()
        if mode == 'fit':
            text = "Fit: Resizes the image to fit within the given size, maintaining the aspect ratio. The empty area is filled with transparency."
        elif mode == 'fill':
            text = "Fill: Crops the image to fit the size, maintaining the center and cutting off excess."
        elif mode == 'stretch':
            text = "Stretch: Stretches the image to exactly match the given size, distorting the aspect ratio."
        self.tooltip_label.config(text=text)

    def hide_tooltip(self, event):
        self.tooltip_label.config(text="")

    def save_combined(self):
        if not self.cached_frames:
            messagebox.showwarning("No Preview", "Please preview first before saving.")
            return

        save_path = filedialog.asksaveasfilename(defaultextension=".gif", filetypes=[("GIF files", "*.gif")])
        if save_path:
            save_params = {
                'duration': 100,
                'loop': 0,
                'disposal': 2,
                'optimize': True
            }

            # Flatten RGBA frames onto white background to avoid artifacts
            final_frames = []
            for frame in self.cached_frames:
                rgba = frame.convert("RGBA")
                background = Image.new("RGBA", rgba.size, (255, 255, 255, 255))  # white background
                composited = Image.alpha_composite(background, rgba)
                final_frames.append(composited.convert("P", palette=Image.ADAPTIVE))

            # Save using the first frame and appending the rest
            final_frames[0].save(
                save_path,
                save_all=True,
                append_images=final_frames[1:],
                **save_params
            )

            messagebox.showinfo("Saved", f"GIF saved successfully to:\n{save_path}")
def main():
    root = tk.Tk()
    app = GifCombinerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
