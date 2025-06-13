import os
import numpy as np
import pydicom
import SimpleITK as sitk
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import tempfile
import zipfile
import shutil
import traceback
import logging
import glob

def create_2d_model_from_dicom_folder(dicom_folder, output_path, lower_threshold=100, upper_threshold=300):
    """
    Create a 2D visualization model from a folder of DICOM files.
    Instead of generating STL, it creates a detailed 2D visualization.
    
    Args:
        dicom_folder: Path to the folder containing DICOM files
        output_path: Path to save the output visualization image
        lower_threshold: Lower threshold for segmentation (HU value)
        upper_threshold: Upper threshold for segmentation (HU value)
        
    Returns:
        Path to the generated image
    """
    try:
        # Find all DICOM files in the directory
        dicom_files = []
        for root, _, files in os.walk(dicom_folder):
            for file in files:
                # Include files with .dcm extension or no extension (common for DICOM)
                file_path = os.path.join(root, file)
                try:
                    if file.lower().endswith('.dcm') or not os.path.splitext(file)[1]:
                        pydicom.dcmread(file_path, stop_before_pixels=True)  # Check if it's a valid DICOM
                        dicom_files.append(file_path)
                except:
                    pass  # Not a valid DICOM file, skip
        
        if not dicom_files:
            raise ValueError("No valid DICOM files found in the directory")
        
        print(f"[2D Model] Found {len(dicom_files)} DICOM files")
        
        # Sort DICOM files by instance number or position
        sorted_dicom_files = sort_dicom_files(dicom_files)
        
        # Read all DICOM files
        images = []
        for dicom_file in sorted_dicom_files:
            try:
                dcm = pydicom.dcmread(dicom_file)
                if hasattr(dcm, 'pixel_array'):
                    pixel_data = dcm.pixel_array
                    images.append((dicom_file, pixel_data))
            except Exception as e:
                print(f"Error reading {dicom_file}: {str(e)}")
        
        if not images:
            raise ValueError("No valid pixel data found in DICOM files")
        
        # Create the visualization based on the type of DICOM data
        # Determine appropriate visualization based on the number of slices
        if len(images) > 10:
            # Many slices: Create a montage of key slices
            output_img = create_dicom_montage(images, lower_threshold, upper_threshold)
        else:
            # Few slices: Process each slice with detailed visualization
            output_img = create_single_slice_view(images, lower_threshold, upper_threshold)
        
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save the visualization
        output_img.save(output_path)
        
        # Generate additional views if there are enough slices
        additional_outputs = []
        
        # If we have enough slices, create an axial, coronal, and sagittal view
        if len(images) >= 5:
            try:
                # Read the series as a 3D volume using SimpleITK
                reader = sitk.ImageSeriesReader()
                dicom_names = reader.GetGDCMSeriesFileNames(dicom_folder)
                
                if dicom_names:
                    reader.SetFileNames(dicom_names)
                    volume = reader.Execute()
                    
                    # Create additional views
                    mpr_views = create_mpr_views(volume, output_path)
                    additional_outputs.extend(mpr_views)
            except Exception as e:
                print(f"Error creating MPR views: {str(e)}")
        
        # Create a histogram of intensity values
        try:
            hist_path = output_path.replace('.png', '_histogram.png')
            create_intensity_histogram(images, lower_threshold, upper_threshold, hist_path)
            additional_outputs.append(hist_path)
        except Exception as e:
            print(f"Error creating histogram: {str(e)}")
        
        return output_path, additional_outputs
    
    except Exception as e:
        error_details = traceback.format_exc()
        error_message = f"Error creating 2D model from DICOM folder: {str(e)}\n{error_details}"
        print(error_message)
        
        # Create an error image
        error_img = Image.new('RGB', (800, 600), color=(255, 240, 240))
        draw = ImageDraw.Draw(error_img)
        draw.text((50, 50), "Error generating visualization:", fill=(200, 0, 0))
        draw.text((50, 80), str(e), fill=(200, 0, 0))
        draw.text((50, 120), "Please check that your DICOM files are valid", fill=(0, 0, 0))
        draw.text((50, 150), "and from the same series.", fill=(0, 0, 0))
        
        error_path = output_path
        error_img.save(error_path)
        
        raise Exception(error_message)

def sort_dicom_files(dicom_files):
    """
    Sort DICOM files by instance number or position.
    """
    file_positions = []
    
    for file_path in dicom_files:
        try:
            dcm = pydicom.dcmread(file_path, stop_before_pixels=True)
            
            # Try different methods to determine slice position
            position = None
            
            # Method 1: Instance Number
            if hasattr(dcm, 'InstanceNumber'):
                position = float(dcm.InstanceNumber)
            
            # Method 2: Slice Location
            elif hasattr(dcm, 'SliceLocation'):
                position = float(dcm.SliceLocation)
            
            # Method 3: Image Position Patient
            elif hasattr(dcm, 'ImagePositionPatient'):
                position = float(dcm.ImagePositionPatient[2])  # Z position
            
            if position is not None:
                file_positions.append((file_path, position))
            else:
                file_positions.append((file_path, 0))  # Default position
                
        except Exception as e:
            print(f"Error reading DICOM header for sorting: {str(e)}")
            file_positions.append((file_path, 0))  # Default position
    
    # Sort by position
    sorted_files = [file for file, _ in sorted(file_positions, key=lambda x: x[1])]
    return sorted_files

def create_dicom_montage(images, lower_threshold=None, upper_threshold=None):
    """
    Create a montage of DICOM images with segmentation based on threshold values.
    
    Args:
        images: List of tuples, each containing (file_path, pixel_data)
        lower_threshold: Lower threshold for segmentation (default=None for auto-detection)
        upper_threshold: Upper threshold for segmentation (default=None for auto-detection)
        
    Returns:
        Montage image as a PIL Image
    """
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
    import matplotlib.pyplot as plt
    
    if not images or len(images) == 0:
        raise ValueError("No images provided for montage creation")
    
    # Use the first image as a sample to determine dimensions
    # Extract the pixel_data from the tuple (file_path, pixel_data)
    _, sample_data = images[0]
    
    print(f"Sample data shape: {sample_data.shape}, data type: {sample_data.dtype}")
    
    # Fix for dimension handling - properly extract height and width regardless of dimensions
    if len(sample_data.shape) == 2:
        # 2D image: height, width
        height, width = sample_data.shape
        print(f"Using 2D dimensions: height={height}, width={width}")
    elif len(sample_data.shape) == 3:
        # 3D image: could be (slices, height, width) or (height, width, channels)
        if sample_data.shape[2] <= 4:  # Likely (height, width, channels)
            height, width, _ = sample_data.shape
            print(f"Using 3D image dimensions (HWC): height={height}, width={width}, channels={sample_data.shape[2]}")
        else:  # Likely (slices, height, width)
            _, height, width = sample_data.shape
            print(f"Using 3D volume dimensions (SHW): slices={sample_data.shape[0]}, height={height}, width={width}")
    elif len(sample_data.shape) > 3:
        # Multi-dimensional data - extract the spatial dimensions
        height, width = sample_data.shape[-2], sample_data.shape[-1]
        print(f"Using last two dimensions of {len(sample_data.shape)}D data: height={height}, width={width}")
    else:
        # Handle 1D data or other unexpected cases
        raise ValueError(f"Unexpected data shape: {sample_data.shape}")
    
    # Calculate the montage grid size based on number of images
    grid_size = int(np.ceil(np.sqrt(len(images))))
    
    # Determine montage dimensions
    montage_width = grid_size * width
    montage_height = grid_size * height
    
    # Auto-detect threshold values if not provided
    all_pixel_values = []
    for _, img in images[:min(10, len(images))]:  # Sample from first 10 images for efficiency
        # Extract 2D slice according to dimensions
        if len(img.shape) == 2:
            slice_data = img
        elif len(img.shape) == 3:
            if img.shape[2] <= 4:  # (height, width, channels)
                slice_data = np.mean(img, axis=2).astype(img.dtype)
            else:  # (slices, height, width)
                slice_data = img[img.shape[0] // 2]  # Take middle slice
        elif len(img.shape) > 3:
            # Handle higher dimensional data - take a middle slice
            middle_indices = [dim // 2 for dim in img.shape[:-2]]
            slice_data = img[tuple(middle_indices)]
        else:
            continue  # Skip invalid images
            
        # Flatten and add to list for threshold calculation
        all_pixel_values.extend(slice_data.flatten())
    
    # Convert to numpy array for percentile calculation
    if all_pixel_values:
        all_pixel_values = np.array(all_pixel_values)
        
        # Auto-detect thresholds if not provided
        if lower_threshold is None:
            lower_threshold = np.percentile(all_pixel_values, 30)
            print(f"Auto-detected lower threshold: {lower_threshold}")
            
        if upper_threshold is None:
            upper_threshold = np.percentile(all_pixel_values, 70)
            print(f"Auto-detected upper threshold: {upper_threshold}")
    
    # Create an empty canvas for the montage (RGB to support colored overlays)
    montage = np.zeros((montage_height, montage_width, 3), dtype=np.uint8)
    
    # Place each image in the montage
    for i, (file_path, img) in enumerate(images):
        if i >= grid_size * grid_size:
            break  # Stop if we run out of space in the grid
            
        row = i // grid_size
        col = i % grid_size
        
        # Get the 2D slice regardless of original dimensions
        if len(img.shape) == 2:
            slice_data = img
        elif len(img.shape) == 3:
            if img.shape[2] <= 4:  # (height, width, channels)
                # Convert to grayscale if it's an RGB image
                slice_data = np.mean(img, axis=2).astype(img.dtype)
            else:  # (slices, height, width)
                slice_data = img[img.shape[0] // 2]  # Take middle slice
        elif len(img.shape) > 3:
            # Handle higher dimensional data - take a middle slice of appropriate dimensions
            middle_indices = [dim // 2 for dim in img.shape[:-2]]
            slice_data = img[tuple(middle_indices)]
        else:
            continue  # Skip this image if dimensions are invalid
            
        # Normalize the data to 0-255 for visualization
        if slice_data.max() != slice_data.min():
            normalized_data = ((slice_data - slice_data.min()) / 
                            (slice_data.max() - slice_data.min()) * 255).astype(np.uint8)
        else:
            normalized_data = np.zeros_like(slice_data, dtype=np.uint8)
            
        # Apply thresholding to identify regions of interest
        if lower_threshold is not None and upper_threshold is not None:
            try:
                # FIX: Handle threshold conversion more safely to avoid overflow
                # Convert original thresholds to the normalized 0-255 range
                if slice_data.max() != slice_data.min():
                    # Clamp thresholds to the data range before normalization
                    safe_lower = max(slice_data.min(), min(slice_data.max(), lower_threshold))
                    safe_upper = max(slice_data.min(), min(slice_data.max(), upper_threshold))
                    
                    # Calculate normalized thresholds (in 0-255 range)
                    norm_lower = ((safe_lower - slice_data.min()) / 
                                (slice_data.max() - slice_data.min()) * 255)
                    norm_upper = ((safe_upper - slice_data.min()) / 
                                (slice_data.max() - slice_data.min()) * 255)
                    
                    # Ensure they're in valid uint8 range
                    norm_lower = max(0, min(255, norm_lower))
                    norm_upper = max(0, min(255, norm_upper))
                else:
                    norm_lower, norm_upper = 0, 255
                
                # Create mask for thresholded regions
                threshold_mask = np.logical_and(
                    normalized_data >= norm_lower,
                    normalized_data <= norm_upper
                )
            except Exception as e:
                print(f"Error applying thresholds: {str(e)}")
                # Fallback: Don't highlight anything
                threshold_mask = np.zeros_like(normalized_data, dtype=bool)
        else:
            # If no thresholds provided, don't highlight anything
            threshold_mask = np.zeros_like(normalized_data, dtype=bool)
            
        # Create RGB version of the normalized data (grayscale)
        rgb_data = np.stack([normalized_data, normalized_data, normalized_data], axis=2)
        
        # Apply colored overlay for thresholded regions
        rgb_data[threshold_mask, 0] = 255  # Red channel
        rgb_data[threshold_mask, 1] = 0    # Green channel
        rgb_data[threshold_mask, 2] = 0    # Blue channel
            
        # Place the normalized data in the montage
        y_start = row * height
        y_end = (row + 1) * height
        x_start = col * width
        x_end = (col + 1) * width
        
        # Handle size mismatches by resizing or cropping
        if rgb_data.shape[0] != height or rgb_data.shape[1] != width:
            # Resize to match expected dimensions
            pil_img = Image.fromarray(rgb_data)
            pil_img = pil_img.resize((width, height), Image.LANCZOS)
            rgb_data = np.array(pil_img)
            
        # Place in montage
        try:
            # Make sure dimensions match
            if y_end <= montage.shape[0] and x_end <= montage.shape[1]:
                montage[y_start:y_end, x_start:x_end] = rgb_data
        except Exception as e:
            print(f"Error placing image {i} in montage: {str(e)}")
            print(f"Montage shape: {montage.shape}, Image shape: {rgb_data.shape}")
            print(f"Position: y={y_start}:{y_end}, x={x_start}:{x_end}")
    
    # Convert to PIL Image for further processing
    montage_img = Image.fromarray(montage)
    
    # Add some metadata and annotations
    draw = ImageDraw.Draw(montage_img)
    
    # Try to add threshold information
    try:
        if lower_threshold is not None and upper_threshold is not None:
            info_text = f"Threshold: {lower_threshold:.1f} - {upper_threshold:.1f}"
            draw.text((10, 10), info_text, fill=(255, 255, 255))
    except Exception as e:
        print(f"Error adding threshold info: {str(e)}")
    
    return montage_img


def create_single_slice_view(images, lower_threshold, upper_threshold):
    """
    Create a detailed view of a single representative slice.
    """
    # Choose a representative slice (middle slice)
    middle_idx = len(images) // 2
    file_path, pixel_data = images[middle_idx]
    
    # Normalize the pixel data
    normalized_data = normalize_image(pixel_data)
    
    # Create a mask for segmentation
    mask = create_segmentation_mask(normalized_data, lower_threshold, upper_threshold)
    
    # Apply the mask as a colored overlay
    colored_image = apply_color_overlay(normalized_data, mask)
    
    # Resize to a standard size if needed
    max_size = 800
    height, width = colored_image.size
    if height > max_size or width > max_size:
        scale = max_size / max(height, width)
        new_size = (int(width * scale), int(height * scale))
        colored_image = colored_image.resize(new_size, Image.LANCZOS)
    
    # Add annotations
    draw = ImageDraw.Draw(colored_image)
    draw.text((10, 10), f"DICOM Visualization - Slice {middle_idx+1}/{len(images)}", fill=(255, 255, 255))
    draw.text((10, 30), f"Thresholds: Lower={lower_threshold}, Upper={upper_threshold}", fill=(255, 255, 255))
    
    return colored_image

def normalize_image(pixel_data):
    """
    Normalize pixel data to 0-255 range.
    """
    min_val = np.min(pixel_data)
    max_val = np.max(pixel_data)
    if max_val > min_val:
        normalized = ((pixel_data - min_val) / (max_val - min_val) * 255).astype(np.uint8)
    else:
        normalized = np.zeros_like(pixel_data, dtype=np.uint8)
    
    return normalized

def create_segmentation_mask(normalized_data, lower_threshold, upper_threshold):
    """
    Create a binary mask based on threshold values.
    """
    # Rescale thresholds to normalized range if needed
    lower = max(0, min(255, lower_threshold))
    upper = max(0, min(255, upper_threshold))
    
    # Create binary mask
    mask = np.logical_and(normalized_data >= lower, normalized_data <= upper)
    return mask

def apply_color_overlay(normalized_data, mask):
    """
    Apply a color overlay on the image based on the mask.
    """
    # Convert to RGB image
    rgb_image = np.stack([normalized_data, normalized_data, normalized_data], axis=2)
    
    # Create a PIL Image
    pil_image = Image.fromarray(rgb_image)
    
    # Convert mask to PIL format
    if mask.any():  # Check if mask has any True values
        mask_image = Image.fromarray((mask * 255).astype(np.uint8))
        
        # Create a red overlay
        overlay = Image.new('RGB', pil_image.size, (255, 0, 0))
        
        # Composite images
        result = Image.composite(overlay, pil_image, mask_image.convert('L'))
        
        # Enhance the result
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Brightness(result)
        result = enhancer.enhance(1.2)
    else:
        result = pil_image
    
    return result

def create_mpr_views(volume, base_output_path):
    """
    Create Multiplanar Reconstruction (MPR) views: axial, coronal, and sagittal.
    """
    outputs = []
    
    # Create axial view (already have this from main function)
    # Extract coronal and sagittal views
    try:
        # Get dimensions
        size = volume.GetSize()
        
        # Get the middle slices
        axial_idx = size[2] // 2
        coronal_idx = size[1] // 2
        sagittal_idx = size[0] // 2
        
        # Extract the slices
        axial_slice = sitk.Extract(volume, 
                                  [size[0], size[1], 0], 
                                  [0, 0, axial_idx])
        
        coronal_slice = sitk.Extract(volume, 
                                    [size[0], 0, size[2]], 
                                    [0, coronal_idx, 0])
        
        sagittal_slice = sitk.Extract(volume, 
                                     [0, size[1], size[2]], 
                                     [sagittal_idx, 0, 0])
        
        # Convert to numpy arrays for visualization
        axial_array = sitk.GetArrayFromImage(axial_slice)
        coronal_array = sitk.GetArrayFromImage(coronal_slice)
        sagittal_array = sitk.GetArrayFromImage(sagittal_slice)
        
        # Normalize and convert to images
        axial_img = Image.fromarray(normalize_image(axial_array))
        coronal_img = Image.fromarray(normalize_image(coronal_array))
        sagittal_img = Image.fromarray(normalize_image(sagittal_array))
        
        # Save the views
        coronal_path = base_output_path.replace('.png', '_coronal.png')
        sagittal_path = base_output_path.replace('.png', '_sagittal.png')
        
        coronal_img.save(coronal_path)
        sagittal_img.save(sagittal_path)
        
        outputs.extend([coronal_path, sagittal_path])
    except Exception as e:
        print(f"Error creating MPR views: {str(e)}")
    
    return outputs

def create_intensity_histogram(images, lower_threshold, upper_threshold, output_path):
    """
    Create a histogram of the intensity values with threshold markers.
    """
    # Collect intensity values from all images
    all_pixels = []
    for _, pixel_data in images:
        # Flatten and sample pixels to avoid memory issues with large datasets
        flat_pixels = pixel_data.flatten()
        
        # If very large, take a sample
        if len(flat_pixels) > 1000000:
            sample_indices = np.random.choice(len(flat_pixels), 1000000, replace=False)
            flat_pixels = flat_pixels[sample_indices]
            
        all_pixels.append(flat_pixels)
    
    # Combine all pixels
    all_pixels = np.concatenate(all_pixels)
    
    # Create histogram
    plt.figure(figsize=(10, 6))
    plt.hist(all_pixels, bins=100, alpha=0.7)
    plt.axvline(lower_threshold, color='r', linestyle='--', label=f'Lower Threshold ({lower_threshold})')
    plt.axvline(upper_threshold, color='g', linestyle='--', label=f'Upper Threshold ({upper_threshold})')
    plt.title('Intensity Histogram with Segmentation Thresholds')
    plt.xlabel('Intensity')
    plt.ylabel('Frequency')
    plt.legend()
    
    # Save the histogram
    plt.savefig(output_path)
    plt.close()
    
    return output_path

def convert_to_2d_model(input_path, output_path, lower_threshold=None, upper_threshold=None):
    """
    Convert DICOM files to a 3D-style visualization.
    
    Args:
        input_path: Path to a folder containing DICOM files or a single DICOM file
        output_path: Path to save the visualization image
        lower_threshold: Lower threshold for segmentation (HU value), auto-detected if None
        upper_threshold: Upper threshold for segmentation (HU value), auto-detected if None
        
    Returns:
        Path to the generated image and list of additional outputs
    """
    print(f"[3D Visualization] Processing {input_path} to {output_path}")
    
    try:
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Make sure the thresholds are properly parsed
        if lower_threshold is not None and not isinstance(lower_threshold, (int, float)):
            try:
                lower_threshold = float(lower_threshold)
            except (ValueError, TypeError):
                print(f"[3D Visualization] Invalid lower threshold value '{lower_threshold}', using default")
                lower_threshold = 100
        else:
            lower_threshold = 100  # Default value
                
        if upper_threshold is not None and not isinstance(upper_threshold, (int, float)):
            try:
                upper_threshold = float(upper_threshold)
            except (ValueError, TypeError):
                print(f"[3D Visualization] Invalid upper threshold value '{upper_threshold}', using default")
                upper_threshold = 300
        else:
            upper_threshold = 300  # Default value
        
        # Create a temporary directory for processing
        temp_dir = tempfile.mkdtemp()
        print(f"[3D Visualization] Created temporary directory: {temp_dir}")
        
        try:
            # Define input_folder variable that was missing
            input_folder = None
            
            # If input is a ZIP file, extract it to the temporary directory
            if isinstance(input_path, str) and input_path.lower().endswith('.zip'):
                try:
                    with zipfile.ZipFile(input_path, 'r') as zip_ref:
                        zip_ref.extractall(temp_dir)
                    input_folder = temp_dir
                    print(f"[3D Visualization] Extracted ZIP file to {temp_dir}")
                except Exception as e:
                    print(f"[3D Visualization] Error extracting ZIP file: {str(e)}")
                    raise ValueError(f"Failed to extract ZIP file: {str(e)}")
            
            # If input is a directory, use it directly
            elif isinstance(input_path, str) and os.path.isdir(input_path):
                input_folder = input_path
                print(f"[3D Visualization] Using existing folder: {input_folder}")
            
            # If input is a single file, check if it's a DICOM file
            elif isinstance(input_path, str) and os.path.isfile(input_path):
                # If it's a single DICOM file, check if other DICOM files exist in the same directory
                parent_dir = os.path.dirname(input_path)
                
                # Find all potential DICOM files in the parent directory
                all_files = []
                for ext in ['', '.dcm', '.DCM', '.ima', '.IMA']:
                    from glob import glob
                    all_files.extend(glob(os.path.join(parent_dir, f"*{ext}")))
                
                # Count valid DICOM files
                dicom_count = 0
                for file_path in all_files:
                    try:
                        pydicom.dcmread(file_path, stop_before_pixels=True)
                        dicom_count += 1
                    except:
                        pass
                
                print(f"[3D Visualization] Found {dicom_count} DICOM files in parent directory")
                
                if dicom_count > 1:
                    # If multiple DICOM files exist, use the parent directory
                    input_folder = parent_dir
                    print(f"[3D Visualization] Using parent directory containing multiple DICOM files: {input_folder}")
                else:
                    # For a single file, copy it to the temp directory
                    shutil.copy(input_path, os.path.join(temp_dir, os.path.basename(input_path)))
                    input_folder = temp_dir
            else:
                raise ValueError(f"Unsupported input type: {input_path}")
            
            # Check if input_folder is still None
            if input_folder is None:
                raise ValueError("Failed to determine input folder for processing")
                
            # Use the 3D-style visualization 
            main_output = create_3d_style_visualization(
                input_folder, 
                output_path,
                lower_threshold=lower_threshold,
                upper_threshold=upper_threshold
            )
            
            # Return only the main output - no additional outputs
            return main_output, []
            
        finally:
            # Clean up temp directory
            if os.path.exists(temp_dir) and temp_dir != input_path:
                try:
                    shutil.rmtree(temp_dir)
                    print(f"[3D Visualization] Cleaned up temporary directory: {temp_dir}")
                except Exception as e:
                    print(f"[3D Visualization] Error cleaning up temporary directory: {str(e)}")
    
    except Exception as e:
        error_details = traceback.format_exc()
        error_message = f"Error creating 3D visualization: {str(e)}"
        print(error_message)
        print(error_details)
        
        # Generate an error image
        error_path = create_error_image(str(e), output_path)
        
        # Return only the error image
        if error_path:
            return error_path, []
        else:
            raise Exception(error_message)

        
def create_error_image(error_message, output_path):
    """
    Create an error image with detailed error information.
    
    Args:
        error_message: Error message to display on the image
        output_path: Path to save the error image
        
    Returns:
        Path to the saved error image
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
        import os
        
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Create a new image with error styling
        error_img = Image.new('RGB', (800, 600), color=(255, 240, 240))
        draw = ImageDraw.Draw(error_img)
        
        # Add error information
        draw.text((50, 50), "Error generating visualization:", fill=(200, 0, 0))
        
        # Split error message into multiple lines if it's too long
        if len(error_message) > 80:
            lines = []
            current_line = ""
            for word in error_message.split():
                if len(current_line + " " + word) <= 80:
                    current_line += " " + word if current_line else word
                else:
                    lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)
                
            # Draw each line
            y_pos = 80
            for line in lines:
                draw.text((50, y_pos), line, fill=(200, 0, 0))
                y_pos += 20
        else:
            draw.text((50, 80), error_message, fill=(200, 0, 0))
        
        # Add helpful information
        draw.text((50, 140), "Please check:", fill=(0, 0, 0))
        draw.text((70, 170), "• That your DICOM files are valid and from the same series", fill=(0, 0, 0))
        draw.text((70, 195), "• That the threshold values (if specified) are appropriate", fill=(0, 0, 0))
        draw.text((70, 220), "• That all files are accessible to the server", fill=(0, 0, 0))
        
        # Save the error image
        try:
            error_img.save(output_path)
            print(f"Saved error image to {output_path}")
        except Exception as save_error:
            print(f"Failed to save error image: {str(save_error)}")
            
        return output_path
        
    except Exception as e:
        print(f"Error creating error image: {str(e)}")
        # If creating the error image fails, try a simpler approach
        try:
            with open(output_path, 'w') as f:
                f.write(f"Error: {error_message}")
            return output_path
        except:
            return None
        

# Add this function to dicom_visualizer.py
def create_3d_style_visualization(dicom_folder, output_path, lower_threshold=100, upper_threshold=300):
    """
    Create a 3D-style visualization from a DICOM series, with special handling for
    RGB data and improved error handling.
    
    Args:
        dicom_folder: Path to the folder containing DICOM files
        output_path: Path to save the visualization image
        lower_threshold: Lower threshold for segmentation
        upper_threshold: Upper threshold for segmentation
        
    Returns:
        Path to the generated image
    """
    try:
        # Import required libraries
        import os
        import numpy as np
        import pydicom
        import SimpleITK as sitk
        import vtk
        from vtk.util import numpy_support
        from PIL import Image, ImageDraw
        import traceback
        import sys
        
        # Make sure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        print(f"Starting 3D visualization process for folder: {dicom_folder}")
        print(f"Output will be saved to: {output_path}")
        
        # Create a debugging log file for more detailed error tracking
        log_path = output_path.replace('.png', '_debug.log')
        with open(log_path, 'w') as log_file:
            log_file.write(f"Debug log for processing {dicom_folder}\n")
            log_file.write(f"VTK version: {vtk.vtkVersion.GetVTKVersion()}\n")
            log_file.write(f"Python version: {sys.version}\n\n")
        
        def log_debug(message):
            """Helper function to log debug messages"""
            print(message)
            with open(log_path, 'a') as log_file:
                log_file.write(message + "\n")
        
        # Approach 1: Try SimpleITK first
        volume_data = None
        try:
            log_debug("Attempting to load DICOM series with SimpleITK...")
            reader = sitk.ImageSeriesReader()
            dicom_names = reader.GetGDCMSeriesFileNames(dicom_folder)
            
            if dicom_names and len(dicom_names) > 0:
                log_debug(f"Found {len(dicom_names)} DICOM files in the series")
                reader.SetFileNames(dicom_names)
                sitk_image = reader.Execute()
                volume = sitk.GetArrayFromImage(sitk_image)
                log_debug(f"Successfully loaded DICOM series with SimpleITK: {volume.shape}")
                
                # Handle RGB data if present
                if len(volume.shape) == 4 and volume.shape[-1] == 3:
                    log_debug("Detected RGB DICOM data (SimpleITK), using first channel")
                    volume_data = volume[..., 0].copy()  # Use red channel and make explicit copy
                else:
                    volume_data = volume.copy()  # Make explicit copy
                    
                log_debug(f"Processing volume with shape: {volume_data.shape}")
            else:
                log_debug("No DICOM series found with SimpleITK")
                
        except Exception as sitk_error:
            log_debug(f"SimpleITK approach failed: {str(sitk_error)}")
            log_debug(traceback.format_exc())
        
        # Approach 2: If SimpleITK failed, try using pydicom directly
        if volume_data is None:
            log_debug("Falling back to direct processing of DICOM files with pydicom...")
            
            # Find all DICOM files
            dicom_files = []
            for root, _, files in os.walk(dicom_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    if file.lower().endswith('.dcm') or not os.path.splitext(file)[1]:
                        dicom_files.append(file_path)
            
            if not dicom_files:
                raise ValueError(f"No DICOM files found in {dicom_folder}")
            
            log_debug(f"Found {len(dicom_files)} potential DICOM files")
            
            # Sort DICOM files by instance number or position
            sorted_files = []
            for file_path in dicom_files:
                try:
                    dcm = pydicom.dcmread(file_path, stop_before_pixels=True)
                    position = 0
                    if hasattr(dcm, 'InstanceNumber'):
                        position = float(dcm.InstanceNumber)
                    elif hasattr(dcm, 'SliceLocation'):
                        position = float(dcm.SliceLocation)
                    elif hasattr(dcm, 'ImagePositionPatient'):
                        position = float(dcm.ImagePositionPatient[2])
                    sorted_files.append((file_path, position))
                except Exception as e:
                    log_debug(f"Error reading DICOM header for {file_path}: {str(e)}")
                    continue
            
            if not sorted_files:
                raise ValueError("No valid DICOM files found")
                
            # Sort files by position
            sorted_files.sort(key=lambda x: x[1])
            sorted_paths = [file for file, _ in sorted_files]
            
            # Read and stack the DICOM files
            slices = []
            for file_path in sorted_paths:
                try:
                    dcm = pydicom.dcmread(file_path)
                    if hasattr(dcm, 'pixel_array'):
                        pixel_data = dcm.pixel_array
                        
                        # Handle RGB data if present
                        if len(pixel_data.shape) == 3 and pixel_data.shape[2] == 3:
                            pixel_data = pixel_data[..., 0]  # Use red channel
                            
                        slices.append(pixel_data)
                except Exception as e:
                    log_debug(f"Error reading pixel data from {file_path}: {str(e)}")
            
            if not slices:
                raise ValueError("Could not read any valid DICOM slices")
            
            # Stack slices to create volume
            try:
                # Check if all slices have the same shape
                first_shape = slices[0].shape
                uniform_slices = [s for s in slices if s.shape == first_shape]
                
                if len(uniform_slices) != len(slices):
                    log_debug(f"Warning: Found slices with different shapes. Using {len(uniform_slices)} uniform slices.")
                    slices = uniform_slices
                
                # Convert to same data type
                uniform_type_slices = [s.astype(np.float32) for s in slices]
                
                # Stack slices
                volume_data = np.stack(uniform_type_slices)
                log_debug(f"Created volume with shape: {volume_data.shape}")
            except Exception as stack_error:
                log_debug(f"Error stacking slices: {str(stack_error)}")
                log_debug(traceback.format_exc())
                # Fallback to using a single slice if stacking fails
                if slices:
                    middle_slice = slices[len(slices)//2]
                    volume_data = np.stack([middle_slice, middle_slice, middle_slice])
                    log_debug(f"Fallback: Created minimal volume from single slice: {volume_data.shape}")
                else:
                    raise ValueError("Failed to create volume data")
        
        # Make sure we have valid volume data
        if volume_data is None:
            raise ValueError("Failed to load DICOM data through multiple approaches")
            
        # Ensure volume data has a valid data type for VTK
        volume_data = volume_data.astype(np.float32)
        
        # Log some statistics about the volume data
        log_debug(f"Volume data statistics: min={volume_data.min()}, max={volume_data.max()}, mean={volume_data.mean()}")
        
        # Auto-detect thresholds if needed
        if lower_threshold is None or upper_threshold is None:
            log_debug("Auto-detecting threshold values...")
            # Sample the volume to avoid memory issues with large volumes
            sample_size = min(1000000, volume_data.size)
            sample_indices = np.random.choice(volume_data.size, sample_size, replace=False)
            sample_values = volume_data.flat[sample_indices]
            
            if lower_threshold is None:
                lower_threshold = np.percentile(sample_values, 25)
                log_debug(f"Auto-detected lower threshold: {lower_threshold}")
                
            if upper_threshold is None:
                upper_threshold = np.percentile(sample_values, 75)
                log_debug(f"Auto-detected upper threshold: {upper_threshold}")
        
        log_debug(f"Using thresholds - Lower: {lower_threshold}, Upper: {upper_threshold}")
        
        # Create binary mask through thresholding
        try:
            log_debug("Creating binary mask...")
            binary_mask = np.logical_and(
                volume_data > lower_threshold,
                volume_data < upper_threshold
            ).astype(np.uint8)
            
            positive_voxels = np.sum(binary_mask)
            log_debug(f"Created segmentation mask with {positive_voxels} positive voxels")
            
            # Check if we have enough voxels
            if positive_voxels < 100:
                log_debug("Warning: Very few voxels in segmentation mask. Trying wider threshold range...")
                # Try a wider threshold range
                p_low = max(0, np.percentile(volume_data, 10))
                p_high = min(np.max(volume_data), np.percentile(volume_data, 90))
                
                binary_mask = np.logical_and(
                    volume_data > p_low,
                    volume_data < p_high
                ).astype(np.uint8)
                
                positive_voxels = np.sum(binary_mask)
                log_debug(f"Adjusted threshold to {p_low}-{p_high}, now have {positive_voxels} voxels")
                
                if positive_voxels < 100:
                    # Still not enough, use value-based approach
                    median_val = np.median(volume_data)
                    binary_mask = (volume_data > median_val * 0.8).astype(np.uint8)
                    positive_voxels = np.sum(binary_mask)
                    log_debug(f"Using value-based threshold, now have {positive_voxels} voxels")
            
            if positive_voxels < 10:
                raise ValueError("Failed to create a usable segmentation mask")
        except Exception as mask_error:
            log_debug(f"Error creating binary mask: {str(mask_error)}")
            log_debug(traceback.format_exc())
            raise
        
        # Approach 1: Use VTK's marching cubes implementation
        try:
            log_debug("Starting VTK surface generation...")
            
            # Get dimensions for VTK
            dims = binary_mask.shape
            log_debug(f"Binary mask shape: {dims}")
            
            # Create VTK data from binary mask - ensure correct memory layout
            flat_mask = binary_mask.flatten(order='F')  # Fortran order for VTK
            log_debug(f"Flattened mask with {len(flat_mask)} elements")
            
            # Create VTK data array
            vtk_data = numpy_support.numpy_to_vtk(
                flat_mask,
                deep=True,
                array_type=vtk.VTK_UNSIGNED_CHAR
            )
            log_debug("Created VTK data array")
            
            # Create a VTK image with correct dimensions (width, height, depth)
            vtk_image = vtk.vtkImageData()
            vtk_image.SetDimensions(dims[2], dims[1], dims[0])  # Swap dimensions for VTK
            vtk_image.GetPointData().SetScalars(vtk_data)
            log_debug(f"Created VTK image with dimensions: {dims[2]}x{dims[1]}x{dims[0]}")
            
            # Generate the surface using Marching Cubes
            log_debug("Running marching cubes algorithm...")
            mc = vtk.vtkMarchingCubes()
            mc.SetInputData(vtk_image)
            mc.SetValue(0, 0.5)  # Threshold for binary mask
            mc.Update()
            
            # Check if surface was generated
            points = mc.GetOutput().GetNumberOfPoints()
            log_debug(f"Marching cubes generated surface with {points} points")
            
            if points == 0:
                log_debug("Warning: No surface generated. Trying with different parameters...")
                # Try with a lower threshold
                mc.SetValue(0, 0.1)
                mc.Update()
                points = mc.GetOutput().GetNumberOfPoints()
                log_debug(f"Adjusted marching cubes generated surface with {points} points")
                
                if points == 0:
                    # Try with different marching cubes algorithm 
                    log_debug("Still no surface. Trying discrete marching cubes...")
                    dmc = vtk.vtkDiscreteMarchingCubes()
                    dmc.SetInputData(vtk_image)
                    dmc.GenerateValues(1, 1, 1)  # Generate surface for label value 1
                    dmc.Update()
                    
                    points = dmc.GetOutput().GetNumberOfPoints()
                    log_debug(f"Discrete marching cubes generated surface with {points} points")
                    
                    if points == 0:
                        raise ValueError("Failed to generate surface from binary mask with multiple approaches")
                    else:
                        mc = dmc  # Use the successful algorithm
            
            # Clean and enhance the surface
            log_debug("Post-processing the surface...")
            
            # Get largest component for cleaner visualization
            connect = vtk.vtkPolyDataConnectivityFilter()
            connect.SetInputConnection(mc.GetOutputPort())
            connect.SetExtractionModeToLargestRegion()
            connect.Update()
            log_debug("Extracted largest connected component")
            
            # Smooth the surface
            smoother = vtk.vtkSmoothPolyDataFilter()
            smoother.SetInputConnection(connect.GetOutputPort())
            smoother.SetNumberOfIterations(15)
            smoother.SetRelaxationFactor(0.2)
            smoother.Update()
            log_debug("Smoothed the surface")
            
            # Compute surface normals for better rendering
            normals = vtk.vtkPolyDataNormals()
            normals.SetInputConnection(smoother.GetOutputPort())
            normals.ComputePointNormalsOn()
            normals.ComputeCellNormalsOn()
            normals.Update()
            log_debug("Computed surface normals")
            
            # Set up rendering
            log_debug("Setting up rendering pipeline...")
            renderer = vtk.vtkRenderer()
            render_window = vtk.vtkRenderWindow()
            render_window.SetOffScreenRendering(1)  # Headless rendering
            render_window.AddRenderer(renderer)
            render_window.SetSize(800, 600)
            
            # Add the surface to the renderer
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(normals.GetOutputPort())
            
            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            
            # Set color to bright red for aorta
            actor.GetProperty().SetColor(0.9, 0.2, 0.2)
            actor.GetProperty().SetSpecular(0.3)
            actor.GetProperty().SetSpecularPower(20)
            
            renderer.AddActor(actor)
            renderer.SetBackground(0.0, 0.0, 0.0)  # Black background
            
            # Add lighting
            light1 = vtk.vtkLight()
            light1.SetIntensity(0.8)
            light1.SetPosition(-100, 100, 100)
            renderer.AddLight(light1)
            
            light2 = vtk.vtkLight()
            light2.SetIntensity(0.6)
            light2.SetPosition(100, 100, -100)
            renderer.AddLight(light2)
            
            # Set up camera
            renderer.ResetCamera()
            camera = renderer.GetActiveCamera()
            camera.Azimuth(30)
            camera.Elevation(30)
            camera.Zoom(1.5)
            
            # Render and save image
            log_debug("Rendering the scene...")
            render_window.Render()
            
            window_to_image = vtk.vtkWindowToImageFilter()
            window_to_image.SetInput(render_window)
            window_to_image.Update()
            
            # Save as PNG
            log_debug(f"Saving output to {output_path}...")
            writer = vtk.vtkPNGWriter()
            writer.SetFileName(output_path)
            writer.SetInputConnection(window_to_image.GetOutputPort())
            writer.Write()
            
            log_debug(f"Successfully saved 3D visualization to: {output_path}")
            return output_path
            
        except Exception as vtk_error:
            log_debug(f"Error in VTK processing: {str(vtk_error)}")
            log_debug(traceback.format_exc())
            
            # Try fallback method - direct rendering of a slice with overlay
            log_debug("Attempting fallback visualization method...")
            try:
                # Take a representative slice from the volume
                if len(volume_data.shape) == 3 and volume_data.shape[0] > 1:
                    # Use the middle slice
                    slice_idx = volume_data.shape[0] // 2
                    slice_data = volume_data[slice_idx]
                else:
                    # Use the first slice if only one exists
                    slice_data = volume_data[0] if len(volume_data.shape) == 3 else volume_data
                
                # Normalize the slice data to 0-255
                min_val = slice_data.min()
                max_val = slice_data.max()
                normalized = ((slice_data - min_val) / (max_val - min_val) * 255).astype(np.uint8)
                
                # Create a mask for the target area based on thresholds
                mask = np.logical_and(
                    slice_data > lower_threshold,
                    slice_data < upper_threshold
                )
                
                # Create an RGB image with red overlay
                rgb_image = np.stack([normalized, normalized, normalized], axis=2)
                rgb_image[mask, 0] = 255  # Red channel
                rgb_image[mask, 1] = 0  # Green channel
                rgb_image[mask, 2] = 0  # Blue channel
                
                # Create a PIL image and add annotations
                pil_img = Image.fromarray(rgb_image)
                draw = ImageDraw.Draw(pil_img)
                draw.text((10, 10), "DICOM Visualization (Fallback Mode)", fill=(255, 255, 255))
                draw.text((10, 30), f"Slice {slice_idx} of {volume_data.shape[0]}", fill=(255, 255, 255))
                
                # Save the image
                pil_img.save(output_path)
                log_debug(f"Saved fallback visualization to {output_path}")
                return output_path
                
            except Exception as fallback_error:
                log_debug(f"Fallback visualization failed: {str(fallback_error)}")
                log_debug(traceback.format_exc())
                raise  # Re-raise the original VTK error
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error creating 3D visualization: {str(e)}")
        print(error_details)
        
        # Create an error image
        try:
            from PIL import Image, ImageDraw
            error_img = Image.new('RGB', (800, 400), color=(255, 240, 240))
            draw = ImageDraw.Draw(error_img)
            draw.text((50, 50), "Error creating 3D visualization:", fill=(200, 0, 0))
            draw.text((50, 80), str(e), fill=(200, 0, 0))
            draw.text((50, 120), "Please check your DICOM files and try again.", fill=(0, 0, 0))
            
            # Include file info
            draw.text((50, 160), f"Input folder: {dicom_folder}", fill=(0, 0, 0))
            draw.text((50, 180), f"See full log at: {os.path.basename(output_path.replace('.png', '_debug.log'))}", fill=(0, 0, 0))
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            error_img.save(output_path)
            print(f"Created error image at: {output_path}")
            return output_path
        except Exception as error_img_error:
            print(f"Error creating error image: {str(error_img_error)}")
            raise e