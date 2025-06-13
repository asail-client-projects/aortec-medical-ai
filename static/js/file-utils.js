// static/js/file-utils.js
// Utility functions for client-side file handling

class FileProcessor {
    constructor() {
        this.jszip = null;
        this.loadJSZip();
        this.processingQueue = [];
        this.totalFiles = 0;
        this.processedFiles = 0;
        this.onProgress = null;
        this.onComplete = null;
    }

    async loadJSZip() {
        // Dynamically load JSZip library if not already loaded
        if (window.JSZip) {
            this.jszip = new JSZip();
            return;
        }
        
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = 'https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js';
            script.onload = () => {
                this.jszip = new JSZip();
                resolve();
            };
            script.onerror = (err) => reject(err);
            document.head.appendChild(script);
        });
    }

    async processLocalDirectory(directory, progressCallback, completeCallback) {
        this.onProgress = progressCallback;
        this.onComplete = completeCallback;
        
        try {
            // Create form data to send to server
            const formData = new FormData();
            formData.append('directory', directory);
            formData.append('client_side_zip', 'true');
            
            // Show initial progress
            if (this.onProgress) {
                this.onProgress({
                    status: 'starting',
                    message: 'Requesting directory processing...',
                    progress: 0
                });
            }
            
            // Send request to process directory
            const response = await fetch('/process_local_directory_images', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            // Get the list of processed image files
            this.processImages(data.image_paths, data.total_files);
            
        } catch (error) {
            if (this.onProgress) {
                this.onProgress({
                    status: 'error',
                    message: `Error: ${error.message}`,
                    progress: 0
                });
            }
        }
    }
    
    async processImages(imagePaths, totalCount) {
        this.totalFiles = totalCount || imagePaths.length;
        this.processedFiles = 0;
        
        if (this.onProgress) {
            this.onProgress({
                status: 'processing',
                message: `Creating ZIP archive with ${this.totalFiles} images...`,
                progress: 0
            });
        }
        
        // Create a new ZIP file
        this.jszip = new JSZip();
        
        // Process each image
        for (let i = 0; i < imagePaths.length; i++) {
            const imagePath = imagePaths[i];
            const filename = imagePath.split('/').pop();
            
            try {
                // Fetch the image as blob
                const response = await fetch(imagePath);
                if (!response.ok) {
                    console.error(`Failed to fetch ${filename}`);
                    continue;
                }
                
                const imageBlob = await response.blob();
                
                // Add to zip
                this.jszip.file(filename, imageBlob);
                
                // Update progress
                this.processedFiles++;
                if (this.onProgress) {
                    this.onProgress({
                        status: 'processing',
                        message: `Adding images to ZIP: ${this.processedFiles}/${this.totalFiles}`,
                        progress: (this.processedFiles / this.totalFiles) * 100
                    });
                }
            } catch (error) {
                console.error(`Error processing ${filename}: ${error.message}`);
            }
        }
        
        // Generate the ZIP file
        if (this.onProgress) {
            this.onProgress({
                status: 'generating',
                message: 'Generating ZIP file...',
                progress: 95
            });
        }
        
        try {
            const zipBlob = await this.jszip.generateAsync({
                type: 'blob',
                compression: 'DEFLATE',
                compressionOptions: {
                    level: 6
                }
            });
            
            // Create download link
            const timestamp = new Date().toISOString().replace(/[-:.]/g, '').substr(0, 14);
            const downloadUrl = URL.createObjectURL(zipBlob);
            const filename = `converted_images_${timestamp}.zip`;
            
            if (this.onComplete) {
                this.onComplete({
                    status: 'complete',
                    message: 'ZIP file created successfully!',
                    url: downloadUrl,
                    filename: filename,
                    size: zipBlob.size
                });
            }
        } catch (error) {
            if (this.onProgress) {
                this.onProgress({
                    status: 'error',
                    message: `Error generating ZIP: ${error.message}`,
                    progress: 0
                });
            }
        }
    }
}

// Make it available globally
window.fileProcessor = new FileProcessor();