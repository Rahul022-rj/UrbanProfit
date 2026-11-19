
import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline

from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)

# ==================================================
# 1. PROJECT CONFIGURATION
# ==================================================

INPUT_FILE = "data/processed/urbanprofit_cleaned.csv"

MODEL_DIR = "models"
REPORT_DIR = "reports/ml"

os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

RANDOM_STATE = 42
TEST_SIZE = 0.20

print("\n========================================")
print("       URBANPROFIT MACHINE LEARNING")
print("========================================")


# ==================================================
# 2. LOAD DATASET
# ==================================================

print("\n[1] Loading dataset...")

df = pd.read_csv(INPUT_FILE)

print("Dataset shape:", df.shape)

if df.empty:
    raise ValueError("Dataset is empty!")

required_columns = [
    "locality",
    "business_category",
    "population_density",
    "competitor_count",
    "existing_business_count",
    "avg_monthly_rent",
    "distance_main_road_km",
    "transport_access_score",
    "income_index",
    "footfall_index",
    "market_potential_score",
    "potential_category"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing columns in dataset: {missing_columns}"
    )

# Remove incomplete records from model inputs and targets
df = df.dropna(
    subset=required_columns
).copy()

print("Records available for training:", len(df))


# ==================================================
# 3. DEFINE FEATURES AND TARGETS
# ==================================================

print("\n[2] Preparing features and targets...")

features = [
    "locality",
    "business_category",
    "population_density",
    "competitor_count",
    "existing_business_count",
    "avg_monthly_rent",
    "distance_main_road_km",
    "transport_access_score",
    "income_index",
    "footfall_index"
]

categorical_features = [
    "locality",
    "business_category"
]

numerical_features = [
    "population_density",
    "competitor_count",
    "existing_business_count",
    "avg_monthly_rent",
    "distance_main_road_km",
    "transport_access_score",
    "income_index",
    "footfall_index"
]

X = df[features]

y_reg = df["market_potential_score"]

y_cls = df["potential_category"]

print("Input features:", len(features))
print("Regression target: market_potential_score")
print("Classification target: potential_category")


# ==================================================
# 4. DATA PREPROCESSING PIPELINE
# ==================================================

print("\n[3] Creating preprocessing pipeline...")

preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_features
        ),
        (
            "numerical",
            StandardScaler(),
            numerical_features
        )
    ]
)

print("OneHotEncoder: categorical features")
print("StandardScaler: numerical features")


# ==================================================
# 5. REGRESSION MODEL TRAINING
# ==================================================

print("\n========================================")
print("       REGRESSION MODEL TRAINING")
print("========================================")

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y_reg,
    test_size=TEST_SIZE,
    random_state=RANDOM_STATE
)

regression_models = {

    "Linear Regression": LinearRegression(),

    "Decision Tree Regressor": DecisionTreeRegressor(
        max_depth=8,
        min_samples_leaf=5,
        random_state=RANDOM_STATE
    ),

    "Random Forest Regressor": RandomForestRegressor(
        n_estimators=200,
        max_depth=12,
        min_samples_leaf=3,
        random_state=RANDOM_STATE,
        n_jobs=-1
    )
}

regression_results = []

trained_regression_models = {}

regression_predictions = {}

for name, model in regression_models.items():

    print(f"\nTraining: {name}")

    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("model", model)
    ])

    pipeline.fit(X_train, y_train)

    predictions = pipeline.predict(X_test)

    mae = mean_absolute_error(
        y_test,
        predictions
    )

    rmse = mean_squared_error(
        y_test,
        predictions
    ) ** 0.5

    r2 = r2_score(
        y_test,
        predictions
    )

    regression_results.append({
        "Model": name,
        "MAE": round(mae, 4),
        "RMSE": round(rmse, 4),
        "R2_Score": round(r2, 4)
    })

    trained_regression_models[name] = pipeline

    regression_predictions[name] = predictions

    print("MAE:", round(mae, 4))
    print("RMSE:", round(rmse, 4))
    print("R2 Score:", round(r2, 4))


# ==================================================
# 6. SELECT BEST REGRESSION MODEL
# ==================================================

regression_df = pd.DataFrame(regression_results)

regression_df = regression_df.sort_values(
    by="RMSE",
    ascending=True
)

regression_df.to_csv(
    os.path.join(
        REPORT_DIR,
        "regression_results.csv"
    ),
    index=False
)

best_regression_name = regression_df.iloc[0]["Model"]

best_regression_model = trained_regression_models[
    best_regression_name
]

joblib.dump(
    best_regression_model,
    os.path.join(
        MODEL_DIR,
        "best_regression_model.pkl"
    )
)

print("\nBest Regression Model:", best_regression_name)


# Save regression test predictions
best_regression_predictions = regression_predictions[
    best_regression_name
]

regression_prediction_df = pd.DataFrame({
    "Actual_Score": y_test.values,
    "Predicted_Score": best_regression_predictions
})

regression_prediction_df.to_csv(
    os.path.join(
        REPORT_DIR,
        "regression_predictions.csv"
    ),
    index=False
)


# ==================================================
# 7. CLASSIFICATION MODEL TRAINING
# ==================================================

print("\n========================================")
print("      CLASSIFICATION MODEL TRAINING")
print("========================================")

X_train_cls, X_test_cls, y_train_cls, y_test_cls = (
    train_test_split(
        X,
        y_cls,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y_cls
    )
)

classification_models = {

    "Logistic Regression": LogisticRegression(
        max_iter=5000,
        class_weight="balanced",
        solver="lbfgs",
        random_state=RANDOM_STATE
    ),

    "Decision Tree Classifier": DecisionTreeClassifier(
        max_depth=8,
        min_samples_leaf=5,
        class_weight="balanced",
        random_state=RANDOM_STATE
    ),

    "Random Forest Classifier": RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        min_samples_leaf=3,
        class_weight="balanced",
        random_state=RANDOM_STATE,
        n_jobs=-1
    )
}

classification_results = []

trained_classification_models = {}

classification_predictions = {}

for name, model in classification_models.items():

    print(f"\nTraining: {name}")

    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("model", model)
    ])

    pipeline.fit(
        X_train_cls,
        y_train_cls
    )

    predictions = pipeline.predict(
        X_test_cls
    )

    accuracy = accuracy_score(
        y_test_cls,
        predictions
    )

    precision = precision_score(
        y_test_cls,
        predictions,
        average="weighted",
        zero_division=0
    )

    recall = recall_score(
        y_test_cls,
        predictions,
        average="weighted",
        zero_division=0
    )

    f1_weighted = f1_score(
        y_test_cls,
        predictions,
        average="weighted",
        zero_division=0
    )

    f1_macro = f1_score(
        y_test_cls,
        predictions,
        average="macro",
        zero_division=0
    )

    classification_results.append({
        "Model": name,
        "Accuracy": round(accuracy, 4),
        "Precision_Weighted": round(precision, 4),
        "Recall_Weighted": round(recall, 4),
        "F1_Weighted": round(f1_weighted, 4),
        "F1_Macro": round(f1_macro, 4)
    })

    trained_classification_models[name] = pipeline

    classification_predictions[name] = predictions

    print("Accuracy:", round(accuracy, 4))
    print("Precision:", round(precision, 4))
    print("Recall:", round(recall, 4))
    print("Weighted F1:", round(f1_weighted, 4))
    print("Macro F1:", round(f1_macro, 4))


# ==================================================
# 8. SELECT BEST CLASSIFICATION MODEL
# ==================================================

classification_df = pd.DataFrame(
    classification_results
)

classification_df = classification_df.sort_values(
    by="F1_Macro",
    ascending=False
)

classification_df.to_csv(
    os.path.join(
        REPORT_DIR,
        "classification_results.csv"
    ),
    index=False
)

best_classification_name = classification_df.iloc[0]["Model"]

best_classification_model = trained_classification_models[
    best_classification_name
]

joblib.dump(
    best_classification_model,
    os.path.join(
        MODEL_DIR,
        "best_classification_model.pkl"
    )
)

print("\nBest Classification Model:", best_classification_name)


# ==================================================
# 9. CLASSIFICATION EVALUATION
# ==================================================

best_classification_predictions = classification_predictions[
    best_classification_name
]

print("\nClassification Report:")

print(
    classification_report(
        y_test_cls,
        best_classification_predictions,
        labels=["Low", "Medium", "High"],
        zero_division=0
    )
)

# Save classification report
report_dict = classification_report(
    y_test_cls,
    best_classification_predictions,
    labels=["Low", "Medium", "High"],
    output_dict=True,
    zero_division=0
)

pd.DataFrame(report_dict).transpose().to_csv(
    os.path.join(
        REPORT_DIR,
        "classification_report.csv"
    )
)


# ==================================================
# 10. CONFUSION MATRIX
# ==================================================

cm = confusion_matrix(
    y_test_cls,
    best_classification_predictions,
    labels=["Low", "Medium", "High"]
)

confusion_df = pd.DataFrame(
    cm,
    index=["Actual Low", "Actual Medium", "Actual High"],
    columns=[
        "Predicted Low",
        "Predicted Medium",
        "Predicted High"
    ]
)

confusion_df.to_csv(
    os.path.join(
        REPORT_DIR,
        "confusion_matrix.csv"
    )
)


# Save classification predictions
classification_prediction_df = pd.DataFrame({
    "Actual_Category": y_test_cls.values,
    "Predicted_Category": best_classification_predictions
})

classification_prediction_df.to_csv(
    os.path.join(
        REPORT_DIR,
        "classification_predictions.csv"
    ),
    index=False
)


# ==================================================
# 11. FINAL MODEL COMPARISON
# ==================================================

print("\n========================================")
print("          FINAL MODEL RESULTS")
print("========================================")

print("\nREGRESSION COMPARISON:")

print(
    regression_df.to_string(index=False)
)

print("\nCLASSIFICATION COMPARISON:")

print(
    classification_df.to_string(index=False)
)

print("\nBEST REGRESSION MODEL:")
print(best_regression_name)

print("\nBEST CLASSIFICATION MODEL:")
print(best_classification_name)


# ==================================================
# 12. SAVE MODEL INFORMATION
# ==================================================

model_info = {
    "project": "UrbanProfit",
    "data_type": "Synthetic",
    "features": features,
    "regression_target": "market_potential_score",
    "classification_target": "potential_category",
    "best_regression_model": best_regression_name,
    "best_classification_model": best_classification_name,
    "random_state": RANDOM_STATE,
    "test_size": TEST_SIZE
}

joblib.dump(
    model_info,
    os.path.join(
        MODEL_DIR,
        "model_info.pkl"
    )
)


# ==================================================
# 13. COMPLETION
# ==================================================

print("\n========================================")
print("    MACHINE LEARNING COMPLETED")
print("========================================")

print("\nSaved model files:")
print("- models/best_regression_model.pkl")
print("- models/best_classification_model.pkl")
print("- models/model_info.pkl")

print("\nSaved evaluation reports:")

for file in os.listdir(REPORT_DIR):
    print("-", file)

print("\nUrbanProfit ML pipeline completed successfully!")
