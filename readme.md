2. Packaging the App into a Standalone EXE
Now, to package the app into an EXE file (so it can run without Python installed), you can use PyInstaller. Here are the steps:

Step 1: Install PyInstaller
Open your command prompt and run:

bash
Copy
Edit
pip install pyinstaller
Step 2: Package Your App into EXE
Navigate to the folder containing the combine_gifs.py file using your terminal or command prompt.

Run the following command:

bash
Copy
Edit
pyinstaller --onefile --windowed --add-data "path_to_your_gif_folder;." combine_gifs.py
Replace path_to_your_gif_folder with the actual folder where your GIFs are stored, or if not needed, just skip the --add-data part.

--onefile tells PyInstaller to bundle everything into a single EXE file.

--windowed makes sure no console window pops up (perfect for GUI apps).

--add-data ensures that the GIF folder is added to your EXE.

Step 3: Locate the EXE
Once the command runs, PyInstaller will create a dist folder in your project directory. Inside dist, you'll find the combine_gifs.exe file — that’s your standalone app!

