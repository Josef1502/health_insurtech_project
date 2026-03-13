# Note RGPD - Health InsurTech

Dans ce projet, la conformité RGPD est prise en compte dès la conception.

## 1. Minimisation des données
Les données directement identifiantes ne sont pas utilisées dans le modèle :
- nom
- prénom
- email
- téléphone
- numéro de sécurité sociale
- adresse IP

## 2. Finalité
Le traitement a pour seule finalité d’estimer les frais médicaux annuels afin d’aider l’utilisateur à choisir un contrat adapté.

## 3. Transparence
L’application explique les variables utilisées pour la prédiction :
- âge
- IMC
- nombre d’enfants
- statut fumeur
- sexe
- région

## 4. Consentement
Un message d’information RGPD est affiché à l’entrée de l’application.

## 5. Sécurité
L’application est déployée en HTTPS, avec authentification simple et journalisation des accès.

## 6. Durée de conservation
L’application n’a pas vocation à stocker durablement les données saisies par l’utilisateur.