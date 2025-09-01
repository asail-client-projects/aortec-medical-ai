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
                    <h3>Choose whether to upload one image or a folder</h3>
                        <div class="upload-options">
                            <label>
                                <input type="radio" name="upload_type" value="files" checked> Select One File
                            </label>
                            <label>
                                <input type="radio" name="upload_type" value="folder"> Select Folder
                            </label>
                        </div>
                    
                    <div id="upload-section" class="method-section">
                        <h4>Upload Your Files</h4>
                        <form id="upload-form" data-service="image_conversion" enctype="multipart/form-data">
                            <label for="dicom-file">Choose DICOM Files or a Folder</label>
                            <input type="file" id="dicom-file" name="dicom_file" multiple required>
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
    slicer_3d: `
    <div class="service-form-container">
        <h2>Professional 3D DICOM Visualization with 3D Slicer</h2>
        <p>Learn how to create professional-grade 3D models from your DICOM files using 3D Slicer - the industry standard for medical 3D visualization trusted by hospitals worldwide.</p>
        
        <div class="slicer-hero">
            <div class="hero-content">
                <div class="hero-text">
                    <h3>Why Choose 3D Slicer?</h3>
                    <ul class="benefits-list">
                        <li>✅ <strong>Industry Standard</strong> - Used by hospitals and research institutions globally</li>
                        <li>✅ <strong>Completely Free</strong> - Open-source with no licensing costs</li>
                        <li>✅ <strong>Professional Features</strong> - Volume rendering, segmentation, measurements</li>
                        <li>✅ <strong>3D Printing Ready</strong> - Export STL files for 3D printing</li>
                        <li>✅ <strong>Cross Platform</strong> - Available for Windows, Mac, and Linux</li>
                    </ul>
                </div>
                <div class="hero-image">
                    <img src="/static/images/slicer-3d-card.png" alt="3D Slicer Preview" class="preview-img">                </div>
                </div>
        </div>

        <div class="workflow-section">
            <h3> Complete Workflow</h3>
            <div class="workflow-steps">
                <div class="workflow-step">
                    <div class="step-icon">1</div>
                    <div class="step-content">
                        <h4>Download 3D Slicer</h4>
                        <p>First, Get the free professional software</p>
                    </div>
                </div>
                <div class="workflow-arrow">→</div>
                <div class="workflow-step">
                    <div class="step-icon">2</div>
                    <div class="step-content">
                        <h4>Open 3D Slicer</h4>
                        <p>View the 3D Slicer interface</p>
                    </div>
                </div>
                <div class="workflow-arrow">→</div>
                <div class="workflow-step">
                    <div class="step-icon">3</div>
                    <div class="step-content">
                        <h4>Create 3D Models</h4>
                        <p>Follow our step-by-step guide</p>
                    </div>
                </div>
            </div>
        </div>

        <div class="download-section">
            <h3>Download 3D Slicer</h3>
            <p>Choose your operating system to download the latest stable version:</p>
            <div class="download-buttons">
                <a href="https://download.slicer.org/" class="download-btn windows" target="_blank">
                    <i class="fab fa-windows"></i>
                    <div class="btn-content">
                        <span class="os-name">Windows</span>
                        <span class="version">Version 5.8.1</span>
                    </div>
                </a>
                <a href="https://download.slicer.org/" class="download-btn mac" target="_blank">
                    <i class="fab fa-apple"></i>
                    <div class="btn-content">
                        <span class="os-name">macOS</span>
                        <span class="version">Version 5.8.1</span>
                    </div>
                </a>
                <a href="https://download.slicer.org/" class="download-btn linux" target="_blank">
                    <i class="fab fa-linux"></i>
                    <div class="btn-content">
                        <span class="os-name">Linux</span>
                        <span class="version">Version 5.8.1</span>
                    </div>
                </a>
            </div>
        </div>

        <div class="tutorial-section">
            <h3>Learning Resources</h3>
            <div class="tutorial-grid">
                <div class="tutorial-card video-tutorial">
                    <div class="tutorial-icon">🎥</div>
                    <h4>Video Tutorial</h4>
                    <p>Watch a step-by-step video guide on creating 3D models from DICOM files</p>
                    <a href="#" class="tutorial-btn" onclick="showVideoTutorial()">Watch Tutorial</a>
                </div>
                <div class="tutorial-card text-guide">
                    <div class="tutorial-icon">📖</div>
                    <h4>Official Documentation</h4>
                    <p>Comprehensive training materials from the 3D Slicer team</p>
                    <a href="https://training.slicer.org/" class="tutorial-btn" target="_blank">Read Documentation</a>
                </div>
                <div class="tutorial-card quick-start">
                    <div class="tutorial-icon">⚡</div>
                    <h4>Quick Start Guide</h4>
                    <p>Essential steps to get started with 3D DICOM visualization</p>
                    <a href="#" class="tutorial-btn" onclick="showQuickStart()">Get Started</a>
                </div>
            </div>
        </div>

        <div class="video-container" id="video-container" style="display: none;">
            <h4>3D DICOM Visualization Tutorial</h4>
            <div class="video-wrapper">
                <iframe src="https://www.youtube.com/embed/QQ5_1fvFg_w" 
                        title="3D Slicer DICOM Tutorial" 
                        allowfullscreen>
                </iframe>
            </div>
            <p class="video-description">This tutorial shows you how to load DICOM files and create 3D visualizations in 3D Slicer.</p>
        </div>

        <div class="quick-start-guide" id="quick-start" style="display: none;">
            <h4>⚡ Quick Start Guide</h4>
            <div class="steps-container">
                <div class="guide-step">
                    <div class="step-number">1</div>
                    <div class="step-content">
                        <h5>Download and Install 3D Slicer</h5>
                        <p>Use the download buttons above to get 3D Slicer for your operating system. Installation is straightforward - just run the installer.</p>
                    </div>
                </div>
                <div class="guide-step">
                    <div class="step-number">2</div>
                    <div class="step-content">
                        <h5>Launch 3D Slicer</h5>
                        <p>Open 3D Slicer. You'll see the welcome screen with options to load data.</p>
                    </div>
                </div>
                <div class="guide-step">
                    <div class="step-number">3</div>
                    <div class="step-content">
                        <h5>Load Your DICOM Files</h5>
                        <p>Click "Add DICOM Data" and select your DICOM folder. 3D Slicer will automatically organize your series.</p>
                    </div>
                </div>
                <div class="guide-step">
                    <div class="step-number">4</div>
                    <div class="step-content">
                        <h5>Create 3D Visualization</h5>
                        <p>Use Volume Rendering or Segmentation modules to create interactive 3D models of your medical data.</p>
                    </div>
                </div>
                <div class="guide-step">
                    <div class="step-number">5</div>
                    <div class="step-content">
                        <h5>Export Your Models</h5>
                        <p>Export as STL files for 3D printing or save as scenes for sharing with colleagues.</p>
                    </div>
                </div>
            </div>
        </div>

        <div class="features-showcase">
            <h3>What You Can Create</h3>
            <div class="features-grid">
                <div class="feature-card">
                    <div class="feature-icon">🫀</div>
                    <h4>Volume Rendering</h4>
                    <p>Create transparent 3D visualizations showing internal structures</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🦴</div>
                    <h4>Segmentation</h4>
                    <p>Isolate specific organs or tissues for detailed analysis</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">📏</div>
                    <h4>Measurements</h4>
                    <p>Precise 3D measurements and annotations</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🖨️</div>
                    <h4>3D Printing</h4>
                    <p>Export STL files ready for 3D printing</p>
                </div>
            </div>
        </div>

        <div class="support-section">
            <h3>Need Help?</h3>
            <div class="support-options">
                <div class="support-option">
                    <h4>📧 Community Forum</h4>
                    <p>Join thousands of users in the active 3D Slicer community</p>
                    <a href="https://discourse.slicer.org/" target="_blank" class="support-link">Visit Forum</a>
                </div>
                <div class="support-option">
                    <h4>📚 Documentation</h4>
                    <p>Comprehensive guides and API documentation</p>
                    <a href="https://slicer.readthedocs.io/" target="_blank" class="support-link">Read Docs</a>
                </div>
            </div>
        </div>
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


// Function to show video tutorial
function showVideoTutorial() {
    const videoContainer = document.getElementById('video-container');
    const quickStart = document.getElementById('quick-start');
    
    if (videoContainer.style.display === 'none' || !videoContainer.style.display) {
        videoContainer.style.display = 'block';
        quickStart.style.display = 'none';
        
        // Smooth scroll to video
        setTimeout(() => {
            videoContainer.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'center' 
            });
        }, 100);
        
        // Track video view
        trackSlicerAction('video_tutorial_viewed');
    } else {
        videoContainer.style.display = 'none';
    }
}

// Function to show quick start guide
function showQuickStart() {
    const quickStart = document.getElementById('quick-start');
    const videoContainer = document.getElementById('video-container');
    
    if (quickStart.style.display === 'none' || !quickStart.style.display) {
        quickStart.style.display = 'block';
        videoContainer.style.display = 'none';
        
        // Smooth scroll to guide
        setTimeout(() => {
            quickStart.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'center' 
            });
        }, 100);
        
        // Track guide view
        trackSlicerAction('quick_start_viewed');
    } else {
        quickStart.style.display = 'none';
    }
}

// Function to track 3D Slicer related actions for analytics
function trackSlicerAction(action) {
    // Simple analytics tracking
    console.log(`3D Slicer Action: ${action}`);
    
    // You can integrate with Google Analytics or other tracking services here
    if (typeof gtag !== 'undefined') {
        gtag('event', action, {
            'event_category': '3d_slicer',
            'event_label': 'slicer_integration'
        });
    }
}

// Function to detect user's operating system and highlight appropriate download
function detectAndHighlightOS() {

}

// Enhanced file handling for 3D Slicer preparation
function prepareDicomForSlicer(files) {
    // Check if files are suitable for 3D Slicer
    const dicomFiles = Array.from(files).filter(file => {
        const name = file.name.toLowerCase();
        return name.endsWith('.dcm') || 
               name.includes('dicom') || 
               !name.includes('.') || // Files without extension (common for DICOM)
               name.endsWith('.ima');
    });
    
    if (dicomFiles.length === 0) {
        showSlicerTip('No DICOM files detected. 3D Slicer works best with DICOM format files.');
        return false;
    }
    
    if (dicomFiles.length < 10) {
        showSlicerTip(`Only ${dicomFiles.length} DICOM files found. For best 3D reconstruction, ensure you have a complete series (typically 50+ slices).`);
    }
    
    return true;
}

// Function to show contextual tips about 3D Slicer
function showSlicerTip(message, type = 'info') {
    const tipContainer = document.createElement('div');
    tipContainer.className = `slicer-tip ${type}`;
    tipContainer.style.cssText = `
        background: ${type === 'info' ? '#e3f2fd' : '#fff3e0'};
        border-left: 4px solid ${type === 'info' ? '#2196f3' : '#ff9800'};
        padding: 15px;
        margin: 15px 0;
        border-radius: 4px;
        font-size: 0.95em;
        line-height: 1.4;
        animation: slideIn 0.3s ease;
    `;
    tipContainer.innerHTML = `
        <div style="display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 1.2em;">${type === 'info' ? 'ℹ️' : '💡'}</span>
            <span>${message}</span>
        </div>
    `;
    
    // Insert after the upload form
    const uploadForm = document.getElementById('upload-form');
    if (uploadForm) {
        uploadForm.parentNode.insertBefore(tipContainer, uploadForm.nextSibling);
        
        // Auto-remove after 10 seconds
        setTimeout(() => {
            if (tipContainer.parentNode) {
                tipContainer.style.animation = 'slideOut 0.3s ease';
                setTimeout(() => tipContainer.remove(), 300);
            }
        }, 10000);
    }
}

// Function to create downloadable 3D Slicer preparation guide
function generateSlicerGuide() {
    const guideContent = `
# 3D Slicer DICOM Processing Guide

## Prerequisites
- Download 3D Slicer from: https://download.slicer.org/
- Have your DICOM files ready (preferably a complete series)

## Step-by-Step Instructions

### 1. Install and Launch 3D Slicer
- Run the installer for your operating system
- Launch 3D Slicer - you'll see the welcome screen

### 2. Load DICOM Data
- Click "Add DICOM Data" on the welcome screen
- Navigate to your DICOM folder
- Select all DICOM files and click "Import"
- 3D Slicer will automatically organize your data by series

### 3. Load Data into Scene
- In the DICOM browser, select your series
- Click "Load" to bring the data into the main viewer
- You'll see your data in the slice viewers (Red, Yellow, Green)

### 4. Create 3D Visualization
- Switch to the "Volume Rendering" module
- Click the eye icon next to your volume to enable rendering
- Adjust the "Shift" slider to see your 3D model
- Use presets like "CT-Chest" or "CT-Bone" for common visualizations

### 5. Segmentation (Optional)
- Switch to "Segment Editor" module
- Add a new segment for the structure you want to isolate
- Use tools like "Threshold" to automatically segment by intensity
- Use "Paint" and "Erase" tools for manual refinements

### 6. Export Your Work
- For 3D printing: File → Export to STL
- For sharing: File → Save Scene
- For images: Use screen capture tools

## Tips for Success
- Ensure complete DICOM series for best results
- Experiment with different volume rendering presets
- Use segmentation to isolate specific anatomical structures
- Join the 3D Slicer community forum for help

## Resources
- Official Training: https://training.slicer.org/
- Community Forum: https://discourse.slicer.org/
- Documentation: https://slicer.readthedocs.io/

Generated by AORTEC - Advanced Medical Imaging Analysis Platform
`;

    // Create and download the guide
    const blob = new Blob([guideContent], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'AORTEC_3D_Slicer_Guide.md';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    trackSlicerAction('guide_downloaded');
}

/**
//Function to add download guide button
function addDownloadGuideButton() {
    const supportSection = document.querySelector('.support-section .support-options');
    if (supportSection) {
        const guideOption = document.createElement('div');
        guideOption.className = 'support-option';
        guideOption.innerHTML = `
            <h4>📄 Downloadable Guide</h4>
            <p>Download a comprehensive PDF guide for offline reference</p>
            <button onclick="generateSlicerGuide()" class="support-link">Download Guide</button>
        `;
        supportSection.appendChild(guideOption);
    }
}
 */

// Initialize 3D Slicer service enhancements
function initializeSlicerService() {
    // Detect OS and highlight appropriate download
    setTimeout(() => {
        detectAndHighlightOS();
        //addDownloadGuideButton();
    }, 1000);
    
    // Add CSS animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes slideOut {
            from { opacity: 1; transform: translateY(0); }
            to { opacity: 0; transform: translateY(-20px); }
        }
        
        .recommended-badge {
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }
    `;
    document.head.appendChild(style);
}

// Track download clicks
document.addEventListener('click', function(event) {
    if (event.target.closest('.download-btn')) {
        const osType = event.target.closest('.download-btn').className.match(/(windows|mac|linux)/);
        if (osType) {
            trackSlicerAction(`download_${osType[1]}`);
        }
    }
});

// Initialize when slicer service is selected
document.addEventListener('DOMContentLoaded', function() {
    // Check if slicer service is active and initialize
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                const slicerService = document.querySelector('[data-service="slicer_3d"]');
                if (slicerService && document.querySelector('.slicer-hero')) {
                    initializeSlicerService();
                }
            }
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
});