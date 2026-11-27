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

## 5. Tableau de bord

Le tableau de bord Streamlit présente cinq KPI : total des véhicules comptés, nombre de sites actifs, mode au volume le plus élevé, part de ce mode et heure de pointe moyenne. Leurs calculs et limites sont précisés dans [kpi.md](kpi.md).

Une carte met en évidence le total global et des barres horizontales présentent sa répartition par mode. Les évolutions mensuelles sont affichées dans des courbes séparées, avec une échelle verticale indépendante pour chaque mode. Le classement et la carte des sites, puis la carte de chaleur jour/heure, complètent le récit et proposent une piste d'analyse.

Les KPI et les barres de répartition sont globaux. Les filtres année et mode agissent sur les courbes mensuelles, le classement et la carte ; seul le filtre de mode s'applique au profil jour/heure.

## 6. Validations et limites

- **Jeu complet :** téléchargement, lecture Bronze Delta et écriture/relecture Silver Delta réussis sur les volumes ci-dessus.
- **Extrait réel d'une journée :** Bronze, Silver, exploration, Gold et export PostgreSQL ont été exécutés ; Streamlit et son filtre ont été testés. Les six tables de la version `main` ont été exportées et relues sur cet extrait.
- **Sémantique :** le fichier Turtle a été chargé avec `rdflib` (50 triplets). Le notebook SPARQL a échoué sur l'extrait d'une journée, car celui-ci ne contenait aucun nom de site ; les trois requêtes restent à vérifier sur un extrait approprié ou le Silver complet.
- **Parcours complet :** Gold, export PostgreSQL, dashboards et SPARQL n'ont pas encore été validés de bout en bout sur les 14,2 millions de lignes. Les chiffres Gold historiques documentés dans [gold.md](gold.md) ne sont pas les résultats de cette ingestion complète.
- **Interprétation :** un véhicule peut être compté plusieurs fois ; le total ne représente donc pas des personnes uniques. La couverture et les durées de mesure varient et certaines coordonnées manquent. Un volume élevé ne mesure pas directement la saturation, faute de capacité des voies et de données d'exposition.

## 7. Organisation et reproduction

La répartition présentée dans le [README](../README.md) attribue notamment à Cathy le dépôt, l'ingestion Bronze et l'ontologie, à Marie-France la préparation Silver et l'exploration, puis aux deux membres les agrégats Gold, les KPI et les dashboards.

Le README décrit les prérequis, le téléchargement, les services Docker et l'ordre des notebooks. Le guide [pannes.md](pannes.md) rassemble des pistes de dépannage. Avant une remise finale, il reste à synchroniser les branches, exécuter entièrement le parcours depuis un clone neuf et contrôler les résultats sur le jeu complet.
