
import os
import joblib
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ==========================================
# 1. CONFIGURATION
# ==========================================

ML_DIR = "reports/ml"
MODEL_DIR = "models"
OUTPUT_DIR = "reports/visualizations"

os.makedirs(OUTPUT_DIR, exist_ok=True)

sns.set_theme(style="whitegrid")

# ==========================================
# 2. LOAD RESULTS
# ==========================================

regression_df = pd.read_csv(
    os.path.join(ML_DIR, "regression_results.csv")
)

classification_df = pd.read_csv(
    os.path.join(ML_DIR, "classification_results.csv")
)

regression_predictions = pd.read_csv(
    os.path.join(ML_DIR, "regression_predictions.csv")
)

confusion_df = pd.read_csv(
    os.path.join(ML_DIR, "confusion_matrix.csv"),
    index_col=0
)

# ==========================================
# 3. REGRESSION MODEL COMPARISON
# ==========================================

fig, axes = plt.subplots(1, 3, figsize=(17, 5))

metrics = [
    ("MAE", "MAE Comparison"),
    ("RMSE", "RMSE Comparison"),
    ("R2_Score", "R2 Score Comparison")
]

for ax, (metric, title) in zip(axes, metrics):

    sns.barplot(
        data=regression_df,
        x="Model",
        y=metric,
        ax=ax
    )

    ax.set_title(title)
    ax.set_xlabel("Model")
    ax.set_ylabel(metric)
    ax.tick_params(axis="x", rotation=35)

plt.tight_layout()

plt.savefig(
    os.path.join(
        OUTPUT_DIR,
        "regression_comparison.png"
    ),
    dpi=300
)

plt.show()

# ==========================================
# 4. CLASSIFICATION ACCURACY COMPARISON
# ==========================================

plt.figure(figsize=(9, 6))

sns.barplot(
    data=classification_df,
    x="Model",
    y="Accuracy"
)

plt.title("Classification Model Accuracy")
plt.xlabel("Classification Model")
plt.ylabel("Accuracy")

plt.xticks(rotation=25, ha="right")
plt.ylim(0, 1)

plt.tight_layout()

plt.savefig(
    os.path.join(
        OUTPUT_DIR,
        "classification_accuracy.png"
    ),
    dpi=300
)

plt.show()

# ==========================================
# 5. ACTUAL VS PREDICTED
# ==========================================

plt.figure(figsize=(8, 6))

sns.scatterplot(
    data=regression_predictions,
    x="Actual_Score",
    y="Predicted_Score",
    alpha=0.7
)

min_value = min(
    regression_predictions["Actual_Score"].min(),
    regression_predictions["Predicted_Score"].min()
)

max_value = max(
    regression_predictions["Actual_Score"].max(),
    regression_predictions["Predicted_Score"].max()
)

plt.plot(
    [min_value, max_value],
    [min_value, max_value],
    linestyle="--",
    label="Perfect Prediction"
)

plt.title("Actual vs Predicted Market Potential")
plt.xlabel("Actual Score")
plt.ylabel("Predicted Score")
plt.legend()

plt.tight_layout()

plt.savefig(
    os.path.join(
        OUTPUT_DIR,
        "actual_vs_predicted.png"
    ),
    dpi=300
)

plt.show()

# ==========================================
# 6. CONFUSION MATRIX
# ==========================================

plt.figure(figsize=(8, 6))

sns.heatmap(
    confusion_df,
    annot=True,
    fmt="d",
    cmap="Blues",
    linewidths=0.5
)

plt.title("Random Forest Classification Confusion Matrix")
plt.xlabel("Predicted Category")
plt.ylabel("Actual Category")

plt.tight_layout()

plt.savefig(
    os.path.join(
        OUTPUT_DIR,
        "confusion_matrix.png"
    ),
    dpi=300
)

plt.show()

# ==========================================
# 7. RANDOM FOREST FEATURE IMPORTANCE
# ==========================================

model = joblib.load(
    os.path.join(
        MODEL_DIR,
        "best_classification_model.pkl"
    )
)

preprocessor = model.named_steps["preprocessor"]

classifier = model.named_steps["model"]

feature_names = preprocessor.get_feature_names_out()

importance_df = pd.DataFrame({
    "Feature": feature_names,
    "Importance": classifier.feature_importances_
})

importance_df = importance_df.sort_values(
    by="Importance",
    ascending=False
).head(15)

plt.figure(figsize=(11, 7))

sns.barplot(
    data=importance_df,
    x="Importance",
    y="Feature"
)

plt.title("Top 15 Random Forest Feature Importances")
plt.xlabel("Importance")
plt.ylabel("Feature")

plt.tight_layout()

plt.savefig(
    os.path.join(
        OUTPUT_DIR,
        "feature_importance.png"
    ),
    dpi=300
)

plt.show()

importance_df.to_csv(
    os.path.join(
        OUTPUT_DIR,
        "feature_importance.csv"
    ),
    index=False
)

print("\n================================")
print("MODEL VISUALIZATION COMPLETED")
print("================================")

print("All graphs saved in:", OUTPUT_DIR)
