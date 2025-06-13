# Handles segmentation tasks, including refining the segmented data.
#-----------------------------------
import os
import numpy as np
import SimpleITK as sitk
from PIL import Image
import zipfile
import tempfile
from .dicom_processor import read_dicom_folder, extract_zip
import shutil
import pydicom
import vtk
from vtk.util import numpy_support
import traceback
import logging
import matplotlib.pyplot as plt

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

# New improved 3D model generation functions
def convert_to_3d_model(input_path, output_path, lower_threshold=None, upper_threshold=None):
    """
    Convert DICOM files to a 3D STL model with improved accuracy.
    
    Args:
        input_path: Path to a folder containing DICOM files or a single DICOM file
        output_path: Path to save the STL model
        lower_threshold: Lower threshold for segmentation (HU value), auto-detected if None
        upper_threshold: Upper threshold for segmentation (HU value), auto-detected if None
        
    Returns:
        Path to the generated STL file
    """
    print(f"[3D Model] Converting {input_path} to {output_path}")
    
    try:
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Make sure the thresholds are properly parsed
        if lower_threshold is not None and not isinstance(lower_threshold, (int, float)):
            try:
                lower_threshold = float(lower_threshold)
            except (ValueError, TypeError):
                print(f"[3D Model] Invalid lower threshold value '{lower_threshold}', using default")
                lower_threshold = None
                
        if upper_threshold is not None and not isinstance(upper_threshold, (int, float)):
            try:
                upper_threshold = float(upper_threshold)
            except (ValueError, TypeError):
                print(f"[3D Model] Invalid upper threshold value '{upper_threshold}', using default")
                upper_threshold = None
        
        # Create a temporary directory for processing
        temp_dir = tempfile.mkdtemp()
        print(f"[3D Model] Created temporary directory: {temp_dir}")
        
        try:
            # If input is a ZIP file, extract it to the temporary directory
            if isinstance(input_path, str) and input_path.lower().endswith('.zip'):
                try:
                    with zipfile.ZipFile(input_path, 'r') as zip_ref:
                        zip_ref.extractall(temp_dir)
                    input_folder = temp_dir
                    print(f"[3D Model] Extracted ZIP file to {temp_dir}")
                except Exception as e:
                    print(f"[3D Model] Error extracting ZIP file: {str(e)}")
                    raise ValueError(f"Failed to extract ZIP file: {str(e)}")
            
            # If input is a directory, use it directly
            elif isinstance(input_path, str) and os.path.isdir(input_path):
                input_folder = input_path
                print(f"[3D Model] Using existing folder: {input_folder}")
            
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
                
                print(f"[3D Model] Found {dicom_count} DICOM files in parent directory")
                
                if dicom_count > 1:
                    # If multiple DICOM files exist, use the parent directory
                    input_folder = parent_dir
                    print(f"[3D Model] Using parent directory containing multiple DICOM files: {input_folder}")
                else:
                    # For a single file, copy it to the temp directory and warn that it may not produce a good 3D model
                    print("[3D Model] WARNING: Creating a 3D model from a single DICOM file may not produce accurate results.")
                    shutil.copy(input_path, os.path.join(temp_dir, os.path.basename(input_path)))
                    input_folder = temp_dir
            else:
                raise ValueError(f"Unsupported input type: {input_path}")
            
            # Load the DICOM series from the folder
            print(f"[3D Model] Loading DICOM series from {input_folder}")
            
            # Create the 3D model
            return create_3d_model_from_dicom_folder(input_folder, output_path, lower_threshold, upper_threshold)
            
        finally:
            # Clean up the temporary directory if it's not the input_path
            if os.path.exists(temp_dir) and temp_dir != input_path:
                try:
                    shutil.rmtree(temp_dir)
                    print(f"[3D Model] Cleaned up temporary directory: {temp_dir}")
                except Exception as e:
                    print(f"[3D Model] Error cleaning up temporary directory: {str(e)}")
    
    except Exception as e:
        error_details = traceback.format_exc()
        error_message = f"Error creating 3D model: {str(e)}\n{error_details}"
        print(error_message)
        
        # Generate a simple error image instead
        try:
            error_img = Image.new('RGB', (800, 600), color=(255, 240, 240))
            from PIL import ImageDraw
            draw = ImageDraw.Draw(error_img)
            draw.text((50, 50), "Error generating 3D model:", fill=(200, 0, 0))
            draw.text((50, 80), str(e), fill=(200, 0, 0))
            draw.text((50, 120), "Please check if your DICOM files are valid and from the same series.", fill=(0, 0, 0))
            draw.text((50, 150), "Try adjusting threshold values or using a different set of files.", fill=(0, 0, 0))
            
            # Save the error image in place of the preview
            preview_path = output_path.replace('.stl', '_preview.png')
            error_img.save(preview_path)
            print(f"[3D Model] Created error image at {preview_path}")
            
            # Create a simple placeholder STL file
            with open(output_path, 'wb') as f:
                f.write(b'ERROR: Failed to generate STL model')
            
            return output_path
        except:
            # Last resort - just re-raise the original error
            raise Exception(error_message)

def create_3d_model_from_dicom_folder(dicom_folder, output_path, lower_threshold=None, upper_threshold=None):
    """
    Create a 3D model from a folder of DICOM files using VTK.
    
    Args:
        dicom_folder: Path to the folder containing DICOM files
        output_path: Path to save the STL model
        lower_threshold: Lower threshold for segmentation (HU value), auto-detected if None
        upper_threshold: Upper threshold for segmentation (HU value), auto-detected if None
        
    Returns:
        Path to the generated STL file
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
        
        print(f"[3D Model] Found {len(dicom_files)} DICOM files")
        
        # Use VTK's DICOM reader to read the series
        reader = vtk.vtkDICOMImageReader()
        reader.SetDirectoryName(dicom_folder)
        reader.Update()
        
        # Get image data
        image_data = reader.GetOutput()
        dimensions = image_data.GetDimensions()
        spacing = image_data.GetSpacing()
        
        print(f"[3D Model] Image dimensions: {dimensions}, spacing: {spacing}")
        
        # Set default thresholds if not provided and if auto-detection fails
        if lower_threshold is None:
            lower_threshold = 100  # Default fallback value
        
        if upper_threshold is None:
            upper_threshold = 3000  # Default fallback value
        
        # Try to auto-detect threshold values if not provided
        try:
            # Get the scalar range of the volume
            scalar_range = image_data.GetScalarRange()
            print(f"[3D Model] Scalar range: {scalar_range}")
            
            # For CT images, use Hounsfield units (HU)
            # Extract data as numpy array for analysis
            vtk_data = image_data.GetPointData().GetScalars()
            
            # Ensure we have valid data to analyze
            if vtk_data and vtk_data.GetNumberOfTuples() > 0:
                numpy_data = numpy_support.vtk_to_numpy(vtk_data)
                
                # Only reshape if dimensions make sense
                if (dimensions[0] * dimensions[1] * dimensions[2]) == len(numpy_data):
                    numpy_data = numpy_data.reshape(dimensions[2], dimensions[1], dimensions[0])
                    
                    # Get histogram for visualization
                    hist, bin_edges = np.histogram(numpy_data.flatten(), bins=100)
                    
                    # Auto-detect thresholds only if we don't have user-provided values
                    if lower_threshold is None or upper_threshold is None:
                        # Use more robust method to find thresholds
                        sorted_data = np.sort(numpy_data.flatten())
                        
                        # Remove background (usually air) by skipping lowest 10%
                        start_idx = int(len(sorted_data) * 0.1)
                        if start_idx < len(sorted_data):
                            non_background = sorted_data[start_idx:]
                            
                            # Only calculate percentiles if we have enough data
                            if len(non_background) > 0:
                                if lower_threshold is None:
                                    # Default lower threshold: 25th percentile of non-background
                                    lower_threshold = int(np.percentile(non_background, 25))
                                
                                if upper_threshold is None:
                                    # Default upper threshold: 75th percentile of non-background
                                    upper_threshold = int(np.percentile(non_background, 75))
                                    
                                print(f"[3D Model] Auto-detected thresholds - Lower: {lower_threshold}, Upper: {upper_threshold}")
        except Exception as e:
            print(f"[3D Model] Auto-threshold detection failed: {str(e)}. Using default values.")
            # If auto-detection fails, use default values
            if lower_threshold is None:
                lower_threshold = 100  # Common threshold for soft tissue in CT
            
            if upper_threshold is None:
                upper_threshold = 3000  # Maximum typical HU value
        
        # Ensure we have valid threshold values
        print(f"[3D Model] Using thresholds - Lower: {lower_threshold}, Upper: {upper_threshold}")
        
        # Try to create a histogram image for preview if we have valid data
        try:
            plt.figure(figsize=(10, 6))
            vtk_data = image_data.GetPointData().GetScalars()
            if vtk_data and vtk_data.GetNumberOfTuples() > 0:
                numpy_data = numpy_support.vtk_to_numpy(vtk_data)
                plt.hist(numpy_data, bins=100, alpha=0.7)
                plt.axvline(lower_threshold, color='r', linestyle='--', label=f'Lower Threshold ({lower_threshold})')
                plt.axvline(upper_threshold, color='g', linestyle='--', label=f'Upper Threshold ({upper_threshold})')
                plt.title('Intensity Histogram with Segmentation Thresholds')
                plt.xlabel('Intensity')
                plt.ylabel('Frequency')
                plt.legend()
                
                # Save histogram preview
                preview_path = output_path.replace('.stl', '_histogram.png')
                plt.savefig(preview_path)
            plt.close()
        except Exception as e:
            print(f"[3D Model] Could not generate histogram: {str(e)}")
        
        # Create a threshold filter to segment the AAA
        threshold = vtk.vtkImageThreshold()
        threshold.SetInputConnection(reader.GetOutputPort())
        threshold.ThresholdBetween(lower_threshold, upper_threshold)
        threshold.ReplaceInOn()
        threshold.SetInValue(1)
        threshold.ReplaceOutOn()
        threshold.SetOutValue(0)
        threshold.Update()
        
        # Generate surface with marching cubes
        surface = vtk.vtkMarchingCubes() if vtk.vtkVersion().GetVTKMajorVersion() < 6 else vtk.vtkDiscreteMarchingCubes()
        surface.SetInputConnection(threshold.GetOutputPort())
        surface.GenerateValues(1, 1, 1)
        surface.Update()
        
        # Check if the output has any points
        if surface.GetOutput().GetNumberOfPoints() == 0:
            raise ValueError("No surface was generated. Try adjusting threshold values.")
        
        # Smooth the surface
        smoother = vtk.vtkWindowedSincPolyDataFilter()
        smoother.SetInputConnection(surface.GetOutputPort())
        smoother.SetNumberOfIterations(15)
        smoother.SetPassBand(0.1)
        smoother.SetBoundarySmoothing(True)
        smoother.Update()
        
        # Decimate (reduce polygon count) to make the model more manageable
        decimate = vtk.vtkDecimatePro()
        decimate.SetInputConnection(smoother.GetOutputPort())
        decimate.SetTargetReduction(0.5)  # Reduce by 50%
        decimate.PreserveTopologyOn()
        decimate.Update()
        
        # Get the largest connected component to remove small floating pieces
        connect = vtk.vtkPolyDataConnectivityFilter()
        connect.SetInputConnection(decimate.GetOutputPort())
        connect.SetExtractionModeToLargestRegion()
        connect.Update()
        
        # Generate surface normals for better rendering
        normals = vtk.vtkPolyDataNormals()
        normals.SetInputConnection(connect.GetOutputPort())
        normals.SetFeatureAngle(60.0)
        normals.Update()
        
        # Save the model to STL file
        writer = vtk.vtkSTLWriter()
        writer.SetInputConnection(normals.GetOutputPort())
        writer.SetFileName(output_path)
        writer.SetFileTypeToBinary()
        writer.Write()
        
        print(f"[3D Model] Successfully created STL model: {output_path}")
        
        # Generate a preview image
        generate_model_preview(normals.GetOutput(), output_path.replace('.stl', '_preview.png'))
        
        return output_path
        
    except Exception as e:
        error_details = traceback.format_exc()
        error_message = f"Error creating 3D model from DICOM folder: {str(e)}\n{error_details}"
        print(error_message)
        raise Exception(error_message)

def create_3d_model_from_single_dicom(dicom_file, output_path, lower_threshold=None, upper_threshold=None):
    """
    Create a simple 3D model from a single DICOM file - limited functionality.
    
    Args:
        dicom_file: Path to a DICOM file
        output_path: Path to save the STL model
        lower_threshold: Lower threshold for segmentation (HU value)
        upper_threshold: Upper threshold for segmentation (HU value)
        
    Returns:
        Path to the generated STL file
    """
    print("[WARNING] Creating a 3D model from a single DICOM file is not recommended.")
    print("[WARNING] Results may be incomplete or inaccurate without a full DICOM series.")
    
    try:
        # Read the DICOM file
        dcm = pydicom.dcmread(dicom_file)
        print(dicom_file)
        
        # Check if pixel data is available
        if not hasattr(dcm, 'pixel_array'):
            raise ValueError("DICOM file does not contain pixel data")
        
        pixel_data = dcm.pixel_array
        
        # Convert to proper 3D volume (single slice)
        # This won't create a true 3D model, but will create a relief map of the slice
        if len(pixel_data.shape) == 2:
            # Create a 3D volume with a small thickness
            volume = np.zeros((3, pixel_data.shape[0], pixel_data.shape[1]), dtype=np.float32)
            for i in range(3):  # Create 3 slices for minimal thickness
                volume[i, :, :] = pixel_data.astype(np.float32)
        else:
            # In case the single DICOM already contains a 3D volume
            volume = pixel_data.astype(np.float32)
        
        # Convert the volume to a VTK image
        flat_data = volume.ravel()
        
        # Create VTK data array
        vtk_data = numpy_support.numpy_to_vtk(flat_data, deep=True, array_type=vtk.VTK_FLOAT)
        
        # Create a VTK image data
        vtk_image = vtk.vtkImageData()
        vtk_image.SetDimensions(volume.shape[2], volume.shape[1], volume.shape[0])
        vtk_image.GetPointData().SetScalars(vtk_data)
        
        # Auto-detect thresholds if needed
        if lower_threshold is None:
            # Default for a single slice: use the 30th percentile
            lower_threshold = int(np.percentile(volume, 30))
        
        if upper_threshold is None:
            # Default for a single slice: use the 70th percentile
            upper_threshold = int(np.percentile(volume, 70))
        
        print(f"Using thresholds - Lower: {lower_threshold}, Upper: {upper_threshold}")
        
        # Create a threshold filter
        threshold = vtk.vtkImageThreshold()
        threshold.SetInputData(vtk_image)
        threshold.ThresholdBetween(lower_threshold, upper_threshold)
        threshold.ReplaceInOn()
        threshold.SetInValue(1)
        threshold.ReplaceOutOn()
        threshold.SetOutValue(0)
        threshold.Update()
        
        # Generate surface with marching cubes
        surface = vtk.vtkMarchingCubes()
        surface.SetInputConnection(threshold.GetOutputPort())
        surface.SetValue(0, 0.5)
        surface.Update()
        
        # Check if we got any surface
        if surface.GetOutput().GetNumberOfPoints() == 0:
            raise ValueError("No surface could be extracted with the current threshold values")
        
        # Smooth the surface
        smoother = vtk.vtkSmoothPolyDataFilter()
        smoother.SetInputConnection(surface.GetOutputPort())
        smoother.SetNumberOfIterations(15)
        smoother.SetRelaxationFactor(0.1)
        smoother.Update()
        
        # Save the model to STL file
        writer = vtk.vtkSTLWriter()
        writer.SetInputConnection(smoother.GetOutputPort())
        writer.SetFileName(output_path)
        writer.SetFileTypeToBinary()
        writer.Write()
        
        # Generate a warning image for preview
        warning_img = Image.new('RGB', (800, 600), color=(255, 255, 255))
        from PIL import ImageDraw
        draw = ImageDraw.Draw(warning_img)
        draw.text((50, 50), "WARNING: 3D model created from a single DICOM file.", fill=(255, 0, 0))
        draw.text((50, 80), "Results may be incomplete or inaccurate.", fill=(255, 0, 0))
        draw.text((50, 110), "For best results, use a complete DICOM series.", fill=(255, 0, 0))
        draw.text((50, 160), f"Threshold values used: Lower={lower_threshold}, Upper={upper_threshold}", fill=(0, 0, 0))
        
        # Add a small visualization of the slice if possible
        try:
            # Normalize the middle slice for display
            if len(pixel_data.shape) == 2:
                slice_img = pixel_data
            else:
                slice_img = pixel_data[pixel_data.shape[0]//2]
                
            # Normalize to 0-255
            min_val = np.min(slice_img)
            max_val = np.max(slice_img)
            if max_val > min_val:
                norm_slice = ((slice_img - min_val) / (max_val - min_val) * 255).astype(np.uint8)
                pil_slice = Image.fromarray(norm_slice)
                
                # Resize to fit in the preview
                max_size = 300
                ratio = min(max_size / pil_slice.width, max_size / pil_slice.height)
                new_size = (int(pil_slice.width * ratio), int(pil_slice.height * ratio))
                pil_slice = pil_slice.resize(new_size)
                
                # Paste into the warning image
                warning_img.paste(pil_slice, (50, 200))
        except Exception as e:
            print(f"Could not include slice visualization: {str(e)}")
        
        preview_path = output_path.replace('.stl', '_preview.png')
        warning_img.save(preview_path)
        
        print(f"[3D Model] Created limited STL model from single file: {output_path}")
        
        return output_path
    
    except Exception as e:
        error_details = traceback.format_exc()
        error_message = f"Error creating 3D model from single DICOM: {str(e)}\n{error_details}"
        print(error_message)
        
        # Create an error image
        error_img = Image.new('RGB', (800, 600), color=(255, 240, 240))
        from PIL import ImageDraw
        draw = ImageDraw.Draw(error_img)
        draw.text((50, 50), "Error processing single DICOM file:", fill=(200, 0, 0))
        draw.text((50, 80), str(e), fill=(200, 0, 0))
        draw.text((50, 120), "Single DICOM files often do not contain enough information", fill=(0, 0, 0))
        draw.text((50, 150), "for creating useful 3D models. Please use a complete series.", fill=(0, 0, 0))
        
        # Save the error image
        preview_path = output_path.replace('.stl', '_preview.png')
        error_img.save(preview_path)
        
        # Create a simple placeholder STL file
        with open(output_path, 'wb') as f:
            f.write(b'ERROR: Failed to generate STL model from single DICOM')
            
        return output_path
    

def generate_model_preview(poly_data, output_path):
    """
    Generate a preview image of the 3D model.
    
    Args:
        poly_data: VTK PolyData containing the 3D model
        output_path: Path to save the preview image
    """
    try:
        # Check if polydata is valid
        if not poly_data or poly_data.GetNumberOfPoints() == 0:
            raise ValueError("Invalid polydata - no points to render")
            
        # Create a renderer and window
        renderer = vtk.vtkRenderer()
        render_window = vtk.vtkRenderWindow()
        render_window.SetOffScreenRendering(1)  # Off-screen rendering
        render_window.AddRenderer(renderer)
        render_window.SetSize(800, 600)
        
        # Create a render window interactor - needed for off-screen rendering
        interactor = vtk.vtkRenderWindowInteractor()
        interactor.SetRenderWindow(render_window)
        
        # Add the model to the renderer
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(poly_data)
        
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(1.0, 0.5, 0.5)  # Reddish color for AAA
        
        renderer.AddActor(actor)
        renderer.SetBackground(0.1, 0.1, 0.2)  # Dark blue background
        
        # Add orientation axes if available in this VTK version
        try:
            axes = vtk.vtkAxesActor()
            axes.SetTotalLength(50, 50, 50)
            axes.SetShaftTypeToCylinder()
            axes.SetCylinderRadius(0.02)
            
            widget = vtk.vtkOrientationMarkerWidget()
            widget.SetOutlineColor(0.9300, 0.5700, 0.1300)
            widget.SetOrientationMarker(axes)
            widget.SetInteractor(interactor)
            widget.SetViewport(0.0, 0.0, 0.2, 0.2)
            widget.SetEnabled(1)
            widget.InteractiveOff()
        except Exception as e:
            print(f"Could not add orientation axes: {str(e)}")
        
        # Initialize the interactor - required for off-screen rendering
        interactor.Initialize()
        
        # Reset camera to view the entire model
        renderer.ResetCamera()
        camera = renderer.GetActiveCamera()
        camera.Azimuth(30)
        camera.Elevation(30)
        renderer.ResetCameraClippingRange()
        
        # Render the scene
        render_window.Render()
        
        # Save the image
        window_to_image = vtk.vtkWindowToImageFilter()
        window_to_image.SetInput(render_window)
        window_to_image.SetScale(1)
        window_to_image.Update()
        
        writer = vtk.vtkPNGWriter()
        writer.SetFileName(output_path)
        writer.SetInputConnection(window_to_image.GetOutputPort())
        writer.Write()
        
        print(f"[3D Model] Preview image saved to: {output_path}")
    
    except Exception as e:
        print(f"Error generating preview image: {str(e)}")
        # Create a simple placeholder image
        placeholder = Image.new('RGB', (800, 600), color=(200, 200, 200))
        from PIL import ImageDraw
        draw = ImageDraw.Draw(placeholder)
        draw.text((50, 50), f"3D Model Preview Not Available: {str(e)}", fill=(0, 0, 0))
        placeholder.save(output_path)

def generate_html_viewer(stl_path):
    """
    Generate an HTML file with a 3D STL viewer using Three.js.
    
    Args:
        stl_path: Path to the STL file to visualize
        
    Returns:
        HTML content as a string
    """
    # Extract the model filename from the path
    model_filename = os.path.basename(stl_path)
    model_url = f"/serve/processed/{model_filename}"
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AORTEC 3D Model Viewer</title>
        <style>
            body {{ margin: 0; overflow: hidden; }}
            #info {{
                position: absolute;
                top: 10px;
                width: 100%;
                text-align: center;
                color: white;
                font-family: Arial, sans-serif;
                pointer-events: none;
                text-shadow: 0 0 4px #000;
            }}
            #controls {{
                position: absolute;
                bottom: 10px;
                left: 10px;
                background-color: rgba(0,0,0,0.6);
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-family: Arial, sans-serif;
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        <div id="info">AORTEC 3D Model Viewer</div>
        <div id="controls">
            <div>Rotate: Left-click + drag</div>
            <div>Pan: Shift + left-click + drag</div>
            <div>Zoom: Mouse wheel or right-click + drag</div>
        </div>
        
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/stats.js/r17/Stats.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/dat-gui/0.7.7/dat.gui.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/examples/js/controls/OrbitControls.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/examples/js/loaders/STLLoader.js"></script>
        
        <script>
            // Scene setup
            const scene = new THREE.Scene();
            scene.background = new THREE.Color(0x111122);
            
            // Camera setup
            const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 5000);
            camera.position.set(0, 0, 200);
            
            // Renderer setup
            const renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setPixelRatio(window.devicePixelRatio);
            document.body.appendChild(renderer.domElement);
            
            // Lights
            const ambientLight = new THREE.AmbientLight(0x404040, 1);
            scene.add(ambientLight);
            
            const directionalLight1 = new THREE.DirectionalLight(0xffffff, 0.8);
            directionalLight1.position.set(1, 1, 1);
            scene.add(directionalLight1);
            
            const directionalLight2 = new THREE.DirectionalLight(0xffffff, 0.5);
            directionalLight2.position.set(-1, -1, -1);
            scene.add(directionalLight2);
            
            // Controls
            const controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.25;
            controls.rotateSpeed = 0.35;
            
            // STL Model loading
            const loader = new THREE.STLLoader();
            loader.load('{model_url}', function(geometry) {{
                // Center the geometry
                geometry.computeBoundingBox();
                const boundingBox = geometry.boundingBox;
                const center = new THREE.Vector3();
                boundingBox.getCenter(center);
                geometry.translate(-center.x, -center.y, -center.z);
                
                // Calculate size for camera positioning
                const size = new THREE.Vector3();
                boundingBox.getSize(size);
                const maxDim = Math.max(size.x, size.y, size.z);
                const dist = maxDim * 2;
                camera.position.set(dist, dist, dist);
                camera.lookAt(0, 0, 0);
                
                // Create material with aorta-like color
                const material = new THREE.MeshPhongMaterial({{
                    color: 0xee4b4b,
                    specular: 0x111111,
                    shininess: 100,
                    side: THREE.DoubleSide
                }});
                
                const mesh = new THREE.Mesh(geometry, material);
                scene.add(mesh);
                
                // Add wireframe for better visibility
                const wireframeMaterial = new THREE.MeshBasicMaterial({{
                    color: 0xffffff,
                    wireframe: true,
                    transparent: true,
                    opacity: 0.15
                }});
                const wireframe = new THREE.Mesh(geometry, wireframeMaterial);
                scene.add(wireframe);
                
                // Set camera to fit the model
                controls.reset();
                
                // Add a floor grid for orientation
                const gridHelper = new THREE.GridHelper(maxDim * 2, 20, 0x888888, 0x444444);
                gridHelper.position.y = -maxDim / 2;
                scene.add(gridHelper);
                
                // Add axes for orientation
                const axesHelper = new THREE.AxesHelper(maxDim);
                scene.add(axesHelper);
            }});
            
            // Handle window resize
            window.addEventListener('resize', function() {{
                const width = window.innerWidth;
                const height = window.innerHeight;
                camera.aspect = width / height;
                camera.updateProjectionMatrix();
                renderer.setSize(width, height);
            }});
            
            // Animation loop
            function animate() {{
                requestAnimationFrame(animate);
                controls.update();
                renderer.render(scene, camera);
            }}
            
            animate();
        </script>
    </body>
    </html>
    """