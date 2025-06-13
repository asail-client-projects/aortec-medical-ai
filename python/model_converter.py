# Handles 3D model conversion tasks, including generating STL models from DICOM images.
#-----------------------------------
import os
import numpy as np
import vtk
from vtk.util import numpy_support
import pydicom
import SimpleITK as sitk
import tempfile
import zipfile
import shutil
import traceback
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont

def convert_to_3d_model(input_path, output_path, lower_threshold=None, upper_threshold=None):
    """
    Convert DICOM files to a 3D STL model.
    
    Args:
        input_path: Path to a folder containing DICOM files or a single DICOM file
        output_path: Path to save the STL model
        lower_threshold: Lower threshold for segmentation (HU value), auto-detected if None
        upper_threshold: Upper threshold for segmentation (HU value), auto-detected if None
        
    Returns:
        Path to the generated STL file
    """
    print(f"[3D Model] Converting {input_path} to {output_path}")
    
    # Import the functions from segmentation.py to avoid circular imports
    from .segmentation import create_3d_model_from_dicom_folder, create_3d_model_from_single_dicom
    
    try:
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # If input is a ZIP file, extract it to a temporary directory
        if isinstance(input_path, str) and input_path.lower().endswith('.zip'):
            temp_dir = tempfile.mkdtemp()
            try:
                with zipfile.ZipFile(input_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                return create_3d_model_from_dicom_folder(temp_dir, output_path, lower_threshold, upper_threshold)
            finally:
                shutil.rmtree(temp_dir, ignore_errors=True)
        
        # If input is a directory, process it as a DICOM folder
        elif isinstance(input_path, str) and os.path.isdir(input_path):
            return create_3d_model_from_dicom_folder(input_path, output_path, lower_threshold, upper_threshold)
        
        # If input is a single file, check if it's a DICOM file
        elif isinstance(input_path, str) and os.path.isfile(input_path):
            # For a single file, create a temporary directory and try to find related files
            temp_dir = tempfile.mkdtemp()
            try:
                # If it's a single DICOM file, copy it to the temp directory
                if input_path.lower().endswith('.dcm') or (not os.path.splitext(input_path)[1]):
                    # Check if other DICOM files exist in the same directory
                    parent_dir = os.path.dirname(input_path)
                    all_files = os.listdir(parent_dir)
                    dicom_count = sum(1 for f in all_files if f.lower().endswith('.dcm') or not os.path.splitext(f)[1])
                    
                    if dicom_count > 1:
                        # If multiple DICOM files exist, use the whole directory
                        return create_3d_model_from_dicom_folder(parent_dir, output_path, lower_threshold, upper_threshold)
                    else:
                        # For a single file, warn that it may not produce a good 3D model
                        print("[WARNING] Creating a 3D model from a single DICOM file may not produce accurate results.")
                        return create_3d_model_from_single_dicom(input_path, output_path, lower_threshold, upper_threshold)
                else:
                    raise ValueError(f"Unsupported file type: {input_path}")
            finally:
                shutil.rmtree(temp_dir, ignore_errors=True)
        else:
            raise ValueError(f"Unsupported input type: {input_path}")
    
    except Exception as e:
        error_details = traceback.format_exc()
        error_message = f"Error creating 3D model: {str(e)}\n{error_details}"
        print(error_message)
        raise Exception(error_message)

def generate_html_viewer(stl_path):
    """
    Generate an HTML file with a 3D STL viewer using Three.js.
    
    Args:
        stl_path: Path to the STL file to visualize
        
    Returns:
        HTML content as a string
    """
    # Import the function from segmentation.py to avoid circular imports
    from .segmentation import generate_html_viewer as _generate_html_viewer
    return _generate_html_viewer(stl_path)