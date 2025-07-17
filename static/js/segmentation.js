document.addEventListener("DOMContentLoaded", () => {
    const cards = document.querySelectorAll(".card");
    const serviceDetails = document.getElementById("service-details");

    // Service form templates
    const services = {
        image_conversion: `
        <div class="service-form-container">
            <h2>DICOM to Image Converter</h2>
            <p>This tool converts DICOM files into standard image formats. Upload single files, multiple files, or entire folders.</p>
            
            <div class="upload-container">
                <div class="upload-section">
                    <h3>Choose Processing Method</h3>
                    <div class="processing-method">
                        <label>
                            <input type="radio" name="processing_method" value="upload" checked> Upload Files
                        </label>
                        <label>
                            <input type="radio" name="processing_method" value="local"> Use Local Directory
                        </label>
                    </div>
                    
                    <div id="upload-section" class="method-section">
                        <h4>Upload Your Files</h4>
                        <form id="upload-form" data-service="image_conversion" enctype="multipart/form-data">
                            <label for="dicom-file">Choose DICOM Files or a Folder</label>
                            <input type="file" id="dicom-file" name="dicom_file" multiple required>
                            <div class="upload-options">
                                <label>
                                    <input type="radio" name="upload_type" value="files" checked> Select Files
                                </label>
                                <label>
                                    <input type="radio" name="upload_type" value="folder"> Select Folder
                                </label>
                            </div>
                            <button type="submit" class="submit-btn">Convert</button>
                        </form>
                        <p class="file-info">Supported formats: DICOM, ZIP, or files without extension</p>
                    </div>
                    
                    <div id="local-section" class="method-section" style="display: none;">
                        <h4>Use Local Directory</h4>
                        <form id="local-form" data-service="image_conversion">
                            <label for="directory">Full path to DICOM directory:</label>
                            <input type="text" id="directory" name="directory" class="form-control" required 
                                   placeholder="e.g., D:\\path\\to\\dicom\\files">
                            <button type="submit" class="submit-btn">Process Directory</button>
                        </form>
                        <p class="file-info">Enter the full path to a directory on the server that contains DICOM files</p>
                    </div>
                </div>
                
                <div class="preview-section">
                    <h3>Preview</h3>
                    <div id="file-preview" class="preview-container">
                        <p>No files selected. Your uploaded file information will be displayed here.</p>
                    </div>
                    <div class="info-box">
                        <h4>What is the DICOM to Image Converter?</h4>
                        <p>This tool allows you to convert DICOM medical images into standard image formats that can be viewed in any image viewer.</p>
                        <ul>
                            <li>Process single files or entire directories</li>
                            <li>Convert to JPG/PNG format</li>
                            <li>Handle multiple slices from volumetric data</li>
                            <li>Maintain proper windowing and contrast</li>
                        </ul>
                    </div>
                </div>
            </div>
            
            <div class="results-section">
                <h3>Results</h3>
                <div id="results-container" class="results-container">
                    <p>Conversion results will appear here after processing.</p>
                </div>
            </div>
        </div>
    `,

        // Updated model3D service template for DICOM viewer
        model3D: `
        <div class="service-form-container">
            <h2>DICOM Viewer with Measurements</h2>
            <p>Generate a comprehensive DICOM viewer with measurement rulers from your DICOM files. This tool provides precise measurements and navigation through your medical images.</p>
            
            <div class="upload-container">
                <div class="upload-section">
                    <h3>Choose Processing Method</h3>
                    <div class="processing-method">
                        <label>
                            <input type="radio" name="processing_method" value="upload" checked> Upload Files
                        </label>
                        <label>
                            <input type="radio" name="processing_method" value="local"> Use Local Directory
                        </label>
                    </div>
                    
                    <div id="upload-section" class="method-section">
                        <h4>Upload Your DICOM Folder</h4>
                        <form id="upload-form" data-service="3d_model" enctype="multipart/form-data">
                            <label for="dicom-file">Choose a folder containing DICOM files</label>
                            <input type="file" id="dicom-file" name="dicom_file" multiple required webkitdirectory directory>
                            <div class="upload-options" style="display: none;">
                                <label>
                                    <input type="radio" name="upload_type" value="folder" checked> Select Folder
                                </label>
                            </div>
                            <div class="warning-message">
                                Note: For optimal viewing, please select a folder containing a complete DICOM series.
                            </div>
                            
                            <button type="submit" class="submit-btn">Generate DICOM Viewer</button>
                        </form>
                        <p class="file-info">Supported formats: DICOM folder with multiple files</p>
                    </div>
                    
                    <div id="local-section" class="method-section" style="display: none;">
                        <h4>Use Local Directory</h4>
                        <form id="local-form" data-service="3d_model">
                            <label for="directory">Full path to DICOM directory:</label>
                            <input type="text" id="directory" name="directory" class="form-control" required 
                                   placeholder="e.g., D:\\path\\to\\dicom\\files">
                            
                            <button type="submit" class="submit-btn">Process Directory</button>
                        </form>
                        <p class="file-info">Enter the full path to a directory on the server that contains DICOM files</p>
                    </div>
                </div>
                
                <div class="preview-section">
                    <h3>Preview</h3>
                    <div id="file-preview" class="preview-container">
                        <p>No folder selected. Your uploaded folder information will be displayed here.</p>
                    </div>
                    <div class="info-box">
                        <h4>What is the DICOM Viewer?</h4>
                        <p>The DICOM viewer creates comprehensive medical image displays with measurement rulers, allowing for:</p>
                        <ul>
                            <li>Precise measurements in millimeters using built-in rulers</li>
                            <li>Navigation through multiple DICOM slices</li>
                            <li>Professional medical image viewing interface</li>
                            <li>Interactive web-based viewer for easy access</li>
                            <li>Multi-view displays showing different slices</li>
                            <li>Pixel spacing information for accurate measurements</li>
                        </ul>
                        <p>Perfect for medical professionals, students, and researchers who need accurate measurements and clear visualization of medical images.</p>
                    </div>
                </div>
            </div>
            
            <div class="results-section">
                <h3>Results</h3>
                <div id="results-container" class="results-container">
                    <p>DICOM viewer will appear here after processing. You can navigate through slices and make measurements.</p>
                </div>
            </div>
            <p class="processing-note">Note: DICOM viewer generation may take a few minutes depending on the number of files in your series.</p>
        </div>
    `
    };

    // Add click event to each card
    cards.forEach(card => {
        card.addEventListener("click", () => {
            const selectedService = card.dataset.service;
            serviceDetails.innerHTML = services[selectedService];
            serviceDetails.style.display = "block";
            
            // Setup processing method options (for all services now)
            setupProcessingMethod();
            
            // Add event listener to the upload form
            const uploadForm = document.getElementById("upload-form");
            if (uploadForm) {
                // Setup file/folder selection options based on service type
                if (uploadForm.getAttribute("data-service") === "image_conversion") {
                    setupUploadOptions();
                } else if (uploadForm.getAttribute("data-service") === "3d_model") {
                    // For 3D model service, enforce folder selection
                    enforceFolder3DModel();
                }
                
                // Add file selection handler
                const fileInput = document.getElementById("dicom-file");
                if (fileInput) {
                    fileInput.addEventListener("change", handleFileSelect);
                }
                
                // Add form submission handler
                uploadForm.addEventListener("submit", handleFormSubmit);
            }
            
            // Add event listener to the local directory form
            const localForm = document.getElementById("local-form");
            if (localForm) {
                localForm.addEventListener("submit", handleLocalFormSubmit);
            }
            
            // Scroll to service details section
            setTimeout(() => {
                serviceDetails.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }, 100);
        });
    });
    

    function setupUploadOptions() {
        const radioButtons = document.querySelectorAll('input[name="upload_type"]');
        const fileInput = document.getElementById('dicom-file');
        
        radioButtons.forEach(radio => {
            radio.addEventListener('change', function() {
                if (this.value === 'files') {
                    fileInput.removeAttribute('webkitdirectory');
                    fileInput.removeAttribute('directory');
                    fileInput.setAttribute('multiple', '');
                } else if (this.value === 'folder') {
                    fileInput.setAttribute('webkitdirectory', '');
                    fileInput.setAttribute('directory', '');
                    fileInput.setAttribute('multiple', '');
                }
            });
        });
    };
    
    function enforceFolder3DModel() {
        // For 3D model, always set to directory mode
        const fileInput = document.getElementById('dicom-file');
        if (fileInput) {
            fileInput.setAttribute('webkitdirectory', '');
            fileInput.setAttribute('directory', '');
            fileInput.setAttribute('multiple', '');
        }
    }

    function setupProcessingMethod() {
        const radioButtons = document.querySelectorAll('input[name="processing_method"]');
        const uploadSection = document.getElementById('upload-section');
        const localSection = document.getElementById('local-section');
        
        if (!radioButtons.length) return;
        
        radioButtons.forEach(radio => {
            radio.addEventListener('change', function() {
                if (this.value === 'upload') {
                    uploadSection.style.display = 'block';
                    localSection.style.display = 'none';
                } else if (this.value === 'local') {
                    uploadSection.style.display = 'none';
                    localSection.style.display = 'block';
                }
            });
        });
    };
});

function handleFileSelect(event) {
    const fileInput = event.target;
    const previewContainer = document.getElementById("file-preview");
    const isModelService = fileInput.form && fileInput.form.getAttribute("data-service") === "3d_model";
    
    if (fileInput.files.length > 0) {
        let previewHTML = '';
        const fileCount = fileInput.files.length;
        
        // Check if it's a 3D model service and enforce folder upload
        if (isModelService && !fileInput.hasAttribute('webkitdirectory')) {
            previewHTML = `
                <div class="error-container">
                    <p class="error">Error: For 3D model generation, you must select a folder containing DICOM files.</p>
                </div>
            `;
            previewContainer.innerHTML = previewHTML;
            return;
        }
        
        // Additional validation for 3D model - minimum number of files
        if (isModelService && fileCount < 5) {
            previewHTML = `
                <div class="error-container">
                    <p class="error">Warning: 3D model generation typically requires a complete series of DICOM files (20+ images).</p>
                    <p>The selected folder contains only ${fileCount} files, which may not be sufficient for a proper 3D model.</p>
                </div>
            `;
            previewContainer.innerHTML = previewHTML;
            return;
        }
        
        previewHTML += `<p><strong>Selected ${fileCount} file${fileCount > 1 ? 's' : ''}:</strong></p>`;
        
        // Show file list (limited to first 5 for UI clarity)
        previewHTML += '<ul class="file-list">';
        
        const displayLimit = Math.min(fileCount, 5);
        for (let i = 0; i < displayLimit; i++) {
            const file = fileInput.files[i];
            previewHTML += `<li>${file.name} - ${formatFileSize(file.size)}</li>`;
        }
        
        if (fileCount > 5) {
            previewHTML += `<li>...and ${fileCount - 5} more files</li>`;
        }
        
        previewHTML += '</ul>';
        previewHTML += `<p><strong>Total size:</strong> ${formatTotalSize(fileInput.files)}</p>`;
        
        // For 3D model service, add info about DICOM series
        if (isModelService) {
            previewHTML += `
                <div class="dicom-info">
                    <p><strong>Processing Information:</strong></p>
                    <p>DICOM files will be analyzed to create a 3D model of structures based on density values.</p>
                    <p>For best results:</p>
                    <ul>
                        <li>Ensure all files are from the same DICOM series</li>
                        <li>CT scans typically work better than MRI</li>
                        <li>Files should be sequentially ordered slices</li>
                    </ul>
                </div>
            `;
        }
        
        previewContainer.innerHTML = previewHTML;
    } else {
        previewContainer.innerHTML = "<p>No files selected.</p>";
    }
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatTotalSize(files) {
    let totalBytes = 0;
    for (let i = 0; i < files.length; i++) {
        totalBytes += files[i].size;
    }
    return formatFileSize(totalBytes);
}

function handleFormSubmit(event) {
    event.preventDefault();
    
    const form = event.target;
    const serviceType = form.getAttribute("data-service");
    const resultContainer = document.querySelector(".results-container");
    const formData = new FormData(form);
    
    // For 3D model service, verify it's a folder upload
    if (serviceType === "model3D" && data.output.endsWith('.stl')) {
        resultHTML += `
            <div class="model-info">
                <h4>3D Model Generated Successfully</h4>
                <p>Your DICOM series has been converted to a 3D STL model.</p>
                
                <div class="model-actions">
                    <a href="${data.output}" class="download-btn" download>
                        <i class="fas fa-download"></i> Download STL Model
                    </a>
                    <a href="/view_model/${data.output.split('/').pop()}" class="download-btn" target="_blank">
                        <i class="fas fa-eye"></i> View 3D Model
                    </a>
                </div>
                
                <div class="model-stats">
                    <p><strong>File Format:</strong> STL (3D Printable)</p>
                    <p><strong>Compatible with:</strong> 3D viewers, CAD software, 3D printers</p>
                </div>
            </div>
        `;
    }
    
    // Show loading message with progress animation
    resultContainer.innerHTML = `
        <div class="processing-indicator">
            <div class="loading-spinner"></div>
            <p class="loading">Processing... Please wait.</p>
            <p>This may take several minutes for complex visualizations.</p>
        </div>
    `;
    
    // Send AJAX request
    fetch(`/service/${serviceType}`, {
        method: "POST",
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.error) {
            resultContainer.innerHTML = `
                <div class="error-container">
                    <p class="error">Error: ${data.error}</p>
                    <details>
                        <summary>Troubleshooting Tips</summary>
                        <ul>
                            <li>Check if your DICOM files are valid</li>
                            <li>Try different file formats</li>
                            <li>Ensure the server has proper permissions</li>
                        </ul>
                    </details>
                </div>
            `;
        } else {
            // Check if this is image conversion service and there's a ZIP file in the output
            if (serviceType === "image_conversion" && data.output && data.output.toLowerCase().includes('.zip')) {
                // Display simplified result for image conversion with ZIP
                let resultHTML = `<p class="success">${data.message || 'Processing completed successfully!'}</p>`;
                resultHTML += `
                    <div class="result-container">
                        <div class="conversion-summary">
                            <h4>Conversion Complete</h4>
                            <p>Successfully converted ${data.total_files || 'multiple'} DICOM files to standard image format.</p>
                            <p>All images have been packaged into a single ZIP file for easy download.</p>
                        </div>
                        <div class="download-section">
                            <a href="${data.output}" class="download-btn" download>Download All Images (ZIP)</a>
                        </div>
                    </div>
                `;
                resultContainer.innerHTML = resultHTML;
            } else {
                // Standard result display for other services
                let resultHTML = `<p class="success">${data.message || 'Processing completed successfully!'}</p>`;
                resultHTML += `
                    <div class="result-image">
                        <img src="${data.output}" alt="Processed result">
                    </div>
                    <a href="${data.output}" class="download-btn" download>Download Result</a>
                `;
                
                // If there are multiple files, show them all
                if (data.all_outputs && data.all_outputs.length > 1) {
                    resultHTML += `<h4>All Processed Files (${data.all_outputs.length}):</h4><div class="all-results">`;
                    
                    data.all_outputs.forEach(output => {
                        resultHTML += `
                            <div class="result-thumbnail">
                                <img src="${output}" alt="Processed result">
                                <a href="${output}" download>Download</a>
                            </div>
                        `;
                    });
                    
                    resultHTML += `</div>`;
                }
                
                resultContainer.innerHTML = resultHTML;
            }
        }
    })
    .catch(error => {
        resultContainer.innerHTML = `
            <div class="error-container">
                <p class="error">Error: ${error.message}</p>
                <p>There was a problem processing your request. Please try again or contact support if the issue persists.</p>
            </div>
        `;
    });
}

function handleLocalFormSubmit(event) {
    event.preventDefault();
    
    const form = event.target;
    const resultContainer = document.querySelector(".results-container");
    const directory = form.querySelector('#directory').value;
    
    // Determine the service type from the form's data-service attribute
    const serviceType = form.getAttribute('data-service') || '3d_model';
    
    // Show loading message
    resultContainer.innerHTML = `
        <div class="processing-indicator">
            <div class="loading-spinner"></div>
            <p class="loading">Processing local directory...</p>
            <p>Generating 3D STL model from DICOM series...</p>
        </div>
    `;
    
    // Prepare data for sending
    const formData = new FormData();
    formData.append('directory', directory);
    formData.append('service_type', serviceType);
    
    // Add any service-specific parameters
    if (serviceType === '3d_model') {
        // Add thresholds if specified
        const lowerThreshold = form.querySelector('[name="lower_threshold"]')?.value;
        const upperThreshold = form.querySelector('[name="upper_threshold"]')?.value;
        
        if (lowerThreshold) {
            formData.append('lower_threshold', lowerThreshold);
        }
        
        if (upperThreshold) {
            formData.append('upper_threshold', upperThreshold);
        }
    }
    
    console.log('Submitting data:', {
        directory,
        service_type: serviceType,
    });
    
    // Send AJAX request to local processing endpoint
    fetch(`/process_local_directory`, {
        method: "POST",
        body: formData
    })
    .then(response => {
        console.log('Response status:', response.status);
        if (!response.ok) {
            return response.text().then(text => {
                console.error('Error response:', text);
                throw new Error(`HTTP error! Status: ${response.status}`);
            });
        }
        return response.json();
    })
    .then(data => {
        console.log('Response data:', data);
        
        if (data.error) {
            resultContainer.innerHTML = `
                <div class="error-container">
                    <p class="error">Error: ${data.error}</p>
                    <details>
                        <summary>Troubleshooting Tips</summary>
                        <ul>
                            <li>Verify the directory path is correct and accessible by the server</li>
                            <li>Check if your DICOM files are valid</li>
                            <li>Make sure the directory contains a complete DICOM series</li>
                            <li>Try adjusting threshold values if model generation fails</li>
                        </ul>
                    </details>
                </div>
            `;
            return;
        }
        
        // Check if output exists
        if (!data.output) {
            resultContainer.innerHTML = `
                <div class="error-container">
                    <p class="error">Error: Invalid response from server</p>
                    <p>The server returned a success message but no processed files.</p>
                    <pre>${JSON.stringify(data, null, 2)}</pre>
                </div>
            `;
            return;
        }
        
        // Handle STL model results
        if (serviceType === "3d_model" && data.file_type === "stl") {
            handleSTLModelResult(data, resultContainer);
        }
        // Handle image conversion results with ZIP
        else if (serviceType === "image_conversion" && data.output.toLowerCase().includes('.zip')) {
            handleImageConversionResult(data, resultContainer);
        }
        // Handle other results
        else {
            handleGenericResult(data, resultContainer);
        }
    })
    .catch(error => {
        console.error('Error during fetch:', error);
        resultContainer.innerHTML = `
            <div class="error-container">
                <p class="error">Error: ${error.message}</p>
                <p>There was a problem processing your request. Please try again or contact support if the issue persists.</p>
            </div>
        `;
    });
}


function handleDicomVisualizationResult(data, resultContainer) {
    // Build result HTML for 3D Visualization
    let resultHTML = `<p class="success">${data.message || 'Processing completed successfully!'}</p>`;
    
    const mainVisualization = data.output;
    
    resultHTML += `
        <h4>3D Visualization Generated Successfully</h4>
        <div class="result-image">
            <img src="${mainVisualization}" alt="3D Visualization">
        </div>
    `;
    
    // Add download button for the main visualization
    resultHTML += `
        <div class="download-section">
            <a href="${mainVisualization}" class="download-btn" download>Download Visualization</a>
        </div>
    `;
    
    // Add info about the visualization
    resultHTML += `
        <div class="model-info">
            <h4>About Your Visualization</h4>
            <p>This visualization shows a 3D representation of your DICOM data, highlighting anatomical structures based on density values.</p>
            <p>Potential uses:</p>
            <ul>
                <li>Visualization: See anatomical structures clearly</li>
                <li>Education: Identify and study different tissues</li>
                <li>Planning: Use for preliminary analysis</li>
                <li>Documentation: Include in reports and presentations</li>
            </ul>
        </div>
    `;
    
    resultContainer.innerHTML = resultHTML;
}

// First, add this to the top of the file where other libraries are loaded
document.addEventListener("DOMContentLoaded", function() {
    // Dynamically load our file-utils.js script
    const script = document.createElement('script');
    script.src = "/static/js/file-utils.js";
    document.head.appendChild(script);
});

// Then modify the handleLocalFormSubmit function to use client-side ZIP creation
function handleLocalFormSubmit(event) {
    event.preventDefault();
    
    const form = event.target;
    const resultContainer = document.querySelector(".results-container");
    const directory = form.querySelector('#directory').value;
    
    // Determine the service type from the form's data-service attribute
    const serviceType = form.getAttribute('data-service') || '3d_model';
    
    // Show loading message
    resultContainer.innerHTML = `
        <div class="processing-indicator">
            <div class="loading-spinner"></div>
            <p class="loading">Processing local directory...</p>
            <p>This may take several minutes for large datasets.</p>
            <div id="progress-bar-container" style="width: 100%; background-color: #f3f3f3; margin-top: 15px; border-radius: 4px; overflow: hidden;">
                <div id="progress-bar" style="width: 0%; height: 24px; background-color: #f9a826; text-align: center; line-height: 24px; color: white;">0%</div>
            </div>
            <p id="progress-status">Initializing...</p>
        </div>
    `;

    // For image conversion service, use client-side ZIP creation
    if (serviceType === "image_conversion") {
        if (!window.fileProcessor) {
            console.error("File processor not loaded yet. Please try again.");
            resultContainer.innerHTML = `
                <div class="error-container">
                    <p class="error">Error: File processor not loaded. Please refresh the page and try again.</p>
                </div>
            `;
            return;
        }
        
        // Use our client-side file processor
        window.fileProcessor.processLocalDirectory(
            directory,
            // Progress callback
            (progress) => {
                const progressBar = document.getElementById('progress-bar');
                const progressStatus = document.getElementById('progress-status');
                
                if (progressBar && progressStatus) {
                    progressBar.style.width = `${Math.min(progress.progress, 100)}%`;
                    progressBar.innerText = `${Math.round(progress.progress)}%`;
                    progressStatus.innerText = progress.message;
                }
                
                if (progress.status === 'error') {
                    resultContainer.innerHTML = `
                        <div class="error-container">
                            <p class="error">${progress.message}</p>
                            <p>There was a problem processing your files. Please check if your DICOM files are valid.</p>
                        </div>
                    `;
                }
            },
            // Complete callback
            (result) => {
                console.log('ZIP file created:', result);
                
                // Display success message with download link
                let resultHTML = `<p class="success">Processing completed successfully!</p>`;
                resultHTML += `
                    <div class="result-container">
                        <div class="conversion-summary">
                            <h4>Conversion Complete</h4>
                            <p>Successfully converted ${result.size ? formatFileSize(result.size) : 'multiple'} DICOM files to standard image format.</p>
                            <p>All images have been packaged into a single ZIP file for easy download.</p>
                        </div>
                        <div class="download-section">
                            <a href="${result.url}" class="download-btn" download="${result.filename}">Download All Images (ZIP)</a>
                            <p>File size: ${formatFileSize(result.size)}</p>
                        </div>
                    </div>
                `;
                resultContainer.innerHTML = resultHTML;
                
                // Log the direct download link for debugging
                console.log('ZIP file download URL:', result.url);
            }
        );
    } else {
        // For other services, use the original server-side approach
        // Prepare data for sending
        const formData = new FormData();
        formData.append('directory', directory);
        formData.append('service_type', serviceType);
        
        // Add any service-specific parameters
        if (serviceType === '3d_model') {
            // Add thresholds if specified
            const lowerThreshold = form.querySelector('[name="lower_threshold"]')?.value;
            const upperThreshold = form.querySelector('[name="upper_threshold"]')?.value;
            
            if (lowerThreshold) {
                formData.append('lower_threshold', lowerThreshold);
            }
            
            if (upperThreshold) {
                formData.append('upper_threshold', upperThreshold);
            }
        }
        
        console.log('Submitting data:', {
            directory,
            service_type: serviceType,
        });
        
        // Send AJAX request to local processing endpoint
        fetch(`/process_local_directory`, {
            method: "POST",
            body: formData
        })
        .then(response => {
            console.log('Response status:', response.status);
            if (!response.ok) {
                return response.text().then(text => {
                    console.error('Error response:', text);
                    throw new Error(`HTTP error! Status: ${response.status}`);
                });
            }
            return response.json();
        })
        .then(data => {
            console.log('Response data:', data);
            
            // Rest of your original handling code...
            if (data.error) {
                resultContainer.innerHTML = `
                    <div class="error-container">
                        <p class="error">Error: ${data.error}</p>
                        <details>
                            <summary>Troubleshooting Tips</summary>
                            <ul>
                                <li>Verify the directory path is correct and accessible by the server</li>
                                <li>Check if your DICOM files are valid</li>
                                <li>Make sure the directory contains supported file formats</li>
                            </ul>
                        </details>
                    </div>
                `;
            } else {
                // Check if output exists
                if (!data.output) {
                    resultContainer.innerHTML = `
                        <div class="error-container">
                            <p class="error">Error: Invalid response from server</p>
                            <p>The server returned a success message but no processed files.</p>
                            <pre>${JSON.stringify(data, null, 2)}</pre>
                        </div>
                    `;
                    return;
                }
                
                // Regular display for other services
                let resultHTML = `<p class="success">${data.message || 'Processing completed successfully!'}</p>`;
                
                // Main result display
                resultHTML += `
                    <div class="result-image">
                        <img src="${data.output}" alt="Processed result">
                    </div>
                    <a href="${data.output}" class="download-btn" download>Download Result</a>
                `;
                
                // If there are multiple files, show them all
                if (data.all_outputs && data.all_outputs.length > 1) {
                    resultHTML += `<h4>All Processed Files (${data.all_outputs.length}):</h4><div class="all-results">`;
                    
                    data.all_outputs.forEach(output => {
                        resultHTML += `
                            <div class="result-thumbnail">
                                <img src="${output}" alt="Processed result">
                                <a href="${output}" download>Download</a>
                            </div>
                        `;
                    });
                    
                    resultHTML += `</div>`;
                }
                
                resultContainer.innerHTML = resultHTML;
            }
        })
        .catch(error => {
            console.error('Error during fetch:', error);
            resultContainer.innerHTML = `
                <div class="error-container">
                    <p class="error">Error: ${error.message}</p>
                    <p>There was a problem processing your request. Please try again or contact support if the issue persists.</p>
                </div>
            `;
        });
    }
}

function handleSTLModelResult(data, resultContainer) {
    // Display STL model results
    let resultHTML = `<p class="success">${data.message || 'STL model generated successfully!'}</p>`;
    
    resultHTML += `
        <div class="stl-model-container">
            <div class="model-summary">
                <h4>3D STL Model Generated Successfully</h4>
                <p>Your DICOM series has been converted to a downloadable 3D STL model.</p>
                
                <div class="model-info">
                    <div class="info-item">
                        <strong>File Format:</strong> STL (Standard Tessellation Language)
                    </div>
                    <div class="info-item">
                        <strong>Compatible with:</strong> 3D viewers, CAD software, 3D printers
                    </div>
                    <div class="info-item">
                        <strong>Use cases:</strong> Medical visualization, 3D printing, research
                    </div>
                </div>
            </div>
            
            <div class="model-actions">
                <a href="${data.output}" class="download-btn primary" download>
                    <i class="fas fa-download"></i> Download STL Model
                </a>
    `;
    
    // Add viewer button if viewer URL is available
    if (data.viewer_url) {
        resultHTML += `
                <a href="${data.viewer_url}" class="download-btn secondary" target="_blank">
                    <i class="fas fa-eye"></i> View 3D Model
                </a>
        `;
    }
    
    resultHTML += `
            </div>
        </div>
    `;
    
    // Add preview image if available
    const previewUrl = data.output.replace('.stl', '_preview.png');
    resultHTML += `
        <div class="model-preview">
            <h4>Model Preview</h4>
            <img src="${previewUrl}" alt="3D Model Preview" 
                 style="max-width: 100%; border: 1px solid #ddd; border-radius: 5px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);"
                 onerror="this.style.display='none';">
        </div>
    `;
    
    // Add usage instructions
    resultHTML += `
        <div class="usage-instructions">
            <h4>How to Use Your STL Model</h4>
            <div class="instruction-grid">
                <div class="instruction-item">
                    <strong>3D Viewing:</strong> Use the "View 3D Model" button above or import into any STL viewer
                </div>
                <div class="instruction-item">
                    <strong>3D Printing:</strong> Import the STL file into your 3D printer software (Cura, PrusaSlicer, etc.)
                </div>
                <div class="instruction-item">
                    <strong>CAD Software:</strong> Open in Blender, MeshLab, or other 3D modeling applications
                </div>
                <div class="instruction-item">
                    <strong>Medical Analysis:</strong> Use in medical visualization software for further analysis
                </div>
            </div>
        </div>
    `;
    
    resultContainer.innerHTML = resultHTML;
}

function handleImageConversionResult(data, resultContainer) {
    // Display simplified result for image conversion with ZIP
    let resultHTML = `<p class="success">${data.message || 'Processing completed successfully!'}</p>`;
    resultHTML += `
        <div class="result-container">
            <div class="conversion-summary">
                <h4>Conversion Complete</h4>
                <p>Successfully converted ${data.total_files || 'multiple'} DICOM files to standard image format.</p>
                <p>All images have been packaged into a single ZIP file for easy download.</p>
            </div>
            <div class="download-section">
                <a href="${data.output}" class="download-btn" download>Download All Images (ZIP)</a>
            </div>
        </div>
    `;
    resultContainer.innerHTML = resultHTML;
}

function handleGenericResult(data, resultContainer) {
    // Regular display for other services
    let resultHTML = `<p class="success">${data.message || 'Processing completed successfully!'}</p>`;
    
    // Main result display
    resultHTML += `
        <div class="result-image">
            <img src="${data.output}" alt="Processed result">
        </div>
        <a href="${data.output}" class="download-btn" download>Download Result</a>
    `;
    
    // If there are multiple files, show them all
    if (data.all_outputs && data.all_outputs.length > 1) {
        resultHTML += `<h4>All Processed Files (${data.all_outputs.length}):</h4><div class="all-results">`;
        
        data.all_outputs.forEach(output => {
            resultHTML += `
                <div class="result-thumbnail">
                    <img src="${output}" alt="Processed result">
                    <a href="${output}" download>Download</a>
                </div>
            `;
        });
        
        resultHTML += `</div>`;
    }
    
    resultContainer.innerHTML = resultHTML;
}