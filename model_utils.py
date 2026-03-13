import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np

SENSITIVE_COLUMNS = [
    "id_client",
    "nom",
    "prenom",
    "date_naissance",
    "email",
    "telephone",
    "numero_secu_sociale",
    "ville",
    "code_postal",
    "region_fr",
    "adresse_ip",
    "consentement_rgpd",
    "date_inscription",
]

TARGET = "charges"

def load_data(path="data/insurance_data.csv"):
    return pd.read_csv(path)

def prepare_data(df):
    df = df.copy()

    cols_to_drop = [c for c in SENSITIVE_COLUMNS if c in df.columns]
    df = df.drop(columns=cols_to_drop, errors="ignore")

    y = df[TARGET]
    X = df.drop(columns=[TARGET])

    numeric_features = X.select_dtypes(include=["int64", "float64"]).columns.tolist()
    categorical_features = X.select_dtypes(include=["object"]).columns.tolist()

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", SimpleImputer(strategy="median"), numeric_features),
            ("cat", Pipeline([
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("onehot", OneHotEncoder(handle_unknown="ignore"))
            ]), categorical_features),
        ]
    )

    model = Pipeline([
        ("preprocessor", preprocessor),
        ("regressor", LinearRegression())
    ])

    return X, y, model, numeric_features, categorical_features

def train_model(df):
    X, y, model, numeric_features, categorical_features = prepare_data(df)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model.fit(X_train, y_train)
    preds = model.predict(X_test)

    metrics = {
        "MAE": mean_absolute_error(y_test, preds),
        "RMSE": np.sqrt(mean_squared_error(y_test, preds)),
        "R2": r2_score(y_test, preds),
    }

    results = pd.DataFrame({
        "y_true": y_test,
        "y_pred": preds
    })

    return model, metrics, results, X_train, X_test, y_train, y_test

def bias_check(df):
    rows = []

    if "smoker" in df.columns:
        smoker_mean = df.groupby("smoker")["charges"].mean().reset_index()
        rows.append(("smoker", smoker_mean))

    if "region" in df.columns:
        region_mean = df.groupby("region")["charges"].mean().reset_index()
        rows.append(("region", region_mean))

    return rows