# Photogrammetry Script for 3D Model Creation

## Introduction
This script allows you to generate 3D models using photogrammetry techniques. Photogrammetry is a method of creating 3D models from multiple photographs taken from different angles. The provided script automates the process of image processing and model generation.

For a deeper understanding of the theoretical concepts behind photogrammetry, please refer to my research paper:  
[Introduction to 3D Modelling Using Photogrammetry](https://www.researchgate.net/publication/371038790_introduction_to_3D_modelling_using_photogrammetry).

## Requirements

### Software Setup
1. **Operating System**: This script is compatible with **Linux**, **macOS**, and **Windows**.
2. **Python**: Ensure that Python 3.6 or higher is installed.
   - Install Python from [official Python website](https://www.python.org/downloads/).
3. **Dependencies**: The script relies on several Python libraries. You can install them using `pip`.

### Installing Dependencies
Run the following command to install the necessary libraries:

```bash
pip install -r requirements.txt
```

The `requirements.txt` file attached includes the following dependencies:
- OpenCV
- NumPy
- SciPy
- Matplotlib
- Pillow
- PCL (Point Cloud Library)
- PyVista (for 3D visualization)
- scikit-learn


### Additional Software (Required for Metashape)
To process and build the 3D models, you will need **Metashape** (formerly Agisoft Photoscan). The script uses the **Metashape Python API** for advanced photogrammetry tasks.

1. **Download Metashape**:  
   Download Metashape from the official website:  
   [Agisoft Metashape](https://www.agisoft.com/downloads/).

2. **Install Metashape**:
   - Follow the installation instructions provided on the Metashape website for your operating system.
   - Ensure that you have the **Metashape Python API** installed. This is necessary for interacting with Metashape from within the script.

   After installation, you may need to set the environment variable to point to the Metashape installation directory.

3. **Metashape Python API Setup**:
   Once Metashape is installed, you can access its Python API by importing it in your Python code. The module should be installed automatically with Metashape. If not, refer to the official documentation for how to install it.

   Test the installation by running:

   ```python
   import Metashape
   ```

   If there are no errors, the API is installed correctly.

## Setting Up the Script

### 1. Clone the Repository
To get started, clone this repository to your local machine:

```bash
git clone https://github.com/yourusername/photogrammetry-script.git
cd photogrammetry-script
```

### 2. Image Collection
Capture multiple images of the object or scene you wish to model. Ensure the following:
- Images should be taken from multiple angles to capture all features of the object.
- The more images you capture, the more detailed your 3D model will be.
- Try to keep the object in the center of the frame, with good lighting conditions and minimal blur.

Place the images in the `input_images` folder within the project directory.

### 3. Configuration
If necessary, adjust the configuration settings in the `config.yaml` file. You can modify settings like:
- Image resolution.
- Output folder paths.
- Camera calibration parameters (optional, for more accurate results).

## Running the Script

Once everything is set up, run the script to process the images and generate the 3D model:

```bash
python photogrammetry_script.py
```

The script will:
- Process the input images.
- Extract features and match them across different images.
- Create a point cloud.
- Generate a 3D mesh model.

The resulting 3D model will be saved in the `output_model` folder.

## Using Metashape for Advanced 3D Reconstruction

In the script, Metashape is used to create the 3D model from the photos. Below are some basic commands to interact with the Metashape API. These commands should be placed inside the script to automate model generation:

```python
import Metashape

# Create a new Metashape project
doc = Metashape.Document()
chunk = doc.addChunk()

# Add photos to the chunk
photos = ["path_to_photo1.jpg", "path_to_photo2.jpg", "path_to_photo3.jpg"]
chunk.addPhotos(photos)

# Align photos
chunk.matchPhotos(accuracy=Metashape.HighAccuracy, filter_mask=True)
chunk.alignCameras()

# Build a dense cloud
chunk.buildDenseCloud(quality=Metashape.MediumQuality, filter=Metashape.AggressiveFiltering)

# Build a mesh
chunk.buildMesh(surface_type=Metashape.Arbitrary, interpolation=Metashape.EnabledInterpolation)

# Build a texture
chunk.buildUV()
chunk.buildTexture(blending_mode=Metashape.MosaicBlending)

# Export the model
chunk.exportModel(path="output_model/3d_model.obj")
```

This code will:
- Add photos to the project.
- Align them to create a point cloud.
- Build a mesh and texture.
- Export the final 3D model in OBJ format.

You can customize the quality and accuracy of each step in the process based on your requirements.

## Post-Processing (Optional)

After generating the 3D model, you may want to refine it. Here are a few tools you can use:
- **MeshLab**: For cleaning and smoothing the model.
- **Blender**: For advanced editing and rendering.

### Visualizing the 3D Model
You can use **PyVista** to visualize the generated 3D model directly in Python.

To visualize the model, run:

```bash
python visualize_model.py
```

This will open an interactive window where you can rotate and zoom into the 3D model.

## Troubleshooting

- **Issue: Missing Dependencies**
  - Ensure that all required packages are installed. Run `pip install -r requirements.txt` again if necessary.
  
- **Issue: Poor Quality Model**
  - Ensure that your images have good overlap and high resolution.
  - Adjust camera calibration settings in `config.yaml` for better accuracy.

## Conclusion
With this script, you can easily generate 3D models using photogrammetry techniques. If you're interested in the theoretical concepts behind photogrammetry, feel free to read my research paper at the link provided earlier.

For further questions, feel free to open an issue in the repository or contact me directly.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


