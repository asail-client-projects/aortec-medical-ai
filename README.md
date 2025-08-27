# AORTEC - Advanced Medical Imaging Analysis Platform

AORTEC is a comprehensive web-based platform for medical imaging analysis, specifically designed for Abdominal Aortic Aneurysm (AAA) detection, measurement, and risk assessment. The platform combines DICOM image processing with AI-powered prediction models to provide healthcare professionals with advanced diagnostic tools.

## 🏥 Features

### Core Services
- **DICOM to Image Converter**: Convert DICOM medical images to standard formats (JPG/PNG)
- **3D DICOM Viewer**: Interactive viewer with measurement rulers and navigation
- **Image Segmentation**: Advanced segmentation for AAA analysis
- **Growth Rate Prediction**: AI-powered prediction of aneurysm growth over time
- **Rupture Risk Assessment**: Machine learning models for rupture risk evaluation

### Key Capabilities
- 📏 Precise measurements with millimeter accuracy
- 🔍 Interactive navigation through DICOM slices  
- 📊 Statistical analysis and visualization
- 📱 Mobile-responsive design
- 🔒 Secure file processing
- 📈 Comprehensive reporting with CSV exports

## 🛠️ Technology Stack

### Backend
- **Python 3.x** - Core application language
- **Flask** - Web framework
- **TensorFlow/Keras** - Machine learning models
- **scikit-learn** - Data preprocessing and ML utilities
- **SimpleITK** - Medical image processing
- **pydicom** - DICOM file handling
- **matplotlib** - Visualization and plotting

### Frontend
- **HTML5/CSS3** - Modern web standards
- **JavaScript (ES6+)** - Interactive functionality
- **Responsive Design** - Mobile-first approach

### Medical Imaging Libraries
- **SimpleITK** - Advanced medical image processing
- **pydicom** - DICOM standard implementation
- **PIL/Pillow** - Image manipulation
- **NumPy** - Numerical computations

## 📋 Prerequisites

### System Requirements
- Python 3.8 or higher
- 4GB+ RAM (8GB recommended for large DICOM datasets)
- 2GB+ free disk space
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Python Dependencies
```bash
Flask>=2.0.0
tensorflow>=2.8.0
scikit-learn>=1.0.0
SimpleITK>=2.1.0
pydicom>=2.3.0
matplotlib>=3.5.0
pandas>=1.4.0
numpy>=1.21.0
Pillow>=9.0.0
```

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/aortec.git
cd aortec
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Create Required Directories
```bash
mkdir uploads processed models data
```

### 5. Set Environment Variables
```bash
# On Windows
set FLASK_APP=app.py
set FLASK_ENV=development

# On macOS/Linux
export FLASK_APP=app.py
export FLASK_ENV=development
```

## ▶️ Running the Application

### Development Mode
```bash
python app.py
```

The application will be available at `http://localhost:5000`

### Production Mode
```bash
# Using Gunicorn (recommended)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Or using Flask's built-in server
flask run --host=0.0.0.0 --port=5000
```

## 📖 Usage Guide

### DICOM File Processing

#### 1. Image Conversion
- Navigate to "Segmentation" → "DICOM to Image Converter"
- Upload single DICOM files or entire folders
- Download converted images individually or as ZIP

#### 2. 3D Viewer Generation
- Go to "Segmentation" → "DICOM 3D Model Viewer"
- Upload a complete DICOM series (folder recommended)
- Generate interactive viewer with measurement rulers
- Navigate through slices using keyboard arrows or buttons

### AI-Powered Analysis

#### 1. Growth Rate Prediction
- Visit "Extensions" → "Predict Rate of Growth"
- Upload Excel/CSV file with patient data
- Required columns: "Current Axial Diameter (mm)", "ILT Volume (mL)"
- Optional: Previous measurements, patient demographics
- Download results with 5-year projections

#### 2. Rupture Risk Assessment
- Go to "Extensions" → "Predict Risk of Rupture"
- Upload patient data with diameter and clinical parameters
- Get risk percentages for current, 1-year, and 5-year timeframes
- Receive detailed patient-specific risk trajectories

### Data Format Requirements

#### Excel/CSV Files
**Required Columns:**
- `Current Axial Diameter (mm)` - Aneurysm size
- `ILT Volume (mL)` - Intraluminal thrombus volume

**Optional Columns:**
- `Patient ID` - Unique identifier
- `Age` - Patient age
- `Gender` - M/F
- `Smoking History` - Yes/No
- `Blood Pressure (mmHg)` - Systolic BP
- `Peak Wall Stress (kPa)` - Biomechanical parameter

#### DICOM Files
- Standard DICOM format (.dcm extension or no extension)
- Complete series recommended for optimal results
- CT scans preferred for AAA analysis

## 🏗️ Project Structure

```
aortec/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── python/               # Core processing modules
│   ├── dicom_processor.py    # DICOM file handling
│   ├── dicom_visualizer.py   # 3D viewer generation
│   ├── growth_rate.py        # Growth prediction AI
│   ├── rupture_risk.py       # Risk assessment AI
│   ├── segmentation.py       # Image segmentation
│   └── model_converter.py    # Model processing
├── static/               # Frontend assets
│   ├── css/                 # Stylesheets
│   ├── js/                  # JavaScript files
│   └── images/              # UI images
├── templates/            # HTML templates
├── uploads/              # Temporary file storage
├── processed/            # Output files
├── models/               # AI model files
└── data/                 # Training datasets
```

## 🔧 Configuration

### Model Training
The AI models can be retrained with new data:

```python
# Growth rate model
from python.growth_rate import train_model
train_model()

# Rupture risk model  
from python.rupture_risk import train_model
train_model(force=True)
```

### File Upload Limits
Modify in `app.py`:
```python
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 * 1024  # 2GB
```

### Processing Thresholds
Adjust in processing functions:
```python
# For 3D model generation
lower_threshold = 100  # HU units
upper_threshold = 300  # HU units
```

## 🐛 Troubleshooting

### Common Issues

**1. DICOM Processing Errors**
- Ensure files are valid DICOM format
- Check file permissions
- Verify complete series for 3D processing

**2. AI Model Loading Issues**
- Run model training if models are missing
- Check Python dependencies
- Ensure sufficient memory for TensorFlow

**3. Large File Upload Problems**
- Increase `MAX_CONTENT_LENGTH` in configuration
- Use folder upload for multiple files
- Consider file compression

**4. Memory Issues**
- Reduce batch size for large datasets
- Process files individually if needed
- Increase system RAM allocation

### Debug Mode
Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Follow PEP 8 style guidelines
4. Add tests for new functionality
5. Update documentation
6. Submit pull request

### Code Style
- Follow PEP 8 conventions
- Use meaningful variable names
- Add docstrings to functions
- Comment complex algorithms

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

### Documentation
- API documentation available at `/docs` when running
- Code documentation in source files
- User guide in `/tutorials` section

### Contact
- **Email**: support@aortec.com
- **Issues**: GitHub Issues tab
- **Discussions**: GitHub Discussions

### Medical Disclaimer
This software is for research and educational purposes. It should not be used as the sole basis for clinical decisions. Always consult qualified healthcare professionals for medical diagnosis and treatment.

## 🙏 Acknowledgments

- Medical imaging community for DICOM standards
- TensorFlow team for machine learning framework
- SimpleITK developers for medical image processing tools
- Flask community for web framework support

## 📊 Citation

If you use AORTEC in your research, please cite:

```bibtex
@software{aortec2024,
  title={AORTEC: Advanced Medical Imaging Analysis Platform},
  author={Your Team},
  year={2024},
  url={https://github.com/your-username/aortec}
}
```

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Compatibility**: Python 3.8+, Modern Browsers
