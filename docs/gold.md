# Couche Gold — dictionnaire des tables

## Objectif et exécution

`work/03_gold.ipynb` lit la couche Silver au chemin `s3a://datalake/silver/comptage_multimodal_paris` et écrit les tables prêtes pour les analyses et le dashboard sous `s3a://datalake/gold/<nom_de_table>`. Le notebook suit le format actif indiqué par `commun.spark_utils` (Delta quand disponible, Parquet en repli).

## Accès au data lake RustFS

- **Console web locale :** [http://localhost:9001/rustfs/console/](http://localhost:9001/rustfs/console/). Cette URL ouvre l'interface d'administration, pas le point d'accès S3 utilisé par Spark. Selon la version de RustFS, la racine `http://localhost:9001/` peut renvoyer une erreur 403.
- **Point d'accès S3 dans Compose :** `http://rustfs:9000`, défini par `S3_ENDPOINT`.
- **Identifiants :** définir `S3_ACCESS_KEY` et `S3_SECRET_KEY` dans le fichier `.env` à la racine du projet. Ce fichier est ignoré par Git; ne pas inscrire le mot de passe dans la documentation ou le code.

Les observations dont `aberrant_q999 = true` sont exclues des agrégats Gold, mais restent dans Silver. La règle est un filtre analytique, pas une suppression ni une validation définitive d'erreur. Le notebook vérifie que les totaux des tables de classement et mensuelle correspondent au total Silver retenu après ce filtre.

## Accès à PostgreSQL et Adminer

Lancer `docker compose up -d`; Adminer est alors disponible à [http://localhost:8080](http://localhost:8080/). Choisir le système PostgreSQL, le serveur `postgres`, la base `nyctaxi` et les identifiants définis par `PG_USER` et `PG_PASSWORD` (valeurs locales par défaut : `cours` / `cours`). PostgreSQL est également joignable depuis l'hôte à `localhost:5432`.

Après le notebook Gold, exécuter `work/05_export_postgres.ipynb` pour remplacer les quatre tables `public.gold_*` correspondantes et vérifier leur nombre de lignes après relecture. Le notebook ne remplace pas les autres tables PostgreSQL. Les dashboards Streamlit et Grafana lisent ces tables ; voir les commandes de démarrage dans le README.

## Convention de mesure horaire

Silver peut contenir plusieurs trajectoires pour un site et un mode au même instant. Pour les séries mensuelles et la carte de chaleur, ces observations sont additionnées d'abord au grain **site × mode × heure mesurée**. Les moyennes portent ensuite sur ces heures site-mode effectivement observées; les heures sans donnée ne sont pas inventées. Cela limite le biais lié aux durées de collecte différentes, sans remplacer une mesure d'exposition ou de capacité routière.

Le classement garde `type_voie` comme dimension : un site associé à plusieurs types de voie peut donc avoir plusieurs lignes. Les totaux ne sont pas attribués arbitrairement à un seul type de voie.

## Tables

Les nombres de lignes dépendent des données présentes dans Bronze; le notebook les affiche après chaque exécution. Les résultats ci-dessous sont historiques et doivent être recalculés après une nouvelle ingestion.

### `gold_sites_classement`

- **Chemin :** `s3a://datalake/gold/gold_sites_classement`
- **Grain :** une ligne par identifiant de site, mode, année et type de voie.
- **Question :** quels sites et types de voie concentrent les volumes observés, par mode et par année ?

| Colonne | Type Spark | Description |
|---|---|---|
| `identifiant_site` | string | Identifiant du site de comptage. |
| `nom_du_site` | string | Libellé descriptif du site, nullable. |
| `latitude` | double | Latitude du site, nullable. |
| `longitude` | double | Longitude du site, nullable. |
| `geo_connue` | boolean | Indique des coordonnées dans les plages géographiques valides. |
| `mode_deplacement` | string | Mode enregistré. |
| `annee` | integer | Année locale de l'observation. |
| `type_voie` | string | Type de voie, nullable si inconnu. |
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

## Résultats de l'exécution antérieure (historique)

Ces résultats proviennent d'un Bronze antérieur de 12 302 768 lignes. Le CSV local examiné depuis est interrompu et ne permet pas de confirmer ces agrégats. Après téléchargement et ingestion d'un export complet, réexécuter Silver, Gold et l'export PostgreSQL et recalculer ces chiffres.

Avec 12 302 284 lignes Silver, dont 12 798 signalées par `aberrant_q999`, les tables Gold contenaient :

| Table | Lignes vérifiées après écriture et relecture |
|---|---:|
| `gold_sites_classement` | 2 888 |
| `gold_serie_mensuelle` | 572 |
| `gold_heatmap_heure_jour` | 1 347 |
| `gold_kpi` | 5 |

Le total `total_usagers` est de 649 841 460 dans Silver retenue, `gold_sites_classement` et `gold_serie_mensuelle`. Les 107 sites actifs comprennent 66 sites sans coordonnées géographiques valides; ils restent disponibles pour les analyses temporelles, mais pas pour la carte. Cette exécution a utilisé Spark 4.3.0 et le repli Parquet, Delta n'étant pas pris en charge par cette version dans `commun.spark_utils`.

| KPI | Valeur de cette exécution |
|---|---:|
| Total des véhicules comptés | 649 841 460 |
| Sites actifs | 107 |
| Mode au volume le plus élevé | Véhicules légers < 3,5 t |
| Part du mode principal | 45,68 % |
| Heure de pointe moyenne | 18 h |

## Limites d'interprétation

- Un volume élevé n'est pas à lui seul un indicateur de saturation : ni la capacité de la voie ni l'exposition totale des capteurs ne sont mesurées.
- `moyenne_par_heure` moyenne les heures site-mode disponibles; elle ne prétend pas corriger toutes les différences de couverture et ne doit pas être présentée comme une moyenne d'heures civiles complètes.
- Les seuils `aberrant_q999` sont heuristiques et calculés par mode en Silver. Les observations signalées peuvent être réintégrées pour une analyse de sensibilité, mais ne figurent pas dans ces tables Gold.
- La convention Spark `jour_semaine` commence le dimanche (1) ; vérifier les libellés de jour dans le dashboard.

Les définitions et usages des cinq indicateurs de `gold_kpi` sont détaillés dans [`kpi.md`](kpi.md). Des graphiques de vérification des agrégats sont proposés dans `work/04_exploration_gold.ipynb`.
