 # Rapport de projet — Comptages multimodaux à Paris

## 1. Objectif

Ce projet de visualisation, réalisé par Cathy et Marie-France en M1 Big Data et IA, étudie les comptages multimodaux de la Ville de Paris. Il aide un responsable de la mobilité urbaine à repérer les sites et les périodes qui méritent une analyse approfondie.

**Question principale :** quels sites et types de voie enregistrent les volumes observés les plus élevés, à quels jours et horaires, et comment ces volumes évoluent-ils selon le mode de déplacement ?

La revue hebdomadaire des comptages et les arbitrages trimestriels d'aménagement sont des hypothèses de conception, non des fréquences fournies par les données.

## 2. Données

La source est le jeu ouvert [Comptages multimodaux de Paris](https://opendata.paris.fr/explore/dataset/comptage-multimodal-comptages/information/), distinct de NYC Taxi. Il contient notamment l'identifiant du site et de la trajectoire, la date et l'heure, le mode de déplacement, le nombre de véhicules et, lorsqu'elles sont disponibles, des coordonnées.

Lors d'un téléchargement réalisé le 27 novembre 2026 dans un clone séparé, le CSV contenait **14 223 800 lignes**, nombre conforme aux métadonnées de l'API. Il dépasse le seuil demandé de deux millions de lignes. La source évolue : ce nombre ne garantit pas celui d'un téléchargement ultérieur. Les données sont exclues de Git.

## 3. Architecture et traitement

1. **Téléchargement :** le script récupère le CSV et ses métadonnées, puis vérifie la structure et le nombre d'enregistrements avant de l'installer.
2. **Bronze :** les données brutes sont chargées en Delta dans RustFS, sans modification des colonnes d'origine.
3. **Silver :** les données sont typées et contrôlées ; les attributs descriptifs manquants sont complétés lorsque possible. Les valeurs élevées sont signalées par un seuil exploratoire par mode, sans suppression automatique.
4. **Gold :** les observations non signalées alimentent des agrégats par site, mois, jour et heure, ainsi que cinq indicateurs. Ils sont exportés dans PostgreSQL pour les tableaux de bord.
5. **Sémantique :** une ontologie Turtle décrit les concepts du domaine ; un notebook construit un graphe RDF sur un extrait Silver et propose trois requêtes SPARQL.

Sur `silver`, le notebook Gold produit quatre tables. La branche `main` intègre aussi les tables de classement mensuel et de série quotidienne ; les branches doivent être resynchronisées pour disposer du même périmètre.

## 4. Qualité des données : résultat Silver complet

Dans le clone de validation, Bronze a été écrit et relu en Delta avec **14 223 800 lignes**. L'exécution Silver complète a ensuite produit les résultats suivants :

| Règle | Lignes retirées | Lignes restantes |
|---|---:|---:|
| Départ Bronze | 0 | 14 223 800 |
| Doublons exacts | 0 | 14 223 800 |
| Trajectoire absente | 5 | 14 223 795 |
| Date absente, illisible ou hors période | 214 | 14 223 581 |
| Identifiant de site absent | 0 | 14 223 581 |
| Mode absent | 0 | 14 223 581 |
| Comptage absent ou non numérique | 292 | 14 223 289 |
| Comptage négatif | 0 | 14 223 289 |
| Complétion des attributs descriptifs | 0 | 14 223 289 |
| **Total** | **511** | **14 223 289** |

Ce résultat est propre à l'export téléchargé. Des libellés de mode inhabituels apparaissent dans cette exécution ; ils nécessitent une vérification métier avant interprétation. Les règles et leur justification sont détaillées dans [silver.md](silver.md).

La complétion a récupéré **49 547 noms de site** et **49 545 coordonnées** ; aucun type de voie ni sens de circulation n'a été récupéré. Après complétion, il restait respectivement **3 819 155**, **3 925 001**, **3 868 702** et **3 868 702** valeurs inconnues.

Le seuil exploratoire du 99,9e percentile a signalé **14 675 observations** sans les retirer de Silver. Gold les exclut de ses calculs. Par exemple, le seuil est de 1 245 pour les véhicules légers et de 1 266 pour les vélos. Ce signalement n'est pas la preuve que les observations sont erronées.

## 5. Résultats Gold et indicateurs

Les chiffres suivants proviennent du traitement de l'export complet dans le clone de validation, avec la version de `main`. Les nombres de lignes ont été vérifiés à la relecture en Delta et dans PostgreSQL.

| Table | Lignes Delta et PostgreSQL |
|---|---:|
| Classement des sites `gold_sites_classement` | 2 906 |
| Classement mensuel `gold_sites_mensuel` | 12 484 |
| Série mensuelle `gold_serie_mensuelle` | 574 |
| Série quotidienne `gold_serie_quotidienne` | 16 240 |
| Profil jour/heure `gold_heatmap_heure_jour` | 1 349 |
| Indicateurs `gold_kpi` | 5 |

| Indicateur | Résultat complet | Interprétation |
|---|---:|---|
| Total des véhicules comptés | 746 281 181 | Somme des comptages retenus, non un nombre de véhicules ou de personnes uniques. |
| Sites actifs | 108 | Sites ayant au moins une observation non signalée ; leurs durées de mesure peuvent différer. |
| Mode au volume le plus élevé | Véhicules légers < 3,5 t | Il domine les comptages disponibles, sans représenter nécessairement tous les déplacements réels. |
| Part du mode principal | 45,73 % | Part des véhicules légers dans le total retenu. |
| Heure de pointe moyenne | 18 h | Heure locale avec le total moyen par site-heure le plus élevé, tous modes réunis. |

La somme des volumes mensuels et le total Gold sont tous deux de **746 281 181**. Les données mensuelles vont de janvier 2011 à novembre 2026 ; cela ne signifie pas que chaque site ou mode est mesuré pendant toute cette période.

## 6. Graphiques et interprétations

Le tableau de bord Streamlit présente cinq KPI : total des véhicules comptés, nombre de sites actifs, mode au volume le plus élevé, part de ce mode et heure de pointe moyenne. Leurs calculs et limites sont précisés dans [kpi.md](kpi.md).

Une carte met en évidence le total global et des barres horizontales présentent sa répartition par mode. Les évolutions mensuelles sont affichées dans des courbes séparées, avec une échelle verticale indépendante pour chaque mode. Le classement et la carte des sites, puis la carte de chaleur jour/heure, complètent le récit et proposent une piste d'analyse.

Les KPI et les barres de répartition sont globaux. Les filtres année et mode agissent sur les courbes mensuelles, le classement et la carte ; seul le filtre de mode s'applique au profil jour/heure.

### Total et répartition par mode

| Mode | Véhicules comptés |
|---|---:|
| Véhicules légers < 3,5 t | 341 260 844 |
| Trottinettes + vélos | 169 457 527 |
| Vélos | 98 946 200 |
| 2 roues motorisées | 61 820 736 |
| van | 25 744 187 |
| Trottinettes | 21 202 548 |
| Autobus et autocars | 14 107 711 |
| Véhicules lourds > 3,5 t | 13 690 921 |

La catégorie combinée « Trottinettes + vélos » reste distincte des catégories séparées : il ne faut pas l'attribuer automatiquement aux seuls vélos ou trottinettes. Cinq libellés inhabituels représentent ensemble 50 507 comptages ; leur présence limite la fiabilité des comparaisons et demande une vérification de la source.

### Courbes mensuelles

Les courbes séparent les modes pour rendre leurs variations lisibles. Tous modes confondus, juin 2025 atteint **28 265 059** comptages, le plus grand total mensuel observé. Pour les véhicules légers, octobre 2025 atteint **13 020 224** comptages sur **60 sites actifs**. Ces pics peuvent aussi traduire des variations de couverture, pas seulement une évolution du trafic. Les axes verticaux étant indépendants, il faut lire les valeurs pour comparer deux modes.

### Classement et carte des sites

Sur l'ensemble des années et modes retenus, le site **CF0001_9 boulevard de Sébastopol** totalise **59 101 880** comptages et arrive en tête du classement. Il s'agit d'une piste à examiner, pas d'une preuve de saturation : la durée et les conditions de collecte peuvent différer selon les sites. Parmi les **108 sites actifs**, **41** disposent de coordonnées valides dans le classement ; les autres restent dans les tableaux mais ne figurent pas sur la carte. Les marqueurs ont une taille fixe : les volumes se lisent dans le classement.

### Carte de chaleur jour/heure

Pour les véhicules légers, le dimanche à 17 h présente une moyenne de **394,05 véhicules par site-heure**, calculée sur **7 021 site-heures** observées. Cette moyenne n'est pas directement comparable à un total global. Des libellés de mode anormaux ne comptant chacun qu'une observation produisent des valeurs artificiellement élevées : leurs cases ne doivent pas être interprétées comme des pics de circulation fiables.

### Comparaison naïve et corrigée

L'exploration Silver montre les mêmes valeurs avec un axe tronqué, puis avec un axe commençant à zéro. Le premier graphique exagère les écarts de longueur entre barres ; le second facilite une comparaison proportionnelle. La correction concerne la perception des données, pas une modification des comptages.

L'exploration Gold compare aussi un classement par total à un classement par moyenne horaire, au grain site, mode, année et type de voie. Le classement par total place en tête le boulevard de Sébastopol, véhicules légers en 2022, avec **5 559 008 comptages en 7 702 heures**. Le classement par moyenne est dominé par un libellé anormal (`10146`), avec **10 146 véhicules sur une seule heure** : ce résultat illustre pourquoi la durée observée et la qualité des données doivent accompagner l'interprétation. Les deux classements ne mesurent pas la même chose et leurs hauteurs de barres ne sont pas directement comparables.

Les explorations présentent également la moyenne par observation selon l'heure en Silver, ainsi que la moyenne par site-mode-heure et le nombre de sites actifs par mois en Gold. Ces moyennes ont des dénominateurs différents ; il ne faut pas les comparer comme s'il s'agissait du même indicateur. La couverture des sites aide à repérer les variations de collecte.

## 7. Validations et limites

- **Jeu complet :** téléchargement, Bronze, Silver, Gold et export PostgreSQL ont été exécutés sur les volumes ci-dessus. Les notebooks d'exploration Silver et Gold ont aussi été exécutés sur ce jeu.
- **Extrait réel d'une journée :** Bronze, Silver, exploration, Gold et export PostgreSQL ont été exécutés ; Streamlit et son filtre ont été testés. Les six tables de la version `main` ont été exportées et relues sur cet extrait.
- **Sémantique :** l'ontologie a été chargée avec `rdflib` (50 triplets). Les trois requêtes ont ensuite été exécutées sur 200 observations issues du Silver complet, constituant un graphe de 1 270 triplets ; leurs résultats ne décrivent que cet extrait. Un premier extrait d'une journée avait échoué faute de noms de site.
- **Dashboard :** la base du dashboard de validation contient désormais les agrégats du jeu complet. Les chiffres Gold historiques documentés dans [gold.md](gold.md) correspondent à une autre ingestion.
- **Score :** aucun calcul de score composite n'a été identifié dans les fichiers du projet ; aucun résultat de score n'est donc inventé ici.
- **Interprétation :** un véhicule peut être compté plusieurs fois ; le total ne représente donc pas des personnes uniques. La couverture et les durées de mesure varient et certaines coordonnées manquent. Un volume élevé ne mesure pas directement la saturation, faute de capacité des voies et de données d'exposition.

## 8. Organisation et reproduction

La répartition présentée dans le [README](../README.md) attribue notamment à Cathy le dépôt, l'ingestion Bronze et l'ontologie, à Marie-France la préparation Silver et l'exploration, puis aux deux membres les agrégats Gold, les KPI et les dashboards.

Le README décrit les prérequis, le téléchargement, les services Docker et l'ordre des notebooks. Le guide [pannes.md](pannes.md) rassemble des pistes de dépannage. Avant une remise finale, il reste à synchroniser les branches et à vérifier les libellés de mode anormaux ; les explorations et requêtes SPARQL ont été exécutées après la production Gold plutôt que dans un unique enchaînement automatique.
