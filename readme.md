# GIF Combiner 

A lightweight Python desktop app to combine and resize GIFs into a unified animated GIF compatible with AIO LCD displays or other fixed-size animation use cases.

Built using **Tkinter** and **Pillow**, this tool allows you to preview, resize, and save combined GIFs with adjustable aspect ratio handling.

---

## ✨ Features

- 📁 Load multiple GIFs from a folder  
- 🔁 Repeat each frame multiple times  
- 🖼️ Resize using **Fit**, **Fill**, or **Stretch** modes  
- 🧵 Multithreaded frame loading for performance  
- 🎞️ Live animated preview inside the UI  
- 💾 Save optimized GIFs  
- 🗜️ Optional compression using dithering and color quantization  
- 💬 Tooltips to explain modes  
- 📌 Status bar used for loading/saving indicators  

---

## 🛠 How to Run from Source

### Prerequisites

- Python 3.8+
- Install required dependencies:
  
```bash
pip install -r requirements.txt
```

### Run the App

```bash
python main.py
```

---

## 📦 Packaging into a Standalone EXE

You can use PyInstaller to create a standalone executable for Windows.

### Step 1: Install PyInstaller

```bash
pip install pyinstaller
```

### Step 2: Build the EXE

Navigate to the folder containing `main.py` and run:

```bash
pyinstaller --onefile --windowed main.py
```

- `--onefile`: bundles everything into a single EXE  
- `--windowed`: suppresses the console window for GUI apps

### Step 3: Locate the EXE

After completion, look in the `dist/` directory. The `combine_gifs.exe` file is your standalone app.

---

## 📂 How It Works

1. Select a folder containing `.gif` files.
2. Each GIF is decomposed into frames and optionally repeated.
3. Frames are resized using your chosen mode:
   - **Fit**: Maintains aspect ratio, adds padding.
   - **Fill**: Crops to center and resizes to fill.
   - **Stretch**: Resizes exactly, may distort.
4. The app previews the animated output.
5. Save your final animation as an optimized `.gif`.

---

## 👨‍💻 Developer

**Author:** aghinsa@gmail.com  
**License:** MIT