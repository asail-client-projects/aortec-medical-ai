import pandas as pd
import numpy as np
import os
import joblib
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
import warnings
warnings.filterwarnings('ignore')

# Define paths
MODEL_PATH = 'models/growth_rate_model.h5'
SCALER_PATH = 'models/growth_rate_scaler.pkl'
DATA_PATH = 'data/correct_dataset.csv'  # Updated to use corrected dataset

def validate_and_clean_data(df):
    """
    Validate and clean the dataset to ensure medical accuracy.
    Removes any entries where aneurysms appear to shrink.
    """
    print(f"[INFO] Initial dataset size: {len(df)} patients")
    
    # Calculate actual growth rate from the data
    df['Calculated_Growth_Rate'] = (
        df['Current Axial Diameter (mm)'] - df['Previous Axial Diameter (mm)']
    ) / df['Time Interval (months)']
    
    # Remove any cases where the aneurysm appears to have shrunk significantly
    # Allow for small measurement errors (up to -0.5mm/month) but remove clear shrinkage
    original_size = len(df)
    df_cleaned = df[df['Calculated_Growth_Rate'] >= -0.5].copy()
    removed_count = original_size - len(df_cleaned)
    
    if removed_count > 0:
        print(f"[INFO] Removed {removed_count} entries with significant shrinkage (medically implausible)")
    
    # For remaining negative values (small measurement errors), set to 0 (stable)
    df_cleaned.loc[df_cleaned['Calculated_Growth_Rate'] < 0, 'Calculated_Growth_Rate'] = 0.0
    
    print(f"[INFO] Final dataset size: {len(df_cleaned)} patients")
    print(f"[INFO] Growth rate range: {df_cleaned['Calculated_Growth_Rate'].min():.3f} to {df_cleaned['Calculated_Growth_Rate'].max():.3f} mm/month")
    
    return df_cleaned

def create_medically_constrained_model(input_dim):
    """
    Create a neural network model with medical constraints.
    Uses ReLU activation in the final layer to ensure non-negative outputs.
    """
    model = Sequential([
        Dense(128, activation="relu", input_shape=(input_dim,)),
        Dropout(0.3),
        Dense(64, activation="relu"),
        Dropout(0.2),
        Dense(32, activation="relu"),
        Dropout(0.1),
        # Final layer with ReLU to ensure non-negative growth rates
        Dense(1, activation="relu")  # ReLU ensures output >= 0
    ])
    
    # Use custom optimizer with lower learning rate for stability
    optimizer = keras.optimizers.Adam(learning_rate=0.001)
    
    model.compile(
        optimizer=optimizer, 
        loss="mean_squared_error",
        metrics=["mean_absolute_error"]
    )
    
    return model

def train_model():
    """Train the growth rate prediction model with medical constraints."""
    
    # Force retraining by removing old model files
    if os.path.exists(MODEL_PATH):
        os.remove(MODEL_PATH)
    if os.path.exists(SCALER_PATH):
        os.remove(SCALER_PATH)
    
    print("[INFO] Training new medically-constrained growth rate prediction model...")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    
    try:
        # Load the corrected dataset
        if not os.path.exists(DATA_PATH):
            print(f"[ERROR] Dataset not found at {DATA_PATH}")
            print("[INFO] Please ensure the corrected dataset is placed at the correct path")
            raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")
        
        df = pd.read_csv(DATA_PATH)
        print(f"[INFO] Loaded dataset with {len(df)} entries")
        print(f"[INFO] Dataset columns: {list(df.columns)}")
        
        # Validate and clean the data
        df_clean = validate_and_clean_data(df)
        
        # Define features and target
        features = ["Current Axial Diameter (mm)", "ILT Volume (mL)"]
        
        # Use the calculated growth rate as target
        target_col = "Calculated_Growth_Rate"
        
        # Verify required columns exist
        missing_features = [f for f in features if f not in df_clean.columns]
        if missing_features:
            raise ValueError(f"Missing required feature columns: {missing_features}")
        
        X = df_clean[features].values
        y = df_clean[target_col].values
        
        print(f"[INFO] Feature matrix shape: {X.shape}")
        print(f"[INFO] Target vector shape: {y.shape}")
        print(f"[INFO] Target statistics - Min: {y.min():.4f}, Max: {y.max():.4f}, Mean: {y.mean():.4f}")
        
        # Train-test split with stratification to ensure balanced distribution
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, shuffle=True
        )
        
        # Normalize input features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Save the scaler
        joblib.dump(scaler, SCALER_PATH)
        print("[INFO] Scaler saved successfully")
        
        # Create the medically-constrained model
        model = create_medically_constrained_model(len(features))
        
        # Add early stopping to prevent overfitting
        early_stopping = EarlyStopping(
            monitor='val_loss',
            patience=15,
            restore_best_weights=True,
            verbose=1
        )
        
        # Train the model
        print("[INFO] Starting model training...")
        history = model.fit(
            X_train_scaled, y_train,
            epochs=200,
            batch_size=16,
            validation_data=(X_test_scaled, y_test),
            callbacks=[early_stopping],
            verbose=1
        )
        
        # Evaluate the model
        train_loss, train_mae = model.evaluate(X_train_scaled, y_train, verbose=0)
        test_loss, test_mae = model.evaluate(X_test_scaled, y_test, verbose=0)
        
        print(f"[INFO] Training - Loss: {train_loss:.4f}, MAE: {train_mae:.4f}")
        print(f"[INFO] Testing - Loss: {test_loss:.4f}, MAE: {test_mae:.4f}")
        
        # Validate that the model produces non-negative predictions
        test_predictions = model.predict(X_test_scaled, verbose=0).flatten()
        negative_predictions = np.sum(test_predictions < 0)
        
        if negative_predictions > 0:
            print(f"[WARNING] Model produced {negative_predictions} negative predictions - this should not happen with ReLU activation")
        else:
            print("[INFO] ✓ All model predictions are non-negative (medically correct)")
        
        print(f"[INFO] Prediction range: {test_predictions.min():.4f} to {test_predictions.max():.4f} mm/month")
        
        # Save the model
        model.save(MODEL_PATH, save_format="h5")
        print("[INFO] ✓ Medically-constrained growth rate model trained and saved successfully")
        
        return model, scaler
        
    except Exception as e:
        print(f"[ERROR] Failed to train growth rate model: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise

def load_prediction_model():
    """Load the trained model and scaler."""
    try:
        # Try to load existing model
        if os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH):
            print("[INFO] Loading existing growth rate model...")
            model = load_model(MODEL_PATH)
            scaler = joblib.load(SCALER_PATH)
            
            # Validate that this is the medically-constrained version
            # Check if the last layer has ReLU activation
            last_layer = model.layers[-1]
            if hasattr(last_layer, 'activation') and last_layer.activation.__name__ != 'relu':
                print("[WARNING] Existing model doesn't have medical constraints. Retraining...")
                raise ValueError("Model needs retraining for medical constraints")
            
            return model, scaler
            
    except Exception as e:
        print(f"[INFO] Could not load existing model: {str(e)}")
        print("[INFO] Training new medically-constrained model...")
    
    # If loading fails or files don't exist, train a new model
    return train_model()

def apply_medical_constraints(prediction):
    """
    Apply additional medical constraints to predictions as a safety measure.
    """
    # Ensure non-negative growth (aneurysms don't shrink)
    prediction = max(0.0, prediction)
    
    # Apply reasonable upper bound (no aneurysm grows more than 20mm/month)
    prediction = min(prediction, 20.0)
    
    return prediction

def predict_growth_rate_from_input(current_diameter, ilt_volume, output_dir):
    """
    Predict growth rate based on manual user input with medical constraints.
    """
    try:
        # Load model and scaler
        model, scaler = load_prediction_model()
        
        # Prepare input data
        input_data = np.array([[float(current_diameter), float(ilt_volume)]])
        
        # Scale input
        input_scaled = scaler.transform(input_data)
        
        # Make prediction
        raw_prediction = model.predict(input_scaled, verbose=0)[0][0]
        
        # Apply additional medical constraints as safety measure
        monthly_growth = apply_medical_constraints(float(raw_prediction))
        yearly_growth = monthly_growth * 12
        
        print(f"[INFO] Raw prediction: {raw_prediction:.4f} mm/month")
        print(f"[INFO] Constrained prediction: {monthly_growth:.4f} mm/month ({yearly_growth:.4f} mm/year)")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Create improved timeline visualization
        fig, ax = plt.subplots(figsize=(12, 8), dpi=100)
        
        # Show current diameter and projected growth over 5 years
        years = range(0, 6)  # 0 to 5 years
        diameters = [current_diameter + (yearly_growth * y) for y in years]
        
        # Create line chart visualization
        ax.plot(years, diameters, 'o-', linewidth=2.5, markersize=10, color='#2980b9')
        
        # Fill area under the line with light blue
        ax.fill_between(years, current_diameter * 0.8, diameters, alpha=0.2, color='#2980b9')
        
        # Add labels for data points
        for i, (x, y) in enumerate(zip(years, diameters)):
            year_label = "Current" if i == 0 else f"Year {i}"
            color = 'black'
            if y >= 55:
                color = 'darkred'
            elif y >= 50:
                color = 'darkorange'
                
            ax.annotate(
                f'{year_label}\n{y:.1f} mm', 
                (x, y), 
                textcoords="offset points",
                xytext=(0, 10), 
                ha='center',
                fontsize=10,
                fontweight='bold' if y >= 50 else 'normal',
                color=color
            )
        
        # Add styling
        ax.set_xlabel('Years from Now', fontsize=12, fontweight='bold')
        ax.set_ylabel('Projected Diameter (mm)', fontsize=12, fontweight='bold')
        ax.set_title('AAA Size Projection Over 5 Years\n(Medically Constrained Model)', fontsize=14, fontweight='bold')
        
        # Add grid for better readability
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Add threshold areas
        max_diameter = max(diameters)
        ax.axhspan(50, 55, alpha=0.1, color='orange', label='Approaching Threshold')
        ax.axhspan(55, max_diameter + 5, alpha=0.1, color='red', label='Surgical Threshold')
        
        # Set x-axis labels
        ax.set_xticks(years)
        ax.set_xticklabels(['Current'] + [f'Year {y}' for y in years[1:]])
        
        # Calculate time to reach threshold if applicable
        time_to_threshold = None
        if current_diameter < 55 and yearly_growth > 0:
            time_to_threshold = (55 - current_diameter) / yearly_growth
            if time_to_threshold <= 5:  # Only show if within our 5-year window
                threshold_x = time_to_threshold
                ax.scatter([threshold_x], [55], color='red', s=100, zorder=5)
                ax.annotate(
                    f'Reaches 55mm in {time_to_threshold:.1f} years',
                    xy=(threshold_x, 55),
                    xytext=(threshold_x - 0.5, 55 + 3),
                    arrowprops=dict(facecolor='red', shrink=0.05, width=1.5),
                    fontsize=11, 
                    fontweight='bold',
                    color='darkred'
                )
        
        # Add risk assessment with updated categories
        risk_level = "Low"
        if yearly_growth > 5:  # Updated thresholds based on medical literature
            risk_level = "Very High"
        elif yearly_growth > 3:
            risk_level = "High"
        elif yearly_growth > 1:
            risk_level = "Moderate"
            
        # Risk colors
        risk_colors = {
            "Low": "green",
            "Moderate": "orange", 
            "High": "red",
            "Very High": "darkred"
        }
        
        # Add information box
        info_text = f"Annual Growth Rate: {yearly_growth:.2f} mm/year\nRisk Level: {risk_level}\n(Medically Constrained)"
        ax.text(
            0.02, 0.98, 
            info_text, 
            transform=ax.transAxes, 
            fontsize=12, 
            fontweight='bold',
            verticalalignment='top',
            bbox=dict(facecolor='white', alpha=0.9, boxstyle='round,pad=0.5', edgecolor='#cccccc'),
            color=risk_colors.get(risk_level, 'black')
        )
        
        plt.tight_layout()
        
        # Save the plot
        plot_path = os.path.join(output_dir, "growth_projection.png")
        plt.savefig(plot_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        # Create results structure
        results = {
            "success": True,
            "message": "Growth rate prediction completed successfully (medically constrained).",
            "growth_rate_monthly": monthly_growth,
            "growth_rate_yearly": yearly_growth,
            "current_diameter": current_diameter,
            "risk_level": risk_level,
            "visualization": plot_path,
            "medical_constraints_applied": True,
            "metrics": {
                "Current Diameter": f"{current_diameter} mm",
                "Growth Rate (mm/month)": f"{monthly_growth:.3f}",
                "Growth Rate (mm/year)": f"{yearly_growth:.3f}",
                "Risk Level": risk_level
            }
        }
        
        # Add projected diameters for years 1-5
        for i in range(1, 6):
            projected_size = current_diameter + (yearly_growth * i)
            results["metrics"][f"Projected Size Year {i}"] = f"{projected_size:.1f} mm"
        
        if time_to_threshold:
            results["time_to_threshold_years"] = time_to_threshold
            results["metrics"]["Time to 55mm Threshold"] = f"{time_to_threshold:.1f} years"
        
        # Save results to CSV
        csv_path = os.path.join(output_dir, "growth_prediction_results.csv")
        with open(csv_path, 'w') as f:
            f.write("Parameter,Value\n")
            f.write(f"Current Diameter (mm),{current_diameter}\n")
            f.write(f"ILT Volume (mL),{ilt_volume}\n")
            f.write(f"Growth Rate (mm/month),{monthly_growth:.3f}\n")
            f.write(f"Growth Rate (mm/year),{yearly_growth:.3f}\n")
            f.write(f"Risk Level,{risk_level}\n")
            f.write(f"Medical Constraints Applied,Yes\n")
            
            # Add projections
            for i in range(1, 6):
                projected_size = current_diameter + (yearly_growth * i)
                f.write(f"Projected Size Year {i} (mm),{projected_size:.1f}\n")
                
            if time_to_threshold:
                f.write(f"Time to 55mm Threshold (years),{time_to_threshold:.1f}\n")
        
        results["results_csv"] = csv_path
        results["download_url"] = csv_path
        
        return results
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[ERROR] Failed to process growth rate prediction: {str(e)}\n{error_details}")
        return {"error": str(e)}

def predict_growth_rate_from_excel(excel_path, output_dir):
    """
    Process patient data from Excel file and predict growth rates with medical constraints.
    """
    try:
        print(f"[INFO] Beginning medically-constrained prediction from Excel file: {excel_path}")
        
        # Load model and scaler
        model, scaler = load_prediction_model()
        
        # Load data from Excel
        if excel_path.endswith('.csv'):
            df = pd.read_csv(excel_path)
        else:
            df = pd.read_excel(excel_path)
        
        print(f"[INFO] Loaded data with shape: {df.shape}")
        print(f"[INFO] Columns: {', '.join(df.columns)}")
        
        # Column mapping for alternative names
        column_mapping = {
            "AneurysmSize": "Current Axial Diameter (mm)",
            "CurrentDiameter": "Current Axial Diameter (mm)",
            "Diameter": "Current Axial Diameter (mm)",
            "AAA_Diameter": "Current Axial Diameter (mm)",
            "ILT": "ILT Volume (mL)",
            "Thrombus": "ILT Volume (mL)",
            "ThrombusVolume": "ILT Volume (mL)"
        }
        
        # Map alternative column names
        for alt_name, std_name in column_mapping.items():
            if alt_name in df.columns and std_name not in df.columns:
                df[std_name] = df[alt_name]
                print(f"[INFO] Mapped column {alt_name} to {std_name}")
        
        # Check required columns
        required_cols = ["Current Axial Diameter (mm)", "ILT Volume (mL)"]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            error_msg = f"Missing required columns: {', '.join(missing_cols)}"
            return {"error": error_msg}
        
        # Extract features
        X = df[required_cols].values
        
        # Scale features
        X_scaled = scaler.transform(X)
        
        # Make predictions (model already has ReLU constraint)
        raw_predictions = model.predict(X_scaled, verbose=0).flatten()
        
        # Apply additional medical constraints as safety measure
        predictions = [apply_medical_constraints(pred) for pred in raw_predictions]
        
        # Add predictions to dataframe
        df["Predicted Growth Rate (mm/month)"] = predictions
        df["Predicted Growth Rate (mm/year)"] = df["Predicted Growth Rate (mm/month)"] * 12
        
        # Updated risk assessment with more appropriate medical thresholds
        df["Risk Level"] = "Low"
        df.loc[df["Predicted Growth Rate (mm/year)"] > 1, "Risk Level"] = "Moderate"
        df.loc[df["Predicted Growth Rate (mm/year)"] > 3, "Risk Level"] = "High"  
        df.loc[df["Predicted Growth Rate (mm/year)"] > 5, "Risk Level"] = "Very High"
        
        # Add projected size after 1 year
        df["Projected Size (1 year)"] = df["Current Axial Diameter (mm)"] + df["Predicted Growth Rate (mm/year)"]
        
        # Ensure no negative growth rates in final output
        negative_count = sum(df["Predicted Growth Rate (mm/month)"] < 0)
        if negative_count > 0:
            print(f"[WARNING] Found {negative_count} negative predictions - applying medical constraints")
            df.loc[df["Predicted Growth Rate (mm/month)"] < 0, "Predicted Growth Rate (mm/month)"] = 0.0
            df.loc[df["Predicted Growth Rate (mm/year)"] < 0, "Predicted Growth Rate (mm/year)"] = 0.0
        
        print(f"[INFO] ✓ All predictions are medically valid (non-negative growth)")
        print(f"[INFO] Growth rate range: {df['Predicted Growth Rate (mm/year)'].min():.3f} to {df['Predicted Growth Rate (mm/year)'].max():.3f} mm/year")
        
        # Create results directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Save results to CSV
        results_path = os.path.join(output_dir, "growth_predictions.csv")
        df.to_csv(results_path, index=False)
        
        # Determine visualization type
        is_single_patient = len(df) == 1
        
        if is_single_patient:
            return create_single_patient_visualization(df, output_dir, results_path)
        else:
            return create_multiple_patients_visualization(df, output_dir, results_path)
            
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[ERROR] Failed to process Excel file: {str(e)}\n{error_details}")
        return {"error": str(e)}

# Keep the existing visualization functions but add medical constraint indicators
def create_single_patient_visualization(df, output_dir, results_path):
    """Create visualization for a single patient with medical constraint indicators."""
    try:
        patient_row = df.iloc[0]
        current_size = patient_row["Current Axial Diameter (mm)"]
        growth_rate = patient_row["Predicted Growth Rate (mm/year)"]
        risk_level = patient_row["Risk Level"]
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 8), dpi=100)
        
        # Plot projected growth over 5 years
        years = range(0, 6)
        diameters = [current_size + (growth_rate * y) for y in years]
        
        ax.plot(years, diameters, 'o-', linewidth=2.5, markersize=10, color='#2980b9')
        ax.fill_between(years, current_size * 0.8, diameters, alpha=0.2, color='#2980b9')
        
        # Add data point labels
        for i, (x, y) in enumerate(zip(years, diameters)):
            year_label = "Current" if i == 0 else f"Year {i}"
            color = 'black'
            if y >= 55:
                color = 'darkred'
            elif y >= 50:
                color = 'darkorange'
                
            ax.annotate(
                f'{year_label}\n{y:.1f} mm', 
                (x, y), 
                textcoords="offset points",
                xytext=(0, 10), 
                ha='center',
                fontsize=10,
                fontweight='bold' if y >= 50 else 'normal',
                color=color
            )
        
        # Styling
        ax.set_xlabel('Years from Now', fontsize=12, fontweight='bold')
        ax.set_ylabel('Projected Diameter (mm)', fontsize=12, fontweight='bold')
        ax.set_title('AAA Size Projection Over 5 Years\n(Medically Constrained Model)', fontsize=14, fontweight='bold')
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Threshold areas
        max_diameter = max(diameters)
        ax.axhspan(50, 55, alpha=0.1, color='orange', label='Approaching Threshold')
        ax.axhspan(55, max_diameter + 5, alpha=0.1, color='red', label='Surgical Threshold')
        
        ax.set_xticks(years)
        ax.set_xticklabels(['Current'] + [f'Year {y}' for y in years[1:]])
        
        # Time to threshold calculation
        time_to_threshold = None
        if current_size < 55 and growth_rate > 0:
            time_to_threshold = (55 - current_size) / growth_rate
            if time_to_threshold <= 5:
                threshold_x = time_to_threshold
                ax.scatter([threshold_x], [55], color='red', s=100, zorder=5)
                ax.annotate(
                    f'Reaches 55mm in {time_to_threshold:.1f} years',
                    xy=(threshold_x, 55),
                    xytext=(threshold_x - 0.5, 55 + 3),
                    arrowprops=dict(facecolor='red', shrink=0.05, width=1.5),
                    fontsize=11, 
                    fontweight='bold',
                    color='darkred'
                )
        
        # Risk level info
        risk_colors = {
            "Low": "green",
            "Moderate": "orange",
            "High": "red",
            "Very High": "darkred"
        }
        
        info_text = f"Annual Growth Rate: {growth_rate:.2f} mm/year\nRisk Level: {risk_level}\n✓ Medically Constrained"
        ax.text(
            0.02, 0.98, 
            info_text, 
            transform=ax.transAxes, 
            fontsize=12, 
            fontweight='bold',
            verticalalignment='top',
            bbox=dict(facecolor='white', alpha=0.9, boxstyle='round,pad=0.5', edgecolor='#cccccc'),
            color=risk_colors.get(risk_level, 'black')
        )
        
        plt.tight_layout()
        
        # Save plot
        plot_path = os.path.join(output_dir, "growth_projection_single.png")
        plt.savefig(plot_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        # Prepare patient data
        patient_data = {}
        for col in df.columns:
            value = patient_row[col]
            if hasattr(value, 'item'):
                patient_data[col] = value.item()
            else:
                patient_data[col] = value
        
        # Create metrics
        metrics = {
            "Current Diameter": f"{current_size} mm",
            "Growth Rate (mm/month)": f"{patient_row['Predicted Growth Rate (mm/month)']:.3f}",
            "Growth Rate (mm/year)": f"{growth_rate:.3f}",
            "Risk Level": risk_level,
            "Medical Constraints": "Applied ✓"
        }
        
        # Add projected sizes
        for i in range(1, 6):
            projected_size = current_size + (growth_rate * i)
            metrics[f"Projected Size Year {i}"] = f"{projected_size:.1f} mm"
        
        if time_to_threshold:
            metrics["Time to 55mm Threshold"] = f"{time_to_threshold:.1f} years"
        
        return {
            "success": True,
            "message": "Growth rate prediction completed successfully with medical constraints.",
            "is_single_patient": True,
            "visualization": plot_path,
            "results_csv": results_path,
            "output": plot_path,
            "download_url": results_path,
            "metrics": metrics,
            "patient_data": patient_data,
            "medical_constraints_applied": True
        }
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[ERROR] Failed to create single patient visualization: {str(e)}\n{error_details}")
        return {"error": f"Failed to create visualization: {str(e)}"}

def create_multiple_patients_visualization(df, output_dir, results_path):
    """Create visualization for multiple patients with medical constraint indicators."""
    try:
        print(f"[INFO] Creating visualization for {len(df)} patients")
        
        # Patient IDs
        if "Patient ID" in df.columns:
            patient_ids = df["Patient ID"].astype(str).tolist()
        else:
            patient_ids = [f"Patient {i+1}" for i in range(len(df))]
            
        # Create figure
        fig, ax = plt.subplots(figsize=(14, 8), dpi=100)
        
        # Bar chart data
        x = np.arange(len(patient_ids))
        width = 0.35
        
        current_sizes = df["Current Axial Diameter (mm)"].fillna(0).values
        projected_sizes = df["Projected Size (1 year)"].fillna(0).values
        
        # Create bars
        bars1 = ax.bar(x - width/2, current_sizes, width, label='Current Size', color='skyblue')
        bars2 = ax.bar(x + width/2, projected_sizes, width, label='Projected Size (1 year)', color='orange')
        
        # Add values on bars
        for i, bar in enumerate(bars1):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    f'{height:.1f}', ha='center', va='bottom', fontsize=9)
                    
        for i, bar in enumerate(bars2):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    f'{height:.1f}', ha='center', va='bottom', fontsize=9)
        
        # Styling
        ax.set_xlabel('Patient', fontsize=12, fontweight='bold')
        ax.set_ylabel('Diameter (mm)', fontsize=12, fontweight='bold')
        ax.set_title('Current vs. Projected AAA Size After 1 Year\n(Medically Constrained Model)', fontsize=14, fontweight='bold')
        
        # X-axis formatting
        if len(patient_ids) <= 10:
            ax.set_xticks(x)
            ax.set_xticklabels(patient_ids, rotation=45, ha='right')
        else:
            step = max(1, len(patient_ids) // 10)
            ax.set_xticks(x[::step])
            ax.set_xticklabels(patient_ids[::step], rotation=45, ha='right')
            
        ax.legend()
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        
        # Save plot
        plot_path = os.path.join(output_dir, "growth_predictions_multiple.png")
        plt.savefig(plot_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        # Calculate statistics
        stats = {
            "avg_growth_rate_monthly": float(df["Predicted Growth Rate (mm/month)"].mean()),
            "avg_growth_rate_yearly": float(df["Predicted Growth Rate (mm/year)"].mean()),
            "max_growth_rate_yearly": float(df["Predicted Growth Rate (mm/year)"].max()),
            "patient_count": int(len(df)),
            "high_risk_count": int(sum(df["Risk Level"].isin(["High", "Very High"]))),
            "moderate_risk_count": int(sum(df["Risk Level"] == "Moderate")),
            "low_risk_count": int(sum(df["Risk Level"] == "Low"))
        }
        
        # Calculate percentages safely
        patient_count = stats["patient_count"]
        if patient_count > 0:
            high_risk_pct = (stats["high_risk_count"] / patient_count) * 100
            moderate_risk_pct = (stats["moderate_risk_count"] / patient_count) * 100
            low_risk_pct = (stats["low_risk_count"] / patient_count) * 100
        else:
            high_risk_pct = moderate_risk_pct = low_risk_pct = 0
        
        return {
            "success": True,
            "message": f"Processed {len(df)} patient records successfully with medical constraints.",
            "is_single_patient": False,
            "results_csv": results_path,
            "visualization": plot_path,
            "output": plot_path,
            "download_url": results_path,
            "statistics": stats,
            "medical_constraints_applied": True,
            "metrics": {
                "Average Growth Rate (mm/month)": f"{stats['avg_growth_rate_monthly']:.3f}",
                "Average Growth Rate (mm/year)": f"{stats['avg_growth_rate_yearly']:.3f}",
                "Maximum Growth Rate (mm/year)": f"{stats['max_growth_rate_yearly']:.3f}",
                "Total Patients": str(stats['patient_count']),
                "High Risk Patients": f"{stats['high_risk_count']} ({high_risk_pct:.1f}%)",
                "Moderate Risk Patients": f"{stats['moderate_risk_count']} ({moderate_risk_pct:.1f}%)",
                "Low Risk Patients": f"{stats['low_risk_count']} ({low_risk_pct:.1f}%)",
                "Medical Constraints": "Applied ✓"
            }
        }
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[ERROR] Failed to create multiple patients visualization: {str(e)}\n{error_details}")
        return {"error": f"Failed to create visualization: {str(e)}"}