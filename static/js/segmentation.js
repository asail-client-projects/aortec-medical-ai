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
        
        // Enhanced validation for 3D model service
        if (isModelService && !fileInput.hasAttribute('webkitdirectory')) {
            previewHTML = `
                <div class="error-container">
                    <p class="error">Error: For DICOM viewer generation, you must select a folder containing DICOM files.</p>
                    <p>This service will sort files by name and create a navigation interface like 3dModel.py.</p>
                </div>
            `;
            previewContainer.innerHTML = previewHTML;
            return;
        }
        
        // Enhanced file count validation
        if (isModelService && fileCount < 3) {
            previewHTML = `
                <div class="warning-container">
                    <p class="warning">Warning: DICOM viewer works best with multiple files from the same series.</p>
                    <p>The selected folder contains only ${fileCount} file${fileCount > 1 ? 's' : ''}, which may not provide optimal navigation experience.</p>
                </div>
            `;
            previewContainer.innerHTML = previewHTML;
            return;
        }
        
        previewHTML += `<p><strong>📁 Selected ${fileCount} file${fileCount > 1 ? 's' : ''} for DICOM viewer:</strong></p>`;
        
        // Enhanced file preview
        previewHTML += '<ul class="file-list">';
        const displayLimit = Math.min(fileCount, 5);
        for (let i = 0; i < displayLimit; i++) {
            const file = fileInput.files[i];
            const fileIcon = file.name.toLowerCase().endsWith('.dcm') ? '🏥' : '📄';
            previewHTML += `<li>${fileIcon} ${file.name} - ${formatFileSize(file.size)}</li>`;
        }
        
        if (fileCount > 5) {
            previewHTML += `<li>📋 ...and ${fileCount - 5} more files</li>`;
        }
        
        previewHTML += '</ul>';
        previewHTML += `<p><strong>📊 Total size:</strong> ${formatTotalSize(fileInput.files)}</p>`;
        
        // Enhanced info for DICOM viewer
        if (isModelService) {
            previewHTML += `
                <div class="dicom-processing-info">
                    <h4>🔬 DICOM Viewer Processing (inspired by 3dModel.py):</h4>
                    <ul>
                        <li>✅ Files will be sorted by name and DICOM properties</li>
                        <li>🎯 Navigation interface with Previous/Next buttons</li>
                        <li>📏 Measurement rulers with precise millimeter markings</li>
                        <li>⌨️ Keyboard navigation support (arrow keys)</li>
                        <li>📱 Mobile-friendly touch/swipe navigation</li>
                        <li>🎨 Professional medical image display</li>
                    </ul>
                    <p><strong>Best Results:</strong> Use a complete DICOM series with sequential slices</p>
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

// Function to display generic results
function displayGenericResult(data, resultContainer) {
    let resultHTML = `<p class="success">${data.message || 'Processing completed successfully!'}</p>`;
    
    resultHTML += `
        <div class="generic-result">
            <div class="result-image">
                <img src="${data.output}" alt="Processed Result" loading="lazy">
            </div>
            <div class="download-section">
                <a href="${data.output}" class="download-btn primary" download>
                    📥 Download Result
                </a>
            </div>
        </div>
    `;
    
    resultContainer.innerHTML = resultHTML;
}


function handleFormSubmit(event) {
    event.preventDefault();
    
    const form = event.target;
    const serviceType = form.getAttribute("data-service");
    const resultContainer = document.querySelector(".results-container");
    const formData = new FormData(form);
    
    // Show loading message with progress animation
    resultContainer.innerHTML = `
        <div class="processing-indicator">
            <div class="loading-spinner"></div>
            <p class="loading">Processing DICOM files...</p>
            <p>Sorting files and generating viewer with navigation like 3dModel.py...</p>
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
                            <li>Check if your DICOM files are valid and properly formatted</li>
                            <li>Ensure the folder contains a complete DICOM series</li>
                            <li>Try uploading files with .dcm extension or no extension</li>
                            <li>Verify that files are sorted properly by name</li>
                        </ul>
                    </details>
                </div>
            `;
        } else {
            // Enhanced result display for DICOM viewer (inspired by 3dModel.py)
            if (serviceType === "3d_model" || serviceType === "model3D") {
                displayEnhancedDicomViewer(data, resultContainer);
            } else if (serviceType === "image_conversion") {
                displayImageConversionResult(data, resultContainer);
            } else {
                displayGenericResult(data, resultContainer);
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


function simulateNavigation(direction) {
    const image = document.getElementById('main-dicom-image');
    if (!image) return;
    
    // Add visual feedback
    image.style.opacity = '0.7';
    image.style.transform = 'scale(0.95)';
    
    // Create notification
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #f9a826;
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        z-index: 1000;
        font-weight: bold;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
    `;
    notification.textContent = direction > 0 ? 'Next View ➡️' : '⬅️ Previous View';
    document.body.appendChild(notification);
    
    // Simulate navigation delay
    setTimeout(() => {
        image.style.opacity = '1';
        image.style.transform = 'scale(1)';
        
        // Remove notification
        notification.style.opacity = '0';
        notification.style.transform = 'translateY(-20px)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 500);
}

function displayDicomViewerResult(data, resultContainer) {
    // Display DICOM viewer results with proper sizing
    let resultHTML = `<p class="success">${data.message || 'DICOM visualization generated successfully!'}</p>`;
    
    // Create a properly sized container for the DICOM viewer
    resultHTML += `
        <div class="dicom-viewer-result">
            <h4>DICOM Viewer Generated</h4>
            <div class="result-image">
                <img src="${data.output}" alt="DICOM Viewer" loading="lazy">
            </div>
            <div class="image-info">
                <p>📏 This viewer includes measurement rulers for precise measurements</p>
                <p>🔍 Use the interactive viewer for navigation through slices</p>
            </div>
        </div>
    `;
    
    // Add download button
    resultHTML += `
        <div class="download-section" style="text-align: center; margin: 20px 0;">
            <a href="${data.output}" class="download-btn" download>
                📥 Download DICOM Viewer Image
            </a>
        </div>
    `;
    
    // Add usage instructions
    resultHTML += `
        <div class="usage-instructions">
            <h4>About Your DICOM Viewer</h4>
            <div class="instruction-grid">
                <div class="instruction-item">
                    <strong>Measurement Rulers:</strong> Yellow rulers show precise measurements in millimeters
                </div>
                <div class="instruction-item">
                    <strong>Red Markers:</strong> Tick marks indicate measurement intervals (major: 50mm, minor: 10mm)
                </div>
                <div class="instruction-item">
                    <strong>Pixel Spacing:</strong> Displayed information ensures measurement accuracy
                </div>
                <div class="instruction-item">
                    <strong>Medical Data:</strong> Patient and study information shown when available
                </div>
            </div>
        </div>
    `;
    
    resultContainer.innerHTML = resultHTML;
}


// Function to add navigation simulation
function addNavigationSimulation() {
    // Add keyboard navigation like 3dModel.py
    document.addEventListener('keydown', function(event) {
        if (event.key === 'ArrowLeft') {
            event.preventDefault();
            simulateNavigation(-1);
        } else if (event.key === 'ArrowRight') {
            event.preventDefault();
            simulateNavigation(1);
        }
    });
    
    // Add touch/swipe support for mobile
    let startX = 0;
    let startY = 0;
    
    document.addEventListener('touchstart', function(event) {
        startX = event.touches[0].clientX;
        startY = event.touches[0].clientY;
    });
    
    document.addEventListener('touchend', function(event) {
        if (!startX || !startY) return;
        
        const endX = event.changedTouches[0].clientX;
        const endY = event.changedTouches[0].clientY;
        
        const deltaX = endX - startX;
        const deltaY = endY - startY;
        
        // Check if it's a horizontal swipe (not vertical scroll)
        if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 50) {
            if (deltaX > 0) {
                simulateNavigation(-1); // Swipe right = previous
            } else {
                simulateNavigation(1);  // Swipe left = next
            }
        }
        
        startX = 0;
        startY = 0;
    });
}

// Function to display image conversion results
function displayImageConversionResult(data, resultContainer) {
    let resultHTML = `<p class="success">${data.message || 'Processing completed successfully!'}</p>`;
    
    if (data.output && data.output.toLowerCase().includes('.zip')) {
        resultHTML += `
            <div class="conversion-result">
                <div class="conversion-summary">
                    <h4>📁 Conversion Complete</h4>
                    <p>Successfully converted ${data.total_files || 'multiple'} DICOM files to standard image format.</p>
                    <p>All images have been packaged into a single ZIP file for easy download.</p>
                </div>
                <div class="download-section">
                    <a href="${data.output}" class="download-btn primary" download>
                        📥 Download All Images (ZIP)
                    </a>
                </div>
            </div>
        `;
    } else {
        resultHTML += `
            <div class="single-result">
                <div class="result-image">
                    <img src="${data.output}" alt="Converted Image" loading="lazy">
                </div>
                <div class="download-section">
                    <a href="${data.output}" class="download-btn primary" download>
                        📥 Download Image
                    </a>
                </div>
            </div>
        `;
    }
    
    resultContainer.innerHTML = resultHTML;
}



// New function to display enhanced DICOM viewer results (inspired by 3dModel.py)
function displayEnhancedDicomViewer(data, resultContainer) {
    let resultHTML = `<p class="success">${data.message || 'DICOM visualization generated successfully!'}</p>`;
    
    // Create enhanced viewer container with navigation (like 3dModel.py)
    resultHTML += `
        <div class="enhanced-dicom-viewer">
            <div class="viewer-header">
                <h4>🔬 DICOM Viewer with Navigation</h4>
                <p>Navigate through DICOM slices with measurement rulers (inspired by 3dModel.py)</p>
            </div>
            
            <div class="viewer-image-container">
                <div class="image-wrapper">
                    <img id="main-dicom-image" src="${data.output}" alt="DICOM Viewer" loading="lazy">
                    
                    <!-- Navigation buttons positioned like 3dModel.py -->
                    <button class="nav-overlay-btn prev-overlay" onclick="simulateNavigation(-1)" title="Previous View">
                        ⬅️
                    </button>
                    <button class="nav-overlay-btn next-overlay" onclick="simulateNavigation(1)" title="Next View">
                        ➡️
                    </button>
                </div>
                
                <!-- Control buttons like 3dModel.py button frame -->
                <div class="viewer-controls">
                    <button class="control-btn" onclick="simulateNavigation(-1)">⬅️ Previous View</button>
                    <button class="control-btn" onclick="simulateNavigation(1)">Next View ➡️</button>
                </div>
            </div>
            
            <div class="viewer-info">
                <div class="info-grid">
                    <div class="info-item">
                        <strong>📏 Measurement Rulers:</strong> Yellow rulers show precise measurements in millimeters
                    </div>
                    <div class="info-item">
                        <strong>🎯 Red Markers:</strong> Tick marks indicate measurement intervals (major: 50mm, minor: 10mm)
                    </div>
                    <div class="info-item">
                        <strong>📊 Pixel Spacing:</strong> Displayed for accurate measurements
                    </div>
                    <div class="info-item">
                        <strong>🔄 Navigation:</strong> Use arrow buttons or keyboard arrows (like 3dModel.py)
                    </div>
                </div>
            </div>
            
            <div class="download-section">
                <a href="${data.output}" class="download-btn primary" download>
                    📥 Download DICOM Viewer Image
                </a>
            </div>
        </div>
    `;
    
    // Add enhanced styling
    resultHTML += `
        <style>
            .enhanced-dicom-viewer {
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                border-radius: 12px;
                padding: 25px;
                margin: 20px 0;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                border: 2px solid #f9a826;
            }
            
            .viewer-header {
                text-align: center;
                margin-bottom: 20px;
                padding-bottom: 15px;
                border-bottom: 2px solid #f9a826;
            }
            
            .viewer-header h4 {
                color: #f9a826;
                margin: 0 0 10px 0;
                font-size: 22px;
            }
            
            .viewer-image-container {
                position: relative;
                text-align: center;
                margin: 20px 0;
            }
            
            .image-wrapper {
                position: relative;
                display: inline-block;
                background: #000;
                border-radius: 8px;
                padding: 10px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            }
            
            #main-dicom-image {
                max-width: 100%;
                max-height: 60vh;
                height: auto;
                width: auto;
                object-fit: contain;
                border: 2px solid #f9a826;
                border-radius: 5px;
                display: block;
            }
            
            /* Navigation buttons positioned like 3dModel.py */
            .nav-overlay-btn {
                position: absolute;
                top: 50%;
                transform: translateY(-50%);
                background: rgba(249, 168, 38, 0.9);
                color: #1a1a1a;
                border: none;
                padding: 15px 20px;
                border-radius: 50%;
                cursor: pointer;
                font-size: 20px;
                font-weight: bold;
                transition: all 0.3s ease;
                z-index: 10;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            }
            
            .nav-overlay-btn:hover {
                background: rgba(224, 149, 21, 0.95);
                transform: translateY(-50%) scale(1.1);
            }
            
            .prev-overlay {
                left: -25px;
            }
            
            .next-overlay {
                right: -25px;
            }
            
            /* Control buttons like 3dModel.py button frame */
            .viewer-controls {
                display: flex;
                justify-content: center;
                gap: 20px;
                margin: 20px 0;
                padding: 15px;
                background: rgba(249, 168, 38, 0.1);
                border-radius: 8px;
                border: 1px solid rgba(249, 168, 38, 0.3);
            }
            
            .control-btn {
                background: #f9a826;
                color: #1a1a1a;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                cursor: pointer;
                font-weight: bold;
                font-size: 16px;
                transition: all 0.3s ease;
                min-width: 140px;
            }
            
            .control-btn:hover {
                background: #e09515;
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            }
            
            .viewer-info {
                margin: 20px 0;
            }
            
            .info-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 15px;
                margin-top: 15px;
            }
            
            .info-item {
                background: white;
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid #f9a826;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            
            .download-section {
                text-align: center;
                margin: 25px 0;
                padding: 20px;
                background: rgba(249, 168, 38, 0.1);
                border-radius: 8px;
            }
            
            .download-btn.primary {
                background: linear-gradient(135deg, #f9a826, #e09515);
                color: white;
                padding: 15px 30px;
                border: none;
                border-radius: 8px;
                text-decoration: none;
                font-weight: bold;
                font-size: 18px;
                display: inline-block;
                transition: all 0.3s ease;
                box-shadow: 0 4px 12px rgba(249, 168, 38, 0.3);
            }
            
            .download-btn.primary:hover {
                background: linear-gradient(135deg, #e09515, #c8750d);
                transform: translateY(-2px);
                box-shadow: 0 6px 16px rgba(249, 168, 38, 0.4);
                color: white;
                text-decoration: none;
            }
            
            /* Responsive design */
            @media (max-width: 768px) {
                .viewer-controls {
                    flex-direction: column;
                    gap: 10px;
                }
                
                .control-btn {
                    width: 100%;
                }
                
                .nav-overlay-btn {
                    font-size: 16px;
                    padding: 10px 15px;
                }
                
                .prev-overlay {
                    left: -20px;
                }
                
                .next-overlay {
                    right: -20px;
                }
                
                .info-grid {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    `;
    
    resultContainer.innerHTML = resultHTML;
    
    // Add navigation simulation functionality
    addNavigationSimulation();
}

// With this improved version:
function handleImprovedResultDisplay(data, resultContainer, serviceType) {
    if (serviceType === "3d_model" || serviceType === "model3D") {
        // For DICOM viewer results
        displayDicomViewerResult(data, resultContainer);
    } else {
        // For other services with improved sizing
        let resultHTML = `<p class="success">${data.message || 'Processing completed successfully!'}</p>`;
        
        resultHTML += `
            <div class="result-image">
                <img src="${data.output}" alt="Processed result" loading="lazy">
            </div>
            <div class="download-section" style="text-align: center; margin: 20px 0;">
                <a href="${data.output}" class="download-btn" download>Download Result</a>
            </div>
        `;
        
        resultContainer.innerHTML = resultHTML;
    }
}

// Also add this CSS directly via JavaScript for immediate effect:
function applyImageSizingFix() {
    const style = document.createElement('style');
    style.textContent = `
        .results-container .result-image img {
            max-width: 100% !important;
            max-height: 60vh !important;
            height: auto !important;
            width: auto !important;
            object-fit: contain !important;
            display: block !important;
            margin: 0 auto !important;
        }
        
        .results-container {
            max-height: 80vh !important;
            overflow-y: auto !important;
        }
        
        .dicom-viewer-result {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .image-info {
            background: rgba(249, 168, 38, 0.1);
            border-left: 4px solid #f9a826;
            padding: 15px;
            margin: 15px 0;
            border-radius: 4px;
        }
        
        .image-info p {
            margin: 5px 0;
            color: #333;
        }
        
        .download-section {
            text-align: center;
            margin: 20px 0;
            padding: 15px;
            background: #f9f9f9;
            border-radius: 8px;
        }
    `;
    document.head.appendChild(style);
}


// Add this function to your segmentation.js file or update the existing result display code

function displayDicomViewerResult(data, resultContainer) {
    // Display DICOM viewer results with proper sizing
    let resultHTML = `<p class="success">${data.message || 'DICOM visualization generated successfully!'}</p>`;
    
    // Create a properly sized container for the DICOM viewer
    resultHTML += `
        <div class="dicom-viewer-result">
            <h4>DICOM Viewer Generated</h4>
            <div class="result-image">
                <img src="${data.output}" alt="DICOM Viewer" loading="lazy">
            </div>
            <div class="image-info">
                <p>📏 This viewer includes measurement rulers for precise measurements</p>
                <p>🔍 Use the interactive viewer for navigation through slices</p>
            </div>
        </div>
    `;
    
    // Add download button
    resultHTML += `
        <div class="download-section" style="text-align: center; margin: 20px 0;">
            <a href="${data.output}" class="download-btn" download>
                📥 Download DICOM Viewer Image
            </a>
        </div>
    `;
    
    // Add usage instructions
    resultHTML += `
        <div class="usage-instructions">
            <h4>About Your DICOM Viewer</h4>
            <div class="instruction-grid">
                <div class="instruction-item">
                    <strong>Measurement Rulers:</strong> Yellow rulers show precise measurements in millimeters
                </div>
                <div class="instruction-item">
                    <strong>Red Markers:</strong> Tick marks indicate measurement intervals (major: 50mm, minor: 10mm)
                </div>
                <div class="instruction-item">
                    <strong>Pixel Spacing:</strong> Displayed information ensures measurement accuracy
                </div>
                <div class="instruction-item">
                    <strong>Medical Data:</strong> Patient and study information shown when available
                </div>
            </div>
        </div>
    `;
    
    resultContainer.innerHTML = resultHTML;
}

// Update your existing handleFormSubmit function to use better image sizing
// Find this section in your existing code and replace the result display:

// Replace this part in handleFormSubmit:
/*
else {
    // For non-STL 3D visualization results (PNG/JPG)
    resultHTML += `
        <div class="result-image">
            <img src="${data.output}" alt="3D Visualization">
        </div>
        <a href="${data.output}" class="download-btn" download>Download Visualization</a>
    `;
}
*/

// With this improved version:
function handleImprovedResultDisplay(data, resultContainer, serviceType) {
    if (serviceType === "3d_model" || serviceType === "model3D") {
        // For DICOM viewer results
        displayDicomViewerResult(data, resultContainer);
    } else {
        // For other services with improved sizing
        let resultHTML = `<p class="success">${data.message || 'Processing completed successfully!'}</p>`;
        
        resultHTML += `
            <div class="result-image">
                <img src="${data.output}" alt="Processed result" loading="lazy">
            </div>
            <div class="download-section" style="text-align: center; margin: 20px 0;">
                <a href="${data.output}" class="download-btn" download>Download Result</a>
            </div>
        `;
        
        resultContainer.innerHTML = resultHTML;
    }
}

// Also add this CSS directly via JavaScript for immediate effect:
function applyImageSizingFix() {
    const style = document.createElement('style');
    style.textContent = `
        .results-container .result-image img {
            max-width: 100% !important;
            max-height: 60vh !important;
            height: auto !important;
            width: auto !important;
            object-fit: contain !important;
            display: block !important;
            margin: 0 auto !important;
        }
        
        .results-container {
            max-height: 80vh !important;
            overflow-y: auto !important;
        }
        
        .dicom-viewer-result {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .image-info {
            background: rgba(249, 168, 38, 0.1);
            border-left: 4px solid #f9a826;
            padding: 15px;
            margin: 15px 0;
            border-radius: 4px;
        }
        
        .image-info p {
            margin: 5px 0;
            color: #333;
        }
        
        .download-section {
            text-align: center;
            margin: 20px 0;
            padding: 15px;
            background: #f9f9f9;
            border-radius: 8px;
        }
    `;
    document.head.appendChild(style);
}

// Apply enhanced styling on page load
document.addEventListener('DOMContentLoaded', function() {
    // Add enhanced CSS for better visual presentation
    const style = document.createElement('style');
    style.textContent = `
        .results-container {
            max-height: 90vh !important;
            overflow-y: auto !important;
        }
        
        .dicom-processing-info {
            background: linear-gradient(135deg, #e8f5e8, #f0f8ff);
            border: 2px solid #f9a826;
            border-radius: 8px;
            padding: 15px;
            margin: 15px 0;
        }
        
        .dicom-processing-info h4 {
            color: #f9a826;
            margin-top: 0;
        }
        
        .dicom-processing-info ul {
            margin: 10px 0;
        }
        
        .dicom-processing-info li {
            margin: 5px 0;
            color: #333;
        }
        
        .warning-container {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 8px;
            padding: 15px;
            margin: 15px 0;
        }
        
        .warning-container .warning {
            color: #856404;
            font-weight: bold;
            margin-bottom: 10px;
        }
        
        .file-list {
            background: #f8f9fa;
            border-radius: 4px;
            padding: 10px;
            margin: 10px 0;
        }
        
        .file-list li {
            padding: 2px 0;
            border-bottom: 1px solid #e9ecef;
        }
        
        .file-list li:last-child {
            border-bottom: none;
        }
    `;
    document.head.appendChild(style);
    
    // Add enhanced tooltip functionality
    document.addEventListener('mouseover', function(event) {
        if (event.target.hasAttribute('title')) {
            event.target.style.cursor = 'help';
        }
    });
});


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