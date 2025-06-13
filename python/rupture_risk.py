import numpy as np
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
from sklearn.preprocessing import StandardScaler
import joblib
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, Dropout
import time

# Define paths
MODEL_PATH = 'models/rupture_risk_model.h5'
SCALER_PATH = 'models/rupture_risk_scaler.pkl'
GROWTH_MODEL_PATH = 'models/aaa_growth_model.h5'
GROWTH_SCALER_PATH = 'models/aaa_growth_scaler.pkl'

def train_model(force=False):
    """Train the rupture risk prediction model if it doesn't exist already."""
    
    # Check if model already exists
    if not force and os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH):
        print("[INFO] Rupture risk model already exists. Skipping training.")
        return
    
    print("[INFO] Training new rupture risk prediction model...")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    
    try:
        # Create a synthetic dataset for model training
        np.random.seed(42)
        n_samples = 1000
        
        # Generate features
        diameters = np.random.uniform(25, 70, n_samples)  # Axial diameters in mm
        ilt_volumes = np.random.uniform(0, 100, n_samples)  # ILT volumes in mL
        wall_stress = np.random.uniform(50, 250, n_samples)  # Wall stress in kPa
        blood_pressure = np.random.uniform(100, 180, n_samples)  # BP in mmHg
        age = np.random.uniform(50, 85, n_samples)  # Age in years
        smoking = np.random.choice([0, 1], size=n_samples, p=[0.6, 0.4])  # Smoking history
        gender = np.random.choice([0, 1], size=n_samples, p=[0.3, 0.7])  # Gender (more males)
        
        # Define risk logic based on clinical guidelines
        # High risk if diameter > 55mm or wall stress > 180kPa
        rupture_risk = np.zeros(n_samples)
        
        # Base risk component from diameter (highest weight)
        diameter_component = np.clip((diameters - 30) / 30, 0, 1) * 0.6
        
        # Wall stress component
        stress_component = np.clip((wall_stress - 100) / 150, 0, 1) * 0.2
        
        # ILT volume component 
        ilt_component = np.clip(ilt_volumes / 100, 0, 1) * 0.1
        
        # Other factors
        bp_component = np.clip((blood_pressure - 120) / 60, 0, 1) * 0.05
        smoking_component = smoking * 0.03
        age_component = np.clip((age - 50) / 30, 0, 1) * 0.02
        
        # Calculate total risk (binary outcome for training)
        total_risk = diameter_component + stress_component + ilt_component + bp_component + smoking_component + age_component
        rupture_risk = (total_risk > 0.5).astype(int)
        
        # Combine into a dataset
        features = np.column_stack([diameters, ilt_volumes, wall_stress, blood_pressure, age, smoking, gender])
        
        # Train-test split
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(features, rupture_risk, test_size=0.2, random_state=42)
        
        # Normalize input features
        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)
        
        # Save the scaler for later use
        joblib.dump(scaler, SCALER_PATH)
        
        # Build the neural network for binary classification
        model = Sequential([
            Dense(64, activation="relu", input_shape=(features.shape[1],)),
            Dropout(0.2),
            Dense(32, activation="relu"),
            Dropout(0.2),
            Dense(1, activation="sigmoid")  # Binary classification (0=low risk, 1=high risk)
        ])
        
        # Compile the model
        model.compile(optimizer="adam", 
                      loss="binary_crossentropy", 
                      metrics=["accuracy"])
        
        # Train the model
        model.fit(
            X_train, 
            y_train, 
            epochs=100, 
            batch_size=16, 
            validation_data=(X_test, y_test), 
            verbose=0
        )
        
        # Save the model
        model.save(MODEL_PATH)
        print("[INFO] Rupture risk model trained and saved successfully.")
        
    except Exception as e:
        print(f"[ERROR] Failed to train rupture risk model: {str(e)}")
        raise

def train_growth_model(force=False):
    """Train a simplified growth prediction model if it doesn't exist already."""
    
    # Check if model already exists
    if not force and os.path.exists(GROWTH_MODEL_PATH) and os.path.exists(GROWTH_SCALER_PATH):
        print("[INFO] Growth model already exists. Skipping training.")
        return
    
    print("[INFO] Training new AAA growth prediction model...")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(GROWTH_MODEL_PATH), exist_ok=True)
    
    try:
        # Create a synthetic dataset for growth prediction
        np.random.seed(42)
        n_samples = 1000
        
        # Generate features that influence growth
        diameters = np.random.uniform(25, 65, n_samples)
        ilt_volumes = np.random.uniform(0, 100, n_samples)
        
        # Optional features
        wall_stress = np.random.uniform(50, 250, n_samples)
        blood_pressure = np.random.uniform(100, 180, n_samples)
        age = np.random.uniform(50, 85, n_samples)
        smoking = np.random.choice([0, 1], size=n_samples, p=[0.6, 0.4])
        gender = np.random.choice([0, 1], size=n_samples, p=[0.3, 0.7])  # More males than females
        
        # Create growth rates based on influencing factors
        # Base growth related to diameter
        base_growth = 0.1 * np.exp(0.05 * (diameters - 30))
        
        # ILT influence (higher ILT can increase growth)
        ilt_effect = 0.02 * np.sqrt(ilt_volumes)
        
        # Wall stress influence
        stress_effect = 0.01 * (wall_stress / 100)
        
        # Other factors
        bp_effect = 0.005 * ((blood_pressure - 120) / 20)
        age_effect = 0.003 * ((age - 60) / 10)
        smoking_effect = 0.2 * smoking
        gender_effect = 0.1 * gender
        
        # Combine effects with some randomness
        growth_rates = base_growth + ilt_effect + stress_effect + bp_effect + age_effect + smoking_effect + gender_effect
        growth_rates = growth_rates + np.random.normal(0, 0.2, n_samples)  # Add noise
        growth_rates = np.clip(growth_rates, 0, 10)  # Limit to reasonable range
        
        # Create features array
        features = np.column_stack([diameters, ilt_volumes, wall_stress, blood_pressure, age, smoking, gender])
        
        # Train-test split
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(
            features, growth_rates, test_size=0.2, random_state=42
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Save the scaler
        joblib.dump(scaler, GROWTH_SCALER_PATH)
        
        # Build a simple regression model
        model = Sequential([
            Dense(64, activation="relu", input_shape=(features.shape[1],)),
            Dropout(0.2),
            Dense(32, activation="relu"),
            Dropout(0.2),
            Dense(1)  # Regression output
        ])
        
        # Compile
        model.compile(optimizer="adam", loss="mean_squared_error", metrics=["mae"])
        
        # Train
        model.fit(
            X_train_scaled, y_train,
            epochs=100,
            batch_size=16,
            validation_data=(X_test_scaled, y_test),
            verbose=0
        )
        
        # Save model
        model.save(GROWTH_MODEL_PATH)
        print("[INFO] Growth prediction model trained and saved successfully.")
        
    except Exception as e:
        print(f"[ERROR] Failed to train growth model: {str(e)}")
        raise


def load_prediction_models():
    """Load both the rupture risk and growth prediction models"""
    try:
        # First ensure models exist by training if necessary
        train_model()
        train_growth_model()
        
        # Load rupture model and scaler
        rupture_model = load_model(MODEL_PATH, compile=False)  # Add compile=False
        # Manually compile the model with the right loss and metrics
        rupture_model.compile(
            optimizer="adam",
            loss="binary_crossentropy",
            metrics=["accuracy"]
        )
        rupture_scaler = joblib.load(SCALER_PATH)
        
        # Load growth model and scaler
        growth_model = load_model(GROWTH_MODEL_PATH, compile=False)  # Add compile=False
        # Manually compile the growth model with mean_squared_error (not mse)
        growth_model.compile(
            optimizer="adam",
            loss="mean_squared_error",  # Use full name instead of 'mse'
            metrics=["mae"]
        )
        growth_scaler = joblib.load(GROWTH_SCALER_PATH)
        
        return rupture_model, rupture_scaler, growth_model, growth_scaler
    except Exception as e:
        print(f"[ERROR] Failed to load prediction models: {str(e)}")
        # If loading fails, train new models from scratch
        print("[INFO] Training new models from scratch...")
        
        # Remove existing models that might be corrupted
        if os.path.exists(MODEL_PATH):
            os.remove(MODEL_PATH)
        if os.path.exists(GROWTH_MODEL_PATH):
            os.remove(GROWTH_MODEL_PATH)
            
        # Train and save new models
        train_model(force=True)
        train_growth_model(force=True)
        
        # Load the newly created models
        rupture_model = load_model(MODEL_PATH, compile=False)
        rupture_model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
        rupture_scaler = joblib.load(SCALER_PATH)
        
        growth_model = load_model(GROWTH_MODEL_PATH, compile=False)
        growth_model.compile(optimizer="adam", loss="mean_squared_error", metrics=["mae"])
        growth_scaler = joblib.load(GROWTH_SCALER_PATH)
        
        return rupture_model, rupture_scaler, growth_model, growth_scaler

def calculate_rupture_risk(diameter, ilt_volume, wall_stress=None, blood_pressure=None, 
                          age=None, smoking=None, gender=None, model=None, scaler=None):
    """
    Calculate rupture risk percentage based on available patient data.
    
    Args:
        diameter: Axial diameter in mm (required)
        ilt_volume: ILT volume in mL (required)
        wall_stress: Peak wall stress in kPa (optional)
        blood_pressure: Blood pressure in mmHg (optional)
        age: Patient age (optional)
        smoking: Smoking history (Yes/No) (optional)
        gender: Gender (M/F) (optional)
        model: Pre-loaded prediction model (optional)
        scaler: Pre-loaded feature scaler (optional)
        
    Returns:
        float: Rupture risk percentage
    """
    # Load model and scaler if not provided
    if model is None or scaler is None:
        rupture_model, rupture_scaler, _, _ = load_prediction_models()
        model = rupture_model
        scaler = rupture_scaler
    
    # Set default values for missing optional fields
    wall_stress = 150.0 if wall_stress is None else wall_stress
    blood_pressure = 140 if blood_pressure is None else blood_pressure
    age = 65 if age is None else age
    smoking_numeric = 0 if smoking is None else (1 if smoking.lower() in ["yes", "y", "true", "1"] else 0)
    gender_numeric = 1 if gender is None else (1 if gender.lower() in ["m", "male"] else 0)
    
    # Create input data
    input_data = np.array([[
        float(diameter),
        float(ilt_volume),
        float(wall_stress),
        float(blood_pressure),
        float(age),
        smoking_numeric,
        gender_numeric
    ]])
    
    # Scale input
    input_scaled = scaler.transform(input_data)
    
    # Get base prediction from model
    raw_prediction = float(model.predict(input_scaled)[0][0])
    
    # Calculate composite risk score
    # Base model prediction (50%)
    model_component = raw_prediction * 0.5
    
    # Diameter component (30%)
    diameter_component = 0
    if diameter >= 55:  # Critical threshold
        diameter_component = 0.3
    elif diameter >= 50:
        diameter_component = 0.25
    elif diameter >= 45:
        diameter_component = 0.2
    elif diameter >= 40:
        diameter_component = 0.15
    elif diameter >= 35:
        diameter_component = 0.1
    elif diameter >= 30:
        diameter_component = 0.05
    
    # ILT volume component (20%)
    ilt_component = min(0.2, (ilt_volume / 100) * 0.2)
    
    # Combine components
    risk_score = (model_component + diameter_component + ilt_component) * 100
    
    # Ensure risk is between 0-100%
    return min(100, max(0, risk_score))

def predict_growth_rate(diameter, ilt_volume, wall_stress=None, blood_pressure=None, 
                       age=None, smoking=None, gender=None, model=None, scaler=None):
    """
    Predict annual growth rate based on available patient data.
    
    Args:
        diameter: Axial diameter in mm (required)
        ilt_volume: ILT volume in mL (required)
        wall_stress: Peak wall stress in kPa (optional)
        blood_pressure: Blood pressure in mmHg (optional)
        age: Patient age (optional)
        smoking: Smoking history (Yes/No) (optional)
        gender: Gender (M/F) (optional)
        model: Pre-loaded prediction model (optional)
        scaler: Pre-loaded feature scaler (optional)
        
    Returns:
        float: Predicted growth rate in mm/year
    """
    # Load model and scaler if not provided
    if model is None or scaler is None:
        _, _, growth_model, growth_scaler = load_prediction_models()
        model = growth_model
        scaler = growth_scaler
    
    # Set default values for missing optional fields
    wall_stress = 150.0 if wall_stress is None else wall_stress
    blood_pressure = 140 if blood_pressure is None else blood_pressure
    age = 65 if age is None else age
    smoking_numeric = 0 if smoking is None else (1 if smoking.lower() in ["yes", "y", "true", "1"] else 0)
    gender_numeric = 1 if gender is None else (1 if gender.lower() in ["m", "male"] else 0)
    
    # Create input data
    input_data = np.array([[
        float(diameter),
        float(ilt_volume),
        float(wall_stress),
        float(blood_pressure),
        float(age),
        smoking_numeric,
        gender_numeric
    ]])
    
    # Scale input
    input_scaled = scaler.transform(input_data)
    
    # Get prediction from model
    predicted_growth = float(model.predict(input_scaled)[0][0])
    
    # Ensure growth rate is non-negative and reasonable
    return max(0, min(10, predicted_growth))

def risk_category(risk_percentage):
    """Determine risk category based on risk percentage"""
    if risk_percentage < 15:
        return "Low"
    elif risk_percentage < 35:
        return "Moderate"
    elif risk_percentage < 65:
        return "High"
    else:
        return "Very High"

def predict_rupture_risk_from_excel(excel_path, output_dir):
    """
    Process patient data from Excel file and predict rupture risk over time.
    Handles both minimal data (diameter + ILT volume) and more complete patient data.
    
    Args:
        excel_path: Path to Excel file with patient data
        output_dir: Directory to save results
    
    Returns:
        dict: Dictionary with prediction results and visualization paths
    """
    try:
        print(f"[INFO] Processing rupture risk predictions from: {excel_path}")
        
        # Load prediction models
        rupture_model, rupture_scaler, growth_model, growth_scaler = load_prediction_models()
        
        # Load data from Excel
        if excel_path.endswith('.csv'):
            df = pd.read_csv(excel_path)
        else:
            df = pd.read_excel(excel_path)
        
        print(f"[INFO] Loaded {len(df)} records from file")
        
        # Map column names to expected format if needed (handle variations in column names)
        column_mapping = {
            "AneurysmSize": "Axial Diameter (mm)",
            "Diameter": "Axial Diameter (mm)",
            "AxialDiameter": "Axial Diameter (mm)",
            "AAA_Size": "Axial Diameter (mm)",
            "ILT_Volume": "ILT Volume (mL)",
            "Wall_Stress": "Peak Wall Stress (kPa)",
            "WallStress": "Peak Wall Stress (kPa)",
            "BP": "Blood Pressure (mmHg)",
            "BloodPressure": "Blood Pressure (mmHg)",
            "Smoking": "Smoking History",
            "PatientID": "Patient ID",
            "ID": "Patient ID"
        }
        
        for original, target in column_mapping.items():
            if original in df.columns and target not in df.columns:
                df[target] = df[original]
        
        # Check for required columns
        required_columns = ["Axial Diameter (mm)", "ILT Volume (mL)"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return {"error": f"Missing required columns: {', '.join(missing_columns)}"}
        
        # Add Patient ID if missing (use row index)
        if "Patient ID" not in df.columns:
            df["Patient ID"] = [f"P{i+1:03d}" for i in range(len(df))]
            
        # Convert categorical variables to numeric if present
        if "Smoking History" in df.columns:
            df["Smoking_Numeric"] = df["Smoking History"].map(
                {"Yes": 1, "No": 0, "yes": 1, "no": 0, "Y": 1, "N": 0, "y": 1, "n": 0})
        else:
            df["Smoking_Numeric"] = 0  # Default if not provided
            df["Smoking History"] = "No"  # For display purposes
            
        if "Gender" in df.columns:
            df["Gender_Numeric"] = df["Gender"].map(
                {"M": 1, "F": 0, "m": 1, "f": 0, "Male": 1, "Female": 0, "male": 1, "female": 0})
        else:
            df["Gender_Numeric"] = 1  # Default to male (more common for AAA)
            df["Gender"] = "M"  # For display purposes
            
        # Add default values for other optional columns if missing
        if "Peak Wall Stress (kPa)" not in df.columns:
            # Estimate wall stress from diameter (simplified relationship)
            df["Peak Wall Stress (kPa)"] = df["Axial Diameter (mm)"] * 3
            
        if "Blood Pressure (mmHg)" not in df.columns:
            df["Blood Pressure (mmHg)"] = 140  # Default value
            
        if "Age" not in df.columns:
            df["Age"] = 65  # Default value
        
        # Calculate current rupture risk for each patient
        df["Current Risk (%)"] = df.apply(
            lambda row: calculate_rupture_risk(
                row["Axial Diameter (mm)"],
                row["ILT Volume (mL)"],
                row["Peak Wall Stress (kPa)"],
                row["Blood Pressure (mmHg)"],
                row["Age"],
                "Yes" if "Smoking_Numeric" in row and row["Smoking_Numeric"] == 1 else "No",
                "M" if "Gender_Numeric" in row and row["Gender_Numeric"] == 1 else "F",
                rupture_model,
                rupture_scaler
            ),
            axis=1
        )
        
        # Calculate growth rate for each patient
        df["Growth Rate (mm/year)"] = df.apply(
            lambda row: predict_growth_rate(
                row["Axial Diameter (mm)"],
                row["ILT Volume (mL)"],
                row["Peak Wall Stress (kPa)"],
                row["Blood Pressure (mmHg)"],
                row["Age"],
                "Yes" if "Smoking_Numeric" in row and row["Smoking_Numeric"] == 1 else "No",
                "M" if "Gender_Numeric" in row and row["Gender_Numeric"] == 1 else "F",
                growth_model,
                growth_scaler
            ),
            axis=1
        )
        
        # Calculate predicted diameter at future time points
        df["Diameter at 1 Year (mm)"] = df["Axial Diameter (mm)"] + df["Growth Rate (mm/year)"]
        df["Diameter at 5 Years (mm)"] = df["Axial Diameter (mm)"] + (df["Growth Rate (mm/year)"] * 5)
        
        # Calculate risk at future time points
        df["Risk at 1 Year (%)"] = df.apply(
            lambda row: calculate_rupture_risk(
                row["Diameter at 1 Year (mm)"],
                row["ILT Volume (mL)"],  # ILT might also grow but using current value as simplification
                row["Peak Wall Stress (kPa)"], 
                row["Blood Pressure (mmHg)"],
                row["Age"] + 1 if "Age" in df.columns else 66,
                "Yes" if "Smoking_Numeric" in row and row["Smoking_Numeric"] == 1 else "No",
                "M" if "Gender_Numeric" in row and row["Gender_Numeric"] == 1 else "F",
                rupture_model,
                rupture_scaler
            ),
            axis=1
        )
        
        df["Risk at 5 Years (%)"] = df.apply(
            lambda row: calculate_rupture_risk(
                row["Diameter at 5 Years (mm)"],
                row["ILT Volume (mL)"],  # Simplified - using current ILT
                row["Peak Wall Stress (kPa)"],
                row["Blood Pressure (mmHg)"],
                row["Age"] + 5 if "Age" in df.columns else 70,
                "Yes" if "Smoking_Numeric" in row and row["Smoking_Numeric"] == 1 else "No",
                "M" if "Gender_Numeric" in row and row["Gender_Numeric"] == 1 else "F",
                rupture_model,
                rupture_scaler
            ),
            axis=1
        )
        
        # Determine risk categories
        df["Current Risk Category"] = df["Current Risk (%)"].apply(risk_category)
        df["Risk Category at 1 Year"] = df["Risk at 1 Year (%)"].apply(risk_category)
        df["Risk Category at 5 Years"] = df["Risk at 5 Years (%)"].apply(risk_category)
        
        # Create results directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate timestamp for unique filenames
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        
        # Save detailed results to CSV
        results_path = os.path.join(output_dir, f"rupture_risk_predictions_{timestamp}.csv")
        df.to_csv(results_path, index=False)
        
        # Create visualization of risk progression over time
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))
        
        # Prepare data for plotting
        patients = df["Patient ID"].values
        current_risks = df["Current Risk (%)"].values
        risk_1yr = df["Risk at 1 Year (%)"].values
        risk_5yr = df["Risk at 5 Years (%)"].values
        
        # Set width of bars
        bar_width = 0.25
        
        # Set position of bars on x axis
        r1 = np.arange(len(patients))
        r2 = [x + bar_width for x in r1]
        r3 = [x + bar_width for x in r2]
        
        # Make the plot - limit to 15 patients max for readability
        plot_limit = min(15, len(patients))
        
        # Determine if we need to show all patients or a subset
        if len(patients) > plot_limit:
            # Sort by current risk and take top and bottom patients
            sorted_indices = np.argsort(current_risks)
            # Take some low risk and some high risk patients
            selected_indices = np.concatenate([
                sorted_indices[:plot_limit//3],  # Low risk
                sorted_indices[-(plot_limit - plot_limit//3):]  # High risk
            ])
            # Sort back by patient ID for display
            selected_indices = sorted(selected_indices)
            
            plot_patients = patients[selected_indices]
            plot_current = current_risks[selected_indices]
            plot_1yr = risk_1yr[selected_indices]
            plot_5yr = risk_5yr[selected_indices]
            
            plot_r1 = np.arange(len(plot_patients))
            plot_r2 = [x + bar_width for x in plot_r1]
            plot_r3 = [x + bar_width for x in plot_r2]
            
            bars1 = ax1.bar(plot_r1, plot_current, width=bar_width, label='Current')
            bars2 = ax1.bar(plot_r2, plot_1yr, width=bar_width, label='After 1 Year')
            bars3 = ax1.bar(plot_r3, plot_5yr, width=bar_width, label='After 5 Years')
            
            # Add note about showing subset of patients
            ax1.text(0.5, -0.1, f"Showing a subset of {plot_limit} patients out of {len(patients)} total",
                    ha='center', va='center', transform=ax1.transAxes, fontsize=10, fontstyle='italic')
            
            # Add some text for labels, title and x-axis ticks
            ax1.set_xlabel('Patient ID')
            ax1.set_ylabel('Rupture Risk (%)')
            ax1.set_title('Rupture Risk Progression Over Time')
            ax1.set_xticks([r + bar_width for r in range(len(plot_patients))])
            ax1.set_xticklabels(plot_patients, rotation=45, ha='right')
            
        else:
            # Plot all patients
            bars1 = ax1.bar(r1, current_risks, width=bar_width, label='Current')
            bars2 = ax1.bar(r2, risk_1yr, width=bar_width, label='After 1 Year')
            bars3 = ax1.bar(r3, risk_5yr, width=bar_width, label='After 5 Years')
            
            # Add some text for labels, title and x-axis ticks
            ax1.set_xlabel('Patient ID')
            ax1.set_ylabel('Rupture Risk (%)')
            ax1.set_title('Rupture Risk Progression Over Time')
            ax1.set_xticks([r + bar_width for r in range(len(patients))])
            ax1.set_xticklabels(patients, rotation=45, ha='right')
        
        # Add legend
        ax1.legend()
        
        # Set y-axis limit
        ax1.set_ylim(0, 100)
        
        # Add grid
        ax1.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Second plot - Risk category distribution over time
        # Count patients in each category
        current_categories = df["Current Risk Category"].value_counts()
        yr1_categories = df["Risk Category at 1 Year"].value_counts()
        yr5_categories = df["Risk Category at 5 Years"].value_counts()
        
        # Ensure all categories are represented
        all_categories = ["Low", "Moderate", "High", "Very High"]
        for cat in all_categories:
            if cat not in current_categories:
                current_categories[cat] = 0
            if cat not in yr1_categories:
                yr1_categories[cat] = 0
            if cat not in yr5_categories:
                yr5_categories[cat] = 0
        
        # Sort by severity
        current_counts = [current_categories.get(cat, 0) for cat in all_categories]
        yr1_counts = [yr1_categories.get(cat, 0) for cat in all_categories]
        yr5_counts = [yr5_categories.get(cat, 0) for cat in all_categories]
        
        # Set width of bars
        bar_width = 0.25
        
        # Set position of bars on x axis
        r1 = np.arange(len(all_categories))
        r2 = [x + bar_width for x in r1]
        r3 = [x + bar_width for x in r2]
        
        # Make the plot
        bars1 = ax2.bar(r1, current_counts, width=bar_width, label='Current')
        bars2 = ax2.bar(r2, yr1_counts, width=bar_width, label='After 1 Year')
        bars3 = ax2.bar(r3, yr5_counts, width=bar_width, label='After 5 Years')
        
        # Add some text for labels, title and x-axis ticks
        ax2.set_xlabel('Risk Category')
        ax2.set_ylabel('Number of Patients')
        ax2.set_title('Risk Category Distribution Over Time')
        ax2.set_xticks([r + bar_width for r in range(len(all_categories))])
        ax2.set_xticklabels(all_categories)
        
        # Add legend
        ax2.legend()
        
        # Add grid
        ax2.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Add data labels on bars
        def add_labels(bars):
            for bar in bars:
                height = bar.get_height()
                if height > 0:  # Only add label if bar has height
                    ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                            f'{int(height)}', ha='center', va='bottom')
                            
        add_labels(bars1)
        add_labels(bars2)
        add_labels(bars3)
        
        # Tight layout and save
        plt.tight_layout()
        plot_path = os.path.join(output_dir, f"rupture_risk_progression_{timestamp}.png")
        plt.savefig(plot_path)
        plt.close()
        
        # Create second visualization - patient-specific progression charts
        # Choose up to 4 patients to showcase detailed progression
        patient_count = min(4, len(df))
        if len(df) > patient_count:
            # Get a mix of different risk levels
            risk_sorted = df.sort_values("Current Risk (%)")
            sample_indices = [
                int(i * len(df) / patient_count) for i in range(patient_count)
            ]
            selected_patients = risk_sorted.iloc[sample_indices]
        else:
            selected_patients = df
        
        # Create individual patient charts
        fig, axes = plt.subplots(1, patient_count, figsize=(15, 5))
        if patient_count == 1:
            axes = [axes]  # Make axes iterable if only one subplot
            
        for i, (_, patient) in enumerate(selected_patients.iterrows()):
            # Get patient data
            patient_id = patient["Patient ID"]
            risks = [
                patient["Current Risk (%)"],
                patient["Risk at 1 Year (%)"],
                patient["Risk at 5 Years (%)"]
            ]
            diameters = [
                patient["Axial Diameter (mm)"],
                patient["Diameter at 1 Year (mm)"],
                patient["Diameter at 5 Years (mm)"]
            ]
            
            # Plot risk progression
            color = 'green' if risks[0] < 35 else 'orange' if risks[0] < 65 else 'red'
            axes[i].plot([0, 1, 5], risks, marker='o', color=color, linewidth=2)
            
            # Add threshold lines
            axes[i].axhline(y=35, color='orange', linestyle='--', alpha=0.5, label='Moderate Risk')
            axes[i].axhline(y=65, color='red', linestyle='--', alpha=0.5, label='High Risk')
            
            # Add current diameter info
            for j, (year, risk, diameter) in enumerate(zip([0, 1, 5], risks, diameters)):
                axes[i].annotate(f"{diameter:.1f}mm", 
                                xy=(year, risk), 
                                xytext=(0, 10), 
                                textcoords='offset points',
                                ha='center')
            
            # Set labels and title
            axes[i].set_xlabel('Years')
            if i == 0:
                axes[i].set_ylabel('Rupture Risk (%)')
            axes[i].set_title(f"Patient {patient_id}")
            
            # Set x and y limits
            axes[i].set_xlim(-0.5, 5.5)
            axes[i].set_ylim(0, 100)
            
            # Add risk category labels on y-axis
            axes[i].text(-0.5, 17.5, "Low", va='center', ha='center', 
                         bbox=dict(facecolor='green', alpha=0.2))
            axes[i].text(-0.5, 50, "Moderate", va='center', ha='center', 
                         bbox=dict(facecolor='orange', alpha=0.2))
            axes[i].text(-0.5, 82.5, "High", va='center', ha='center', 
                         bbox=dict(facecolor='red', alpha=0.2))
        
        # Add overall title
        fig.suptitle("Patient-Specific AAA Rupture Risk Progression", fontsize=16)
        plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust for suptitle
        
        # Save the plot
        patient_plot_path = os.path.join(output_dir, f"patient_risk_progression_{timestamp}.png")
        plt.savefig(patient_plot_path)
        plt.close()
        
        # Prepare summary statistics
        stats = {
            "avg_current_risk": float(df["Current Risk (%)"].mean()),
            "max_current_risk": float(df["Current Risk (%)"].max()),
            "avg_risk_1yr": float(df["Risk at 1 Year (%)"].mean()),
            "avg_risk_5yr": float(df["Risk at 5 Years (%)"].mean()),
            "patient_count": len(df),
            "high_risk_current": len(df[df["Current Risk Category"].isin(["High", "Very High"])]),
            "high_risk_1yr": len(df[df["Risk Category at 1 Year"].isin(["High", "Very High"])]),
            "high_risk_5yr": len(df[df["Risk Category at 5 Years"].isin(["High", "Very High"])]),
            "low_risk_current": len(df[df["Current Risk Category"] == "Low"]),
            "moderate_risk_current": len(df[df["Current Risk Category"] == "Moderate"])
        }
        
        # Calculate progression metrics
        risk_increases = (df["Risk at 5 Years (%)"] - df["Current Risk (%)"]).values
        stats["avg_risk_increase_5yr"] = float(np.mean(risk_increases))
        stats["pct_significant_increase"] = float(len(risk_increases[risk_increases > 20]) / len(risk_increases) * 100)
        
        # Calculate percentage of patients who progress to high risk
        current_low_mod = df[df["Current Risk Category"].isin(["Low", "Moderate"])]
        if len(current_low_mod) > 0:
            progressed = current_low_mod[current_low_mod["Risk Category at 5 Years"].isin(["High", "Very High"])]
            stats["pct_progress_to_high"] = float(len(progressed) / len(current_low_mod) * 100)
        else:
            stats["pct_progress_to_high"] = 0.0
        
        return {
            "success": True,
            "message": f"Processed {len(df)} patient records successfully.",
            "results_csv": results_path,
            "visualization": plot_path,
            "patient_visualization": patient_plot_path,
            "statistics": stats,
            "detailed_results": df.to_dict(orient="records")
        }
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[ERROR] Failed to process rupture risk prediction: {str(e)}\n{error_details}")
        return {"error": str(e)}

def predict_rupture_risk_from_input(diameter, ilt_volume, wall_stress=None, blood_pressure=None, 
                                   age=None, smoking=None, gender=None, output_dir=None):
    """
    Predict rupture risk based on manual user input.
    
    Args:
        diameter: Axial diameter in mm
        ilt_volume: Intraluminal thrombus volume in mL
        wall_stress: Peak wall stress in kPa
        blood_pressure: Blood pressure in mmHg
        age: Patient age
        smoking: Smoking history (Yes/No)
        gender: Gender (M/F)
        output_dir: Directory to save results
    
    Returns:
        dict: Dictionary with prediction results and visualization path
    """
    try:
        # Load prediction models
        rupture_model, rupture_scaler, growth_model, growth_scaler = load_prediction_models()
        
        # Set default values for missing optional parameters
        wall_stress = wall_stress or diameter * 3  # Estimated relationship
        blood_pressure = blood_pressure or 140
        age = age or 65
        smoking_value = 1 if smoking and smoking.lower() in ["yes", "y", "true", "1"] else 0
        gender_value = 1 if not gender or gender.lower() in ["m", "male"] else 0
        
        # Calculate current risk
        current_risk = calculate_rupture_risk(
            diameter, ilt_volume, wall_stress, blood_pressure, 
            age, smoking, gender, rupture_model, rupture_scaler
        )
        
        # Predict growth rate
        growth_rate = predict_growth_rate(
            diameter, ilt_volume, wall_stress, blood_pressure,
            age, smoking, gender, growth_model, growth_scaler
        )
        
        # Calculate future diameters and risks
        diameter_1yr = diameter + growth_rate
        diameter_5yr = diameter + (growth_rate * 5)
        
        risk_1yr = calculate_rupture_risk(
            diameter_1yr, ilt_volume, wall_stress, blood_pressure,
            age + 1, smoking, gender, rupture_model, rupture_scaler
        )
        
        risk_5yr = calculate_rupture_risk(
            diameter_5yr, ilt_volume, wall_stress, blood_pressure,
            age + 5, smoking, gender, rupture_model, rupture_scaler
        )
        
        # Determine risk categories
        current_category = risk_category(current_risk)
        category_1yr = risk_category(risk_1yr)
        category_5yr = risk_category(risk_5yr)
        
        # Create data dictionary for a single patient
        data = {
            "Patient ID": "P001",
            "Axial Diameter (mm)": diameter,
            "ILT Volume (mL)": ilt_volume,
            "Peak Wall Stress (kPa)": wall_stress,
            "Blood Pressure (mmHg)": blood_pressure,
            "Age": age,
            "Smoking History": "Yes" if smoking_value == 1 else "No",
            "Gender": "M" if gender_value == 1 else "F",
            "Current Risk (%)": current_risk,
            "Risk at 1 Year (%)": risk_1yr,
            "Risk at 5 Years (%)": risk_5yr,
            "Growth Rate (mm/year)": growth_rate,
            "Diameter at 1 Year (mm)": diameter_1yr,
            "Diameter at 5 Years (mm)": diameter_5yr,
            "Current Risk Category": current_category,
            "Risk Category at 1 Year": category_1yr,
            "Risk Category at 5 Years": category_5yr
        }
        
        # Convert to DataFrame for visualization
        df = pd.DataFrame([data])
        
        # Create output directory if provided
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate timestamp for unique filenames
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            
            # Save results to CSV
            results_path = os.path.join(output_dir, f"rupture_risk_prediction_{timestamp}.csv")
            df.to_csv(results_path, index=False)
            
            # Create visualization - patient risk progression 
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Plot risk progression over time
            years = [0, 1, 5]
            risks = [current_risk, risk_1yr, risk_5yr]
            
            # Choose color based on current risk
            color = 'green' if current_risk < 35 else 'orange' if current_risk < 65 else 'red'
            
            # Plot risk progression
            ax.plot(years, risks, marker='o', color=color, linewidth=2, label='Rupture Risk')
            
            # Add annotations for each point
            for i, (year, risk, diam) in enumerate(zip(years, risks, [diameter, diameter_1yr, diameter_5yr])):
                ax.annotate(f"{risk:.1f}%\n{diam:.1f}mm", 
                          xy=(year, risk), 
                          xytext=(0, 10),
                          textcoords="offset points",
                          ha='center')
            
            # Add threshold lines
            ax.axhline(y=35, color='orange', linestyle='--', alpha=0.5, label='Moderate Risk Threshold')
            ax.axhline(y=65, color='red', linestyle='--', alpha=0.5, label='High Risk Threshold')
            
            # Set labels and title
            ax.set_xlabel('Years from Now')
            ax.set_ylabel('Rupture Risk (%)')
            ax.set_title(f'AAA Rupture Risk Progression Over Time\nGrowth Rate: {growth_rate:.2f} mm/year')
            
            # Set axis limits and ticks
            ax.set_xlim(-0.5, 5.5)
            ax.set_ylim(0, 100)
            ax.set_xticks(years)
            ax.set_xticklabels(['Current', '1 Year', '5 Years'])
            
            # Add grid
            ax.grid(True, linestyle='--', alpha=0.7)
            
            # Add legend
            ax.legend(loc='upper left')
            
            # Add risk categories on the right side
            for y_pos, cat, cat_color in zip([17.5, 50, 82.5], 
                                            ['Low Risk', 'Moderate Risk', 'High Risk'],
                                            ['green', 'orange', 'red']):
                ax.text(5.2, y_pos, cat, va='center', ha='left', fontweight='bold',
                      color=cat_color)
            
            # Save the plot
            plot_path = os.path.join(output_dir, f"risk_progression_{timestamp}.png")
            plt.tight_layout()
            plt.savefig(plot_path, dpi=100)
            plt.close()
            
            # Create results structure
            return {
                "success": True,
                "message": "Rupture risk prediction completed successfully.",
                "current_risk": current_risk,
                "risk_1yr": risk_1yr,
                "risk_5yr": risk_5yr,
                "growth_rate": growth_rate,
                "current_category": current_category,
                "category_5yr": category_5yr,
                "visualization": plot_path,
                "results_csv": results_path,
                "patient_data": data
            }
        else:
            # Just return the results without saving files
            return {
                "success": True,
                "message": "Rupture risk prediction completed successfully.",
                "current_risk": current_risk,
                "risk_1yr": risk_1yr,
                "risk_5yr": risk_5yr,
                "growth_rate": growth_rate,
                "current_category": current_category,
                "category_5yr": category_5yr,
                "patient_data": data
            }
            
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[ERROR] Failed to process rupture risk prediction: {str(e)}\n{error_details}")
        return {"error": str(e)}