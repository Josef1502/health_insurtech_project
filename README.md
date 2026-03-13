# Health InsurTech

Application réalisée dans le cadre du mini projet final.

Fonctionnalités :
- analyse des données d’assurance santé
- modèle de régression interprétable
- dashboard interactif
- simulation des frais médicaux
- authentification simple
- message de consentement RGPD
- logs
- déploiement sécurisé

## Cheminement du projet
health_insurtech_project/
├── app.py
├── model_utils.py
├── requirements.txt
├── README.md
├── .gitignore
├── rgpd_note.md
├── slides_plan.md
├── data/
│   └── insurance_data.csv
└── .streamlit/
    ├── config.toml


## Lancement local

```bash
python -m streamlit run app.py