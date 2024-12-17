import Metashape
import cv2
import numpy as np
import os
import datetime
import math
from sklearn.cluster import KMeans
from abc import ABC, abstractmethod


# Abstract Base Class for Image Capturing
class ImageCaptureInterface(ABC):
    @abstractmethod
    def capture_images(self):
        pass

    @abstractmethod
    def save_image(self, frame, prefix):
        pass


# Concrete ImageCapture Implementation
class ImageCapture(ImageCaptureInterface):
    def __init__(self, image_folder):
        self.image_folder = image_folder
        if not os.path.exists(image_folder):
            os.makedirs(image_folder)

    def capture_images(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open camera.")
            return

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to capture image.")
                break

            cv2.imshow("Capture", frame)
            key = cv2.waitKey(1) & 0xFF

            if key == ord('s'):
                self.save_image(frame, "simage")

            elif key == ord('m'):
                self.save_image(frame, "mimage")
                yield frame  # Return the captured frame to process measurements

            elif key == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    def save_image(self, frame, prefix):
        date_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        image_filename = f"{self.image_folder}/{prefix}{date_str}.jpg"
        cv2.imwrite(image_filename, frame)
        print(f"Saved image: {image_filename}")


class ImageProcessorInterface(ABC):
    @abstractmethod
    def detect_extreme_points(self, image):
        pass


class ImageProcessor(ImageProcessorInterface):
    def __init__(self, k=2, lower_color_range=None, upper_color_range=None):
        self.k = k
        self.lower_color_range = lower_color_range
        self.upper_color_range = upper_color_range

    def detect_extreme_points(self, image):
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv_image, self.lower_color_range, self.upper_color_range)
        cyan_pixels = np.column_stack(np.where(mask > 0))

        if len(cyan_pixels) < 2:
            return 0, 0

        kmeans = KMeans(n_clusters=self.k, random_state=0).fit(cyan_pixels)
        min_x, max_x = np.min(cyan_pixels[:, 1]), np.max(cyan_pixels[:, 1])
        min_y, max_y = np.min(cyan_pixels[:, 0]), np.max(cyan_pixels[:, 0])

        x_distance = max_x - min_x
        y_distance = max_y - min_y

        return x_distance, y_distance


class Measurement:
    def __init__(self):
        self.x_distances = []
        self.y_distances = []

    def collect_measurement(self, x_distance, y_distance):
        self.x_distances.append(x_distance)
        self.y_distances.append(y_distance)

    def calculate_average_distances(self, scale, ground_offset):
        if not self.x_distances or not self.y_distances:
            print("No measurement data collected.")
            return None, None

        plate_width = sum(self.x_distances) / len(self.x_distances)
        plate_height = sum(self.y_distances) / len(self.y_distances)
        scaled_width = plate_width * scale
        scaled_height = math.sqrt(plate_height ** 2 - (scaled_width // 2.0) ** 2) + ground_offset

        return scaled_width, scaled_height


class MissionObject(ABC):
    @abstractmethod
    def set_dimensions(self, width, height):
        pass

    @abstractmethod
    def get_dimensions(self):
        pass


class Plate(MissionObject):
    def __init__(self, lower_range, upper_range):
        self.lower_range = lower_range
        self.upper_range = upper_range
        self.width = None
        self.height = None

    def set_dimensions(self, width, height):
        self.width = width
        self.height = height

    def get_dimensions(self):
        return self.width, self.height


class ModelBuilder:
    def __init__(self, chunk, reference_distance=0.30):
        self.chunk = chunk
        self.reference_distance = reference_distance
        self.scale_factor = None

    def detect_markers_and_scale(self, marker_name_1="Marker_1", marker_name_2="Marker_2"):
        try:
            marker_1_position = self.chunk.markers[0].position
            marker_2_position = self.chunk.markers[1].position
        except:
            print(f"Error: Could not find both markers. Length of markers array is {len(self.chunk.markers)}")
            return None

        distance = math.sqrt(
            (marker_1_position.x - marker_2_position.x) ** 2 +
            (marker_1_position.y - marker_2_position.y) ** 2 +
            (marker_1_position.z - marker_2_position.z) ** 2
        )

        self.scale_factor = self.reference_distance / distance
        return self.scale_factor

    def apply_scaling(self, scale_factor):
        for point in self.chunk.dense_cloud.points:
            point.coord = Metashape.Vector([point.coord.x * scale_factor, point.coord.y * scale_factor, point.coord.z * scale_factor])
        self.chunk.updateTransform()

    def build_3d_model(self, image_list, output_model_path, marker_name_1="Marker_1", marker_name_2="Marker_2"):
        self.chunk.addPhotos(image_list)
        self.chunk.matchPhotos(accuracy=Metashape.HighAccuracy, generic_preselection=True, reference_preselection=False)
        self.chunk.alignCameras()
        self.chunk.buildDepthMaps(quality=Metashape.MediumQuality, filter_mode=Metashape.MildFiltering)
        self.chunk.buildDenseCloud()
        self.chunk.buildModel(surface_type=Metashape.Arbitrary, source_data=Metashape.DenseCloudData, interpolation=Metashape.EnabledInterpolation)
        self.chunk.buildUV(mapping_mode=Metashape.GenericMapping)
        self.chunk.buildTexture(blending_mode=Metashape.MosaicBlending, size=4096)

        scale_factor = self.detect_markers_and_scale(marker_name_1, marker_name_2)
        if scale_factor:
            self.apply_scaling(scale_factor)
            self.chunk.exportModel(output_model_path, format=Metashape.ModelFormatOBJ, texture_format=Metashape.ImageFormatJPEG, save_texture=True)
            print(f"Scaled 3D model exported to {output_model_path}")
        else:
            print("Model scaling failed due to marker detection issues.")


class Workflow:
    def __init__(self, image_folder, output_model_path):
        self.image_folder = image_folder
        self.output_model_path = output_model_path
        self.image_capture = ImageCapture(image_folder)
        self.image_processor = ImageProcessor(k=2, lower_color_range=np.array([80, 100, 100]), upper_color_range=np.array([100, 255, 255]))
        self.measurement = Measurement()
        self.plate = Plate(np.array([80, 100, 100]), np.array([100, 255, 255]))

    def run(self):
        captured_images = self.image_capture.capture_images()

        for image in captured_images:
            x_distance, y_distance = self.image_processor.detect_extreme_points(image)
            self.measurement.collect_measurement(x_distance, y_distance)

        scaled_width, scaled_height = self.measurement.calculate_average_distances(scale=2.0, ground_offset=1.0)
        self.plate.set_dimensions(scaled_width, scaled_height)

        model_builder = ModelBuilder(Metashape.app.document.chunk)
        model_builder.build_3d_model(captured_images, self.output_model_path)
        print(f"Plate Dimensions: {self.plate.get_dimensions()}")


if __name__ == "__main__":
    workflow = Workflow(image_folder='images', output_model_path='3d_model.obj')
    workflow.run()
