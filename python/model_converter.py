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
from skimage import measure
from PIL import Image, ImageDraw, ImageFont
import time

def convert_to_3d_model(input_path, output_path, lower_threshold=None, upper_threshold=None):
    """
    Convert DICOM series to a TRUE 3D STL model.
    
    Args:
        input_path: Path to a folder containing DICOM files
        output_path: Path to save the STL model
        lower_threshold: Lower threshold for segmentation (HU value)
        upper_threshold: Upper threshold for segmentation (HU value)
        
    Returns:
        Path to the generated STL file
    """
    print(f"[3D STL Model] Converting {input_path} to {output_path}")
    
    try:
        # Ensure output is STL file
        if not output_path.endswith('.stl'):
            output_path = output_path.replace('.png', '.stl')
        
        # Create output directory
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Validate thresholds
        lower_threshold = validate_threshold(lower_threshold, 100)
        upper_threshold = validate_threshold(upper_threshold, 300)
        
        # Prepare input folder
        temp_dir = tempfile.mkdtemp()
        try:
            input_folder = prepare_input_folder(input_path, temp_dir)
            
            # Load DICOM series as 3D volume
            volume_data, spacing, origin = load_dicom_volume(input_folder)
            
            print(f"[3D STL Model] Volume shape: {volume_data.shape}")
            print(f"[3D STL Model] Spacing: {spacing}")
            print(f"[3D STL Model] Data range: {volume_data.min()} - {volume_data.max()}")
            
            # Auto-detect thresholds if needed
            if lower_threshold is None or upper_threshold is None:
                lower_threshold, upper_threshold = auto_detect_thresholds(volume_data, lower_threshold, upper_threshold)
            
            print(f"[3D STL Model] Using thresholds - Lower: {lower_threshold}, Upper: {upper_threshold}")
            
            # Generate 3D mesh using marching cubes
            mesh = create_3d_mesh_from_volume(volume_data, spacing, lower_threshold, upper_threshold)
            
            # Export to STL
            export_stl_file(mesh, output_path)
            
            # Generate preview image
            preview_path = output_path.replace('.stl', '_preview.png')
            generate_3d_preview(mesh, preview_path)
            
            print(f"[3D STL Model] Successfully created STL: {output_path}")
            return output_path
            
        finally:
            # Cleanup
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
    
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"[3D STL Model] ERROR: {str(e)}")
        print(error_details)
        
        # Create error outputs
        create_error_outputs(str(e), output_path)
        return output_path

def validate_threshold(threshold, default_value):
    """Validate and convert threshold value."""
    if threshold is None:
        return default_value
    try:
        return float(threshold)
    except (ValueError, TypeError):
        return default_value

def prepare_input_folder(input_path, temp_dir):
    """Prepare input folder for DICOM processing."""
    if input_path.lower().endswith('.zip'):
        with zipfile.ZipFile(input_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        return temp_dir
    elif os.path.isdir(input_path):
        return input_path
    else:
        raise ValueError(f"Input must be a directory or ZIP file: {input_path}")

def load_dicom_volume(dicom_folder):
    """
    Load DICOM series as 3D volume with proper spacing.
    """
    try:
        # Method 1: Use SimpleITK (preferred)
        reader = sitk.ImageSeriesReader()
        dicom_names = reader.GetGDCMSeriesFileNames(dicom_folder)
        
        if not dicom_names:
            raise ValueError("No DICOM series found")
        
        print(f"[3D STL Model] Loading {len(dicom_names)} DICOM files")
        
        reader.SetFileNames(dicom_names)
        sitk_image = reader.Execute()
        
        # Extract volume data
        volume_data = sitk.GetArrayFromImage(sitk_image)
        spacing = sitk_image.GetSpacing()  # (x, y, z)
        origin = sitk_image.GetOrigin()
        
        # Handle RGB data - use first channel
        if len(volume_data.shape) == 4 and volume_data.shape[-1] == 3:
            print("[3D STL Model] Converting RGB to grayscale")
            volume_data = volume_data[..., 0]
        
        # Convert to float for processing
        volume_data = volume_data.astype(np.float32)
        
        return volume_data, spacing, origin
        
    except Exception as e:
        print(f"[3D STL Model] SimpleITK failed, trying manual method: {str(e)}")
        return load_dicom_volume_manual(dicom_folder)

def load_dicom_volume_manual(dicom_folder):
    """Manual DICOM loading fallback."""
    dicom_files = []
    
    # Find DICOM files
    for root, _, files in os.walk(dicom_folder):
        for file in files:
            file_path = os.path.join(root, file)
            if file.lower().endswith('.dcm') or '.' not in file:
                try:
                    pydicom.dcmread(file_path, stop_before_pixels=True)
                    dicom_files.append(file_path)
                except:
                    continue
    
    if not dicom_files:
        raise ValueError("No valid DICOM files found")
    
    # Sort files by slice position
    sorted_files = sort_dicom_files(dicom_files)
    
    # Read metadata from first file
    first_dcm = pydicom.dcmread(sorted_files[0])
    pixel_spacing = getattr(first_dcm, 'PixelSpacing', [1.0, 1.0])
    slice_thickness = getattr(first_dcm, 'SliceThickness', 1.0)
    spacing = (float(pixel_spacing[0]), float(pixel_spacing[1]), float(slice_thickness))
    origin = (0.0, 0.0, 0.0)
    
    # Load all slices
    slices = []
    for file_path in sorted_files:
        try:
            dcm = pydicom.dcmread(file_path)
            pixel_data = dcm.pixel_array.astype(np.float32)
            
            # Handle RGB
            if len(pixel_data.shape) == 3 and pixel_data.shape[2] == 3:
                pixel_data = pixel_data[..., 0]
            
            slices.append(pixel_data)
        except Exception as e:
            print(f"[3D STL Model] Error reading {file_path}: {str(e)}")
    
    if not slices:
        raise ValueError("No valid slices loaded")
    
    # Stack slices into volume
    volume_data = np.stack(slices)
    print(f"[3D STL Model] Manual loading - Volume shape: {volume_data.shape}")
    
    return volume_data, spacing, origin

def sort_dicom_files(dicom_files):
    """Sort DICOM files by slice position."""
    file_positions = []
    
    for file_path in dicom_files:
        try:
            dcm = pydicom.dcmread(file_path, stop_before_pixels=True)
            
            # Get position for sorting
            position = 0
            if hasattr(dcm, 'InstanceNumber'):
                position = float(dcm.InstanceNumber)
            elif hasattr(dcm, 'SliceLocation'):
                position = float(dcm.SliceLocation)
            elif hasattr(dcm, 'ImagePositionPatient'):
                position = float(dcm.ImagePositionPatient[2])
            
            file_positions.append((file_path, position))
        except:
            file_positions.append((file_path, 0))
    
    # Sort by position
    sorted_files = [file for file, _ in sorted(file_positions, key=lambda x: x[1])]
    return sorted_files

def auto_detect_thresholds(volume_data, lower_threshold, upper_threshold):
    """Auto-detect segmentation thresholds."""
    # Sample for efficiency
    sample_size = min(50000, volume_data.size)
    sample_indices = np.random.choice(volume_data.size, sample_size, replace=False)
    sample_values = volume_data.flat[sample_indices]
    
    # Remove background
    non_zero = sample_values[sample_values > 0]
    
    if len(non_zero) == 0:
        return 50, 200
    
    if lower_threshold is None:
        lower_threshold = float(np.percentile(non_zero, 30))
    
    if upper_threshold is None:
        upper_threshold = float(np.percentile(non_zero, 70))
    
    # Ensure reasonable values
    lower_threshold = max(1, lower_threshold)
    upper_threshold = min(upper_threshold, volume_data.max())
    
    return lower_threshold, upper_threshold

def create_3d_mesh_from_volume(volume_data, spacing, lower_threshold, upper_threshold):
    """Create 3D mesh using marching cubes algorithm."""
    print("[3D STL Model] Creating binary mask...")
    
    # Create binary mask
    binary_mask = np.logical_and(
        volume_data >= lower_threshold,
        volume_data <= upper_threshold
    ).astype(np.uint8)
    
    positive_voxels = np.sum(binary_mask)
    print(f"[3D STL Model] Segmented {positive_voxels} voxels")
    
    if positive_voxels < 1000:
        print(f"[3D STL Model] WARNING: Very few voxels found ({positive_voxels})")
        # Try with adjusted thresholds
        lower_threshold = np.percentile(volume_data[volume_data > 0], 10)
        upper_threshold = np.percentile(volume_data[volume_data > 0], 90)
        binary_mask = np.logical_and(
            volume_data >= lower_threshold,
            volume_data <= upper_threshold
        ).astype(np.uint8)
        positive_voxels = np.sum(binary_mask)
        print(f"[3D STL Model] Adjusted thresholds: {positive_voxels} voxels")
    
    if positive_voxels < 100:
        raise ValueError("Insufficient voxels for 3D model generation")
    
    print("[3D STL Model] Running marching cubes algorithm...")
    
    try:
        # Use marching cubes to generate mesh
        vertices, faces, normals, values = measure.marching_cubes(
            binary_mask, 
            level=0.5,
            spacing=spacing
        )
        
        print(f"[3D STL Model] Generated mesh: {len(vertices)} vertices, {len(faces)} faces")
        
        # Create VTK mesh
        mesh = create_vtk_mesh(vertices, faces)
        
        # Clean and smooth
        mesh = clean_and_smooth_mesh(mesh)
        
        return mesh
        
    except Exception as e:
        print(f"[3D STL Model] Marching cubes error: {str(e)}")
        raise

def create_vtk_mesh(vertices, faces):
    """Create VTK PolyData from vertices and faces."""
    # Create points
    points = vtk.vtkPoints()
    for vertex in vertices:
        points.InsertNextPoint(vertex)
    
    # Create polygons
    polygons = vtk.vtkCellArray()
    for face in faces:
        polygon = vtk.vtkPolygon()
        polygon.GetPointIds().SetNumberOfIds(3)
        for i in range(3):
            polygon.GetPointIds().SetId(i, face[i])
        polygons.InsertNextCell(polygon)
    
    # Create mesh
    mesh = vtk.vtkPolyData()
    mesh.SetPoints(points)
    mesh.SetPolys(polygons)
    
    return mesh

def clean_and_smooth_mesh(mesh):
    """Clean and smooth the mesh."""
    print("[3D STL Model] Cleaning and smoothing mesh...")
    
    # Clean duplicate points
    cleaner = vtk.vtkCleanPolyData()
    cleaner.SetInputData(mesh)
    cleaner.Update()
    
    # Get largest component
    connectivity = vtk.vtkPolyDataConnectivityFilter()
    connectivity.SetInputConnection(cleaner.GetOutputPort())
    connectivity.SetExtractionModeToLargestRegion()
    connectivity.Update()
    
    # Smooth the mesh
    smoother = vtk.vtkSmoothPolyDataFilter()
    smoother.SetInputConnection(connectivity.GetOutputPort())
    smoother.SetNumberOfIterations(10)
    smoother.SetRelaxationFactor(0.1)
    smoother.FeatureEdgeSmoothingOff()
    smoother.BoundarySmoothingOn()
    smoother.Update()
    
    # Generate normals
    normals = vtk.vtkPolyDataNormals()
    normals.SetInputConnection(smoother.GetOutputPort())
    normals.ComputePointNormalsOn()
    normals.ComputeCellNormalsOn()
    normals.Update()
    
    return normals.GetOutput()

def export_stl_file(mesh, output_path):
    """Export mesh to STL file."""
    print(f"[3D STL Model] Exporting STL to: {output_path}")
    
    # Write STL file
    stl_writer = vtk.vtkSTLWriter()
    stl_writer.SetFileName(output_path)
    stl_writer.SetInputData(mesh)
    stl_writer.SetFileTypeToBinary()
    stl_writer.Write()
    
    # Verify file was created
    if not os.path.exists(output_path):
        raise FileNotFoundError(f"STL file was not created: {output_path}")
    
    file_size = os.path.getsize(output_path)
    print(f"[3D STL Model] STL file created successfully ({file_size} bytes)")

def generate_3d_preview(mesh, preview_path):
    """Generate preview image of the 3D model."""
    try:
        print(f"[3D STL Model] Generating preview: {preview_path}")
        
        # Create renderer
        renderer = vtk.vtkRenderer()
        render_window = vtk.vtkRenderWindow()
        render_window.SetOffScreenRendering(1)
        render_window.AddRenderer(renderer)
        render_window.SetSize(800, 600)
        
        # Create mapper and actor
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(mesh)
        
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(0.8, 0.2, 0.2)  # Red color
        actor.GetProperty().SetSpecular(0.3)
        actor.GetProperty().SetSpecularPower(20)
        
        renderer.AddActor(actor)
        renderer.SetBackground(0.0, 0.0, 0.0)  # Black background
        
        # Add lighting
        light1 = vtk.vtkLight()
        light1.SetIntensity(0.8)
        light1.SetPosition(1, 1, 1)
        renderer.AddLight(light1)
        
        light2 = vtk.vtkLight()
        light2.SetIntensity(0.5)
        light2.SetPosition(-1, -1, -1)
        renderer.AddLight(light2)
        
        # Position camera
        renderer.ResetCamera()
        camera = renderer.GetActiveCamera()
        camera.Azimuth(45)
        camera.Elevation(30)
        camera.Zoom(1.2)
        
        # Render
        render_window.Render()
        
        # Save image
        window_to_image = vtk.vtkWindowToImageFilter()
        window_to_image.SetInput(render_window)
        window_to_image.Update()
        
        writer = vtk.vtkPNGWriter()
        writer.SetFileName(preview_path)
        writer.SetInputConnection(window_to_image.GetOutputPort())
        writer.Write()
        
        print(f"[3D STL Model] Preview saved successfully")
        
    except Exception as e:
        print(f"[3D STL Model] Preview generation failed: {str(e)}")
        create_simple_preview(preview_path)

def create_simple_preview(preview_path):
    """Create simple text preview."""
    img = Image.new('RGB', (400, 300), color=(50, 50, 50))
    draw = ImageDraw.Draw(img)
    draw.text((50, 100), "3D STL Model Generated", fill=(255, 255, 255))
    draw.text((50, 130), "Download STL to view in 3D", fill=(200, 200, 200))
    img.save(preview_path)

def create_error_outputs(error_message, output_path):
    """Create error outputs."""
    # Error preview
    preview_path = output_path.replace('.stl', '_preview.png')
    error_img = Image.new('RGB', (800, 600), color=(255, 240, 240))
    draw = ImageDraw.Draw(error_img)
    draw.text((50, 50), "Error generating 3D STL model:", fill=(200, 0, 0))
    draw.text((50, 80), str(error_message)[:80], fill=(200, 0, 0))
    error_img.save(preview_path)
    
    # Placeholder STL
    with open(output_path, 'w') as f:
        f.write("# Error: Could not generate STL model")

def generate_html_viewer(stl_path):
    """Generate HTML viewer for STL model."""
    model_filename = os.path.basename(stl_path)
    model_url = f"/serve/processed/{model_filename}"
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AORTEC 3D STL Viewer</title>
        <style>
            body {{ margin: 0; overflow: hidden; background: #000; }}
            #info {{
                position: absolute; top: 10px; width: 100%; text-align: center;
                color: white; font-family: Arial, sans-serif; pointer-events: none;
            }}
        </style>
    </head>
    <body>
        <div id="info">AORTEC 3D STL Model Viewer - Use mouse to rotate, zoom, and pan</div>
        
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/examples/js/controls/OrbitControls.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/examples/js/loaders/STLLoader.js"></script>
        
        <script>
            // Scene setup
            const scene = new THREE.Scene();
            scene.background = new THREE.Color(0x222222);
            
            const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 5000);
            const renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.body.appendChild(renderer.domElement);
            
            // Lighting
            const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
            scene.add(ambientLight);
            
            const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
            directionalLight.position.set(1, 1, 1);
            scene.add(directionalLight);
            
            // Controls
            const controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            
            // Load STL
            const loader = new THREE.STLLoader();
            loader.load('{model_url}', function(geometry) {{
                // Center geometry
                geometry.computeBoundingBox();
                const center = new THREE.Vector3();
                geometry.boundingBox.getCenter(center);
                geometry.translate(-center.x, -center.y, -center.z);
                
                // Material
                const material = new THREE.MeshPhongMaterial({{
                    color: 0xff4444,
                    specular: 0x111111,
                    shininess: 100
                }});
                
                const mesh = new THREE.Mesh(geometry, material);
                scene.add(mesh);
                
                // Position camera
                const size = new THREE.Vector3();
                geometry.boundingBox.getSize(size);
                const maxDim = Math.max(size.x, size.y, size.z);
                camera.position.set(maxDim, maxDim, maxDim);
                camera.lookAt(0, 0, 0);
                controls.reset();
            }});
            
            // Animation loop
            function animate() {{
                requestAnimationFrame(animate);
                controls.update();
                renderer.render(scene, camera);
            }}
            animate();
            
            // Handle resize
            window.addEventListener('resize', function() {{
                camera.aspect = window.innerWidth / window.innerHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(window.innerWidth, window.innerHeight);
            }});
        </script>
    </body>
    </html>
    """
    return html_content