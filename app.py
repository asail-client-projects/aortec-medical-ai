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


@app.route('/serve/processed/<path:filename>')
def serve_processed_file(filename):
    """
    Serve a processed file (e.g., STL model, ZIP archive) for download.
    """
    # Search for the file in various locations
    possible_paths = [
        os.path.join(PROCESSED_FOLDER, filename),
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
    Simplified service handler for processing services.
    Only handles image_conversion now - 3D Slicer service is informational only.
    """
    try:
        # Only process image_conversion service
        if service_name != "image_conversion":
            return jsonify({"error": f"Service '{service_name}' is not available for file processing. Please use the information provided in the service."}), 400
        
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
        
        # Process each file for image conversion
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
        
        # Return results
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
                return jsonify({'error': result['error']}), 400
                
            # Format response with statistics and visualization
            stats = result['statistics']
            patient_visualization_url = None
            if 'patient_visualization' in result and result['patient_visualization']:
                patient_visualization_url = f"/serve/processed/rupture_risk/{os.path.basename(result['patient_visualization'])}"

            download_url = None  
            if 'results_csv' in result and result['results_csv']:
                download_url = f"/serve/processed/rupture_risk/{os.path.basename(result['results_csv'])}"

            return jsonify({
                'success': True,
                'message': result['message'],
                # ❌ REMOVED: 'output': visualization_url,  # This was the misleading chart
                'patient_visualization': patient_visualization_url,
                'download_url': download_url,
                'statistics': result.get('statistics', {}),
                'detailed_results': result.get('detailed_results', [])
            }),200
        
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


@app.route('/api/slicer_analytics', methods=['POST'])
def track_slicer_analytics():
    """
    Optional route to track 3D Slicer service usage for analytics.
    This helps you understand how users interact with the service.
    """
    try:
        data = request.get_json()
        action = data.get('action', '')
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        user_agent = request.headers.get('User-Agent', '')
        
        # Log analytics data (you can store in database, file, or send to analytics service)
        analytics_data = {
            'timestamp': timestamp,
            'action': action,
            'user_agent': user_agent,
            'ip': request.remote_addr
        }
        
        # Simple file logging (you can replace with database storage)
        log_file = os.path.join('logs', 'slicer_analytics.log')
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        with open(log_file, 'a') as f:
            f.write(f"{timestamp} - {action} - {request.remote_addr}\n")
        
        return jsonify({'status': 'success'}), 200
        
    except Exception as e:
        print(f"Analytics tracking error: {str(e)}")
        return jsonify({'status': 'error'}), 500

@app.route('/api/track_download/<os_type>')
def track_slicer_download(os_type):
    """
    Track when users click download links for different operating systems.
    """
    try:
        # Log the download
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} - Download: {os_type} - {request.remote_addr}\n"
        
        log_file = os.path.join('logs', 'slicer_downloads.log')
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        with open(log_file, 'a') as f:
            f.write(log_entry)
        
        # Redirect to the actual 3D Slicer download page
        return redirect('https://download.slicer.org/')
        
    except Exception as e:
        print(f"Download tracking error: {str(e)}")
        # Fallback: redirect to download page even if tracking fails
        return redirect('https://download.slicer.org/')

# Optional: Create a route to serve usage statistics (for admin dashboard)
@app.route('/admin/slicer_stats')
def slicer_usage_stats():
    """
    Display 3D Slicer service usage statistics (admin only).
    You might want to add authentication here.
    """
    try:
        stats = {
            'total_visits': 0,
            'video_views': 0,
            'guide_views': 0,
            'downloads_by_os': {'windows': 0, 'mac': 0, 'linux': 0}
        }
        
        # Read analytics log if it exists
        analytics_file = os.path.join('logs', 'slicer_analytics.log')
        if os.path.exists(analytics_file):
            with open(analytics_file, 'r') as f:
                lines = f.readlines()
                stats['total_visits'] = len(lines)
                
                for line in lines:
                    if 'video_tutorial_viewed' in line:
                        stats['video_views'] += 1
                    elif 'quick_start_viewed' in line:
                        stats['guide_views'] += 1
        
        # Read download log if it exists
        downloads_file = os.path.join('logs', 'slicer_downloads.log')
        if os.path.exists(downloads_file):
            with open(downloads_file, 'r') as f:
                lines = f.readlines()
                
                for line in lines:
                    if 'windows' in line.lower():
                        stats['downloads_by_os']['windows'] += 1
                    elif 'mac' in line.lower():
                        stats['downloads_by_os']['mac'] += 1
                    elif 'linux' in line.lower():
                        stats['downloads_by_os']['linux'] += 1
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

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
