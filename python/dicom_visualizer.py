# Enhanced dicom_visualizer.py with navigation inspired by 3dModel.py
import os
import pydicom
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_agg import FigureCanvasAgg
import tempfile
import base64
import io
from PIL import Image
import json
import re

class WebDicomViewer:
    """
    Enhanced web-compatible DICOM viewer with navigation functionality 
    inspired by 3dModel.py tkinter implementation
    """
    
    def __init__(self, dicom_folder):
        self.dicom_folder = dicom_folder
        self.image_paths = []
        self.current_index = 0
        self.load_dicom_files()
    
    def load_dicom_files(self):
        """Load and sort DICOM files by name (inspired by 3dModel.py sorting)"""
        files = []
        for root, _, filenames in os.walk(self.dicom_folder):
            for filename in filenames:
                filepath = os.path.join(root, filename)
                # Same logic as 3dModel.py: .dcm files or files without extension
                if filename.lower().endswith('.dcm') or '.' not in filename:
                    try:
                        # Test if it's a valid DICOM file
                        pydicom.dcmread(filepath, stop_before_pixels=True)
                        files.append(filepath)
                    except:
                        continue
        
        # Sort files by name first, then by instance number like 3dModel.py
        files.sort(key=lambda f: os.path.basename(f))
        
        # Further sort by DICOM properties if available
        self.image_paths = sorted(files, key=self._get_sort_key)
        
        if not self.image_paths:
            raise ValueError("No DICOM files found in the specified folder.")
    
    def _get_sort_key(self, filepath):
        """Get sorting key for DICOM files - enhanced version"""
        try:
            ds = pydicom.dcmread(filepath, stop_before_pixels=True)
            # Try multiple sorting criteria
            if hasattr(ds, 'InstanceNumber'):
                return (int(ds.InstanceNumber), os.path.basename(filepath))
            elif hasattr(ds, 'SliceLocation'):
                return (float(ds.SliceLocation), os.path.basename(filepath))
            elif hasattr(ds, 'ImagePositionPatient'):
                # Use Z-coordinate for sorting
                return (float(ds.ImagePositionPatient[2]), os.path.basename(filepath))
            else:
                return (0, os.path.basename(filepath))
        except:
            return (0, os.path.basename(filepath))
    
    def get_image_data(self, index):
        """Get DICOM image data at specific index"""
        if 0 <= index < len(self.image_paths):
            return self._load_dicom_image(self.image_paths[index])
        return None
    
    def _load_dicom_image(self, filepath):
        """Load a single DICOM image - same logic as 3dModel.py"""
        try:
            ds = pydicom.dcmread(filepath)
            if not hasattr(ds, 'pixel_array'):
                raise ValueError(f"File {filepath} has no pixel data.")
            
            # Use pixel_array directly like 3dModel.py
            pixel_array = ds.pixel_array
            
            # Handle multi-frame if necessary
            if len(pixel_array.shape) == 3 and pixel_array.shape[0] > 1:
                if pixel_array.shape[2] == 3:
                    # RGB data - keep as-is
                    pass
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
    
    def create_viewer_image_web(self, index=None, save_path=None):
        """
        Create a viewer image with ruler exactly like 3dModel.py 
        but optimized for web display
        """
        if index is None:
            index = 0  # Start from first image like 3dModel.py
        
        dicom_data = self.get_image_data(index)
        if not dicom_data:
            raise ValueError(f"Could not load DICOM image at index {index}")
        
        img = dicom_data['image']
        ds = dicom_data['dataset']
        
        # Create matplotlib figure - same size as 3dModel.py
        fig, ax = plt.subplots(figsize=(8, 8))
        fig.patch.set_facecolor('black')
        
        # Display the image exactly like 3dModel.py: ax.imshow(img, cmap='gray')
        ax.imshow(img, cmap='gray')
        
        # Add ruler with exact same logic as 3dModel.py
        self._draw_ruler_web(ax, img.shape, ds)
        
        # Remove axes exactly like 3dModel.py
        ax.axis('off')
        
        # Add title with slice information (inspired by 3dModel.py navigation)
        title = f"AORTEC DICOM Viewer - Image {index + 1} of {len(self.image_paths)}"
        fig.suptitle(title, color='white', fontsize=14, y=0.95)
        
        # Add image info like 3dModel.py
        info_text = self._get_image_info(ds)
        fig.text(0.02, 0.02, info_text, color='white', fontsize=8, 
                verticalalignment='bottom', bbox=dict(boxstyle="round,pad=0.2", 
                facecolor='black', alpha=0.7))
        
        # Use tight_layout like 3dModel.py
        fig.tight_layout()
        
        if save_path:
            # Save to file
            plt.savefig(save_path, dpi=100, bbox_inches='tight', 
                       facecolor='black', edgecolor='none')
            plt.close()
            return save_path
        else:
            # Return as base64 string for web display
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight', 
                       facecolor='black', edgecolor='none')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            return f"data:image/png;base64,{image_base64}"
    
    def _draw_ruler_web(self, ax, shape, ds):
        """Draw ruler exactly like 3dModel.py draw_ruler method"""
        height, width = shape[:2]
        
        # Get pixel spacing exactly like 3dModel.py
        pixel_spacing_mm = 1.0
        if hasattr(ds, 'PixelSpacing'):
            pixel_spacing_mm = float(ds.PixelSpacing[0])
        
        # Ruler parameters exactly like 3dModel.py
        major_tick_mm = 50
        minor_tick_mm = 10
        ruler_margin_px = 30
        
        # Calculate ruler dimensions exactly like 3dModel.py
        v_ruler_pixels = height - 2 * ruler_margin_px
        v_ruler_mm = v_ruler_pixels * pixel_spacing_mm
        
        h_ruler_pixels = width - 2 * ruler_margin_px
        h_ruler_mm = h_ruler_pixels * pixel_spacing_mm
        
        # Vertical ruler position exactly like 3dModel.py
        v_x = width - ruler_margin_px
        v_y_bottom = height - ruler_margin_px
        v_y_top = v_y_bottom - v_ruler_pixels
        
        # Horizontal ruler position exactly like 3dModel.py
        h_x_right = v_x
        h_x_left = v_x - h_ruler_pixels
        h_y = v_y_bottom
        
        # Draw vertical ruler exactly like 3dModel.py
        ax.plot([v_x, v_x], [v_y_bottom, v_y_top], color='yellow', linewidth=2)
        
        # Vertical ruler ticks exactly like 3dModel.py
        for mm in range(0, int(v_ruler_mm) + 1, major_tick_mm):
            y_pos = v_y_bottom - mm / pixel_spacing_mm
            ax.plot([v_x - 8, v_x + 8], [y_pos, y_pos], color='red', linewidth=2)
            ax.text(v_x + 12, y_pos, f"{mm}", color='yellow', fontsize=6, va='center')
        
        for mm in range(0, int(v_ruler_mm) + 1, minor_tick_mm):
            if mm % major_tick_mm == 0:
                continue
            y_pos = v_y_bottom - mm / pixel_spacing_mm
            ax.plot([v_x - 4, v_x + 4], [y_pos, y_pos], color='red', linewidth=1)
        
        # Vertical ruler label exactly like 3dModel.py
        ax.text(v_x + 20, v_y_bottom - v_ruler_pixels / 2, f"{v_ruler_mm:.1f} mm",
                color='yellow', rotation=90, fontsize=8, va='center',
                bbox=dict(facecolor='black', alpha=0.5, pad=2))
        
        # Draw horizontal ruler exactly like 3dModel.py
        ax.plot([h_x_left, h_x_right], [h_y, h_y], color='yellow', linewidth=2)
        
        # Horizontal ruler ticks exactly like 3dModel.py
        for mm in range(0, int(h_ruler_mm) + 1, major_tick_mm):
            x_pos = h_x_right - mm / pixel_spacing_mm
            ax.plot([x_pos, x_pos], [h_y - 8, h_y + 8], color='red', linewidth=2)
            ax.text(x_pos, h_y + 12, f"{mm}", color='yellow', fontsize=6, ha='center')
        
        for mm in range(0, int(h_ruler_mm) + 1, minor_tick_mm):
            if mm % major_tick_mm == 0:
                continue
            x_pos = h_x_right - mm / pixel_spacing_mm
            ax.plot([x_pos, x_pos], [h_y - 4, h_y + 4], color='red', linewidth=1)
        
        # Horizontal ruler label exactly like 3dModel.py
        ax.text(h_x_right - h_ruler_pixels / 2, h_y + 25, f"{h_ruler_mm:.1f} mm",
                color='yellow', fontsize=8, ha='center',
                bbox=dict(facecolor='black', alpha=0.5, pad=2))
        
        # Pixel spacing info exactly like 3dModel.py
        ax.text(ruler_margin_px, ruler_margin_px,
                f"Pixel Spacing: {pixel_spacing_mm:.2f} mm/pixel",
                color='white', fontsize=8, weight='bold')
    
    def _get_image_info(self, ds):
        """Get image information for display - same as 3dModel.py would show"""
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
    
    def generate_interactive_html_viewer(self, output_path):
        """
        Generate an HTML file with interactive DICOM viewer 
        with navigation buttons like 3dModel.py (⬅️ Previous View / Next View ➡️)
        """
        # Generate all images as base64 (starting from index 0)
        images_data = []
        for i in range(len(self.image_paths)):
            img_data = self.create_viewer_image_web(i)
            images_data.append(img_data)
        
        # HTML template with navigation inspired by 3dModel.py
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
                    position: relative;
                    text-align: center;
                    margin-bottom: 20px;
                    background-color: #000;
                    border-radius: 5px;
                    padding: 10px;
                }}
                .dicom-image {{
                    max-width: 100%;
                    max-height: 60vh;
                    width: auto;
                    height: auto;
                    border: 2px solid #f9a826;
                    border-radius: 5px;
                    object-fit: contain;
                }}
                /* Navigation buttons positioned like 3dModel.py */
                .nav-btn {{
                    position: absolute;
                    top: 50%;
                    transform: translateY(-50%);
                    background-color: rgba(249, 168, 38, 0.9);
                    color: #1a1a1a;
                    border: none;
                    padding: 15px 20px;
                    border-radius: 5px;
                    cursor: pointer;
                    font-weight: bold;
                    font-size: 16px;
                    transition: all 0.3s ease;
                    z-index: 10;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.3);
                }}
                .nav-btn:hover {{
                    background-color: rgba(224, 149, 21, 0.95);
                    transform: translateY(-50%) scale(1.05);
                }}
                .nav-btn:disabled {{
                    background-color: rgba(102, 102, 102, 0.5);
                    cursor: not-allowed;
                    transform: translateY(-50%);
                }}
                .prev-btn {{
                    left: 10px;
                }}
                .next-btn {{
                    right: 10px;
                }}
                /* Controls section - inspired by 3dModel.py button frame */
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
                    .nav-btn {{
                        font-size: 14px;
                        padding: 10px 15px;
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
                    <!-- Navigation buttons positioned like 3dModel.py -->
                    <button class="nav-btn prev-btn" id="prev-nav-btn" onclick="changeImage(-1)">⬅️</button>
                    <img id="dicom-image" class="dicom-image" src="{images_data[0]}" alt="DICOM Image">
                    <button class="nav-btn next-btn" id="next-nav-btn" onclick="changeImage(1)">➡️</button>
                </div>
                
                <!-- Additional controls like 3dModel.py buttons -->
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
                    <h3>How to Use the Viewer (Inspired by 3dModel.py)</h3>
                    <ul>
                        <li><strong>Navigation:</strong> Use the arrow buttons on the image or the Previous/Next buttons below</li>
                        <li><strong>Keyboard:</strong> Use arrow keys ← → for quick navigation (like 3dModel.py)</li>
                        <li><strong>Measurements:</strong> Yellow rulers show precise measurements in millimeters</li>
                        <li><strong>Red Markers:</strong> Tick marks indicate measurement intervals (major: 50mm, minor: 10mm)</li>
                        <li><strong>Pixel Spacing:</strong> Displayed in the top-left corner for accuracy</li>
                        <li><strong>Sorting:</strong> Images are sorted by name and DICOM properties</li>
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
                    document.getElementById('prev-nav-btn').disabled = currentIndex === 0;
                    document.getElementById('next-nav-btn').disabled = currentIndex === totalImages - 1;
                }}
                
                function changeImage(direction) {{
                    const newIndex = currentIndex + direction;
                    if (newIndex >= 0 && newIndex < totalImages) {{
                        currentIndex = newIndex;
                        updateImage();
                    }}
                }}
                
                // Keyboard navigation exactly like 3dModel.py
                document.addEventListener('keydown', function(event) {{
                    if (event.key === 'ArrowLeft') {{
                        event.preventDefault();
                        changeImage(-1);
                    }} else if (event.key === 'ArrowRight') {{
                        event.preventDefault();
                        changeImage(1);
                    }}
                }});
                
                // Initialize the viewer (start from first image like 3dModel.py)
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
        
        # Save the HTML file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path
    
    def get_viewer_metadata(self):
        """Get metadata about the DICOM series for web display"""
        return {
            'total_images': len(self.image_paths),
            'image_paths': self.image_paths,
            'folder_path': self.dicom_folder,
            'sorted_by': 'name_and_dicom_properties'
        }

# Updated conversion function
def convert_to_2d_model(dicom_folder, output_path, lower_threshold=None, upper_threshold=None):
    """
    Convert DICOM folder to 2D model visualization with navigation.
    Enhanced version inspired by 3dModel.py functionality.
    """
    try:
        # Create the enhanced web viewer
        viewer = WebDicomViewer(dicom_folder)
        
        # Generate the main viewer image (starting from first image like 3dModel.py)
        main_output = viewer.create_viewer_image_web(0, output_path)  # Start from index 0
        
        # Generate additional outputs
        additional_outputs = []
        
        # Create a multi-view image showing multiple slices
        multi_output = output_path.replace('.png', '_multi.png')
        try:
            import matplotlib.pyplot as plt
            import numpy as np
            
            fig, axes = plt.subplots(2, 3, figsize=(15, 10))
            fig.patch.set_facecolor('black')
            fig.suptitle('AORTEC DICOM Viewer - Multiple Views', color='white', fontsize=16)
            
            # Show evenly spaced slices
            indices = np.linspace(0, len(viewer.image_paths) - 1, 6, dtype=int)
            
            for i, idx in enumerate(indices):
                row = i // 3
                col = i % 3
                
                dicom_data = viewer.get_image_data(idx)
                if dicom_data:
                    img = dicom_data['image']
                    axes[row, col].imshow(img, cmap='gray')
                    axes[row, col].set_title(f"Slice {idx + 1}/{len(viewer.image_paths)}", color='white')
                    axes[row, col].axis('off')
            
            plt.tight_layout()
            plt.savefig(multi_output, dpi=150, bbox_inches='tight', 
                       facecolor='black', edgecolor='none')
            plt.close()
            
            additional_outputs.append(multi_output)
        except Exception as e:
            print(f"Error creating multi-view: {str(e)}")
        
        return main_output, additional_outputs
        
    except Exception as e:
        print(f"Error in convert_to_2d_model: {str(e)}")
        raise

def create_2d_model_from_dicom_folder(dicom_folder, output_path, lower_threshold=None, upper_threshold=None):
    """
    Alternative function name for compatibility.
    """
    return convert_to_2d_model(dicom_folder, output_path, lower_threshold, upper_threshold)[0]

# Integration function for web application
def create_dicom_web_viewer(dicom_folder, output_path):
    """
    Create a web-compatible DICOM viewer with navigation like 3dModel.py
    """
    try:
        # Create the enhanced viewer
        viewer = WebDicomViewer(dicom_folder)
        
        # Generate the interactive HTML viewer
        html_output = output_path.replace('.stl', '.html').replace('.png', '.html')
        viewer.generate_interactive_html_viewer(html_output)
        
        # Also generate a preview image (first slice like 3dModel.py)
        preview_output = output_path.replace('.stl', '_preview.png').replace('.html', '_preview.png')
        viewer.create_viewer_image_web(0, preview_output)  # Start from first image
        
        return {
            'html_viewer': html_output,
            'preview_image': preview_output,
            'metadata': viewer.get_viewer_metadata()
        }
        
    except Exception as e:
        print(f"Error creating DICOM web viewer: {str(e)}")
        raise