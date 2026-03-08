# SKILL.md

## Compétence 1: Analyse Exploratoire des Données (EDA)

### Objectif
Transformer un jeu de données brut en constats exploitables, avec une vue claire sur:
- la qualité des données,
- les tendances principales,
- les anomalies,
- les premières pistes d'action.

### Entrées attendues
- Source de données (CSV, JSON, table SQL, etc.)
- Description métier minimale (contexte, KPI, période)
- Question d'analyse prioritaire

### Étapes de travail
1. Comprendre le besoin
- Reformuler la question métier.
- Définir les dimensions et métriques clés.

2. Auditer la qualité des données
- Vérifier valeurs manquantes, doublons, types incohérents.
- Identifier outliers et distributions suspectes.

3. Explorer les données
- Produire statistiques descriptives (moyenne, médiane, quartiles).
- Segmenter par dimensions utiles (temps, catégorie, zone, profil).
- Visualiser tendances et corrélations.

4. Interpréter
- Distinguer faits observés et hypothèses.
- Relier les résultats au contexte métier.

5. Recommander
- Proposer 3 à 5 actions concrètes, priorisées par impact/effort.
- Lister les analyses complémentaires à mener.

### Livrables
- Résumé exécutif (5-10 lignes)
- Table de qualité des données (problème, impact, correction proposée)
- 3 à 6 graphiques commentés
- Recommandations actionnables

### Critères de qualité
- Résultats traçables et reproductibles
- Hypothèses explicitement signalées
- Chiffres cohérents avec la source
- Recommandations reliées à un indicateur mesurable

## Compétence 2: Modélisation Prédictive Supervisée

### Objectif
Construire un modèle de machine learning capable de prédire une variable cible (classification ou régression) avec des performances robustes et interprétables.

### Entrées attendues
- Jeu de données labellisé (features + cible)
- Définition claire de la cible
- Critère de succès métier (ex: réduction du churn, hausse du taux de conversion)
- Contrainte d'usage (latence, fréquence de mise à jour, explicabilité)

### Étapes de travail
1. Cadrer le problème
- Définir le type de tâche (classification/régression).
- Choisir les métriques alignées au besoin métier.

2. Préparer les données
- Nettoyer, encoder, normaliser selon les besoins.
- Gérer déséquilibres de classes et fuite de données.
- Créer un split train/validation/test rigoureux.

3. Entraîner et comparer
- Établir un baseline simple.
- Tester plusieurs algorithmes et réglages (cross-validation).
- Sélectionner le meilleur compromis performance/stabilité.

4. Évaluer et expliquer
- Mesurer les performances sur le jeu de test.
- Analyser erreurs et cas limites.
- Produire une interprétation (importance des variables, SHAP ou équivalent).

5. Préparer l'industrialisation
- Sauvegarder pipeline + modèle.
- Définir monitoring (dérive des données, dérive de performance).
- Proposer un plan de réentraînement.

### Livrables
- Notebook ou script reproductible d'entraînement
- Rapport d'évaluation (métriques + matrice d'erreur si classification)
- Tableau de comparaison des modèles testés
- Recommandation de mise en production (go/no-go + conditions)

### Critères de qualité
- Pas de fuite de données dans le pipeline
- Évaluation sur données non vues
- Résultats stables sur plusieurs runs
- Modèle interprétable au niveau attendu par le métier

## Compétence 3: Conception et Fiabilisation de Pipeline ETL/ELT

### Objectif
Construire un pipeline de données robuste qui collecte, transforme et charge les données de manière fiable, traçable et maintenable.

### Entrées attendues
- Sources de données (API, fichiers, bases, flux)
- Schéma cible (data warehouse, data lake, mart)
- Fréquence d'alimentation (batch, micro-batch, streaming)
- Exigences SLA/SLO (fraîcheur, disponibilité, volumétrie)

### Étapes de travail
1. Concevoir l'architecture
- Définir les couches (raw, staging, curated).
- Choisir les formats et la stratégie de partitionnement.

2. Implémenter l'ingestion
- Gérer extraction incrémentale et reprise sur erreur.
- Assurer idempotence et traçabilité des runs.

3. Implémenter les transformations
- Standardiser schémas, types et règles métier.
- Ajouter tests de qualité (nulls, unicité, référentiel, fraîcheur).

4. Orchestrer et monitorer
- Planifier les jobs avec dépendances explicites.
- Mettre en place logs, alertes et tableaux de bord d'exécution.

5. Sécuriser et documenter
- Gérer secrets et droits d'accès minimaux.
- Documenter contrats de données et procédures d'exploitation.

### Livrables
- Pipeline versionné (code + configuration)
- Dictionnaire de données et mapping des transformations
- Suite de tests de qualité automatisés
- Dashboard d'observabilité (succès/échec, latence, volume)

### Critères de qualité
- Rejouabilité sans duplication de données
- Détection proactive des anomalies de qualité
- Respect des SLA de disponibilité et fraîcheur
- Documentation suffisante pour passation à l'équipe
