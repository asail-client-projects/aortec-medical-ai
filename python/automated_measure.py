import os
import pydicom
import numpy as np
from skimage import measure, morphology
from skimage.filters import threshold_otsu
from skimage.segmentation import clear_border
from scipy.spatial.distance import euclidean
from matplotlib import pyplot as plt


def load_dicom_images(input_path):
    """Load DICOM images from a folder or single file."""
    images = []
    slices = []

    if os.path.isdir(input_path):
        dicom_files = [os.path.join(input_path, f) for f in os.listdir(input_path) if f.endswith('.dcm')]
    else:
        dicom_files = [input_path]

    for dicom_file in dicom_files:
        dicom_data = pydicom.dcmread(dicom_file)
        images.append(dicom_data.pixel_array)
        slices.append(dicom_data)

    # Sort slices by ImagePositionPatient if available
    slices.sort(key=lambda x: x.ImagePositionPatient[2] if hasattr(x, 'ImagePositionPatient') else 0)
    return slices, np.array(images)


def segment_aaa(image):
    """Segment the AAA region in a single DICOM image."""
    # Thresholding
    thresh = threshold_otsu(image)
    binary_image = image > thresh

    # Remove small objects and clear borders
    cleared = clear_border(binary_image)
    cleaned = morphology.remove_small_objects(cleared, min_size=100)

    # Find the largest connected component (assume it is the AAA)
    labeled_image = measure.label(cleaned)
    regions = measure.regionprops(labeled_image)
    if not regions:
        return None

    largest_region = max(regions, key=lambda r: r.area)
    return largest_region.convex_image, largest_region.bbox


def calculate_aaa_metrics(segmented_images, pixel_spacing):
    """Calculate metrics such as maximum diameter and volume."""
    max_diameter = 0
    volume = 0

    for image, spacing in zip(segmented_images, pixel_spacing):
        if image is None:
            continue

        # Compute diameter
        coords = np.argwhere(image)
        if len(coords) > 1:
            dists = [euclidean(p1, p2) for p1 in coords for p2 in coords]
            max_diameter = max(max_diameter, max(dists) * spacing)

        # Compute volume (number of pixels times pixel area)
        volume += np.sum(image) * spacing**2

    return max_diameter, volume


def save_results(output_path, max_diameter, volume):
    """Save the computed results to a text file."""
    result_file = os.path.join(output_path, "aaa_measurements.txt")
    with open(result_file, "w") as f:
        f.write(f"Maximum Diameter: {max_diameter:.2f} mm\n")
        f.write(f"Volume: {volume:.2f} mm^3\n")
    print(f"Results saved to {result_file}")


def visualize_segmentation(input_images, segmented_images, output_path):
    """Visualize and save the segmented images."""
    for i, (original, segmented) in enumerate(zip(input_images, segmented_images)):
        if segmented is None:
            continue

        plt.figure(figsize=(10, 5))
        plt.subplot(1, 2, 1)
        plt.imshow(original, cmap='gray')
        plt.title("Original Image")

        plt.subplot(1, 2, 2)
        plt.imshow(segmented, cmap='gray')
        plt.title("Segmented AAA")

        save_path = os.path.join(output_path, f"segmentation_{i + 1}.png")
        plt.savefig(save_path)
        plt.close()


def automated_measure(input_path, output_path):
    """Main function to perform automated measurement."""
    # Load DICOM images
    slices, images = load_dicom_images(input_path)

    # Extract pixel spacing (assume square pixels for simplicity)
    pixel_spacing = [float(slice.PixelSpacing[0]) for slice in slices]

    # Segment images
    segmented_images = []
    for image in images:
        segmented, bbox = segment_aaa(image)
        segmented_images.append(segmented)

    # Calculate metrics
    max_diameter, volume = calculate_aaa_metrics(segmented_images, pixel_spacing)

    # Save results
    save_results(output_path, max_diameter, volume)

    # Visualize and save segmentation
    visualize_segmentation(images, segmented_images, output_path)

    print("Automated measurement completed.")