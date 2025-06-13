import SimpleITK as sitk
import numpy as np
import os
import matplotlib.pyplot as plt


def simulate_aneurysm_growth(image, growth_rate=0.2, iterations=5):
    """
    Simulate aneurysm growth over time by expanding the segmented region.
    Args:
        image (SimpleITK.Image): The segmented aneurysm image.
        growth_rate (float): The rate of growth per iteration.
        iterations (int): Number of growth iterations to simulate.
    Returns:
        List of SimpleITK.Image: Simulated growth images.
    """
    simulated_images = []
    current_image = sitk.GetArrayFromImage(image)

    for i in range(iterations):
        # Calculate the dilation radius as an integer
        radius = int(np.ceil(growth_rate * (i + 1)))

        # Apply binary dilation
        dilated_image = sitk.BinaryDilate(
            sitk.GetImageFromArray(current_image.astype(np.uint8)),
            [radius] * image.GetDimension()  # Specify radius for each dimension
        )

        # Update the binary mask
        dilated_array = sitk.GetArrayFromImage(dilated_image)
        current_image = np.maximum(current_image, dilated_array)

        # Store the simulated image
        simulated_images.append(sitk.GetImageFromArray(current_image))

    return simulated_images



def save_simulation_results(simulated_images, output_folder):
    """
    Save the simulated images as PNG files.
    Args:
        simulated_images (list of SimpleITK.Image): The simulated growth images.
        output_folder (str): Directory to save the results.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for idx, sim_image in enumerate(simulated_images):
        sim_array = sitk.GetArrayFromImage(sim_image)
        for slice_idx in range(sim_array.shape[0]):
            plt.figure(figsize=(8, 8))
            plt.imshow(sim_array[slice_idx], cmap='gray')
            plt.title(f"Simulation {idx + 1}, Slice {slice_idx + 1}")
            plt.axis('off')
            plt.savefig(os.path.join(output_folder, f"sim_{idx+1}_slice_{slice_idx+1}.png"))
            plt.close()


def ai_simulator(input_path, output_path):
    """
    Main function for the AI simulator service.
    Args:
        input_path (str): Path to the input DICOM folder.
        output_path (str): Path to save simulation results.
    """
    # Step 1: Load the DICOM series
    reader = sitk.ImageSeriesReader()
    dicom_files = reader.GetGDCMSeriesFileNames(input_path)
    reader.SetFileNames(dicom_files)
    image = reader.Execute()

    print("[INFO] Loaded DICOM series.")

    # Step 2: Segment the aneurysm
    from automated_measure import segment_aneurysm
    segmented_image = segment_aneurysm(image)

    print("[INFO] Segmented aneurysm.")

    # Step 3: Simulate aneurysm growth
    simulated_images = simulate_aneurysm_growth(segmented_image)

    print("[INFO] Simulated aneurysm growth.")

    # Step 4: Save results
    save_simulation_results(simulated_images, output_path)

    print("[INFO] Saved simulation results.")
