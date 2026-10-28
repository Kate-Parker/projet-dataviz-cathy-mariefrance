# projet-dataviz-cathy-mariefrance
Projet de visualisation de données — M1 Big Data &amp; IA réalise par Marie-France &amp; Cathy

Nous avons utilise de donnees qui proviennent de open data de la ville de Paris;
ce jeu de donnees contient + de 2millions de lignes et respecte les prequis pour le projet;
Theme:Mobilité et espace public
Sujet:Comptages multimodal(velo,trotinette,autobus)etc 

https://opendata.paris.fr/explore/dataset/comptage-multimodal-comptages/information/?disjunctive.mode&disjunctive.trajectoire&disjunctive.voie&disjunctive.sens&disjunctive.label


Comptages multimodal (CSV) ─► data lake S3 : bronze ─► silver ─► gold ─► PostgreSQL 
                                                     └──► ontologie RDF/OWL ─► graphe de connaissances



pour le deroule du projet nous avons fais un cahier de charges et attribuer les differents taches;

##Cathy: Bronze

1. Dépôt GitHub & Versioning
Initialisation et structure : Création du dépôt, organisation des dossiers (scripts, notebooks, données, ontologie) et configuration des règles de collaboration.

Sécurité et bonnes pratiques : Mise en place d'un fichier .gitignore pour exclure les données sensibles, les environnements virtuels et les fichiers temporaires/système.

Gestion des accès : Ajout du collaborateur -- Laminendao & mariefrance

2. Script de Téléchargement des Données
Script de téléchargement des fichiers Comptages multimodaux

3. Architecture Conteneurisée (docker-compose.yml)
Déploiement d'un écosystème reproductible via Docker Compose orchestrant trois services clés :

RustFS : Système de stockage objet haute performance pour centraliser les données au format Delta.

PostgreSQL : Base de données relationnelle pour la persistance et les métadonnées.

Jupyter : Environnement de développement interactif pour l'exécution des notebooks de traitement.

4. Notebook Bronze (Ingestion en Delta Lake)
Objectif : Charger les données brutes issues du téléchargement et les persister au format Delta dans RustFS.

Principe clé : Zéro transformation à cette étape. Les données sont conservées dans leur état brut d'origine (couche Bronze).

5. Modélisation Sémantique (.ttl)
Création de l'ontologie : Conception d'un fichier au format (.ttl) modélisant les concepts métier du domaine Comptages multimodaux.

Principe clés : Définition formelle des classes,propriétés et des liens logiques entre les entités pour permettre le raisonnement sémantique

6. Requêtes SPARQL (3)


## Marie-France:Silver --Qualité et persona 

1. Persona et README.md (dataset + décideur + question principale) 
Persona choisi ; Responsable de la mobilité urbain
Problématique métier et question centrale;
-Quels sont les axes et créneaux horaires les plus saturés et sur quel type de voie?
-Ou et quand la fréquentation des differents modes de deplacement evolue + ou moins et quel secteur


2. Notebook Silver : nettoyage et typage, avec le tableau de chaque règle de nettoyage et le nombre de lignes retirées
3. Notebook d’exploration : graphiques sur les données silver 
4. Avant/après : graphique naïf puis corrigé, justifié par les principes de perception 



Cathy + Marie France:Définir le schéma des tables gold à partir de la question du persona
Notebook Gold : agrégats construits depuis silver 
Export des tables gold vers PostgreSQL 
Fiches KPI (3 à 5)
Dashboard Streamlit (récit, filtre) et service docker compose 
Test complet : clone → téléchargement → docker compose up -d → notebooks → dashboard 



