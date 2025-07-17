# Updated segmentation.py - Now compatible with DICOM viewer approach
import os
import numpy as np
import SimpleITK as sitk
from PIL import Image
import zipfile
import tempfile
import shutil
import pydicom
import traceback
import logging
import matplotlib.pyplot as plt
from .dicom_processor import read_dicom_folder, extract_zip

def apply_segmentation(input_folder, output_folder, lower_threshold=100, upper_threshold=300):
    """
    Apply segmentation to all DICOM files in a folder to highlight aortic aneurysm regions.
    
    Args:
        input_folder: Path to the folder containing DICOM files
        output_folder: Path to save segmented images
        lower_threshold: Lower intensity threshold for segmentation
        upper_threshold: Upper intensity threshold for segmentation
        
    Returns:
        List of paths to segmented images
    """
    import os
    import glob
    import numpy as np
    import SimpleITK as sitk
    from PIL import Image
    import pydicom
    
    os.makedirs(output_folder, exist_ok=True)
    segmented_files = []
    
    # First try to read as a DICOM series
    try:
        reader = sitk.ImageSeriesReader()
        dicom_names = reader.GetGDCMSeriesFileNames(input_folder)
        
        if dicom_names:
            print(f"Found {len(dicom_names)} DICOM files in series")
            reader.SetFileNames(dicom_names)
            image = reader.Execute()
            image_array = sitk.GetArrayFromImage(image)
            
            # Process each slice
            for i, slice_data in enumerate(image_array):
                # Normalize slice for visualization
                normalized_slice = ((slice_data - slice_data.min()) / 
                                  (slice_data.max() - slice_data.min()) * 255).astype(np.uint8)
                
                # Apply threshold-based segmentation
                binary_mask = np.logical_and(
                    normalized_slice > lower_threshold,
                    normalized_slice < upper_threshold
                ).astype(np.uint8) * 255
                
                # Create RGB image with red overlay
                rgb_image = np.stack([normalized_slice, normalized_slice, normalized_slice], axis=2)
                overlay_mask = binary_mask > 0
                rgb_image[overlay_mask, 0] = 255  # Red channel
                rgb_image[overlay_mask, 1] = 0    # Green channel
                rgb_image[overlay_mask, 2] = 0    # Blue channel
                
                # Save segmented image
                output_file = os.path.join(output_folder, f"segmented_slice_{i:03d}.png")
                Image.fromarray(rgb_image).save(output_file)
                segmented_files.append(output_file)
                
            return segmented_files
    
    except Exception as e:
        print(f"Error reading as DICOM series: {str(e)}")
    
    # If DICOM series reading fails, try processing individual files
    try:
        # Find all potential DICOM files
        file_list = []
        for ext in ['', '.dcm', '.DCM', '.ima', '.IMA']:
            file_list.extend(glob.glob(os.path.join(input_folder, f'*{ext}')))
        
        if not file_list:
            # Try to find image files instead
            for ext in ['.png', '.jpg', '.jpeg', '.bmp']:
                file_list.extend(glob.glob(os.path.join(input_folder, f'*{ext}')))
        
        print(f"Processing {len(file_list)} individual files")
        
        for i, filepath in enumerate(sorted(file_list)):
            try:
                output_file = os.path.join(output_folder, f"segmented_{i:03d}.png")
                segment_dicom_file(filepath, output_file)
                segmented_files.append(output_file)
            except Exception as file_error:
                print(f"Error processing file {filepath}: {str(file_error)}")
        
        return segmented_files
        
    except Exception as e:
        print(f"Error processing folder: {str(e)}")
        raise

def segment_dicom_file(filepath, output_path):
    """
    Apply segmentation to a DICOM file to highlight the aortic aneurysm.
    
    Args:
        filepath: Path to the DICOM file
        output_path: Path to save the segmented image
    
    Returns:
        Path to the segmented image
    """
    try:
        # Check if file exists
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
            
        print(f"Segmenting file: {filepath}")
        
        # Check if the file is a ZIP archive
        if filepath.lower().endswith('.zip'):
            temp_dir = tempfile.mkdtemp()
            try:
                with zipfile.ZipFile(filepath, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                    
                # Apply segmentation to the extracted DICOM folder
                output_dir = os.path.dirname(output_path)
                segmented_files = apply_segmentation(temp_dir, output_dir)
                
                if segmented_files:
                    # Use the first segmented file as the main result
                    shutil.copy(segmented_files[0], output_path)
                    return output_path
                else:
                    raise ValueError("No files were segmented")
            except Exception as e:
                raise Exception(f"Error processing ZIP file: {str(e)}")
            finally:
                # Clean up temporary directory
                shutil.rmtree(temp_dir, ignore_errors=True)
        
        # For single DICOM file
        try:
            # Try to read with SimpleITK first
            try:
                dicom_image = sitk.ReadImage(filepath)
                dicom_array = sitk.GetArrayFromImage(dicom_image)
            except Exception as sitk_error:
                # Fallback to pydicom
                print(f"SimpleITK failed, using pydicom: {str(sitk_error)}")
                dicom_data = pydicom.dcmread(filepath, force=True)
                dicom_array = dicom_data.pixel_array
            
            # Handle both 3D and 2D data
            if len(dicom_array.shape) > 2:
                # Take the middle slice for demonstration
                slice_data = dicom_array[dicom_array.shape[0] // 2]
            else:
                slice_data = dicom_array
            
            # Normalize data to 0-255 for visualization
            normalized_data = ((slice_data - slice_data.min()) / 
                            (slice_data.max() - slice_data.min()) * 255).astype(np.uint8)
            
            # Apply segmentation through thresholding
            # Adjust these thresholds for AAA detection
            lower_threshold = 100
            upper_threshold = 300
            
            binary_mask = np.logical_and(
                normalized_data > lower_threshold, 
                normalized_data < upper_threshold
            ).astype(np.uint8) * 255
            
            # Create RGB image for better visualization
            rgb_image = np.stack([normalized_data, normalized_data, normalized_data], axis=2)
            
            # Add red overlay for segmented regions
            overlay_mask = binary_mask > 0
            rgb_image[overlay_mask, 0] = 255  # Red channel
            rgb_image[overlay_mask, 1] = 0    # Green channel
            rgb_image[overlay_mask, 2] = 0    # Blue channel
            
            # Save the result
            Image.fromarray(rgb_image).save(output_path)
            print(f"Segmentation saved to {output_path}")
            return output_path
            
        except Exception as e:
            # Fallback method for non-DICOM images or if segmentation fails
            try:
                from PIL import Image, ImageEnhance
                
                # Try to open as regular image
                image = Image.open(filepath).convert('L')  # Convert to grayscale
                image_array = np.array(image)
                
                # Apply simple thresholding
                threshold = np.percentile(image_array, 75)
                binary_mask = (image_array > threshold).astype(np.uint8) * 255
                
                # Create a color overlay
                original_image = Image.open(filepath).convert('RGB')
                mask_image = Image.fromarray(binary_mask)
                
                # Create red overlay
                overlay = Image.new('RGB', original_image.size, (255, 0, 0))
                mask_image = mask_image.convert('L')
                
                # Composite images
                result = Image.composite(overlay, original_image, mask_image)
                
                # Adjust brightness and contrast
                enhancer = ImageEnhance.Brightness(result)
                result = enhancer.enhance(1.2)
                
                # Save result
                result.save(output_path)
                return output_path
                
            except Exception as e2:
                print(f"All segmentation methods failed: {str(e2)}")
                # Create a placeholder image with error message
                error_img = Image.new('RGB', (800, 600), color=(255, 255, 255))
                from PIL import ImageDraw, ImageFont
                draw = ImageDraw.Draw(error_img)
                draw.text((50, 50), f"Segmentation failed: {str(e)}", fill=(255, 0, 0))
                error_img.save(output_path)
                return output_path
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        error_message = f"Error in segmentation: {str(e)}\n{error_details}"
        print(error_message)
        raise Exception(error_message)
    
def process_dicom_folder_for_segmentation(folder_path, output_folder):
    """
    Process a folder of DICOM files for segmentation.
    
    Args:
        folder_path: Path to the folder containing DICOM files
        output_folder: Path to save segmented images
        
    Returns:
        List of paths to the segmented images
    """
    return apply_segmentation(folder_path, output_folder)

# Legacy compatibility functions - redirect to new DICOM viewer implementation
def convert_to_3d_model(input_path, output_path, lower_threshold=None, upper_threshold=None):
    """
    Legacy function - now redirects to DICOM viewer implementation.
    """
    from .model_converter import convert_to_3d_model as new_convert_to_3d_model
    return new_convert_to_3d_model(input_path, output_path, lower_threshold, upper_threshold)

def create_3d_model_from_dicom_folder(dicom_folder, output_path, lower_threshold=None, upper_threshold=None):
    """
    Legacy function - now redirects to DICOM viewer implementation.
    """
    from .model_converter import process_dicom_folder_for_viewer
    
    # Create output directory
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)
    
    # Use the new DICOM viewer functionality
    viewer_result = process_dicom_folder_for_viewer(dicom_folder, output_dir)
    
    # Copy the main image to the requested output path
    if os.path.exists(viewer_result['main_image']):
        shutil.copy(viewer_result['main_image'], output_path)
    
    return output_path

def create_3d_model_from_single_dicom(dicom_file, output_path, lower_threshold=None, upper_threshold=None):
    """
    Legacy function - now creates a simple viewer from single DICOM file.
    """
    print("[WARNING] Creating a viewer from a single DICOM file is not optimal.")
    print("[WARNING] Results may be incomplete without a full DICOM series.")
    
    try:
        # Read the DICOM file
        dcm = pydicom.dcmread(dicom_file)
        
        # Check if pixel data is available
        if not hasattr(dcm, 'pixel_array'):
            raise ValueError("DICOM file does not contain pixel data")
        
        pixel_data = dcm.pixel_array
        
        # Normalize the data
        if pixel_data.max() != pixel_data.min():
            normalized_data = ((pixel_data - pixel_data.min()) / 
                            (pixel_data.max() - pixel_data.min()) * 255).astype(np.uint8)
        else:
            normalized_data = np.zeros_like(pixel_data, dtype=np.uint8)
        
        # Create a simple viewer-like image
        fig, ax = plt.subplots(figsize=(10, 8))
        fig.patch.set_facecolor('black')
        
        # Display the image
        ax.imshow(normalized_data, cmap='gray', aspect='equal')
        
        # Add title
        ax.set_title("DICOM Viewer - Single File", color='white', fontsize=16)
        
        # Add warning text
        ax.text(0.02, 0.98, "WARNING: Single DICOM file viewer\nFor best results, use a complete series", 
                transform=ax.transAxes, color='yellow', fontsize=10,
                verticalalignment='top', bbox=dict(boxstyle="round,pad=0.3", 
                facecolor='red', alpha=0.7))
        
        # Remove axes
        ax.set_xticks([])
        ax.set_yticks([])
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight', 
                   facecolor='black', edgecolor='none')
        plt.close()
        
        print(f"[Single DICOM Viewer] Created viewer from single file: {output_path}")
        return output_path
    
    except Exception as e:
        error_details = traceback.format_exc()
        error_message = f"Error creating viewer from single DICOM: {str(e)}\n{error_details}"
        print(error_message)
        
        # Create an error image
        error_img = Image.new('RGB', (800, 600), color=(255, 240, 240))
        from PIL import ImageDraw
        draw = ImageDraw.Draw(error_img)
        draw.text((50, 50), "Error processing single DICOM file:", fill=(200, 0, 0))
        draw.text((50, 80), str(e), fill=(200, 0, 0))
        draw.text((50, 120), "Single DICOM files often do not contain enough information", fill=(0, 0, 0))
        draw.text((50, 150), "for creating useful viewers. Please use a complete series.", fill=(0, 0, 0))
        
        # Save the error image
        error_img.save(output_path)
        return output_path

def generate_model_preview(poly_data, output_path):
    """
    Legacy function - now creates a simple preview image.
    """
    try:
        # Create a simple placeholder image
        placeholder = Image.new('RGB', (800, 600), color=(50, 50, 50))
        from PIL import ImageDraw
        draw = ImageDraw.Draw(placeholder)
        draw.text((50, 50), "DICOM Viewer Generated", fill=(255, 255, 255))
        draw.text((50, 80), "Use the interactive viewer for full functionality", fill=(200, 200, 200))
        placeholder.save(output_path)
        print(f"[Preview] Created preview image: {output_path}")
    except Exception as e:
        print(f"Error generating preview image: {str(e)}")

def generate_html_viewer(stl_path):
    """
    Legacy function - now redirects to new HTML viewer implementation.
    """
    from .model_converter import generate_html_viewer as new_generate_html_viewer
    
    # Extract directory from STL path to use as DICOM folder
    dicom_folder = os.path.dirname(stl_path)
    return new_generate_html_viewer(dicom_folder)