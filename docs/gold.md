# Couche Gold — dictionnaire des tables

## Objectif et exécution

`work/03_gold.ipynb` lit la couche Silver au chemin `s3a://datalake/silver/comptage_multimodal_paris`, écrit les tables prêtes pour les analyses et le dashboard sous `s3a://datalake/gold/<nom_de_table>`, puis les exporte vers PostgreSQL. Le notebook suit le format actif indiqué par `commun.spark_utils` (Delta quand disponible, Parquet en repli).

Les observations dont `aberrant_q999 = true` sont exclues des agrégats Gold, mais restent dans Silver. La règle est un filtre analytique, pas une suppression ni une validation définitive d'erreur. Le notebook vérifie que les totaux du classement et des séries quotidienne et mensuelle correspondent au total Silver retenu après ce filtre.

## Convention de mesure horaire

Silver peut contenir plusieurs trajectoires pour un site et un mode au même instant. Pour les séries mensuelles et la carte de chaleur, ces observations sont additionnées d'abord au grain **site × mode × heure mesurée**. Les moyennes portent ensuite sur ces heures site-mode effectivement observées; les heures sans donnée ne sont pas inventées. Cela limite le biais lié aux durées de collecte différentes, sans remplacer une mesure d'exposition ou de capacité routière.

Le classement ne fragmente pas le total d'un site selon `type_voie` : la question métier porte sur le volume total par site. Les rangs sont calculés séparément pour chaque couple année-mois et mode; les sites ex æquo partagent le même rang.

## Tables

Les nombres de lignes dépendent des données présentes dans Bronze et seront affichés par le notebook après exécution. Ne pas inscrire de nombres estimés dans ce dictionnaire.

### `gold_sites_classement`

- **Chemin :** `s3a://datalake/gold/gold_sites_classement`
- **Grain :** une ligne par identifiant de site, mode, année et mois.
- **Question :** quels sites concentrent les volumes observés, par mode et par période ?

| Colonne | Type Spark | Description |
|---|---|---|
| `rang` | integer | Rang du site pour le mode et la période; les volumes ex æquo partagent le rang. |
| `identifiant_site` | string | Identifiant du site de comptage. |
| `nom_du_site` | string | Libellé descriptif du site, nullable. |
| `latitude` | double | Latitude du site, nullable. |
| `longitude` | double | Longitude du site, nullable. |
| `geo_connue` | boolean | Indique des coordonnées dans les plages géographiques valides. |
| `mode_deplacement` | string | Mode enregistré. |
| `annee` | integer | Année locale de l'observation. |
| `mois` | integer | Mois local de l'observation (1 à 12). |
| `total_usagers` | long | Somme des véhicules comptés sur les heures mesurées de ce groupe. |
| `moyenne_par_heure` | double | Moyenne des totaux horaires observés dans ce groupe. |
| `nb_heures_mesurees` | long | Nombre d'heures distinctes observées pour ce groupe. |

Les lignes sans coordonnées restent dans la table et doivent être filtrées uniquement pour l'affichage cartographique.

### `gold_serie_mensuelle`

- **Chemin :** `s3a://datalake/gold/gold_serie_mensuelle`
- **Grain :** une ligne par année, mois et mode.
- **Question :** comment le volume mesuré et la couverture des sites évoluent-ils selon le mode ?

| Colonne | Type Spark | Description |
|---|---|---|
| `annee` | integer | Année locale. |
| `mois` | integer | Mois (1 à 12). |
| `mode_deplacement` | string | Mode enregistré. |
| `total_usagers` | long | Somme mensuelle des totaux horaires site-mode observés. |
| `nb_sites_actifs` | long | Nombre de sites ayant au moins une heure mesurée dans le mois. |
| `moyenne_par_heure` | double | Moyenne des totaux site-mode-heure observés dans le mois. |
| `nb_sites_heures_mesurees` | long | Nombre d'heures site-mode présentes dans le mois. |

### `gold_serie_quotidienne`

- **Chemin :** `s3a://datalake/gold/gold_serie_quotidienne`
- **Grain :** une ligne par date et mode.
- **Question :** comment les volumes journaliers et la couverture des sites évoluent-ils au fil du temps ?

| Colonne | Type Spark | Description |
|---|---|---|
| `jour` | date | Jour local de l'observation. |
| `mode_deplacement` | string | Mode enregistré. |
| `total_usagers` | long | Somme des totaux horaires site-mode de la journée. |
| `nb_sites_actifs` | long | Nombre de sites ayant au moins une heure mesurée dans la journée. |
| `moyenne_par_heure` | double | Moyenne des totaux site-mode-heure observés dans la journée. |
| `nb_sites_heures_mesurees` | long | Nombre d'heures site-mode présentes dans la journée. |

### `gold_heatmap_heure_jour`

- **Chemin :** `s3a://datalake/gold/gold_heatmap_heure_jour`
- **Grain :** une ligne par mode, jour de semaine et heure.
- **Question :** à quels jours et horaires les comptages moyens observés sont-ils les plus élevés ?

| Colonne | Type Spark | Description |
|---|---|---|
| `mode_deplacement` | string | Mode enregistré. |
| `jour_semaine` | integer | Jour Spark : 1 = dimanche, 2 = lundi, …, 7 = samedi. |
| `heure` | integer | Heure locale (0 à 23). |
| `moyenne_par_heure` | double | Moyenne des totaux site-mode-heure disponibles pour ce créneau. |
| `nb_sites_heures_mesurees` | long | Nombre de site-heures utilisées pour la moyenne. |
| `nb_sites_actifs` | long | Nombre de sites représentés dans les observations du créneau. |

### `gold_kpi`

- **Chemin :** `s3a://datalake/gold/gold_kpi`
- **Grain :** une ligne par indicateur global.
- **Question :** quels chiffres synthétiques donner au tableau de bord ?

| Colonne | Type Spark | Description |
|---|---|---|
| `kpi_id` | string | Identifiant stable de l'indicateur. |
| `libelle` | string | Libellé destiné à l'affichage. |
| `valeur_numerique` | double | Valeur numérique, nullable pour un KPI textuel. |
| `valeur_texte` | string | Valeur textuelle, nullable pour un KPI numérique. |
| `unite` | string | Unité ou type de valeur. |
| `definition` | string | Définition et méthode de calcul. |

Les cinq KPI produits sont le total des comptages, le nombre de sites actifs, le mode au volume le plus élevé, la part de ce mode et l'heure dont le total moyen par site-heure (tous modes réunis) est le plus élevé.

## Export PostgreSQL

Les cinq tables sont écrites dans le schéma `public`, sous les mêmes noms `gold_*`. La connexion utilise `PG_HOST`, `PG_DB`, `PG_USER` et `PG_PASSWORD` définis dans l'environnement Compose. Dans la configuration du projet, la base par défaut est `comptagemultimodal`; depuis l'hôte, PostgreSQL est accessible sur `localhost:5432` (ce port est celui de la base, pas une interface web).

L'export utilise `overwrite` pour remplacer uniquement les tables Gold homonymes à chaque exécution. Le notebook relit chaque table par JDBC et compare son nombre de lignes avec l'agrégat Spark avant d'afficher la réussite.

## Voir les tables dans Adminer

Sur macOS, démarrez uniquement l'interface Adminer avec `docker compose up -d adminer` afin de ne pas tenter de démarrer un deuxième PostgreSQL si le port `5432` est déjà occupé. Ouvrez ensuite [http://localhost:8080](http://localhost:8080) et connectez-vous avec :

- Système : PostgreSQL
- Serveur : `host.docker.internal`
- Utilisateur : valeur de `PG_USER` (par défaut `cours`)
- Mot de passe : valeur de `PG_PASSWORD` (par défaut `cours`)
- Base de données : valeur de `PG_DB` (par défaut `comptagemultimodal`)

Dans Adminer, sélectionnez **SQL command** pour exécuter des requêtes, ou ouvrez le schéma `public` et choisissez une table puis **Select data**. Pour voir les indicateurs : `SELECT * FROM public.gold_kpi;`. Adminer est publié uniquement sur `127.0.0.1`; il est accessible depuis le navigateur de cette machine, pas depuis Internet.

## Limites d'interprétation

- Un volume élevé n'est pas à lui seul un indicateur de saturation : ni la capacité de la voie ni l'exposition totale des capteurs ne sont mesurées.
- `moyenne_par_heure` moyenne les heures site-mode disponibles; elle ne prétend pas corriger toutes les différences de couverture et ne doit pas être présentée comme une moyenne d'heures civiles complètes.
- Les seuils `aberrant_q999` sont heuristiques et calculés par mode en Silver. Les observations signalées peuvent être réintégrées pour une analyse de sensibilité, mais ne figurent pas dans ces tables Gold.
- La convention Spark `jour_semaine` commence le dimanche (1) ; vérifier les libellés de jour dans le dashboard.
- L'export PostgreSQL utilise le mode `overwrite` : chaque exécution remplace les tables Gold homonymes dans `public`.
