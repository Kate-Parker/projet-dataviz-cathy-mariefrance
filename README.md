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

## Lancement local

Depuis la racine du dépôt :

```bash
bash scripts/telecharger_donnees.sh
docker compose up -d
```

Le CSV est stocké dans `data/raw/` (ignoré par Git). Pour le remplacer après une mise à jour, utiliser `bash scripts/telecharger_donnees.sh --force`. Les variables locales peuvent être configurées en copiant `.env.example` vers `.env`.

### Exécuter le parcours Delta sans toucher aux données existantes

L'environnement habituel peut contenir des tables Parquet. Ne pas les remplacer
par du Delta dans les mêmes chemins. Pour créer un lac et une base indépendants,
utiliser un nom de projet Compose distinct et la configuration Delta :

```bash
docker compose -p dataviz-delta -f compose.yaml -f compose.delta.yaml up -d
```

Ouvrir Jupyter sur [http://localhost:18888/lab](http://localhost:18888/lab).
L'image utilise Spark 4.0.1. Le projet Compose distinct possède ses propres
volumes RustFS et PostgreSQL, mais partage les fichiers du dépôt, dont le CSV.
Exécuter `work/notebook_b.ipynb`, puis les notebooks Silver et Gold et enfin
`work/05_export_postgres.ipynb` dans cet environnement. Bronze exige Delta,
conserve les colonnes d'origine et refuse d'écraser un chemin déjà présent.
Les notebooks Silver, Gold et l'export remplacent leurs tables dans le projet
Compose utilisé : vérifier qu'il s'agit bien de l'environnement isolé.

Pour ses dashboards, démarrer les profils avec le même nom et les mêmes fichiers :

```bash
docker compose -p dataviz-delta -f compose.yaml -f compose.delta.yaml --profile app --profile bi up -d --build
```

Streamlit utilise alors [http://localhost:18501](http://localhost:18501/) et
Grafana [http://localhost:13000](http://localhost:13000/). Pour arrêter ces
conteneurs sans supprimer leurs volumes, utiliser `docker compose -p dataviz-delta -f compose.yaml -f compose.delta.yaml stop`.

- **Adminer :** [http://localhost:8080](http://localhost:8080/). Choisir le système PostgreSQL, le serveur `postgres`, la base `nyctaxi` et les identifiants définis par `PG_USER` et `PG_PASSWORD` (valeurs locales par défaut : `cours` / `cours`).
- **PostgreSQL depuis l'hôte :** `localhost:5432`, base `nyctaxi`.
- **JupyterLab :** [http://localhost:8888/lab](http://localhost:8888/lab), jeton défini par `JUPYTER_TOKEN` (par défaut `cours`).
- **RustFS :** console [http://localhost:9001/rustfs/console/](http://localhost:9001/rustfs/console/); Spark utilise le point d'accès interne `http://rustfs:9000`.

### Tableaux de bord et requêtes SPARQL

1. Pour créer de nouvelles tables, utiliser l'environnement Delta isolé décrit ci-dessus et exécuter dans l'ordre `work/notebook_b.ipynb`, `work/02_silver.ipynb`, puis `work/03_gold.ipynb`. Les dashboards de l'environnement habituel restent utilisables avec leurs tables PostgreSQL déjà chargées.
2. Exécuter `work/05_export_postgres.ipynb`. Il remplace les quatre tables `gold_*` de PostgreSQL par celles du data lake et vérifie leur nombre de lignes.
3. Pour les tables PostgreSQL déjà chargées dans l'environnement habituel, démarrer les tableaux de bord :

   ```bash
   docker compose --profile app --profile bi up -d --build
   ```

4. Ouvrir Streamlit sur [http://localhost:8501](http://localhost:8501/) et Grafana sur [http://localhost:3000](http://localhost:3000/). Le compte Grafana local par défaut est `admin` / `admin` ; modifier ces valeurs dans `.env` avant un usage autre que local. Le mot de passe n'est initialisé qu'à la création du volume Grafana ; ensuite, le modifier dans Grafana. Dans Grafana, ouvrir le dossier **Mobilité**, puis **Comptages multimodaux à Paris**.
5. Pour les trois requêtes SPARQL, exécuter `semantique/requete_1_modes.sparql.ipynb` après Silver. Il charge jusqu'à 200 observations Silver de janvier 2025 dans un graphe RDF en mémoire : les résultats concernent cet extrait, pas tout le jeu de données.

### Serveur SPARQL optionnel

```bash
docker compose --profile semantique up -d fuseki
```

Ouvrir [http://localhost:3030](http://localhost:3030/). Le jeu `comptages`
est persistant ; le compte administrateur local est `admin` et son mot de passe
est réglé par `FUSEKI_ADMIN_PASSWORD` (`admin` par défaut, à modifier dans
`.env` pour tout usage autre que local). Le notebook SPARQL exporte un fichier
Turtle dans `data/semantique/` ; dans Fuseki, sélectionner **manage datasets**,
puis le jeu `comptages` et l'option d'ajout de données pour charger ce fichier.
Le serveur ne charge pas automatiquement les données : ce fichier est un
**extrait**, pas un graphe complet du jeu. Éviter de charger plusieurs extraits
dans le même graphe sans les gérer, car leurs identifiants d'observation se
recoupent. Pour l'environnement Delta isolé, ajouter le profil `semantique` à
la commande Compose isolée et utiliser le port `13030`.

Les KPI Streamlit sont globaux. Les filtres année et mode s'appliquent aux graphiques mensuels et au classement ; le profil jour/heure n'est filtrable que par mode car sa table Gold ne contient pas l'année. Les dashboards signalent les limites d'interprétation : un volume n'est pas une mesure de saturation.

PostgreSQL initialise sa base et son utilisateur seulement lors de la création d'un volume neuf. Si un ancien volume ne contient pas `nyctaxi`, créer cette base sans supprimer les données existantes :

```bash
docker compose exec postgres psql -U cours -d postgres -c "CREATE DATABASE nyctaxi OWNER cours"
```

Adapter l'utilisateur si nécessaire. Modifier `PG_DB`, `PG_USER` ou `PG_PASSWORD` dans `.env` ne modifie pas les bases, utilisateurs ou mots de passe déjà enregistrés dans le volume.

## Livrables Silver et Gold

- `work/02_silver.ipynb` : typage, règles de qualité, complétion prudente des attributs descriptifs, variables temporelles et géographiques, signalement non destructif des valeurs élevées, écriture de la table Silver et graphique avant/après.
- `work/03_exploration_silver.ipynb` : exploration des volumes mensuels, profils horaires et sites/types de voie à investiguer.
- `docs/silver.md` : justification des règles et bilan mesuré sur l'exécution Silver actuelle.
- `work/03_gold.ipynb` : agrégats par site, mois, jour/heure et KPI pour alimenter le dashboard à partir de Silver.
- `docs/gold.md` : dictionnaire des tables Gold, grain des agrégats et limites d'interprétation.
- `docs/kpi.md` : définition, méthode de calcul, usage et limites des cinq KPI.
- `docs/audit.md` : état des exigences et différences constatées entre les branches.
- `docs/pannes.md` : dépannage des erreurs courantes.
- `work/04_exploration_gold.ipynb` : graphiques d'exploration construits à partir des tables Gold.
- `work/05_export_postgres.ipynb` : export et relecture des tables Gold dans PostgreSQL.

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



