# Updated model_converter.py - Now implements DICOM viewer functionality
import os
import numpy as np
import pydicom
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_agg import FigureCanvasAgg
from PIL import Image, ImageDraw, ImageFont
import tempfile
import shutil
import traceback
import cv2
import base64
import io
from matplotlib.figure import Figure
import time

class DicomViewer:
    def __init__(self, dicom_folder):
        self.dicom_folder = dicom_folder
        self.image_paths = []
        self.current_index = 0
        self.load_dicom_files()
    
    def load_dicom_files(self):
        """Load all DICOM files from the folder"""
        files = []
        for root, _, filenames in os.walk(self.dicom_folder):
            for filename in filenames:
                filepath = os.path.join(root, filename)
                if filename.lower().endswith('.dcm') or '.' not in filename:
                    try:
                        # Test if it's a valid DICOM file
                        pydicom.dcmread(filepath, stop_before_pixels=True)
                        files.append(filepath)
                    except:
                        continue
        
        # Sort files by instance number or filename
        self.image_paths = sorted(files, key=self._get_sort_key)
        
        if not self.image_paths:
            raise ValueError("No DICOM files found in the specified folder.")
    
    def _get_sort_key(self, filepath):
        """Get sorting key for DICOM files"""
        try:
            ds = pydicom.dcmread(filepath, stop_before_pixels=True)
            if hasattr(ds, 'InstanceNumber'):
                return int(ds.InstanceNumber)
            elif hasattr(ds, 'SliceLocation'):
                return float(ds.SliceLocation)
            else:
                return os.path.basename(filepath)
        except:
            return os.path.basename(filepath)
    
    def get_image_at_index(self, index):
        """Get DICOM image at specific index"""
        if 0 <= index < len(self.image_paths):
            return self._load_dicom_image(self.image_paths[index])
        return None
    
    def _load_dicom_image(self, filepath):
        """Load a single DICOM image exactly like the original"""
        try:
            ds = pydicom.dcmread(filepath)
            if not hasattr(ds, 'pixel_array'):
                raise ValueError(f"File {filepath} has no pixel data.")
            
            # Use pixel_array directly like the original - NO conversions
            pixel_array = ds.pixel_array
            
            # Only handle multi-frame if absolutely necessary
            if len(pixel_array.shape) == 3 and pixel_array.shape[0] > 1:
                # Multi-frame - take first frame only if it's actually multi-frame
                if pixel_array.shape[2] == 3:
                    # This is RGB data - DON'T convert to grayscale, keep original
                    pass  # Keep as-is
                else:
                    # True multi-frame, take the middle frame
                    pixel_array = pixel_array[pixel_array.shape[0] // 2]
            
            return {
                'image': pixel_array,
                'dataset': ds,
                'filepath': filepath
            }
        except Exception as e:
            print(f"Error loading DICOM image {filepath}: {str(e)}")
            return None
    
    def create_viewer_image(self, index=None, output_path=None):
        """Create a viewer image with ruler exactly like the original tkinter version"""
        if index is None:
            index = len(self.image_paths) // 2  # Use middle image
        
        dicom_data = self.get_image_at_index(index)
        if not dicom_data:
            raise ValueError(f"Could not load DICOM image at index {index}")
        
        img = dicom_data['image']
        ds = dicom_data['dataset']
        
        # Create matplotlib figure with same size as original (8,8)
        fig, ax = plt.subplots(figsize=(8, 8))
        fig.patch.set_facecolor('black')
        
        # Display the image EXACTLY like the original - no processing at all
        # Just like: self.ax.imshow(img, cmap='gray')
        ax.imshow(img, cmap='gray')
        
        # Add ruler with exact same parameters as original
        self._draw_ruler(ax, img.shape, ds)
        
        # Remove axes exactly like original
        ax.axis('off')
        
        # Add title with slice information
        title = f"AORTEC DICOM Viewer - Image {index + 1} of {len(self.image_paths)}"
        fig.suptitle(title, color='white', fontsize=14, y=0.95)
        
        # Add image info in bottom left like original
        info_text = self._get_image_info(ds)
        fig.text(0.02, 0.02, info_text, color='white', fontsize=8, 
                verticalalignment='bottom', bbox=dict(boxstyle="round,pad=0.2", 
                facecolor='black', alpha=0.7))
        
        # Use tight_layout like original
        fig.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=100, bbox_inches='tight', 
                       facecolor='black', edgecolor='none')
            plt.close()
            return output_path
        else:
            # Return as base64 string for web display
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight', 
                       facecolor='black', edgecolor='none')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            return f"data:image/png;base64,{image_base64}"
    
    def _draw_ruler(self, ax, shape, ds):
        """Draw ruler on the image exactly like the original implementation"""
        height, width = shape[:2]
        
        # Get pixel spacing exactly like original
        pixel_spacing_mm = 1.0
        if hasattr(ds, 'PixelSpacing'):
            pixel_spacing_mm = float(ds.PixelSpacing[0])
        
        # Ruler parameters exactly like original
        major_tick_mm = 50
        minor_tick_mm = 10
        ruler_margin_px = 30
        
        # Calculate ruler dimensions exactly like original
        v_ruler_pixels = height - 2 * ruler_margin_px
        v_ruler_mm = v_ruler_pixels * pixel_spacing_mm
        
        h_ruler_pixels = width - 2 * ruler_margin_px
        h_ruler_mm = h_ruler_pixels * pixel_spacing_mm
        
        # Vertical ruler position exactly like original
        v_x = width - ruler_margin_px
        v_y_bottom = height - ruler_margin_px
        v_y_top = v_y_bottom - v_ruler_pixels
        
        # Horizontal ruler position exactly like original
        h_x_right = v_x
        h_x_left = v_x - h_ruler_pixels
        h_y = v_y_bottom
        
        # Draw vertical ruler exactly like original
        ax.plot([v_x, v_x], [v_y_bottom, v_y_top], color='yellow', linewidth=2)
        
        # Vertical ruler ticks exactly like original
        for mm in range(0, int(v_ruler_mm) + 1, major_tick_mm):
            y_pos = v_y_bottom - mm / pixel_spacing_mm
            ax.plot([v_x - 8, v_x + 8], [y_pos, y_pos], color='red', linewidth=2)
            ax.text(v_x + 12, y_pos, f"{mm}", color='yellow', fontsize=6, va='center')
        
        for mm in range(0, int(v_ruler_mm) + 1, minor_tick_mm):
            if mm % major_tick_mm == 0:
                continue
            y_pos = v_y_bottom - mm / pixel_spacing_mm
            ax.plot([v_x - 4, v_x + 4], [y_pos, y_pos], color='red', linewidth=1)
        
        # Vertical ruler label exactly like original
        ax.text(v_x + 20, v_y_bottom - v_ruler_pixels / 2, f"{v_ruler_mm:.1f} mm",
                color='yellow', rotation=90, fontsize=8, va='center',
                bbox=dict(facecolor='black', alpha=0.5, pad=2))
        
        # Draw horizontal ruler exactly like original
        ax.plot([h_x_left, h_x_right], [h_y, h_y], color='yellow', linewidth=2)
        
        # Horizontal ruler ticks exactly like original
        for mm in range(0, int(h_ruler_mm) + 1, major_tick_mm):
            x_pos = h_x_right - mm / pixel_spacing_mm
            ax.plot([x_pos, x_pos], [h_y - 8, h_y + 8], color='red', linewidth=2)
            ax.text(x_pos, h_y + 12, f"{mm}", color='yellow', fontsize=6, ha='center')
        
        for mm in range(0, int(h_ruler_mm) + 1, minor_tick_mm):
            if mm % major_tick_mm == 0:
                continue
            x_pos = h_x_right - mm / pixel_spacing_mm
            ax.plot([x_pos, x_pos], [h_y - 4, h_y + 4], color='red', linewidth=1)
        
        # Horizontal ruler label exactly like original
        ax.text(h_x_right - h_ruler_pixels / 2, h_y + 25, f"{h_ruler_mm:.1f} mm",
                color='yellow', fontsize=8, ha='center',
                bbox=dict(facecolor='black', alpha=0.5, pad=2))
        
        # Pixel spacing info exactly like original
        ax.text(ruler_margin_px, ruler_margin_px,
                f"Pixel Spacing: {pixel_spacing_mm:.2f} mm/pixel",
                color='white', fontsize=8, weight='bold')
    
    def _get_image_info(self, ds):
        """Get image information for display"""
        info = []
        
        if hasattr(ds, 'PatientName'):
            info.append(f"Patient: {ds.PatientName}")
        if hasattr(ds, 'StudyDate'):
            info.append(f"Study Date: {ds.StudyDate}")
        if hasattr(ds, 'Modality'):
            info.append(f"Modality: {ds.Modality}")
        if hasattr(ds, 'SliceThickness'):
            info.append(f"Slice Thickness: {ds.SliceThickness} mm")
        if hasattr(ds, 'KVP'):
            info.append(f"KVP: {ds.KVP}")
        
        return "\n".join(info)
    
    def create_multi_view_image(self, output_path, num_views=6):
        """Create a multi-view image showing several slices"""
        if len(self.image_paths) < num_views:
            num_views = len(self.image_paths)
        
        # Calculate indices for evenly spaced views
        indices = np.linspace(0, len(self.image_paths) - 1, num_views, dtype=int)
        
        # Create subplot grid
        cols = 3
        rows = (num_views + cols - 1) // cols
        fig, axes = plt.subplots(rows, cols, figsize=(15, 5 * rows))
        fig.patch.set_facecolor('black')
        
        if rows == 1:
            axes = [axes] if num_views == 1 else axes
        else:
            axes = axes.flatten()
        
        for i, idx in enumerate(indices):
            dicom_data = self.get_image_at_index(idx)
            if dicom_data:
                img = dicom_data['image']
                ds = dicom_data['dataset']
                
                ax = axes[i]
                # Use image directly like original - no processing
                ax.imshow(img, cmap='gray', aspect='equal')
                ax.set_title(f"Slice {idx + 1}", color='white', fontsize=12)
                ax.set_xticks([])
                ax.set_yticks([])
                
                # Add mini ruler
                self._draw_mini_ruler(ax, img.shape, ds)
        
        # Hide unused subplots
        for i in range(num_views, len(axes)):
            axes[i].set_visible(False)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight', 
                   facecolor='black', edgecolor='none')
        plt.close()
        
        return output_path
    
    def _draw_mini_ruler(self, ax, shape, ds):
        """Draw a simplified ruler for multi-view"""
        height, width = shape[:2]
        
        # Get pixel spacing
        pixel_spacing_mm = 1.0
        if hasattr(ds, 'PixelSpacing'):
            pixel_spacing_mm = float(ds.PixelSpacing[0])
        
        # Mini ruler parameters
        ruler_length = min(width, height) // 4
        ruler_x = width - ruler_length - 20
        ruler_y = height - 30
        
        # Draw ruler line
        ax.plot([ruler_x, ruler_x + ruler_length], [ruler_y, ruler_y], 
               color='yellow', linewidth=2)
        
        # Add measurement
        ruler_mm = ruler_length * pixel_spacing_mm
        ax.text(ruler_x + ruler_length/2, ruler_y - 10, f"{ruler_mm:.0f} mm",
                color='yellow', fontsize=8, ha='center', va='top')


def convert_to_3d_model(input_path, output_path, lower_threshold=None, upper_threshold=None):
    """
    Convert DICOM files to a DICOM viewer with measurements (replacing old STL generation).
    
    Args:
        input_path: Path to a folder containing DICOM files
        output_path: Path to save the main viewer image
        lower_threshold: Not used in viewer (kept for compatibility)
        upper_threshold: Not used in viewer (kept for compatibility)
        
    Returns:
        Path to the main generated viewer image
    """
    print(f"[DICOM Viewer] Converting {input_path} to viewer at {output_path}")
    
    try:
        # Create output directory
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Prepare input folder
        temp_dir = tempfile.mkdtemp()
        try:
            input_folder = prepare_input_folder(input_path, temp_dir)
            
            # Create DICOM viewer
            viewer = DicomViewer(input_folder)
            
            # Generate main viewer image (middle slice)
            middle_index = len(viewer.image_paths) // 2
            main_output = output_path.replace('.stl', '.png') if output_path.endswith('.stl') else output_path
            if not main_output.endswith('.png'):
                main_output += '.png'
            
            viewer.create_viewer_image(middle_index, main_output)
            
            # Generate multi-view image
            multi_output = main_output.replace('.png', '_multi.png')
            viewer.create_multi_view_image(multi_output)
            
            # Generate navigation images
            prev_output = main_output.replace('.png', '_prev.png')
            next_output = main_output.replace('.png', '_next.png')
            
            prev_index = max(0, middle_index - 1)
            next_index = min(len(viewer.image_paths) - 1, middle_index + 1)
            
            viewer.create_viewer_image(prev_index, prev_output)
            viewer.create_viewer_image(next_index, next_output)
            
            print(f"[DICOM Viewer] Successfully created viewer: {main_output}")
            return main_output
            
        finally:
            # Cleanup
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
    
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"[DICOM Viewer] ERROR: {str(e)}")
        print(error_details)
        
        # Create error outputs
        create_error_outputs(str(e), output_path)
        return output_path

def prepare_input_folder(input_path, temp_dir):
    """Prepare input folder for DICOM processing."""
    import zipfile
    
    if isinstance(input_path, str) and input_path.lower().endswith('.zip'):
        with zipfile.ZipFile(input_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        return temp_dir
    elif os.path.isdir(input_path):
        return input_path
    else:
        raise ValueError(f"Input must be a directory or ZIP file: {input_path}")

def create_error_outputs(error_message, output_path):
    """Create error outputs."""
    # Error image
    error_img = Image.new('RGB', (800, 600), color=(255, 240, 240))
    draw = ImageDraw.Draw(error_img)
    draw.text((50, 50), "Error generating DICOM viewer:", fill=(200, 0, 0))
    draw.text((50, 80), str(error_message)[:80], fill=(200, 0, 0))
    
    # Ensure output has .png extension
    if not output_path.endswith('.png'):
        output_path = output_path.replace('.stl', '.png') if '.stl' in output_path else output_path + '.png'
    
    error_img.save(output_path)

def generate_html_viewer(dicom_folder):
    """
    Generate an HTML viewer for DICOM files with navigation buttons like the original 3dModel.py.
    
    Args:
        dicom_folder: Path to folder containing DICOM files
        
    Returns:
        HTML content as a string
    """
    try:
        viewer = DicomViewer(dicom_folder)
        
        # Generate all images as base64
        images_data = []
        for i in range(len(viewer.image_paths)):
            img_data = viewer.create_viewer_image(i)
            images_data.append(img_data)
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>AORTEC DICOM Viewer</title>
            <style>
                body {{
                    margin: 0;
                    padding: 20px;
                    background-color: #1a1a1a;
                    color: white;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                }}
                .viewer-container {{
                    max-width: 1000px;
                    width: 100%;
                    background-color: #2a2a2a;
                    border-radius: 10px;
                    padding: 20px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.5);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 20px;
                    border-bottom: 2px solid #f9a826;
                    padding-bottom: 15px;
                }}
                .image-container {{
                    text-align: center;
                    margin-bottom: 20px;
                    background-color: #000;
                    border-radius: 5px;
                    padding: 10px;
                }}
                .dicom-image {{
                    max-width: 100%;
                    max-height: 70vh;
                    width: auto;
                    height: auto;
                    border: 2px solid #f9a826;
                    border-radius: 5px;
                }}
                .controls {{
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    gap: 20px;
                    margin-bottom: 20px;
                    padding: 15px;
                    background-color: #3a3a3a;
                    border-radius: 8px;
                }}
                .btn {{
                    background-color: #f9a826;
                    color: #1a1a1a;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 5px;
                    cursor: pointer;
                    font-weight: bold;
                    font-size: 16px;
                    transition: all 0.3s ease;
                    min-width: 140px;
                }}
                .btn:hover {{
                    background-color: #e09515;
                    transform: translateY(-2px);
                }}
                .btn:disabled {{
                    background-color: #666;
                    cursor: not-allowed;
                    transform: none;
                }}
                .slice-info {{
                    background-color: #3a3a3a;
                    padding: 15px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                    text-align: center;
                }}
                .slice-number {{
                    font-size: 18px;
                    font-weight: bold;
                    color: #f9a826;
                }}
                .progress-bar {{
                    width: 100%;
                    height: 25px;
                    background-color: #444;
                    border-radius: 12px;
                    margin: 15px 0;
                    overflow: hidden;
                    position: relative;
                }}
                .progress-fill {{
                    height: 100%;
                    background: linear-gradient(90deg, #f9a826 0%, #e09515 100%);
                    transition: width 0.3s ease;
                    border-radius: 12px;
                }}
                .progress-text {{
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    font-weight: bold;
                    font-size: 12px;
                    color: white;
                    text-shadow: 1px 1px 1px rgba(0,0,0,0.8);
                }}
                .instructions {{
                    background-color: #3a3a3a;
                    padding: 15px;
                    border-radius: 5px;
                    margin-top: 20px;
                }}
                .instructions h3 {{
                    color: #f9a826;
                    margin-top: 0;
                }}
                .keyboard-hint {{
                    text-align: center;
                    color: #ccc;
                    font-size: 14px;
                    margin-top: 10px;
                }}
                @media (max-width: 768px) {{
                    .controls {{
                        flex-direction: column;
                        gap: 15px;
                    }}
                    .btn {{
                        width: 200px;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="viewer-container">
                <div class="header">
                    <h1>AORTEC DICOM Viewer</h1>
                    <p>Navigate through DICOM slices with measurement rulers</p>
                </div>
                
                <div class="image-container">
                    <img id="dicom-image" class="dicom-image" src="{images_data[0]}" alt="DICOM Image">
                </div>
                
                <div class="controls">
                    <button class="btn" id="prev-btn" onclick="changeImage(-1)">⬅️ Previous View</button>
                    <button class="btn" id="next-btn" onclick="changeImage(1)">Next View ➡️</button>
                </div>
                
                <div class="slice-info">
                    <div class="slice-number">
                        Current Slice: <span id="current-slice">1</span> of <span id="total-slices">{len(images_data)}</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" id="progress-fill" style="width: {100/len(images_data) if len(images_data) > 0 else 0}%"></div>
                        <div class="progress-text" id="progress-text">1 / {len(images_data)}</div>
                    </div>
                    <div class="keyboard-hint">
                        💡 Use keyboard arrow keys ← → for quick navigation
                    </div>
                </div>
                
                <div class="instructions">
                    <h3>How to Use the Viewer</h3>
                    <ul>
                        <li><strong>Navigation:</strong> Use the Previous/Next buttons or keyboard arrow keys</li>
                        <li><strong>Measurements:</strong> Yellow rulers show precise measurements in millimeters</li>
                        <li><strong>Red Markers:</strong> Tick marks indicate measurement intervals (major: 50mm, minor: 10mm)</li>
                        <li><strong>Pixel Spacing:</strong> Displayed in the top-left corner for accuracy</li>
                        <li><strong>Medical Information:</strong> Patient and study details shown in the bottom-left</li>
                    </ul>
                </div>
            </div>
            
            <script>
                const images = {images_data};
                let currentIndex = 0;
                const totalImages = images.length;
                
                function updateImage() {{
                    const imageElement = document.getElementById('dicom-image');
                    const currentSliceElement = document.getElementById('current-slice');
                    const progressFillElement = document.getElementById('progress-fill');
                    const progressTextElement = document.getElementById('progress-text');
                    
                    imageElement.src = images[currentIndex];
                    currentSliceElement.textContent = currentIndex + 1;
                    
                    const progressPercent = ((currentIndex + 1) / totalImages) * 100;
                    progressFillElement.style.width = progressPercent + '%';
                    progressTextElement.textContent = `${{currentIndex + 1}} / ${{totalImages}}`;
                    
                    // Update button states
                    document.getElementById('prev-btn').disabled = currentIndex === 0;
                    document.getElementById('next-btn').disabled = currentIndex === totalImages - 1;
                }}
                
                function changeImage(direction) {{
                    const newIndex = currentIndex + direction;
                    if (newIndex >= 0 && newIndex < totalImages) {{
                        currentIndex = newIndex;
                        updateImage();
                    }}
                }}
                
                // Keyboard navigation (matching original 3dModel.py functionality)
                document.addEventListener('keydown', function(event) {{
                    if (event.key === 'ArrowLeft') {{
                        event.preventDefault();
                        changeImage(-1);
                    }} else if (event.key === 'ArrowRight') {{
                        event.preventDefault();
                        changeImage(1);
                    }}
                }});
                
                // Initialize the viewer
                updateImage();
                
                // Add smooth transitions
                document.getElementById('dicom-image').addEventListener('load', function() {{
                    this.style.opacity = '0';
                    setTimeout(() => {{
                        this.style.transition = 'opacity 0.3s ease';
                        this.style.opacity = '1';
                    }}, 50);
                }});
            </script>
        </body>
        </html>
        """
        
        return html_content
        
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"Error creating HTML viewer: {str(e)}\n{error_details}")
        return f"""
        <html>
        <body style="background: #1a1a1a; color: white; font-family: Arial; padding: 20px;">
            <h1 style="color: #f9a826;">Error Loading DICOM Viewer</h1>
            <p>Error: {str(e)}</p>
            <p>Please check that your DICOM files are valid and try again.</p>
        </body>
        </html>
        """


def process_dicom_folder_for_viewer(dicom_folder, output_folder):
    """
    Process a DICOM folder and create viewer images (main function for web app).
    
    Args:
        dicom_folder: Path to folder containing DICOM files
        output_folder: Path to save output images
        
    Returns:
        Dictionary with paths to generated images
    """
    try:
        os.makedirs(output_folder, exist_ok=True)
        
        # Create DICOM viewer
        viewer = DicomViewer(dicom_folder)
        
        # Generate main viewer image (middle slice)
        middle_index = len(viewer.image_paths) // 2
        main_output = os.path.join(output_folder, "dicom_viewer_main.png")
        viewer.create_viewer_image(middle_index, main_output)
        
        # Generate multi-view image
        multi_output = os.path.join(output_folder, "dicom_viewer_multi.png")
        viewer.create_multi_view_image(multi_output)
        
        # Generate navigation images (previous, current, next)
        nav_images = []
        for i, name in enumerate(['previous', 'current', 'next']):
            nav_index = max(0, min(len(viewer.image_paths) - 1, middle_index - 1 + i))
            nav_output = os.path.join(output_folder, f"dicom_viewer_{name}.png")
            viewer.create_viewer_image(nav_index, nav_output)
            nav_images.append(nav_output)
        
        # Generate interactive HTML viewer
        html_output = os.path.join(output_folder, "interactive_viewer.html")
        html_content = generate_html_viewer(dicom_folder)
        with open(html_output, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return {
            'main_image': main_output,
            'multi_view': multi_output,
            'navigation_images': nav_images,
            'interactive_viewer': html_output,
            'total_slices': len(viewer.image_paths),
            'viewer': viewer
        }
        
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"Error processing DICOM folder: {str(e)}\n{error_details}")
        raise