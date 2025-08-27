# Acts as the main entry point of the application. Handles Flask routing and connects with the other modules.
#-----------------------------------
import os
import pydicom
import shutil
import numpy as np
import SimpleITK as sitk
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
from python.dicom_processor import process_dicom_file, read_dicom_folder, extract_zip, process_zip_file
from python.segmentation import segment_dicom_file, apply_segmentation, process_dicom_folder_for_segmentation
from python.model_converter import process_dicom_folder_for_viewer, generate_html_viewer
from python.growth_rate import predict_growth_rate_from_excel, predict_growth_rate_from_input
from python.rupture_risk import predict_rupture_risk_from_excel, predict_rupture_risk_from_input
import glob
from flask_cors import CORS
import time
import tempfile


# Initialize Flask app
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 * 1024  # 2 GB max upload size
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable caching for development
CORS(app)  # Enable Cross-Origin Resource Sharing

# Configuration
UPLOAD_FOLDER = 'uploads/'
PROCESSED_FOLDER = 'processed/'
ALLOWED_EXTENSIONS = {'dcm', 'png', 'jpg', 'jpeg', 'zip', '', 'xlsx', 'xls', 'csv'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

# Ensure upload and processed folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if a file has an allowed extension or no extension."""
    if '.' not in filename:  # No extension
        return True
    return filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def process_dicom_folder_for_image_conversion(directory, output_dir):
    """
    Process DICOM folder for image conversion.
    """
    from python.dicom_processor import apply_segmentation
    return apply_segmentation(directory, output_dir)


@app.route('/service/dicom_viewer', methods=['POST'])
def process_dicom_viewer():
    """
    Process uploaded DICOM files and create an interactive viewer.
    This uses your 3dModel.py logic but for web browsers.
    """
    try:
        if 'dicom_file' not in request.files:
            return jsonify({'error': 'No files uploaded'})
        
        files = request.files.getlist('dicom_file')
        
        if len(files) == 0 or files[0].filename == '':
            return jsonify({'error': 'No files selected'})
        
        # Check if enough files are uploaded for a proper viewer
        if len(files) < 3:
            return jsonify({'error': 'For optimal viewing, please upload at least 3 DICOM files from the same series.'})
        
        # Create timestamp for unique folder
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        upload_dir = os.path.join(UPLOAD_FOLDER, f'viewer_{timestamp}')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save uploaded files
        for file in files:
            filename = secure_filename(file.filename)
            file_path = os.path.join(upload_dir, filename)
            file.save(file_path)
        
        # Define output path for HTML viewer
        output_filename = f'dicom_viewer_{timestamp}.html'
        output_path = os.path.join(PROCESSED_FOLDER, output_filename)
        
        # Process uploaded files to generate interactive viewer
        try:
            # Import the web-compatible DICOM viewer
            from python.dicom_web_viewer import create_dicom_web_viewer
            
            # Generate DICOM viewer (similar to your 3dModel.py but for web)
            result = create_dicom_web_viewer(upload_dir, output_path)
            
            # Prepare URLs for response
            viewer_url = f"/serve/processed/{output_filename}"
            preview_url = f"/serve/processed/{os.path.basename(result['preview_image'])}"
            
            # Prepare response
            return jsonify({
                'message': 'DICOM viewer generated successfully!',
                'output': preview_url,  # Preview image for immediate display
                'viewer_url': viewer_url,  # Interactive viewer
                'metadata': result['metadata'],
                'type': 'dicom_viewer'
            })
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            app.logger.error(f"Error processing DICOM viewer: {str(e)}\n{error_details}")
            return jsonify({'error': f"Error generating DICOM viewer: {str(e)}"})
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        app.logger.error(f"Server error in DICOM viewer route: {str(e)}\n{error_details}")
        return jsonify({'error': f"Server error: {str(e)}"})


@app.route('/process_local_directory', methods=['POST'])
def process_local_directory():
    """Process DICOM files from a local directory on the server."""
    directory = request.form.get('directory')
    service_type = request.form.get('service_type')
    
    # Log request details for debugging
    print(f"Processing local directory: {directory}")
    print(f"Service type: {service_type}")
    print(f"Form data: {request.form}")
    
    if not directory or not os.path.exists(directory):
        return jsonify({'error': f'Directory not found: {directory}'}), 404
        
    try:
        output_dir = os.path.join(app.config['PROCESSED_FOLDER'], f'local_{service_type}')
        os.makedirs(output_dir, exist_ok=True)
        
        processed_files = []
        
        if service_type == 'segmentation':
            # Process for segmentation
            processed_files = process_dicom_folder_for_segmentation(directory, output_dir)
            
        elif service_type == '3d_model':
            # Process for 3D MODEL - FIXED FUNCTION CALL
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            output_filename = f'aaa_model_{timestamp}.stl'  # STL file
            output_path = os.path.join(output_dir, output_filename)
            
            # Get threshold parameters if provided
            lower_threshold = request.form.get('lower_threshold', None)
            upper_threshold = request.form.get('upper_threshold', None)
            
            # Convert string values to float if provided
            if lower_threshold and lower_threshold.strip():
                try:
                    lower_threshold = float(lower_threshold)
                except ValueError:
                    lower_threshold = None
            else:
                lower_threshold = None
                
            if upper_threshold and upper_threshold.strip():
                try:
                    upper_threshold = float(upper_threshold)
                except ValueError:
                    upper_threshold = None
            else:
                upper_threshold = None
            
            # Log threshold values for debugging
            print(f"Using threshold values - Lower: {lower_threshold}, Upper: {upper_threshold}")
            
            # FIXED: Use the correct function from model_converter.py for STL generation
            from python.model_converter import convert_to_3d_model
            
            # Generate STL model (NOT 2D visualization!)
            try:
                stl_output = convert_to_3d_model(
                    directory,
                    output_path,
                    lower_threshold=lower_threshold,
                    upper_threshold=upper_threshold
                )
                
                # Verify the STL file was created
                if not os.path.exists(stl_output):
                    raise FileNotFoundError(f"Expected STL file was not created: {stl_output}")
                
                # Check if preview image exists
                preview_path = stl_output.replace('.stl', '_preview.png')
                
                processed_files = [stl_output]
                if os.path.exists(preview_path):
                    processed_files.append(preview_path)
                    
                print(f"Generated STL file: {stl_output}")
            except Exception as stl_error:
                # If STL generation fails, create an error message
                import traceback
                print(f"Error in STL generation: {str(stl_error)}")
                print(traceback.format_exc())
                
                # Create a simple error file
                error_path = output_path.replace('.stl', '_error.txt')
                with open(error_path, 'w') as f:
                    f.write(f"Error generating 3D STL model: {str(stl_error)}")
                
                processed_files = [error_path]
        
        # Add the image_conversion service processing
        elif service_type == "image_conversion":
            # Process image conversion
            from python.dicom_processor import process_dicom_folder
            processed_files = process_dicom_folder(directory, output_dir)
        
        if not processed_files:
            return jsonify({'error': 'No files could be processed'}), 400
        
        # Make sure files exist
        processed_files = [f for f in processed_files if os.path.exists(f)]
        if not processed_files:
            return jsonify({'error': 'Files were processed but could not be found'}), 500
            
        # Return the results - SIMPLIFIED
        output_url = f"/serve/processed/local_{service_type}/{os.path.basename(processed_files[0])}"
        
        # SIMPLIFIED response without all_outputs
        response_data = {
            "message": f"File processed successfully", 
            "output": output_url
        }
        
        # Add viewer URL for STL files
        if service_type == '3d_model' and processed_files[0].endswith('.stl'):
            stl_filename = os.path.basename(processed_files[0])
            response_data["viewer_url"] = f"/view_model/{stl_filename}"
            response_data["file_type"] = "stl"
        
        # Log the response for debugging
        print(f"Sending response: {response_data}")
        
        return jsonify(response_data), 200
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in local processing: {str(e)}\n{error_details}")
        return jsonify({"error": str(e)}), 500
    

@app.route('/view_dicom/<path:viewer_name>')
def view_dicom_viewer(viewer_name):
    """
    Serve the interactive DICOM viewer HTML file.
    This replaces the tkinter GUI with a web interface.
    """
    # Ensure viewer name is sanitized
    viewer_name = secure_filename(viewer_name)
    
    # Try to find the viewer in various locations
    possible_paths = [
        os.path.join(PROCESSED_FOLDER, viewer_name),
        os.path.join(PROCESSED_FOLDER, 'local_3d_model', viewer_name),
        os.path.join(PROCESSED_FOLDER, f"{viewer_name}.html"),
        os.path.join(PROCESSED_FOLDER, 'local_3d_model', f"{viewer_name}.html"),
    ]
    
    # Add .html extension and check
    if not viewer_name.lower().endswith('.html'):
        html_path = f"{viewer_name}.html"
        possible_paths.append(os.path.join(PROCESSED_FOLDER, html_path))
        possible_paths.append(os.path.join(PROCESSED_FOLDER, 'local_3d_model', html_path))
    
    viewer_path = None
    for path in possible_paths:
        if os.path.exists(path):
            viewer_path = path
            break
    
    # Check if file exists
    if not viewer_path:
        return f"DICOM viewer not found: {viewer_name}", 404
    
    # Read and serve the HTML content
    try:
        with open(viewer_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        return html_content
    except Exception as e:
        return f"Error loading DICOM viewer: {str(e)}", 500

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return jsonify({'message': 'File uploaded successfully', 'filename': filename}), 200

    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/process/<filename>', methods=['POST'])
def process_file(filename):
    """Process an uploaded file (placeholder for actual processing)."""
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    output_path = os.path.join(app.config['PROCESSED_FOLDER'], f'processed_{filename}')

    if not os.path.exists(input_path):
        return jsonify({'error': 'File not found'}), 404

    # Placeholder for processing logic
    with open(input_path, 'rb') as f_in, open(output_path, 'wb') as f_out:
        f_out.write(f_in.read())

    return jsonify({'message': 'File processed successfully', 'processed_filename': f'processed_{filename}'}), 200

@app.route('/serve/<folder>/<path:filename>', methods=['GET'])
def serve_file(folder, filename):
    """Serve a file from a specified folder with support for subfolders."""
    valid_folders = {'uploads': app.config['UPLOAD_FOLDER'], 'processed': app.config['PROCESSED_FOLDER']}
    if folder not in valid_folders:
        return jsonify({'error': 'Invalid folder'}), 400

    filepath = os.path.join(valid_folders[folder], filename)
    
    print(f"Attempting to serve file: {filepath}")
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=False)
    else:
        print(f"File not found: {filepath}")

    return jsonify({'error': 'File not found'}), 404


@app.route('/test_file/<path:filepath>', methods=['GET'])
def test_file(filepath):
    """Test if a file exists and its permissions."""
    # Full system path
    system_path = os.path.join(app.config['PROCESSED_FOLDER'], filepath)
    
    result = {
        "requested_path": filepath,
        "system_path": system_path,
        "exists": os.path.exists(system_path),
        "size": os.path.getsize(system_path) if os.path.exists(system_path) else None,
        "is_file": os.path.isfile(system_path) if os.path.exists(system_path) else None,
        "readable": os.access(system_path, os.R_OK) if os.path.exists(system_path) else None
    }
    
    return jsonify(result)


@app.errorhandler(404)
def page_not_found(e):
    """Custom 404 page with fallback."""
    try:
        return render_template('404.html'), 404
    except:
        # Fallback if 404.html doesn't exist
        return '''
        <html>
        <body style="background:#1a1a1a;color:white;font-family:Arial;text-align:center;padding:100px;">
            <h1 style="color:#f9a826;">404 - Page Not Found</h1>
            <p>The requested resource was not found.</p>
            <a href="/" style="color:#f9a826;">Return to Home</a>
        </body>
        </html>
        ''', 404


# Add these routes to your Flask application
@app.route('/service/3d_model', methods=['POST'])
def process_3d_model():
    """
    Process uploaded DICOM files and convert them to visualizations.
    This now creates a 2D visualization rather than a 3D STL model.
    """
    try:
        if 'dicom_file' not in request.files:
            return jsonify({'error': 'No files uploaded'})
        
        files = request.files.getlist('dicom_file')
        
        if len(files) == 0 or files[0].filename == '':
            return jsonify({'error': 'No files selected'})
        
        # Check if enough files are uploaded for a proper visualization
        if len(files) < 5:
            return jsonify({'error': 'For optimal visualization, a complete series of DICOM files is required (typically 5+ files). Please select a folder with more DICOM files.'})
        
        # Create timestamp for unique folder
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        upload_dir = os.path.join(UPLOAD_FOLDER, f'model_{timestamp}')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save uploaded files
        for file in files:
            filename = secure_filename(file.filename)
            file_path = os.path.join(upload_dir, filename)
            file.save(file_path)
        
        # Define output path
        output_filename = f'dicom_visualization_{timestamp}.png'
        output_path = os.path.join(PROCESSED_FOLDER, output_filename)
        
        # Process uploaded files to generate visualization
        try:
            # Get threshold parameters if provided
            lower_threshold = request.form.get('lower_threshold', None)
            upper_threshold = request.form.get('upper_threshold', None)
            
            # Convert string values to float if provided
            if lower_threshold and lower_threshold.strip():
                lower_threshold = float(lower_threshold)
            else:
                lower_threshold = None
                
            if upper_threshold and upper_threshold.strip():
                upper_threshold = float(upper_threshold)
            else:
                upper_threshold = None
            
            # Import the new 2D model function
            from python.dicom_visualizer import convert_to_2d_model
            
            # Generate 2D model visualization
            main_output, additional_outputs = convert_to_2d_model(
                upload_dir, 
                output_path,
                lower_threshold=lower_threshold,
                upper_threshold=upper_threshold
            )
            
            # Prepare URLs for response
            output_url = f"/serve/processed/{output_filename}"
            
            # SIMPLIFIED RESPONSE - REMOVE all_outputs
            # Prepare response with only main output
            return jsonify({
                'message': 'DICOM visualization generated successfully!',
                'output': output_url
                # REMOVED: 'all_outputs': all_outputs
            })
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            app.logger.error(f"Error processing 3D model: {str(e)}\n{error_details}")
            return jsonify({'error': f"Error generating 3D model: {str(e)}"})
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        app.logger.error(f"Server error in 3D model route: {str(e)}\n{error_details}")
        return jsonify({'error': f"Server error: {str(e)}"})
    

@app.route('/view_model/<path:model_name>')
def view_model(model_name):
    """
    Render a model viewer for the given model name.
    Now supports both HTML viewers and image displays.
    """
    # Ensure model name is sanitized
    model_name = secure_filename(model_name)
    
    # Try to find the model in various locations
    possible_paths = [
        os.path.join(PROCESSED_FOLDER, model_name),
        os.path.join(PROCESSED_FOLDER, 'local_3d_model', model_name),
        os.path.join(PROCESSED_FOLDER, f"{model_name}.html"),
        os.path.join(PROCESSED_FOLDER, 'local_3d_model', f"{model_name}.html"),
        os.path.join(PROCESSED_FOLDER, f"{model_name}.png"),
        os.path.join(PROCESSED_FOLDER, 'local_3d_model', f"{model_name}.png"),
    ]
    
    # Check for HTML files in dicom_viewer folders
    import glob
    dicom_viewer_folders = glob.glob(os.path.join(PROCESSED_FOLDER, '**/dicom_viewer_*'), recursive=True)
    for folder in dicom_viewer_folders:
        possible_paths.append(os.path.join(folder, model_name))
        possible_paths.append(os.path.join(folder, 'interactive_viewer.html'))
    
    model_path = None
    for path in possible_paths:
        if os.path.exists(path):
            model_path = path
            break
    
    # Check if file exists
    if not model_path:
        return f"Model not found: {model_name}", 404
    
    # Determine if it's an HTML file or an image
    if model_path.lower().endswith('.html'):
        # For HTML files, read and return content
        try:
            with open(model_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            return html_content
        except Exception as e:
            return f"Error reading HTML file: {str(e)}", 500
    else:
        # For images, create a simple HTML page to display the image
        image_url = f"/serve/processed/{os.path.relpath(model_path, PROCESSED_FOLDER)}"
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
                    font-family: Arial, sans-serif;
                    text-align: center;
                }}
                h1 {{
                    color: #f9a826;
                }}
                .viewer-container {{
                    margin: 20px auto;
                    background-color: #2a2a2a;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.3);
                    max-width: 90%;
                }}
                img {{
                    max-width: 100%;
                    height: auto;
                    border: 2px solid #f9a826;
                    border-radius: 5px;
                }}
                .instructions {{
                    background-color: #3a3a3a;
                    border: 1px solid #555;
                    border-radius: 4px;
                    padding: 15px;
                    margin: 15px 0;
                    text-align: left;
                }}
                .instructions h3 {{
                    color: #f9a826;
                    margin-top: 0;
                }}
            </style>
        </head>
        <body>
            <h1>AORTEC DICOM Viewer</h1>
            <div class="viewer-container">
                <img src="{image_url}" alt="DICOM Viewer">
                <div class="instructions">
                    <h3>About this visualization:</h3>
                    <p>This image shows a DICOM viewer with measurement rulers. The yellow rulers indicate measurements in millimeters, and the red tick marks show measurement intervals.</p>
                    <ul>
                        <li>Yellow rulers show precise measurements in millimeters</li>
                        <li>Red tick marks indicate measurement intervals</li>
                        <li>Pixel spacing information is displayed for accuracy</li>
                        <li>This viewer helps with medical image analysis and measurements</li>
                    </ul>
                </div>
            </div>
        </body>
        </html>
        """
        return html_content


@app.route('/serve/processed/<path:filename>')
def serve_processed_file(filename):
    """
    Serve a processed file (e.g., STL model, ZIP archive) for download.
    """
    # Search for the file in various locations
    possible_paths = [
        os.path.join(PROCESSED_FOLDER, filename),
        os.path.join(PROCESSED_FOLDER, 'local_3d_model', filename),
        os.path.join(PROCESSED_FOLDER, 'local_image_conversion', filename),
    ]
    
    file_path = None
    for path in possible_paths:
        if os.path.exists(path):
            file_path = path
            break

    # Add specific folder for rupture risk
    if not file_path and 'rupture_risk' in filename:
        risk_folder_path = os.path.join(PROCESSED_FOLDER, 'rupture_risk', os.path.basename(filename))
        if os.path.exists(risk_folder_path):
            file_path = risk_folder_path
            
    # Add specific folder for growth rate
    if not file_path and 'growth' in filename:
        growth_folder_path = os.path.join(PROCESSED_FOLDER, 'growth_rate', os.path.basename(filename))
        if os.path.exists(growth_folder_path):
            file_path = growth_folder_path
    
    # Check if file exists
    if not file_path:
        print(f"File not found in any location: {filename}")
        return "File not found", 404
    
    # Determine MIME type based on file extension
    mime_type = 'application/octet-stream'  # Default
    
    if filename.lower().endswith('.stl'):
        mime_type = 'application/vnd.ms-pki.stl'
    elif filename.lower().endswith('.zip'):
        mime_type = 'application/zip'
    elif filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg'):
        mime_type = 'image/jpeg'
    elif filename.lower().endswith('.png'):
        mime_type = 'image/png'
    
    print(f"Serving file: {file_path} with MIME type: {mime_type}")
    
    # Always use as_attachment=True for ZIP files to force download
    as_attachment = filename.lower().endswith('.zip')
    
    # For newer Flask versions, use download_name instead of attachment_filename
    try:
        response = send_file(
            file_path, 
            mimetype=mime_type, 
            as_attachment=as_attachment,
            download_name=os.path.basename(file_path) if as_attachment else None
        )
        # Add Cache-Control header to prevent caching issues
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        # For ZIP files, add Content-Disposition header to force download
        if as_attachment:
            response.headers['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
            # Set content length header explicitly
            response.headers['Content-Length'] = str(os.path.getsize(file_path))
        
        return response
    except Exception as e:
        print(f"Error serving file {file_path}: {str(e)}")
        return f"Error serving file: {str(e)}", 500
                                                      

@app.route('/test_file_access/<path:filename>', methods=['GET'])
def test_file_access(filename):
    """Test if a processed file can be accessed directly."""
    file_path = os.path.join(app.config['PROCESSED_FOLDER'], filename)
    
    if os.path.exists(file_path):
        try:
            # Open and read a small part of the file to verify access
            with open(file_path, 'rb') as f:
                file_start = f.read(1024)  # Read first 1KB
                
            return jsonify({
                'status': 'success',
                'message': 'File exists and is readable',
                'size': os.path.getsize(file_path),
                'file_type': 'ZIP' if filename.lower().endswith('.zip') else 'Other'
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'File exists but cannot be read: {str(e)}'
            })
    else:
        return jsonify({
            'status': 'error',
            'message': 'File not found'
        })
    

# Dynamic service routes
# Fix the import error in your app.py service handler

@app.route('/service/<service_name>', methods=['POST'])
def service_handler(service_name):
    """
    Unified service handler for all processing services.
    Handles both 3d_model and image_conversion services.
    """
    try:
        # File upload - handle multiple files
        if 'dicom_file' not in request.files:
            return jsonify({"error": "No files provided"}), 400
        
        files = request.files.getlist('dicom_file')
        if not files or len(files) == 0:
            return jsonify({"error": "No files provided"}), 400
        
        # Create a temporary directory for processing multiple files
        import tempfile
        temp_dir = tempfile.mkdtemp()
        
        processed_files = []
        
        # Special handling for 3D model service
        if service_name == "3d_model":
            # Check if enough files are uploaded for a proper visualization
            if len(files) < 5:
                return jsonify({'error': 'For optimal visualization, a complete series of DICOM files is required (typically 5+ files). Please select a folder with more DICOM files.'}), 400
            
            # Create timestamp for unique folder
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            upload_dir = os.path.join(UPLOAD_FOLDER, f'model_{timestamp}')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Save uploaded files
            for file in files:
                filename = secure_filename(file.filename)
                file_path = os.path.join(upload_dir, filename)
                file.save(file_path)
            
            # Define output path
            output_filename = f'dicom_visualization_{timestamp}.png'
            output_path = os.path.join(PROCESSED_FOLDER, output_filename)
            
            try:
                # Get threshold parameters if provided
                lower_threshold = request.form.get('lower_threshold', None)
                upper_threshold = request.form.get('upper_threshold', None)
                
                # Convert string values to float if provided
                if lower_threshold and lower_threshold.strip():
                    lower_threshold = float(lower_threshold)
                else:
                    lower_threshold = None
                    
                if upper_threshold and upper_threshold.strip():
                    upper_threshold = float(upper_threshold)
                else:
                    upper_threshold = None
                
                # FIXED IMPORT - Use the correct function name from dicom_visualizer.py
                # Looking at your dicom_visualizer.py, the function is called create_2d_model_from_dicom_folder
                from python.dicom_visualizer import create_2d_model_from_dicom_folder
                
                # Generate 2D model visualization using the correct function
                main_output = create_2d_model_from_dicom_folder(
                    upload_dir, 
                    output_path,
                    lower_threshold=lower_threshold,
                    upper_threshold=upper_threshold
                )
                
                # Prepare URLs for response - SIMPLIFIED
                output_url = f"/serve/processed/{output_filename}"
                
                # SIMPLIFIED response for 3D model
                return jsonify({
                    'message': 'DICOM visualization generated successfully!',
                    'output': output_url
                }), 200
                
            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                app.logger.error(f"Error processing 3D model: {str(e)}\n{error_details}")
                return jsonify({'error': f"Error generating 3D model: {str(e)}"}), 500
        
        # Handle other services (image_conversion, segmentation, etc.)
        else:
            # Process each file
            for uploaded_file in files:
                if uploaded_file.filename == '':
                    continue
                    
                filename = secure_filename(uploaded_file.filename)
                filepath = os.path.join(temp_dir, filename)
                uploaded_file.save(filepath)
                
                # Process based on the service selected
                if service_name == "image_conversion":
                    # Check if it's a ZIP file
                    if filename.lower().endswith('.zip'):
                        from python.dicom_processor import process_zip_file
                        output_files = process_zip_file(filepath, app.config['PROCESSED_FOLDER'])
                        processed_files.extend(output_files)
                    else:
                        # Process as DICOM file
                        base_filename = os.path.basename(filepath)
                        output_path = os.path.join(app.config['PROCESSED_FOLDER'], f"{base_filename}.jpg")
                        
                        try:
                            from python.dicom_processor import process_dicom_file
                            output_file = process_dicom_file(filepath, output_path)
                            processed_files.append(output_file)
                        except Exception as e:
                            print(f"Error processing {filename}: {str(e)}")
                
                elif service_name == "segmentation":
                    # Process as segmentation
                    base_filename = os.path.basename(filepath)
                    output_path = os.path.join(app.config['PROCESSED_FOLDER'], f"{base_filename}_segmented.png")
                    
                    try:
                        from python.segmentation import segment_dicom_file
                        output_file = segment_dicom_file(filepath, output_path)
                        processed_files.append(output_file)
                    except Exception as e:
                        print(f"Error processing segmentation for {filename}: {str(e)}")
            
            # Return results for non-3D services
            if not processed_files:
                return jsonify({"error": "No valid files could be processed"}), 400
                
            # Return the first processed file for display - SIMPLIFIED
            output_url = f"/serve/processed/{os.path.basename(processed_files[0])}"
            
            # SIMPLIFIED response
            return jsonify({
                "message": f"File processed successfully", 
                "output": output_url
            }), 200
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in service handler: {str(e)}\n{error_details}")
        return jsonify({"error": str(e)}), 500


@app.route('/extension_service/growth_rate', methods=['POST'])
def growth_rate_service():
    """Handle growth rate prediction service requests."""
    try:
        print("[DEBUG] Starting growth rate prediction service")
        print("[DEBUG] Form data:", request.form)
        
        # Check if there's an Excel file upload
        if 'excel_file' in request.files and request.files['excel_file'].filename != '':
            # Handle Excel file upload
            excel_file = request.files['excel_file']
            print(f"[DEBUG] Processing Excel file: {excel_file.filename}")
            
            # Get the file type (single or multiple) - default to single if not specified
            file_type = request.form.get('file_type', 'single')
            print(f"[DEBUG] File type selected: {file_type}")
            
            # Save the uploaded file
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(excel_file.filename))
            excel_file.save(file_path)
            print(f"[DEBUG] File saved to {file_path}")
            
            # Process the Excel file
            output_dir = os.path.join(app.config['PROCESSED_FOLDER'], 'growth_rate')
            os.makedirs(output_dir, exist_ok=True)
            
            # Get file size to help with debugging
            file_size = os.path.getsize(file_path)
            print(f"[DEBUG] File size: {file_size} bytes")
            
            # Try to preview the first few rows if it's a CSV
            try:
                if file_path.endswith('.csv'):
                    with open(file_path, 'r') as f:
                        first_few_lines = [next(f) for _ in range(5)]
                        print(f"[DEBUG] First few lines of CSV:\n{''.join(first_few_lines)}")
            except Exception as e:
                print(f"[DEBUG] Couldn't preview file: {str(e)}")
            
            # Process the file
            result = predict_growth_rate_from_excel(file_path, output_dir)
            
            # Check for errors
            if 'error' in result:
                print(f"[ERROR] Error processing growth rate: {result['error']}")
                return jsonify({'error': result['error']}), 400
            
            # Format response - construct proper file paths for URLs
            vis_filename = os.path.basename(result['visualization'])
            csv_filename = os.path.basename(result['results_csv'])
            
            visualization_url = f"/serve/processed/growth_rate/{vis_filename}"
            csv_url = f"/serve/processed/growth_rate/{csv_filename}"
            
            print(f"[DEBUG] Visualization URL: {visualization_url}")
            print(f"[DEBUG] CSV URL: {csv_url}")
            
            # Build response with all data from the result
            response = {
                'message': result['message'],
                'output': visualization_url,
                'download_url': csv_url,
                'metrics': result.get('metrics', {}),
                'is_single_patient': result.get('is_single_patient', False)
            }
            
            # Include patient data if present
            if 'patient_data' in result:
                response['patient_data'] = result['patient_data']
            
            # Include statistics if available
            if 'statistics' in result:
                response['statistics'] = result['statistics']
            
            print(f"[DEBUG] Response prepared: {response}")
            return jsonify(response), 200
        else:
            print("[ERROR] No file uploaded")
            return jsonify({'error': 'No file uploaded. Please select an Excel or CSV file.'}), 400
            
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[ERROR] Growth rate service error: {str(e)}\n{error_details}")
        return jsonify({"error": str(e)}), 500
    

@app.route('/train_growth_model', methods=['GET'])
def train_growth_model():
    try:
        from python.growth_rate import train_model
        train_model()
        return jsonify({"message": "Model trained successfully"}), 200
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return jsonify({"error": str(e), "details": error_details}), 500


@app.route('/extension_service/rupture_risk', methods=['POST'])
def rupture_risk_service():
    """Handle rupture risk prediction service requests."""
    try:
        print("="*50)
        print("[DEBUG] Received rupture risk prediction request")
        
        # Check if there's an Excel file upload
        if 'excel_file' in request.files and request.files['excel_file'].filename != '':
            # Handle Excel file upload
            excel_file = request.files['excel_file']
            print(f"[DEBUG] Received Excel file: {excel_file.filename}")
            
            # Save the uploaded file
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(excel_file.filename))
            excel_file.save(file_path)
            print(f"[DEBUG] Saved Excel file to: {file_path}")
            
            # Process the Excel file
            output_dir = os.path.join(app.config['PROCESSED_FOLDER'], 'rupture_risk')
            os.makedirs(output_dir, exist_ok=True)
            
            result = predict_rupture_risk_from_excel(file_path, output_dir)
            
            if 'error' in result:
                print(f"[ERROR] Error processing rupture risk: {result['error']}")
                return jsonify({'error': result['error']}), 400
                
            # Format response with statistics and visualization
            stats = result['statistics']
            visualization_url = f"/serve/processed/rupture_risk/{os.path.basename(result['visualization'])}"
            patient_visualization_url = f"/serve/processed/rupture_risk/{os.path.basename(result['patient_visualization'])}"
            csv_url = f"/serve/processed/rupture_risk/{os.path.basename(result['results_csv'])}"
            
            response = {
                'message': result['message'],
                'output': visualization_url,
                'patient_visualization': patient_visualization_url,
                'download_url': csv_url,
                'statistics': stats,
                'detailed_results': result.get('detailed_results', [])
            }
            
            return jsonify(response), 200
        
        else:
            print("[ERROR] No file uploaded")
            return jsonify({'error': 'No file uploaded. Please select an Excel or CSV file.'}), 400
            
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[ERROR] Rupture risk service error: {str(e)}\n{error_details}")
        return jsonify({"error": str(e)}), 500

# Add this new route to app.py
@app.route('/download/zip/<path:filename>')
def download_zip_file(filename):
    """
    Special route specifically for downloading ZIP files with proper headers.
    """
    # Find the ZIP file
    zip_path = os.path.join(PROCESSED_FOLDER, filename)
    if not os.path.exists(zip_path):
        # Check in subfolders
        for subfolder in ['local_image_conversion', 'temp_*']:
            for path in glob.glob(os.path.join(PROCESSED_FOLDER, subfolder, filename)):
                if os.path.exists(path):
                    zip_path = path
                    break
    
    if not os.path.exists(zip_path):
        print(f"ZIP file not found: {filename}")
        return "ZIP file not found", 404
    
    # Verify file size
    file_size = os.path.getsize(zip_path)
    if file_size == 0:
        return "ZIP file is empty", 500
    
    try:
        # Create response with explicit file streaming
        response = send_file(
            zip_path,
            mimetype='application/zip',
            as_attachment=True,
            download_name=os.path.basename(zip_path)
        )
        
        # Add additional headers for proper download
        response.headers['Content-Disposition'] = f'attachment; filename="{os.path.basename(zip_path)}"'
        response.headers['Content-Length'] = str(file_size)
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        print(f"Sending ZIP file: {zip_path}, size: {file_size} bytes, headers: {response.headers}")
        return response
    except Exception as e:
        print(f"Error sending ZIP file {zip_path}: {str(e)}")
        return f"Error sending ZIP file: {str(e)}", 500


# Home page route
@app.route('/')
def home():
    return render_template('index.html')

# About page route
@app.route('/about')
def about():
    return render_template('about.html')

# Extensions page route
@app.route('/extensions')
def extensions():
    return render_template('extensions.html')

# Tutorials page route
@app.route('/tutorials')
def tutorials():
    return render_template('tutorials.html')

# Contact page route
@app.route('/contact')
def contact():
    return render_template('contact.html')

# Segmentation page route
@app.route('/segmentation')
def segmentation():
    return render_template('segmentation.html')

#  Legal page route
@app.route('/legal')
def legal_disclaimers():
    return render_template('legal.html')

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=True)
