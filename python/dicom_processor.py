# Contains functions related to loading, processing, and converting DICOM images.
#-----------------------------------
import os
import zipfile
import pydicom
import numpy as np
from PIL import Image
import SimpleITK as sitk

def read_dicom_folder(folder_path):
    """Reads all DICOM files from a folder."""
    dicom_files = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".dcm"):
                dicom_files.append(os.path.join(root, file))
    if not dicom_files:
        raise ValueError("No DICOM files found in the specified folder.")
    return dicom_files

def extract_zip(zip_path, extract_to):
    """Extracts a zip file to a specified folder."""
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    return extract_to

def convert_dicom_to_images(dicom_files, output_folder, image_format="jpg"):
    """Converts a list of DICOM files to images."""
    os.makedirs(output_folder, exist_ok=True)
    for dicom_file in dicom_files:
        try:
            ds = pydicom.dcmread(dicom_file)
            if not hasattr(ds, "pixel_array"):
                raise ValueError(f"File {dicom_file} has no pixel data.")
            pixel_array = ds.pixel_array
            image = Image.fromarray((pixel_array / np.max(pixel_array) * 255).astype(np.uint8))
            output_file = os.path.join(
                output_folder, os.path.splitext(os.path.basename(dicom_file))[0] + f".{image_format}"
            )
            image.save(output_file)
        except Exception as e:
            print(f"Error converting {dicom_file}: {e}")
    return output_folder

def process_dicom_file(filepath, output_path):
    """
    Process a DICOM file and save it as an image with improved error handling.
    
    Args:
        filepath: Path to the DICOM file (with or without extension)
        output_path: Path to save the processed image
    """
    # Import PIL at the top level to ensure it's available throughout the function
    from PIL import Image
    
    try:
        # Check if file exists
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
            
        # Log file metadata
        file_size = os.path.getsize(filepath)
        print(f"Processing file: {filepath}, Size: {file_size} bytes")
        
        # Try to read the file as DICOM using SimpleITK
        try:
            import SimpleITK as sitk
            dicom_image = sitk.ReadImage(filepath)
            
            # Get and print image properties for debugging
            size = dicom_image.GetSize()
            spacing = dicom_image.GetSpacing()
            print(f"DICOM image loaded. Size: {size}, Spacing: {spacing}")
            
            # Extract the image data
            dicom_array = sitk.GetArrayFromImage(dicom_image)
            
            # Check array shape and content
            print(f"Array shape: {dicom_array.shape}, Min: {dicom_array.min()}, Max: {dicom_array.max()}")
            
            if dicom_array.min() == dicom_array.max():
                raise ValueError("Image has no contrast (min value equals max value)")
                
            # Normalize to 0-255 for standard image format
            if dicom_array.max() != dicom_array.min():  # Avoid division by zero
                dicom_array = ((dicom_array - dicom_array.min()) / 
                            (dicom_array.max() - dicom_array.min()) * 255).astype(np.uint8)
            else:
                dicom_array = np.zeros_like(dicom_array, dtype=np.uint8)
            
            # Save as image
            if len(dicom_array.shape) > 2:  # If it's 3D data, take the middle slice
                print(f"3D DICOM with {dicom_array.shape[0]} slices, using middle slice")
                middle_slice = dicom_array.shape[0] // 2
                img = Image.fromarray(dicom_array[middle_slice])
            else:
                img = Image.fromarray(dicom_array)
            
            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            img.save(output_path)
            print(f"Image saved to {output_path}")
            return output_path
            
        except Exception as sitk_error:
            print(f"SimpleITK failed: {str(sitk_error)}")
            
            # Fallback to pydicom
            print("Trying pydicom as fallback...")
            import pydicom
            
            # Force reading even if issues
            dicom_data = pydicom.dcmread(filepath, force=True)
            
            # Check if pixel data exists
            if not hasattr(dicom_data, 'PixelData'):
                raise ValueError(f"File does not contain pixel data: {filepath}")
                
            # Convert to image
            pixel_array = dicom_data.pixel_array
            
            # Check array shape and content
            print(f"Array shape: {pixel_array.shape}, Min: {pixel_array.min()}, Max: {pixel_array.max()}")
            
            # Normalize to 0-255 for standard image format
            if pixel_array.max() != pixel_array.min():  # Avoid division by zero
                pixel_array = ((pixel_array - pixel_array.min()) / 
                             (pixel_array.max() - pixel_array.min()) * 255).astype(np.uint8)
            else:
                pixel_array = np.zeros_like(pixel_array, dtype=np.uint8)
            
            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save as image
            img = Image.fromarray(pixel_array)
            img.save(output_path)
            print(f"Image saved to {output_path} using pydicom")
            return output_path
    
    except Exception as e:
        # Create detailed error message
        import traceback
        error_details = traceback.format_exc()
        error_message = f"Error processing DICOM file: {str(e)}\n{error_details}"
        print(error_message)
        
        # Create a simple error image instead of failing completely
        try:
            # Create a small error image with text
            error_img = Image.new('RGB', (400, 100), color=(255, 200, 200))
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(error_img)
            draw.text((10, 10), f"Error: {str(e)[:50]}...", fill=(200, 0, 0))
            draw.text((10, 40), "This DICOM file could not be processed", fill=(0, 0, 0))
            
            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save error image
            error_img.save(output_path)
            print(f"Created error image at {output_path}")
            return output_path
        except:
            # If even creating an error image fails, re-raise the original exception
            raise Exception(error_message)
    

def process_zip_file(zip_filepath, output_folder):
    """
    Extract files from a ZIP file and process them as DICOM files.
    
    Args:
        zip_filepath: Path to the ZIP file containing DICOM files
        output_folder: Path to save the processed images
        
    Returns:
        List of paths to the processed images
    """
    import zipfile
    import tempfile
    import os
    
    # Create a temporary directory for extraction
    temp_dir = tempfile.mkdtemp()
    
    # Extract ZIP file
    with zipfile.ZipFile(zip_filepath, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    
    # Process all files in the extracted folder as potential DICOM files
    processed_files = []
    for root, _, files in os.walk(temp_dir):
        for file in files:
            file_path = os.path.join(root, file)
            output_path = os.path.join(output_folder, f"{file}.jpg")
            
            try:
                # Try to process as DICOM file
                process_dicom_file(file_path, output_path)
                processed_files.append(output_path)
            except Exception as e:
                print(f"Error processing {file}: {str(e)}")
    
    return processed_files

def inspect_dicom_file(filepath):
    """
    Inspect and print detailed information about a DICOM file.
    Useful for debugging problematic files.
    
    Args:
        filepath: Path to the DICOM file
    """
    try:
        import pydicom
        
        # Try to read the file
        print(f"Attempting to read: {filepath}")
        try:
            ds = pydicom.dcmread(filepath, force=True)
        except Exception as e:
            print(f"Error reading file with pydicom: {str(e)}")
            return
            
        # Basic file info
        print(f"File successfully read with pydicom")
        print(f"Transfer Syntax: {ds.file_meta.TransferSyntaxUID if hasattr(ds, 'file_meta') else 'Not available'}")
        
        # Check for pixel data
        if hasattr(ds, 'PixelData'):
            print(f"Pixel Data: Present (length: {len(ds.PixelData)} bytes)")
            
            # Try to access pixel array
            try:
                pixel_array = ds.pixel_array
                print(f"Pixel Array: Shape {pixel_array.shape}, "
                      f"Min {pixel_array.min()}, Max {pixel_array.max()}, "
                      f"Data type {pixel_array.dtype}")
            except Exception as e:
                print(f"Error accessing pixel array: {str(e)}")
        else:
            print("Pixel Data: Not present")
            
        # Important DICOM attributes
        print("\nKey DICOM attributes:")
        important_tags = [
            'PatientID', 'Modality', 'SOPClassUID', 'PhotometricInterpretation',
            'BitsAllocated', 'BitsStored', 'HighBit', 'PixelRepresentation',
            'Rows', 'Columns', 'SamplesPerPixel'
        ]
        
        for tag in important_tags:
            if hasattr(ds, tag):
                print(f"  {tag}: {getattr(ds, tag)}")
            else:
                print(f"  {tag}: Not present")
                
    except Exception as e:
        print(f"Inspection error: {str(e)}")


def create_zip_archive(files_to_zip, output_zip_path):
    """Create a ZIP archive with improved error handling."""
    try:
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_zip_path), exist_ok=True)
        
        # Create the ZIP file
        with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in files_to_zip:
                if os.path.exists(file):
                    # Add file to the zip with just its basename
                    zipf.write(file, os.path.basename(file))
        
        # Verify the zip file was created successfully
        if not os.path.exists(output_zip_path):
            raise FileNotFoundError(f"ZIP file was not created: {output_zip_path}")
        
        # Check if the ZIP file is valid
        with zipfile.ZipFile(output_zip_path, 'r') as test_zip:
            # Test ZIP file integrity
            test_result = test_zip.testzip()
            if test_result is not None:
                raise zipfile.BadZipFile(f"Bad ZIP file, first bad file is {test_result}")
        
        return output_zip_path
    except Exception as e:
        print(f"Error creating ZIP file: {str(e)}")
        raise