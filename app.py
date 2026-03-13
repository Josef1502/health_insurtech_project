import logging
import pandas as pd
import plotly.express as px
import streamlit as st

from model_utils import load_data, train_model, bias_check


# =========================
# Configuration générale
# =========================
logging.basicConfig(level=logging.INFO)
logging.info("Application démarrée")

st.set_page_config(
    page_title="Health InsurTech",
    page_icon="🏥",
    layout="wide"
)


# =========================
# Authentification simple
# =========================
def check_login() -> bool:
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if st.session_state["logged_in"]:
        return True

    st.title("🔐 Authentification")
    st.write("Veuillez vous connecter pour accéder à l'application.")

    username = st.text_input("Identifiant")
    password = st.text_input("Mot de passe", type="password")

    if st.button("Se connecter", use_container_width=True):
        if username == "admin" and password == "admin":
            st.session_state["logged_in"] = True
            st.success("Connexion réussie.")
            st.rerun()
        else:
            st.error("Identifiant ou mot de passe incorrect.")

    return False


if not check_login():
    st.stop()


# =========================
# Consentement RGPD
# =========================
if "consent_ok" not in st.session_state:
    st.session_state["consent_ok"] = False

if not st.session_state["consent_ok"]:
    st.title("📄 Information RGPD")
    st.info(
        "Cette application utilise uniquement les données saisies pour estimer "
        "les frais médicaux annuels. Les données sensibles ne sont pas utilisées "
        "dans le modèle de prédiction."
    )

    if st.button("J’ai compris et j’accepte", use_container_width=True):
        st.session_state["consent_ok"] = True
        st.rerun()

    st.stop()


# =========================
# Chargement des données
# =========================
@st.cache_data
def get_data():
    return load_data()


df = get_data()


# =========================
# En-tête principal
# =========================
st.title("🏥 Health InsurTech")
st.write("Application d’analyse et de simulation des frais médicaux annuels. by Josef-Mario MBAGA")

if st.button("Se déconnecter"):
    st.session_state["logged_in"] = False
    st.session_state["consent_ok"] = False
    st.rerun()


# =========================
# Création des onglets
# =========================
tab1, tab2, tab3, tab4 = st.tabs(
    ["Données", "Dashboard", "Modèle", "Simulation"]
)


# =========================
# Onglet 1 : Données
# =========================
with tab1:
    st.subheader("Aperçu du dataset")
    st.dataframe(df.head(), use_container_width=True)

    col1, col2 = st.columns(2)
    col1.metric("Nombre de lignes", df.shape[0])
    col2.metric("Nombre de colonnes", df.shape[1])

    st.write("### Types de colonnes")
    dtypes_df = pd.DataFrame(df.dtypes, columns=["Type"])
    st.dataframe(dtypes_df, use_container_width=True)


# =========================
# Onglet 2 : Dashboard
# =========================
with tab2:
    st.subheader("Dashboard interactif")

    # 1. Boxplots comparatifs pour détecter les valeurs aberrantes
    st.write("### 1. Boxplots comparatifs pour détecter les valeurs aberrantes")

    boxplot_df = df[["age", "bmi", "charges"]].copy()
    boxplot_scaled = (boxplot_df - boxplot_df.mean()) / boxplot_df.std()

    boxplot_long = boxplot_scaled.melt(
        var_name="Variable",
        value_name="Valeur normalisée"
    )

    fig_box = px.box(
        boxplot_long,
        x="Variable",
        y="Valeur normalisée",
        color="Variable",
        title="Boxplots comparatifs normalisés : âge, IMC et frais médicaux",
        labels={
            "Variable": "Variable",
            "Valeur normalisée": "Valeur normalisée"
        }
    )
    st.plotly_chart(fig_box, use_container_width=True, key="fig_box")

    # 2. Matrice de corrélation
    st.write("### 2. Matrice de corrélation")

    corr_df = df[["age", "bmi", "children", "charges"]].copy()
    corr_matrix = corr_df.corr(numeric_only=True)

    fig_corr_matrix = px.imshow(
        corr_matrix,
        text_auto=".2f",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        title="Matrice de corrélation entre les variables numériques"
    )
    st.plotly_chart(fig_corr_matrix, use_container_width=True, key="fig_corr_matrix")

    # 3. Scatter IMC / âge / frais médicaux
    st.write("### 3. Corrélation entre IMC, âge et frais médicaux")

    fig_corr = px.scatter(
        df,
        x="bmi",
        y="age",
        size="charges",
        color="charges",
        hover_data=["sexe", "region", "children", "smoker"],
        title="Relation entre IMC, âge et frais médicaux",
        labels={
            "bmi": "IMC",
            "age": "Âge",
            "charges": "Frais médicaux"
        }
    )
    st.plotly_chart(fig_corr, use_container_width=True, key="fig_corr")

# =========================
# Onglet 3 : Modèle
# =========================
with tab3:
    st.subheader("Modèle de prédiction interprétable")

    model, metrics, results, X_train, X_test, y_train, y_test = train_model(df)

    m1, m2, m3 = st.columns(3)
    m1.metric("MAE", f"{metrics['MAE']:.2f}")
    m2.metric("RMSE", f"{metrics['RMSE']:.2f}")
    m3.metric("R²", f"{metrics['R2']:.3f}")

    fig_pred = px.scatter(
        results,
        x="y_true",
        y="y_pred",
        title="Valeurs réelles vs valeurs prédites",
        labels={
            "y_true": "Valeurs réelles",
            "y_pred": "Valeurs prédites"
        }
    )
    st.plotly_chart(fig_pred, use_container_width=True, key="fig_pred")

    st.write("### Vérification simple des biais")
    bias_results = bias_check(df)

    for label, table in bias_results:
        st.write(f"#### Groupe : {label}")
        st.dataframe(table, use_container_width=True)

# =========================
# Onglet 4 : Simulation
# =========================
with tab4:
    st.subheader("Simulation des frais médicaux")

    age = st.number_input(
        "Âge",
        min_value=18,
        max_value=100,
        value=30,
        help="Saisir un âge entre 18 et 100 ans."
    )

    bmi = st.number_input(
        "IMC (BMI)",
        min_value=10.0,
        max_value=60.0,
        value=25.0,
        step=0.1,
        help="Saisir un IMC réaliste."
    )

    children = st.number_input(
        "Nombre d'enfants",
        min_value=0,
        max_value=10,
        value=0,
        help="Nombre d'enfants à charge."
    )

    sexe = st.selectbox(
        "Sexe",
        sorted(df["sexe"].dropna().unique().tolist()),
        help="Sélectionner le sexe."
    )

    smoker = st.selectbox(
        "Fumeur",
        sorted(df["smoker"].dropna().unique().tolist()),
        help="Indiquer si la personne fume."
    )

    region = st.selectbox(
        "Région",
        sorted(df["region"].dropna().unique().tolist()),
        help="Choisir la région."
    )

    # On ne l'affiche que si la colonne existe vraiment dans le dataset
    input_data = {
        "age": age,
        "sexe": sexe,
        "bmi": bmi,
        "children": children,
        "smoker": smoker,
        "region": region,
    }

    if "mutuelle_complementaire" in df.columns:
        mutuelle_complementaire = st.selectbox(
            "Mutuelle complémentaire",
            sorted(df["mutuelle_complementaire"].dropna().unique().tolist()),
            help="Présence ou non d'une mutuelle complémentaire."
        )
        input_data["mutuelle_complementaire"] = mutuelle_complementaire

    if age <= 0 or bmi <= 0:
        st.error("Les valeurs saisies sont invalides.")
        st.stop()

    model, metrics, results, X_train, X_test, y_train, y_test = train_model(df)

    # On récupère exactement les colonnes utilisées par le modèle
    expected_columns = X_train.columns.tolist()

    input_df = pd.DataFrame([input_data])

    # Ajouter les colonnes manquantes avec une valeur par défaut
    for col in expected_columns:
        if col not in input_df.columns:
            if col in df.columns:
                if df[col].dtype == "object":
                    input_df[col] = df[col].mode(dropna=True)[0]
                else:
                    input_df[col] = df[col].median()
            else:
                input_df[col] = None

    # Réordonner les colonnes comme à l'entraînement
    input_df = input_df[expected_columns]

    st.write("### Données saisies")
    st.dataframe(input_df, use_container_width=True)

    if st.button("Estimer mes frais", use_container_width=True):
        prediction = model.predict(input_df)[0]
        prediction_mensuelle = prediction / 12

        st.success("Estimation réalisée avec succès.")

        col1, col2 = st.columns(2)
        col1.metric("Frais médicaux annuels estimés", f"{prediction:.2f} €")
        col2.metric("Frais médicaux mensuels estimés", f"{prediction_mensuelle:.2f} €")