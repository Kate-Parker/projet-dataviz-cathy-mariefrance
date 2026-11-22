# projet-dataviz-cathy-mariefrance
Projet de visualisation de données — M1 Big Data &amp; IA réalise par Marie-France &amp; Cathy

Nous avons utilise de donnees qui proviennent de open data de la ville de Paris;
ce jeu de donnees contient + de 2millions de lignes et respecte les prequis pour le projet;
Theme:Mobilité et espace public
Sujet:Comptages multimodal(velo,trotinette,autobus)etc 

https://opendata.paris.fr/explore/dataset/comptage-multimodal-comptages/information/?disjunctive.mode&disjunctive.trajectoire&disjunctive.voie&disjunctive.sens&disjunctive.label


Comptages multimodal (CSV) ─► data lake S3 : bronze ─► silver ─► gold ─► PostgreSQL 
                                                     └──► ontologie RDF/OWL ─► graphe de connaissances

## Persona et question métier

**Persona :** responsable de la mobilité urbaine à la Ville de Paris, qui doit repérer les sites et périodes nécessitant une analyse plus approfondie pour l'aménagement et la gestion des déplacements.

**Question principale :** quels sites et types de voie enregistrent les volumes de comptage les plus élevés, à quels jours et horaires, et comment ces volumes évoluent-ils selon le mode de déplacement ?

Les comptages décrivent les passages mesurés par les capteurs. Ils ne donnent pas à eux seuls la capacité d'un axe ni son taux de saturation ; les résultats servent à identifier des tendances et des zones à examiner, en tenant compte de la couverture et des périodes de collecte.

**Source :** [Comptages multimodaux de la Ville de Paris](https://opendata.paris.fr/explore/dataset/comptage-multimodal-comptages/information/). Les volumes de données et les résultats de qualité sont calculés à l'exécution des notebooks, car ils dépendent du fichier ingéré dans Bronze.

## Livrables Silver et Gold

- `work/02_silver.ipynb` : typage, règles de qualité, complétion prudente des attributs descriptifs, variables temporelles et géographiques, signalement non destructif des valeurs élevées, écriture de la table Silver et graphique avant/après.
- `work/03_exploration_silver.ipynb` : exploration des volumes mensuels, profils horaires et sites/types de voie à investiguer.
- `docs/silver.md` : justification des règles et bilan mesuré sur l'exécution Silver actuelle.
- `work/03_gold.ipynb` : agrégats par site, mois, jour/heure et KPI pour alimenter le dashboard à partir de Silver.
- `docs/gold.md` : dictionnaire des tables Gold, grain des agrégats et limites d'interprétation.
- `docs/kpi.md` : définition, méthode de calcul, usage et limites des cinq KPI.
- `work/04_exploration_gold.ipynb` : graphiques d'exploration construits à partir des tables Gold.

Lors de la dernière exécution, 66 des 107 sites actifs n'avaient pas de coordonnées valides : ils sont conservés dans les agrégats, mais doivent être exclus de la carte. Les nombres et KPI de `docs/gold.md` correspondent aux données actuellement présentes dans Bronze et sont à recalculer après toute nouvelle ingestion.



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



