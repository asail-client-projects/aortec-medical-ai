document.addEventListener("DOMContentLoaded", () => {
    const extensionCards = document.querySelectorAll(".extension-card:not(.coming-soon)");
    const serviceDetails = document.getElementById("service-details");

    // Service form templates
    const services = {
        automated_measurement: `
            <div class="service-form-container">
                <h2>Automated Measurement of AAA</h2>
                <p>Upload DICOM files to accurately measure the size of the aneurysm.</p>
                
                <div class="upload-container">
                    <div class="upload-section">
                        <h3>Choose Processing Method</h3>
                        <div class="processing-method">
                            <label>
                                <input type="radio" name="processing_method" value="upload" checked> Upload Files
                            </label>
                            <label>
                                <input type="radio" name="processing_method" value="model"> Use Generated 3D Model
                            </label>
                        </div>
                        
                        <div id="upload-section" class="method-section">
                            <h4>Upload Your Files</h4>
                            <form id="upload-form" data-service="automated_measurement" enctype="multipart/form-data">
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
                                <button type="submit" class="submit-btn">Process Files</button>
                            </form>
                            <p class="file-info">Supported formats: DICOM, ZIP, or folders containing DICOM files</p>
                        </div>
                        
                        <div id="model-section" class="method-section" style="display: none;">
                            <h4>Upload 3D Model</h4>
                            <form id="model-form" data-service="automated_measurement" enctype="multipart/form-data">
                                <label for="model-file">Choose 3D Model File</label>
                                <input type="file" id="model-file" name="model_file" accept=".stl,.obj" required>
                                <button type="submit" class="submit-btn">Process Model</button>
                            </form>
                            <p class="file-info">Supported formats: STL, OBJ (previously generated from DICOM)</p>
                        </div>
                    </div>
                    
                    <div class="preview-section">
                        <h3>Preview</h3>
                        <div id="file-preview" class="preview-container">
                            <p>No files selected. Your uploaded file information will be displayed here.</p>
                        </div>
                    </div>
                </div>
                
                <div class="results-section">
                    <h3>Results</h3>
                    <div id="results-container" class="results-container">
                        <p>Measurement results will appear here after processing.</p>
                    </div>
                </div>
            </div>
        `,
// Update the growth_rate service template in extensions.js
growth_rate: `
    <div class="service-form-container">
        <h2>Predict Rate of Growth</h2>
        <p>Estimate the growth rate of the aneurysm over time using our AI prediction model.</p>
        
        <!-- File Upload Section -->
        <div id="upload-section" class="method-section">
            <div class="upload-container">
                <div class="upload-section">
                    <h3>Upload Patient Data</h3>
                    <form id="upload-form" data-service="growth_rate" enctype="multipart/form-data">
                        <label for="excel-file">Choose Excel or CSV File</label>
                        <input type="file" id="excel-file" name="excel_file" accept=".xlsx,.xls,.csv" required>
                        <input type="hidden" id="file_type" name="file_type" value="single">
                        <button type="submit" class="submit-btn">Predict Growth Rate</button>
                    </form>
                    <div class="file-info">
                        <p><strong>Required columns in your spreadsheet:</strong></p>
                        <ul>
                            <li>Current Axial Diameter (mm) - The current size of the aneurysm</li>
                            <li>ILT Volume (mL) - The Intraluminal Thrombus volume</li>
                            <li>Time Interval (months) - Time since previous measurement</li>
                        </ul>
                    </div>
                </div>
                
                <div class="preview-section">
                    <h3>Preview</h3>
                    <div id="file-preview" class="preview-container">
                        <p>No file selected. Your uploaded file information will be displayed here.</p>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Results Section -->
        <div class="results-section">
            <h3>Results</h3>
            <div id="results-container" class="results-container">
                <p>Growth rate prediction results will appear here after processing.</p>
            </div>
        </div>
    </div>
`,

rupture_risk: `
    <div class="service-form-container">
        <h2>Predict Risk of Rupture</h2>
        <p>Upload patient data to evaluate the risk of aneurysm rupture.</p>
        
        <div class="upload-container">
            <div class="upload-section">
                <h3>Upload Patient Data</h3>
                <form id="upload-form" data-service="rupture_risk" enctype="multipart/form-data">
                    <label for="excel-file">Choose Excel or CSV File</label>
                    <input type="file" id="excel-file" name="excel_file" accept=".xlsx,.xls,.csv" required>
                    <button type="submit" class="submit-btn">Predict Rupture Risk</button>
                </form>
                <div class="file-info">
                    <p><strong>Required columns in your spreadsheet:</strong></p>
                    <ul>
                        <li>Axial Diameter (mm) - The size of the aneurysm</li>
                        <li>ILT Volume (mL) - The Intraluminal Thrombus volume</li>
                        <li>Blood Pressure (mmHg) - Patient's systolic blood pressure</li>
                        <li>Smoking History - Whether the patient smokes (Yes/No)</li>
                        <li>Age - Patient's age in years</li>
                        <li>Gender - Patient's gender (M/F)</li>
                    </ul>
                    <p><strong>Optional columns that will improve prediction accuracy:</strong></p>
                    <ul>
                        <li>Peak Wall Stress (kPa) - The maximum stress on the aneurysm wall</li>
                    </ul>
                </div>
            </div>
            
            <div class="preview-section">
                <h3>Preview</h3>
                <div id="file-preview" class="preview-container">
                    <p>No file selected. Your uploaded file information will be displayed here.</p>
                </div>
            </div>
        </div>
        
        <div class="results-section">
            <h3>Results</h3>
            <div id="results-container" class="results-container">
                <p>Rupture risk assessment results will appear here after processing. Results will include:</p>
                <ul>
                    <li>Current rupture risk for each patient</li>
                    <li>Predicted risk progression over time (1 and 5 years)</li>
                    <li>Risk category classification (Low, Moderate, High, Very High)</li>
                    <li>Detailed patient-by-patient results table</li>
                </ul>
            </div>
        </div>
    </div>
` ,

        simulator: `
            <div class="service-form-container">
                <h2>AAA Simulator</h2>
                <p>Simulate potential development of an aneurysm over time using AI models.</p>
                
                <div class="upload-container">
                    <div class="upload-section">
                        <h3>Upload DICOM Files</h3>
                        <form id="upload-form" data-service="simulator" enctype="multipart/form-data">
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
                            <div class="simulation-options">
                                <h4>Simulation Parameters</h4>
                                <div class="param-group">
                                    <label for="time-period">Time Period:</label>
                                    <select id="time-period" name="time_period">
                                        <option value="1">1 Year</option>
                                        <option value="2">2 Years</option>
                                        <option value="5" selected>5 Years</option>
                                        <option value="10">10 Years</option>
                                    </select>
                                </div>
                                <div class="param-group">
                                    <label for="time-steps">Time Steps:</label>
                                    <input type="number" id="time-steps" name="time_steps" min="2" max="10" value="5">
                                </div>
                            </div>
                            <button type="submit" class="submit-btn">Run Simulation</button>
                        </form>
                        <p class="file-info">Supported formats: DICOM, ZIP, or folders containing DICOM files</p>
                    </div>
                    
                    <div class="preview-section">
                        <h3>Preview</h3>
                        <div id="file-preview" class="preview-container">
                            <p>No files selected. Your uploaded file information will be displayed here.</p>
                        </div>
                    </div>
                </div>
                
                <div class="results-section">
                    <h3>Results</h3>
                    <div id="results-container" class="results-container">
                        <p>Simulation results will appear here after processing.</p>
                    </div>
                </div>
            </div>
        `,
        other_aneurysms: `
            <div class="service-form-container">
                <h2>Use Segmentation for Other Aneurysms</h2>
                <p>Apply our segmentation model to other types of aneurysms.</p>
                
                <div class="upload-container">
                    <div class="upload-section">
                        <h3>Upload DICOM Files</h3>
                        <form id="upload-form" data-service="other_aneurysms" enctype="multipart/form-data">
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
                            <div class="aneurysm-type">
                                <h4>Aneurysm Type</h4>
                                <select id="aneurysm-type" name="aneurysm_type">
                                    <option value="cerebral">Cerebral Aneurysm</option>
                                    <option value="thoracic">Thoracic Aortic Aneurysm</option>
                                    <option value="popliteal">Popliteal Artery Aneurysm</option>
                                    <option value="femoral">Femoral Artery Aneurysm</option>
                                    <option value="iliac">Iliac Artery Aneurysm</option>
                                    <option value="other">Other (Generic Model)</option>
                                </select>
                            </div>
                            <button type="submit" class="submit-btn">Process Files</button>
                        </form>
                        <p class="file-info">Supported formats: DICOM, ZIP, or folders containing DICOM files</p>
                    </div>
                    
                    <div class="preview-section">
                        <h3>Preview</h3>
                        <div id="file-preview" class="preview-container">
                            <p>No files selected. Your uploaded file information will be displayed here.</p>
                        </div>
                    </div>
                </div>
                
                <div class="results-section">
                    <h3>Results</h3>
                    <div id="results-container" class="results-container">
                        <p>Segmentation results will appear here after processing.</p>
                    </div>
                </div>
            </div>
        `
    };


    // Add click event to each extension card
    extensionCards.forEach(card => {
        card.addEventListener("click", () => {
            const selectedService = card.dataset.service;
            
            if (selectedService && services[selectedService]) {
                serviceDetails.innerHTML = services[selectedService];
                serviceDetails.style.display = "block";
                
                // Setup processing method options if present
                setupProcessingMethod();
                
                // Setup file upload options
                setupUploadOptions();
                
                // Add file selection handler
                setupFileHandlers();
                
                // Add form submission handler
                setupFormSubmissionHandlers();
                
                // Scroll to service details section
                setTimeout(() => {
                    serviceDetails.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }, 100);
            }
        });
    });

    function setupProcessingMethod() {
        const radioButtons = document.querySelectorAll('input[name="processing_method"]');
        if (!radioButtons.length) return;
        
        const uploadSection = document.getElementById('upload-section');
        const modelSection = document.getElementById('model-section');
        
        if (uploadSection && modelSection) {
            radioButtons.forEach(radio => {
                radio.addEventListener('change', function() {
                    if (this.value === 'upload') {
                        uploadSection.style.display = 'block';
                        modelSection.style.display = 'none';
                    } else if (this.value === 'model') {
                        uploadSection.style.display = 'none';
                        modelSection.style.display = 'block';
                    }
                });
            });
        }
    }

    function setupUploadOptions() {
        const radioButtons = document.querySelectorAll('input[name="upload_type"]');
        if (!radioButtons.length) return;
        
        const fileInputs = document.querySelectorAll('input[type="file"][multiple]');
        
        fileInputs.forEach(fileInput => {
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
        });
    }

    function setupFileHandlers() {
        // For DICOM files
        const dicomInput = document.getElementById('dicom-file');
        if (dicomInput) {
            dicomInpuSt.addEventListener('change', handleFileSelect);
        }
        
        // For Excel files
        const excelInput = document.getElementById('excel-file');
        if (excelInput) {
            excelInput.addEventListener('change', handleFileSelect);
        }
        
        // For 3D model files
        const modelInput = document.getElementById('model-file');
        if (modelInput) {
            modelInput.addEventListener('change', handleFileSelect);
        }
    }

    // function setupFormSubmissionHandlers() {
    //     const forms = document.querySelectorAll('form[data-service]');
    //     forms.forEach(form => {
    //         form.addEventListener('submit', handleFormSubmit);
    //     });
    // }

    function handleFileSelect(event) {
        const fileInput = event.target;
        const previewContainer = document.getElementById("file-preview");
        
        if (fileInput.files.length > 0) {
            let previewHTML = '';
            const fileCount = fileInput.files.length;
            
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

    // function handleFormSubmit(event) {
    //     event.preventDefault();
        
    //     const form = event.target;
    //     const serviceType = form.getAttribute("data-service");
    //     const resultContainer = document.querySelector(".results-container");
    //     const formData = new FormData(form);
        
    //     // Show loading message
    //     resultContainer.innerHTML = `<p class="loading">Processing... Please wait.</p>`;
        
    //     // Endpoint URL based on service type
    //     const endpoint = `/extension_service/${serviceType}`;
        
    //     // Send AJAX request
    //     fetch(endpoint, {
    //         method: "POST",
    //         body: formData
    //     })
    //     .then(response => {
    //         if (!response.ok) {
    //             throw new Error(`HTTP error! Status: ${response.status}`);
    //         }
    //         return response.json();
    //     })
    //     .then(data => {
    //         if (data.error) {
    //             resultContainer.innerHTML = `<p class="error">${data.error}</p>`;
    //         } else {
    //             console.log("Response data:", data); // Debug log
    //             let resultHTML = `<p class="success">${data.message || 'Analysis completed successfully.'}</p>`;
                
    //             // Different result display based on service type
    //             if (serviceType === 'automated_measurement') {
    //                 // Display measurement results as a table
    //                 resultHTML += `
    //                     <div class="measurement-results">
    //                         <h4>AAA Measurements</h4>
    //                         <table class="results-table">
    //                             <tr>
    //                                 <th>Measurement</th>
    //                                 <th>Value</th>
    //                             </tr>
    //                             <tr>
    //                                 <td>Maximum Diameter</td>
    //                                 <td>${data.max_diameter} mm</td>
    //                             </tr>
    //                             <tr>
    //                                 <td>Volume</td>
    //                                 <td>${data.volume} mm³</td>
    //                             </tr>
    //                             <tr>
    //                                 <td>Surface Area</td>
    //                                 <td>${data.surface_area} mm²</td>
    //                             </tr>
    //                         </table>
    //                     </div>
    //                     <div class="result-image">
    //                         <img src="${data.output}" alt="Segmented aneurysm visualization">
    //                     </div>
    //                     <a href="${data.output}" class="download-btn" download>Download Visualization</a>
    //                 `;
    //             } else if (serviceType === 'growth_rate' || serviceType === 'rupture_risk') {
    //                 // Display prediction results
    //                 resultHTML += `
    //                     <div class="prediction-results">
    //                         <h4>Prediction Results</h4>
    //                         <table class="results-table">
    //                             <tr>
    //                                 <th>Parameter</th>
    //                                 <th>Value</th>
    //                             </tr>
    //                 `;
                    
    //                 // Add all metrics from the data
    //                 for (const [key, value] of Object.entries(data.metrics)) {
    //                     resultHTML += `
    //                         <tr>
    //                             <td>${key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</td>
    //                             <td>${value}</td>
    //                         </tr>
    //                     `;
    //                 }
                    
    //                 resultHTML += `
    //                         </table>
    //                     </div>
    //                 `;
                    
    //                 // Add chart/visualization if available
    //                 if (data.output) {
    //                     console.log("Image URL:", data.output); // Debug log
    //                     resultHTML += `
    //                         <div class="result-image">
    //                             <p>Image path: ${data.output}</p>
    //                             <img src="${data.output}" alt="Prediction visualization" onerror="this.onerror=null; this.src=''; console.error('Image failed to load:', this.src); this.style.display='none'; this.nextElementSibling.style.display='block';">
    //                             <p style="display:none; color: red;">Image failed to load. Debug info: URL=${data.output}</p>
    //                         </div>
    //                     `;
                        
    //                     // Add download link if available
    //                     if (data.download_url) {
    //                         console.log("Download URL:", data.download_url); // Debug log
    //                         resultHTML += `<a href="${data.download_url}" class="download-btn" download>Download Results CSV</a>`;
    //                     } else {
    //                         resultHTML += `<a href="${data.output}" class="download-btn" download>Download Visualization</a>`;
    //                     }
    //                 }
    //             } else {
    //                 // Generic result display for other services
    //                 resultHTML += `
    //                     <div class="result-image">
    //                         <img src="${data.output}" alt="Processed result">
    //                     </div>
    //                     <a href="${data.output}" class="download-btn" download>Download Result</a>
    //                 `;
                    
    //                 // If there are multiple files, show them all
    //                 if (data.all_outputs && data.all_outputs.length > 1) {
    //                     resultHTML += `<h4>All Processed Files (${data.all_outputs.length}):</h4><div class="all-results">`;
                        
    //                     data.all_outputs.forEach(output => {
    //                         resultHTML += `
    //                             <div class="result-thumbnail">
    //                                 <img src="${output}" alt="Processed result">
    //                                 <a href="${output}" download>Download</a>
    //                             </div>
    //                         `;
    //                     });
                        
    //                     resultHTML += `</div>`;
    //                 }
    //             }
                
    //             resultContainer.innerHTML = resultHTML;
    //         }
    //     })
    //     .catch(error => {
    //         resultContainer.innerHTML = `<p class="error">Error: ${error.message}</p>`;
    //     });
    // }
});



// Replace the setupFormSubmissionHandlers function with this updated version:

function setupFormSubmissionHandlers() {
    // For file upload forms
    const uploadForms = document.querySelectorAll('form[id="upload-form"]');
    uploadForms.forEach(form => {
        form.addEventListener('submit', handleFormSubmit);
    });
    
    // For manual input forms
    const manualForms = document.querySelectorAll('form[id="manual-form"]');
    manualForms.forEach(form => {
        form.addEventListener('submit', handleFormSubmit);
    });
}

// Update the handleFormSubmit function to work with both form types
// function handleFormSubmit(event) {
//     event.preventDefault();
    
//     const form = event.target;
//     const serviceType = form.getAttribute("data-service");
//     const resultContainer = document.querySelector(".results-container");
//     const formData = new FormData(form);
    
//     // Debug log all form data before submission
//     console.log(`Submitting form for service: ${serviceType}`);
//     console.log("Form data being submitted:");
//     for (let [key, value] of formData.entries()) {
//         console.log(`${key}: ${value}`);
//     }
    
//     // Show loading message
//     resultContainer.innerHTML = `<p class="loading">Processing... Please wait.</p>`;
    
//     // Get the file type for growth_rate service
//     if (serviceType === 'growth_rate') {
//         const fileTypeRadios = document.querySelectorAll('input[name="file_type"]');
//         const selectedType = Array.from(fileTypeRadios).find(r => r.checked)?.value || 'single';
//         console.log(`Selected file type is: ${selectedType}`);
        
//         // Double-check the hidden input value
//         const hiddenFileType = document.getElementById('file_type');
//         if (hiddenFileType) {
//             console.log(`Hidden file_type value is: ${hiddenFileType.value}`);
            
//             // Make sure it's set correctly
//             if (hiddenFileType.value !== selectedType) {
//                 console.warn(`Mismatch between selected radio (${selectedType}) and hidden input (${hiddenFileType.value}). Fixing...`);
//                 hiddenFileType.value = selectedType;
//                 formData.set('file_type', selectedType);
//             }
//         }
//     }
    
//     // Scroll to results section immediately
//     const resultsSection = document.querySelector(".results-section");
//     if (resultsSection) {
//         resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
//     }
    
//     // Endpoint URL based on service type
//     const endpoint = `/extension_service/${serviceType}`;
    
//     // Send AJAX request
//     fetch(endpoint, {
//         method: "POST",
//         body: formData
//     })
//     .then(response => {
//         console.log(`Server responded with status: ${response.status}`);
//         if (!response.ok) {
//             throw new Error(`HTTP error! Status: ${response.status}`);
//         }
//         return response.json();
//     })
//     .then(data => {
//         console.log("Received response data:", data);
//         if (data.error) {
//             resultContainer.innerHTML = `<p class="error">${data.error}</p>`;
//         } else {
//             // Process response data and update UI
//             let resultHTML = updateUIWithResults(data, serviceType);
//             resultContainer.innerHTML = resultHTML;
            
//             // Scroll to results again
//             if (resultsSection) {
//                 resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
//             }
//         }
//     })
//     .catch(error => {
//         console.error("Request failed:", error);
//         resultContainer.innerHTML = `<p class="error">Error: ${error.message}</p>`;
//     });
// }

// Function to handle switching between input methods
function setupInputMethodToggle() {
    const radioButtons = document.querySelectorAll('input[name="input_method"]');
    if (!radioButtons.length) return;
    
    const uploadSection = document.getElementById('upload-section');
    const manualSection = document.getElementById('manual-section');
    
    if (uploadSection && manualSection) {
        radioButtons.forEach(radio => {
            radio.addEventListener('change', function() {
                if (this.value === 'upload') {
                    uploadSection.style.display = 'block';
                    manualSection.style.display = 'none';
                } else if (this.value === 'manual') {
                    uploadSection.style.display = 'none';
                    manualSection.style.display = 'block';
                }
            });
        });
    }
}


// // Update the setupFormSubmissionHandlers function
// function setupFormSubmissionHandlers() {
//     const forms = document.querySelectorAll('form[data-service]');
//     forms.forEach(form => {
//         // Remove any existing event listeners (to prevent duplicates)
//         const newForm = form.cloneNode(true);
//         form.parentNode.replaceChild(newForm, form);
        
//         // Add the event listener to the new form
//         newForm.addEventListener('submit', handleFormSubmit);
//     });
// }

// Updated handleFormSubmit function for processing growth rate results
// function handleFormSubmit(event) {
//     event.preventDefault();
    
//     const form = event.target;
//     const serviceType = form.getAttribute("data-service");
//     const resultContainer = document.querySelector(".results-container");
//     const formData = new FormData(form);
    
//     // Show loading message
//     resultContainer.innerHTML = `<p class="loading">Processing... Please wait.</p>`;
    
//     // Scroll to results section immediately
//     const resultsSection = document.querySelector(".results-section");
//     if (resultsSection) {
//         resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
//     }
    
//     // Endpoint URL based on service type
//     const endpoint = `/extension_service/${serviceType}`;
    
//     // Send AJAX request
//     fetch(endpoint, {
//         method: "POST",
//         body: formData
//     })
//     .then(response => {
//         if (!response.ok) {
//             throw new Error(`HTTP error! Status: ${response.status}`);
//         }
//         return response.json();
//     })
//     .then(data => {
//         if (data.error) {
//             resultContainer.innerHTML = `<p class="error">${data.error}</p>`;
//         } else {
//             // Start with a success message
//             let resultHTML = `<p class="success">${data.message || 'Analysis completed successfully.'}</p>`;
            
//             // Check if this is growth_rate service
//             if (serviceType === 'growth_rate') {
//                 // Process based on whether this is a single patient or multiple patients
//                 if (data.is_single_patient) {
//                     // SINGLE PATIENT DISPLAY
                    
//                     // Create a prominent display for the key results
//                     const growthRate = parseFloat(data.metrics['Growth Rate (mm/year)']);
//                     resultHTML += `
//                         <div style="text-align: center; margin: 20px 0;">
//                             <div style="display: inline-block; background-color: #f5f5f5; border-radius: 8px; padding: 15px 30px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
//                                 <h2 style="margin: 0; color: #333; font-size: 16px;">Predicted Annual Growth Rate</h2>
//                                 <p style="font-size: 36px; font-weight: bold; margin: 10px 0; color: #f9a826;">${growthRate.toFixed(2)} mm/year</p>
//                             </div>
//                         </div>
//                     `;
                    
//                     // Display original patient data + predictions
//                     resultHTML += `
//                         <div class="prediction-results">
//                             <h4>Patient Data</h4>
//                             <table class="results-table">
//                                 <tr>
//                                     <th>Parameter</th>
//                                     <th>Value</th>
//                                 </tr>
//                     `;
                    
//                     // Add original data + predicted values
//                     for (const [key, value] of Object.entries(data.metrics)) {
//                         resultHTML += `
//                             <tr>
//                                 <td>${key}</td>
//                                 <td>${value}</td>
//                             </tr>
//                         `;
//                     }
                    
//                     resultHTML += `
//                             </table>
//                         </div>
//                     `;
                    
//                     // Add the projected growth chart
//                     if (data.output) {
//                         resultHTML += `
//                             <div class="result-image">
//                                 <h4>5-Year Size Projection</h4>
//                                 <img src="${data.output}" alt="Growth projection chart" style="max-width: 100%; border: 1px solid #ddd; border-radius: 5px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
//                             </div>
//                         `;
//                     }
                    
//                     // Add download link if available
//                     if (data.download_url) {
//                         resultHTML += `
//                             <div style="text-align: center; margin: 20px 0;">
//                                 <a href="${data.download_url}" class="download-btn" download>
//                                     <i class="fas fa-download"></i> Download Results (CSV)
//                                 </a>
//                             </div>
//                         `;
//                     }
//                 } else {
//                     // MULTIPLE PATIENTS DISPLAY
                    
//                     // Display key metrics as a prominent element
//                     if (data.metrics && data.metrics['Average Growth Rate (mm/year)']) {
//                         resultHTML += `
//                             <div style="text-align: center; margin: 20px 0;">
//                                 <div style="display: inline-block; background-color: #f5f5f5; border-radius: 8px; padding: 15px 30px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
//                                     <h2 style="margin: 0; color: #333; font-size: 16px;">Average Annual Growth Rate</h2>
//                                     <p style="font-size: 36px; font-weight: bold; margin: 10px 0; color: #f9a826;">${data.metrics['Average Growth Rate (mm/year)']}</p>
//                                 </div>
//                             </div>
//                         `;
//                     }
                    
//                     // Add all metrics as a table
//                     resultHTML += `
//                         <div class="prediction-results">
//                             <h4>Prediction Summary</h4>
//                             <table class="results-table">
//                                 <tr>
//                                     <th>Parameter</th>
//                                     <th>Value</th>
//                                 </tr>
//                     `;
                    
//                     // Add metrics from data
//                     if (data.metrics) {
//                         // Define the order we want to display metrics
//                         const metricOrder = [
//                             'Total Patients',
//                             'Average Growth Rate (mm/year)',
//                             'Maximum Growth Rate (mm/year)', 
//                             'High Risk Patients',
//                             'Moderate Risk Patients',
//                             'Low Risk Patients'
//                         ];
                        
//                         // Add ordered metrics first
//                         metricOrder.forEach(key => {
//                             if (data.metrics[key]) {
//                                 resultHTML += `
//                                     <tr>
//                                         <td>${key}</td>
//                                         <td>${data.metrics[key]}</td>
//                                     </tr>
//                                 `;
//                             }
//                         });
                        
//                         // Add any remaining metrics not in our ordered list
//                         for (const [key, value] of Object.entries(data.metrics)) {
//                             if (!metricOrder.includes(key) && key !== 'Average Growth Rate (mm/month)') {
//                                 resultHTML += `
//                                     <tr>
//                                         <td>${key}</td>
//                                         <td>${value}</td>
//                                     </tr>
//                                 `;
//                             }
//                         }
//                     }
                    
//                     resultHTML += `
//                             </table>
//                         </div>
//                     `;
                    
//                     // Add chart for multiple patients
//                     if (data.output) {
//                         resultHTML += `
//                             <div class="result-image">
//                                 <h4>Current vs. Projected Size After 1 Year</h4>
//                                 <img src="${data.output}" alt="Current vs. Projected AAA Size" style="max-width: 100%; border: 1px solid #ddd; border-radius: 5px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
//                             </div>
//                         `;
//                     }
                    
//                     // Add download link
//                     if (data.download_url) {
//                         resultHTML += `
//                             <div style="text-align: center; margin: 20px 0;">
//                                 <a href="${data.download_url}" class="download-btn" download>
//                                     <i class="fas fa-download"></i> Download Full Results (CSV)
//                                 </a>
//                             </div>
//                         `;
//                     }
//                 }
//             } else {
//                 // For other services, keep the generic display
//                 resultHTML += `
//                     <div class="result-image">
//                         <img src="${data.output}" alt="Processed result">
//                     </div>
//                     <a href="${data.output}" class="download-btn" download>Download Result</a>
//                 `;
                
//                 // If there are multiple files, show them all
//                 if (data.all_outputs && data.all_outputs.length > 1) {
//                     resultHTML += `<h4>All Processed Files (${data.all_outputs.length}):</h4><div class="all-results">`;
                    
//                     data.all_outputs.forEach(output => {
//                         resultHTML += `
//                             <div class="result-thumbnail">
//                                 <img src="${output}" alt="Processed result">
//                                 <a href="${output}" download>Download</a>
//                             </div>
//                         `;
//                     });
                    
//                     resultHTML += `</div>`;
//                 }
//             }
            
//             // Update the results container
//             resultContainer.innerHTML = resultHTML;
            
//             // Scroll to results again to ensure it's visible after loading content
//             if (resultsSection) {
//                 resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
//             }
//         }
//     })
//     .catch(error => {
//         resultContainer.innerHTML = `<p class="error">Error: ${error.message}</p>`;
//     });
// }


// Update the setupServiceDetails function to include file type selection
function setupServiceDetails() {
    // Setup processing method options if present
    setupProcessingMethod();
    
    // Setup file type selection for growth_rate
    setupFileTypeSelection();
    
    // Setup file upload options
    setupUploadOptions();
    
    // Add file selection handler
    setupFileHandlers();
    
    // Add form submission handler
    setupFormSubmissionHandlers();
}

// Add/update this to your extensionCards.forEach click handler
extensionCards.forEach(card => {
    card.addEventListener("click", () => {
        const selectedService = card.dataset.service;
        
        if (selectedService && services[selectedService]) {
            serviceDetails.innerHTML = services[selectedService];
            serviceDetails.style.display = "block";
            
            // Setup all event handlers and UI behaviors
            setupServiceDetails();
            
            // Scroll to service details section
            setTimeout(() => {
                serviceDetails.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }, 100);
        }
    });
});

// Add this to setupInputMethodToggle function
function setupInputMethodToggle() {
    const radioButtons = document.querySelectorAll('input[name="input_method"]');
    if (!radioButtons.length) return;
    
    const uploadTitle = document.getElementById('upload-title');
    const singlePatientInfo = document.getElementById('single-patient-info');
    const multiplePatientInfo = document.getElementById('multiple-patients-info');
    const fileTypeInput = document.getElementById('file-type');
    
    if (uploadTitle && singlePatientInfo && multiplePatientInfo && fileTypeInput) {
        radioButtons.forEach(radio => {
            radio.addEventListener('change', function() {
                if (this.value === 'single') {
                    uploadTitle.innerText = 'Upload Single Patient Data';
                    singlePatientInfo.style.display = 'block';
                    multiplePatientInfo.style.display = 'none';
                    fileTypeInput.value = 'single';
                } else if (this.value === 'multiple') {
                    uploadTitle.innerText = 'Upload Multiple Patients Data';
                    singlePatientInfo.style.display = 'none';
                    multiplePatientInfo.style.display = 'block';
                    fileTypeInput.value = 'multiple';
                }
            });
        });
    }
}

// Function to setup file type selection
function setupFileTypeSelection() {
    const radioButtons = document.querySelectorAll('input[name="file_type"]');
    if (!radioButtons.length) return;
    
    const hiddenFileType = document.getElementById('file_type');
    if (!hiddenFileType) {
        console.error("Hidden file_type input not found!");
        return;
    }
    
    // Set the initial value based on the checked radio button
    const checkedRadio = document.querySelector('input[name="file_type"]:checked');
    if (checkedRadio) {
        console.log(`Setting initial file type to: ${checkedRadio.value}`);
        hiddenFileType.value = checkedRadio.value;
    }
    
    // Add change event listeners
    radioButtons.forEach(radio => {
        radio.addEventListener('change', function() {
            console.log(`File type changed to: ${this.value}`);
            hiddenFileType.value = this.value;
        });
    });
}

// Add this to your existing setup code
// Add this at the beginning of the document.addEventListener("DOMContentLoaded", ...) function

document.addEventListener("DOMContentLoaded", () => {
    console.log("DOM fully loaded");
    const extensionCards = document.querySelectorAll(".extension-card:not(.coming-soon)");
    const serviceDetails = document.getElementById("service-details");

    // Service form templates remain the same
    // ...

    // Add click event to each extension card
    extensionCards.forEach(card => {
        card.addEventListener("click", () => {
            const selectedService = card.dataset.service;
            
            if (selectedService && services[selectedService]) {
                serviceDetails.innerHTML = services[selectedService];
                serviceDetails.style.display = "block";
                
                console.log(`Selected service: ${selectedService}`);
                
                // Setup all UI elements and event handlers
                setupProcessingMethod();
                setupFileTypeSelection();
                setupUploadOptions();
                setupFileHandlers();
                setupFormSubmissionHandlers();
                
                // Scroll to service details section
                setTimeout(() => {
                    serviceDetails.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }, 100);
            }
        });
    });

    // Function to initialize all UI elements for a service
    function initializeServiceUI(serviceType) {
        console.log(`Initializing UI for ${serviceType}`);
        
        // Setup processing method options if present
        setupProcessingMethod();
        
        // Setup file type selection for growth_rate
        if (serviceType === 'growth_rate') {
            console.log("Setting up file type selection for growth_rate");
            setupFileTypeSelection();
        }
        
        // Setup file upload options
        setupUploadOptions();
        
        // Add file selection handler
        setupFileHandlers();
        
        // Add form submission handler
        setupFormSubmissionHandlers();
        
        // Add form debugger
        addFormDebugger();
    }

    // Add a debugging function to check form data before submission
    function addFormDebugger() {
        const forms = document.querySelectorAll('form[data-service]');
        forms.forEach(form => {
            form.addEventListener('submit', function(e) {
                // Don't actually prevent submission, just log the data
                const formData = new FormData(this);
                console.log("Form being submitted with data:");
                for (let [key, value] of formData.entries()) {
                    console.log(`${key}: ${value}`);
                }
            });
        });
    }
});

// Separate function to process results and update UI
function updateUIWithResults(data, serviceType) {
    // Start with a success message
    let resultHTML = `<p class="success">${data.message || 'Analysis completed successfully.'}</p>`;
    
    // Check if this is growth_rate service
    if (serviceType === 'growth_rate') {
        // Process based on whether this is a single patient or multiple patients
        if (data.is_single_patient) {
            // SINGLE PATIENT DISPLAY
            resultHTML += generateSinglePatientHTML(data);
        } else {
            // MULTIPLE PATIENTS DISPLAY
            resultHTML += generateMultiplePatientHTML(data);
        }
    } else {
        // For other services, keep the generic display
        resultHTML += generateGenericResultHTML(data);
    }
    
    return resultHTML;
}

// Function to generate HTML for multiple patient results
function generateMultiplePatientHTML(data) {
    let html = '';
    
    // Display key metrics as a prominent element
    if (data.metrics && data.metrics['Average Growth Rate (mm/year)']) {
        html += `
            <div style="text-align: center; margin: 20px 0;">
                <div style="display: inline-block; background-color: #f5f5f5; border-radius: 8px; padding: 15px 30px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                    <h2 style="margin: 0; color: #333; font-size: 16px;">Average Annual Growth Rate</h2>
                    <p style="font-size: 36px; font-weight: bold; margin: 10px 0; color: #f9a826;">${data.metrics['Average Growth Rate (mm/year)']}</p>
                </div>
            </div>
        `;
    }
    
    // Add all metrics as a table
    html += `
        <div class="prediction-results">
            <h4>Prediction Summary</h4>
            <table class="results-table">
                <tr>
                    <th>Parameter</th>
                    <th>Value</th>
                </tr>
    `;
    
    // Add metrics from data
    if (data.metrics) {
        // Define the order we want to display metrics
        const metricOrder = [
            'Total Patients',
            'Average Growth Rate (mm/year)',
            'Maximum Growth Rate (mm/year)', 
            'High Risk Patients',
            'Moderate Risk Patients',
            'Low Risk Patients'
        ];
        
        // Add ordered metrics first
        metricOrder.forEach(key => {
            if (data.metrics[key]) {
                html += `
                    <tr>
                        <td>${key}</td>
                        <td>${data.metrics[key]}</td>
                    </tr>
                `;
            }
        });
        
        // Add any remaining metrics not in our ordered list
        for (const [key, value] of Object.entries(data.metrics)) {
            if (!metricOrder.includes(key) && key !== 'Average Growth Rate (mm/month)') {
                html += `
                    <tr>
                        <td>${key}</td>
                        <td>${value}</td>
                    </tr>
                `;
            }
        }
    }
    
    html += `
            </table>
        </div>
    `;
    
    // Add chart for multiple patients
    if (data.output) {
        html += `
            <div class="result-image">
                <h4>Current vs. Projected Size After 1 Year</h4>
                <img src="${data.output}" alt="Current vs. Projected AAA Size" style="max-width: 100%; border: 1px solid #ddd; border-radius: 5px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            </div>
        `;
    }
    
    // Add download link
    if (data.download_url) {
        html += `
            <div style="text-align: center; margin: 20px 0;">
                <a href="${data.download_url}" class="download-btn" download>
                    <i class="fas fa-download"></i> Download Full Results (CSV)
                </a>
            </div>
        `;
    }
    
    return html;
}

// Function to generate HTML for generic service results
function generateGenericResultHTML(data) {
    let html = `
        <div class="result-image">
            <img src="${data.output}" alt="Processed result">
        </div>
        <a href="${data.output}" class="download-btn" download>Download Result</a>
    `;
    
    // If there are multiple files, show them all
    if (data.all_outputs && data.all_outputs.length > 1) {
        html += `<h4>All Processed Files (${data.all_outputs.length}):</h4><div class="all-results">`;
        
        data.all_outputs.forEach(output => {
            html += `
                <div class="result-thumbnail">
                    <img src="${output}" alt="Processed result">
                    <a href="${output}" download>Download</a>
                </div>
            `;
        });
        
        html += `</div>`;
    }
    
    return html;
}

// Function to handle the display of rupture risk prediction results
function displayRuptureRiskResults(data, resultContainer) {
    console.log("Displaying rupture risk results:", data);
    
    try {
        // Start with a success message
        let resultHTML = `<p class="success">${data.message || 'Analysis completed successfully.'}</p>`;
        
        // Add summary statistics if available
        if (data.statistics) {
            resultHTML += `
                <div class="summary-statistics">
                    <div class="stat-box">
                        <h5>Average Current Risk</h5>
                        <p class="stat-value">${data.statistics.avg_current_risk !== undefined ? parseFloat(data.statistics.avg_current_risk).toFixed(1) : '0.0'}%</p>
                    </div>
                    <div class="stat-box">
                        <h5>Average Risk at 5 Years</h5>
                        <p class="stat-value">${data.statistics.avg_risk_5yr !== undefined ? parseFloat(data.statistics.avg_risk_5yr).toFixed(1) : '0.0'}%</p>
                    </div>
                    <div class="stat-box">
                        <h5>High Risk Patients (Current)</h5>
                        <p class="stat-value">${data.statistics.high_risk_current || 0} 
                        (${data.statistics.patient_count ? ((data.statistics.high_risk_current || 0) / data.statistics.patient_count * 100).toFixed(1) : 0}%)</p>
                    </div>
                    <div class="stat-box">
                        <h5>High Risk Patients (5 Years)</h5>
                        <p class="stat-value">${data.statistics.high_risk_5yr || 0} 
                        (${data.statistics.patient_count ? ((data.statistics.high_risk_5yr || 0) / data.statistics.patient_count * 100).toFixed(1) : 0}%)</p>
                    </div>
                </div>
            `;
        }
        
        // Add primary visualization if available
        if (data.output) {
            resultHTML += `
                <div class="result-image">
                    <h4>Patient Risk Progression</h4>
                    <img src="${data.output}" alt="AAA Risk Progression Visualization" style="max-width: 100%; border: 1px solid #ddd; border-radius: 5px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                </div>
            `;
        }
        
        // Add patient-specific visualization if available
        if (data.patient_visualization) {
            resultHTML += `
                <div class="result-image">
                    <h4>Individual Patient Risk Trajectories</h4>
                    <img src="${data.patient_visualization}" alt="Patient-Specific Risk Trajectories" style="max-width: 100%; border: 1px solid #ddd; border-radius: 5px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                </div>
            `;
        }
        
        // Add detailed results table if available
        if (data.detailed_results && Array.isArray(data.detailed_results) && data.detailed_results.length > 0) {
            resultHTML += `
                <div class="detailed-results">
                    <h4>Detailed Patient Results</h4>
                    <div class="table-responsive">
                        <table class="results-table">
                            <thead>
                                <tr>
                                    <th>Patient ID</th>
                                    <th>Current Diameter</th>
                                    <th>Current Risk</th>
                                    <th>Risk at 1 Year</th>
                                    <th>Risk at 5 Years</th>
                                    <th>Growth Rate</th>
                                </tr>
                            </thead>
                            <tbody>
            `;
            
            data.detailed_results.forEach(patient => {
                // Safely get values with defaults to prevent errors
                const patientId = patient["Patient ID"] || "Unknown";
                const diameter = parseFloat(patient["Axial Diameter (mm)"]) || 0;
                const currentRisk = parseFloat(patient["Current Risk (%)"]) || 0;
                const risk1yr = parseFloat(patient["Risk at 1 Year (%)"]) || 0;
                const risk5yr = parseFloat(patient["Risk at 5 Years (%)"]) || 0;
                const growthRate = parseFloat(patient["Growth Rate (mm/year)"]) || 0;
                
                resultHTML += `
                    <tr>
                        <td>${patientId}</td>
                        <td>${diameter.toFixed(1)} mm</td>
                        <td>${currentRisk.toFixed(1)}%</td>
                        <td>${risk1yr.toFixed(1)}%</td>
                        <td>${risk5yr.toFixed(1)}%</td>
                        <td>${growthRate.toFixed(2)} mm/year</td>
                    </tr>
                `;
            });
            
            resultHTML += `
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        }
        
        // Add download link if available
        if (data.download_url) {
            resultHTML += `
                <div style="text-align: center; margin: 20px 0;">
                    <a href="${data.download_url}" class="download-btn" download>
                        <i class="fas fa-download"></i> Download Complete Results (CSV)
                    </a>
                </div>
            `;
        }
        
        // Apply the HTML to the result container
        resultContainer.innerHTML = resultHTML;
        
        // Add styles for the various components
        addRuptureRiskStyles();
        
    } catch (error) {
        console.error("Error displaying rupture risk results:", error);
        resultContainer.innerHTML = `<p class="error">Error displaying results: ${error.message}</p>`;
    }
}

// Add styles for rupture risk display
function addRuptureRiskStyles() {
    // Check if styles already exist
    if (document.getElementById('rupture-risk-styles')) {
        return;
    }
    
    const styleElement = document.createElement('style');
    styleElement.id = 'rupture-risk-styles';
    styleElement.textContent = `
        .summary-statistics {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-around;
            margin: 20px 0;
        }
        .stat-box {
            flex: 1;
            min-width: 150px;
            padding: 15px;
            margin: 10px;
            background-color: #f5f5f5;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .stat-box h5 {
            margin: 0 0 10px 0;
            font-size: 14px;
            color: #555;
        }
        .stat-value {
            font-size: 24px;
            font-weight: bold;
            color: #333;
            margin: 0;
        }
        .table-responsive {
            overflow-x: auto;
            margin-bottom: 20px;
        }
        .detailed-results {
            margin: 20px 0;
        }
        .detailed-results h4 {
            margin-bottom: 15px;
        }
    `;
    document.head.appendChild(styleElement);
}

// Helper function to get color based on risk percentage
function getRiskColor(riskPercent) {
    if (riskPercent < 15) return '#2ecc71'; // Green - Low
    if (riskPercent < 35) return '#f39c12'; // Orange - Moderate
    if (riskPercent < 65) return '#e74c3c'; // Red - High
    return '#c0392b'; // Dark red - Very High
}

// Helper function to get color based on risk category
function getCategoryColor(category) {
    switch (category) {
        case 'Low': return '#2ecc71';
        case 'Moderate': return '#f39c12';
        case 'High': return '#e74c3c';
        case 'Very High': return '#c0392b';
        default: return '#7f8c8d';
    }
}

// Modify handleFormSubmit to include our new rupture risk display function
function handleFormSubmit(event) {
    event.preventDefault();
    
    const form = event.target;
    const serviceType = form.getAttribute("data-service");
    const resultContainer = document.querySelector(".results-container");
    const formData = new FormData(form);
    
    // Debug log form data
    console.log(`Submitting form for service: ${serviceType}`);
    // console.log("Form data being submitted:");
    // for (let [key, value] of formData.entries()) {
    //     console.log(`${key}: ${value}`);
    // }

        // IMPORTANT: Add this block from version #2 for growth_rate handling
        if (serviceType === 'growth_rate') {
            const fileTypeRadios = document.querySelectorAll('input[name="file_type"]');
            const selectedType = Array.from(fileTypeRadios).find(r => r.checked)?.value || 'single';
            console.log(`Selected file type is: ${selectedType}`);
            
            // Double-check the hidden input value
            const hiddenFileType = document.getElementById('file_type');
            if (hiddenFileType) {
                console.log(`Hidden file_type value is: ${hiddenFileType.value}`);
                
                // Make sure it's set correctly
                if (hiddenFileType.value !== selectedType) {
                    console.warn(`Mismatch between selected radio (${selectedType}) and hidden input (${hiddenFileType.value}). Fixing...`);
                    hiddenFileType.value = selectedType;
                    formData.set('file_type', selectedType);
                }
            }
        }
    
    // Show loading message
    resultContainer.innerHTML = `<p class="loading">Processing... Please wait.</p>`;
    
    // Scroll to results section immediately
    const resultsSection = document.querySelector(".results-section");
    if (resultsSection) {
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    
    // Endpoint URL based on service type
    const endpoint = `/extension_service/${serviceType}`;
    
    // Send AJAX request
    fetch(endpoint, {
        method: "POST",
        body: formData
    })
    .then(response => {
        console.log(`Server responded with status: ${response.status}`);
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log("Received response data:", data);
        
        // Check for errors
        if (data.error) {
            resultContainer.innerHTML = `<p class="error">${data.error}</p>`;
            return;
        }
        
        // Process the response based on service type
        if (serviceType === 'rupture_risk') {
            // Display rupture risk results using the specialized function
            displayRuptureRiskResults(data, resultContainer);
        } 
        else if (serviceType === 'growth_rate') {
            // Handle growth rate results
            let resultHTML = createGrowthRateHTML(data);
            resultContainer.innerHTML = resultHTML;
        }
        else {
            // Generic handler for other services
            let resultHTML = createGenericResultHTML(data);
            resultContainer.innerHTML = resultHTML;
        }
        
        // Scroll to results again
        if (resultsSection) {
            resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    })
    .catch(error => {
        console.error("Request failed:", error);
        resultContainer.innerHTML = `<p class="error">Error: ${error.message}</p>`;
    });
}


    // Helper function for growth rate results HTML
    function createGrowthRateHTML(data) {
        let resultHTML = `<p class="success">${data.message || 'Analysis completed successfully.'}</p>`;
        
        // Check if single or multiple patients
        if (data.is_single_patient) {
            // Single patient display
            if (data.metrics && data.metrics['Growth Rate (mm/year)']) {
                const growthRate = parseFloat(data.metrics['Growth Rate (mm/year)']);
                resultHTML += `
                    <div style="text-align: center; margin: 20px 0;">
                        <div style="display: inline-block; background-color: #f5f5f5; border-radius: 8px; padding: 15px 30px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                            <h2 style="margin: 0; color: #333; font-size: 16px;">Predicted Annual Growth Rate</h2>
                            <p style="font-size: 36px; font-weight: bold; margin: 10px 0; color: #f9a826;">${growthRate.toFixed(2)} mm/year</p>
                        </div>
                    </div>
                `;
            }
            
            // Add metrics table
            resultHTML += createMetricsTable(data.metrics);
            
            // Add visualization if available
            if (data.output) {
                resultHTML += `
                    <div class="result-image">
                        <h4>5-Year Size Projection</h4>
                        <img src="${data.output}" alt="Growth projection chart" style="max-width: 100%; border: 1px solid #ddd; border-radius: 5px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    </div>
                `;
            }
        } else {
            // Multiple patients display
            if (data.metrics && data.metrics['Average Growth Rate (mm/year)']) {
                resultHTML += `
                    <div style="text-align: center; margin: 20px 0;">
                        <div style="display: inline-block; background-color: #f5f5f5; border-radius: 8px; padding: 15px 30px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                            <h2 style="margin: 0; color: #333; font-size: 16px;">Average Annual Growth Rate</h2>
                            <p style="font-size: 36px; font-weight: bold; margin: 10px 0; color: #f9a826;">${data.metrics['Average Growth Rate (mm/year)']}</p>
                        </div>
                    </div>
                `;
            }
            
            // Add metrics table
            resultHTML += createMetricsTable(data.metrics);
            
            // Add visualization if available
            if (data.output) {
                resultHTML += `
                    <div class="result-image">
                        <h4>Current vs. Projected Size</h4>
                        <img src="${data.output}" alt="Current vs. Projected AAA Size" style="max-width: 100%; border: 1px solid #ddd; border-radius: 5px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    </div>
                `;
            }
        }
        
        // Add download link if available
        if (data.download_url) {
            resultHTML += `
                <div style="text-align: center; margin: 20px 0;">
                    <a href="${data.download_url}" class="download-btn" download>
                        <i class="fas fa-download"></i> Download Results (CSV)
                    </a>
                </div>
            `;
        }
        
        return resultHTML;
    }

    // Helper function to create metrics table HTML
    function createMetricsTable(metrics) {
        if (!metrics || Object.keys(metrics).length === 0) {
            return '';
        }
        
        let tableHTML = `
            <div class="prediction-results">
                <h4>Prediction Results</h4>
                <table class="results-table">
                    <tr>
                        <th>Parameter</th>
                        <th>Value</th>
                    </tr>
        `;
        
        for (const [key, value] of Object.entries(metrics)) {
            tableHTML += `
                <tr>
                    <td>${key}</td>
                    <td>${value}</td>
                </tr>
            `;
        }
        
        tableHTML += `
                </table>
            </div>
        `;
        
        return tableHTML;
    }

// Helper function to create generic result HTML
function createGenericResultHTML(data) {
    let resultHTML = `<p class="success">${data.message || 'Analysis completed successfully.'}</p>`;
    
    if (data.output) {
        resultHTML += `
            <div class="result-image">
                <img src="${data.output}" alt="Processed result">
            </div>
            <a href="${data.output}" class="download-btn" download>Download Result</a>
        `;
    }
    
    // If there are multiple files, show them all
    if (data.all_outputs && Array.isArray(data.all_outputs) && data.all_outputs.length > 1) {
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
    
    return resultHTML;
}

    // // CRUCIAL FUNCTION: Display rupture risk results
    // function displayRuptureRiskResults(data, resultContainer) {
    //     console.log("Displaying rupture risk results:", data);
        
    //     try {
    //         // Start with a success message
    //         let resultHTML = `<p class="success">${data.message || 'Analysis completed successfully.'}</p>`;
            
    //         // Add summary statistics if available
    //         if (data.statistics) {
    //             resultHTML += `
    //                 <div class="summary-statistics">
    //                     <div class="stat-box">
    //                         <h5>Average Current Risk</h5>
    //                         <p class="stat-value">${data.statistics.avg_current_risk ? data.statistics.avg_current_risk.toFixed(1) : 0}%</p>
    //                     </div>
    //                     <div class="stat-box">
    //                         <h5>Average Risk at 5 Years</h5>
    //                         <p class="stat-value">${data.statistics.avg_risk_5yr ? data.statistics.avg_risk_5yr.toFixed(1) : 0}%</p>
    //                     </div>
    //                     <div class="stat-box">
    //                         <h5>High Risk Patients (Current)</h5>
    //                         <p class="stat-value">${data.statistics.high_risk_current || 0} 
    //                         (${data.statistics.patient_count ? ((data.statistics.high_risk_current || 0) / data.statistics.patient_count * 100).toFixed(1) : 0}%)</p>
    //                     </div>
    //                     <div class="stat-box">
    //                         <h5>High Risk Patients (5 Years)</h5>
    //                         <p class="stat-value">${data.statistics.high_risk_5yr || 0} 
    //                         (${data.statistics.patient_count ? ((data.statistics.high_risk_5yr || 0) / data.statistics.patient_count * 100).toFixed(1) : 0}%)</p>
    //                     </div>
    //                 </div>
    //             `;
    //         }
            
    //         // Add primary visualization if available
    //         if (data.output) {
    //             resultHTML += `
    //                 <div class="result-image">
    //                     <h4>Patient Risk Progression</h4>
    //                     <img src="${data.output}" alt="AAA Risk Progression Visualization" style="max-width: 100%; border: 1px solid #ddd; border-radius: 5px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
    //                 </div>
    //             `;
    //         }
            
    //         // Add patient-specific visualization if available
    //         if (data.patient_visualization) {
    //             resultHTML += `
    //                 <div class="result-image">
    //                     <h4>Individual Patient Risk Trajectories</h4>
    //                     <img src="${data.patient_visualization}" alt="Patient-Specific Risk Trajectories" style="max-width: 100%; border: 1px solid #ddd; border-radius: 5px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
    //                 </div>
    //             `;
    //         }
            
    //         // Add detailed results table if available
    //         if (data.detailed_results && Array.isArray(data.detailed_results) && data.detailed_results.length > 0) {
    //             resultHTML += `
    //                 <div class="detailed-results">
    //                     <h4>Detailed Patient Results</h4>
    //                     <div class="table-responsive">
    //                         <table class="results-table">
    //                             <thead>
    //                                 <tr>
    //                                     <th>Patient ID</th>
    //                                     <th>Current Diameter</th>
    //                                     <th>Current Risk</th>
    //                                     <th>Risk at 1 Year</th>
    //                                     <th>Risk at 5 Years</th>
    //                                     <th>Growth Rate</th>
    //                                 </tr>
    //                             </thead>
    //                             <tbody>
    //             `;
                
    //             data.detailed_results.forEach(patient => {
    //                 // Safely get values with defaults to prevent errors
    //                 const patientId = patient["Patient ID"] || "Unknown";
    //                 const diameter = parseFloat(patient["Axial Diameter (mm)"]) || 0;
    //                 const currentRisk = parseFloat(patient["Current Risk (%)"]) || 0;
    //                 const risk1yr = parseFloat(patient["Risk at 1 Year (%)"]) || 0;
    //                 const risk5yr = parseFloat(patient["Risk at 5 Years (%)"]) || 0;
    //                 const growthRate = parseFloat(patient["Growth Rate (mm/year)"]) || 0;
                    
    //                 resultHTML += `
    //                     <tr>
    //                         <td>${patientId}</td>
    //                         <td>${diameter.toFixed(1)} mm</td>
    //                         <td>${currentRisk.toFixed(1)}%</td>
    //                         <td>${risk1yr.toFixed(1)}%</td>
    //                         <td>${risk5yr.toFixed(1)}%</td>
    //                         <td>${growthRate.toFixed(2)} mm/year</td>
    //                     </tr>
    //                 `;
    //             });
                
    //             resultHTML += `
    //                             </tbody>
    //                         </table>
    //                     </div>
    //                 </div>
    //             `;
    //         }
            
    //         // Add download link if available
    //         if (data.download_url) {
    //             resultHTML += `
    //                 <div style="text-align: center; margin: 20px 0;">
    //                     <a href="${data.download_url}" class="download-btn" download>
    //                         <i class="fas fa-download"></i> Download Complete Results (CSV)
    //                     </a>
    //                 </div>
    //             `;
    //         }
            
    //         // Apply the HTML to the result container
    //         resultContainer.innerHTML = resultHTML;
            
    //         // Add styles for the various components
    //         addRuptureRiskStyles();
            
    //     } catch (error) {
    //         console.error("Error displaying rupture risk results:", error);
    //         resultContainer.innerHTML = `<p class="error">Error displaying results: ${error.message}</p>`;
    //     }
    // }


    // // Setup form submission handlers
    // function setupFormSubmissionHandlers() {
    //     const forms = document.querySelectorAll('form[data-service]');
    //     forms.forEach(form => {
    //         form.addEventListener('submit', handleFormSubmit);
    //     });
    // }

    // File selection handler
    function setupFileHandlers() {
        // For Excel files
        const excelInput = document.getElementById('excel-file');
        if (excelInput) {
            excelInput.addEventListener('change', function(event) {
                const fileInput = event.target;
                const previewContainer = document.getElementById("file-preview");
                
                if (fileInput.files.length > 0) {
                    let previewHTML = `<p><strong>Selected file:</strong> ${fileInput.files[0].name}</p>`;
                    previewHTML += `<p><strong>Size:</strong> ${formatFileSize(fileInput.files[0].size)}</p>`;
                    previewContainer.innerHTML = previewHTML;
                } else {
                    previewContainer.innerHTML = "<p>No file selected.</p>";
                }
            });
        }
        
        // For DICOM files
        const dicomInput = document.getElementById('dicom-file');
        if (dicomInput) {
            dicomInput.addEventListener('change', function(event) {
                const fileInput = event.target;
                const previewContainer = document.getElementById("file-preview");
                
                if (fileInput.files.length > 0) {
                    let previewHTML = '';
                    const fileCount = fileInput.files.length;
                    
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
                    
                    previewContainer.innerHTML = previewHTML;
                } else {
                    previewContainer.innerHTML = "<p>No files selected.</p>";
                }
            });
        }
        
        // For 3D model files
        const modelInput = document.getElementById('model-file');
        if (modelInput) {
            modelInput.addEventListener('change', function(event) {
                const fileInput = event.target;
                const previewContainer = document.getElementById("file-preview");
                
                if (fileInput.files.length > 0) {
                    let previewHTML = `<p><strong>Selected file:</strong> ${fileInput.files[0].name}</p>`;
                    previewHTML += `<p><strong>Size:</strong> ${formatFileSize(fileInput.files[0].size)}</p>`;
                    previewContainer.innerHTML = previewHTML;
                } else {
                    previewContainer.innerHTML = "<p>No file selected.</p>";
                }
            });
        }
    }

    // Helper function to format file size
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // Helper function to format total size of multiple files
    function formatTotalSize(files) {
        let totalBytes = 0;
        for (let i = 0; i < files.length; i++) {
            totalBytes += files[i].size;
        }
        return formatFileSize(totalBytes);
    } 