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
