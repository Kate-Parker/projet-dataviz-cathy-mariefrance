# Couche Silver — qualité et préparation

## Objectif

La couche Silver transforme les données Bronze en observations typées, contrôlées et directement exploitables pour les analyses temporelles et géographiques. Le notebook lit `s3a://datalake/bronze/comptage_multimodal_paris` et écrit `s3a://datalake/silver/comptage_multimodal_paris`.

Les champs descriptifs manquants (`nom_du_site`, `type_voie`, `sens_de_circulation`, `coordonnees_geo`) ne sont pas un motif de suppression : ils sont complétés à partir des autres observations du site ou de la trajectoire, lorsque c'est possible. Sinon, ils restent nuls. Cela évite de perdre des comptages qui restent utiles aux analyses temporelles.

## Règles de qualité

Exécuter les cellules de `work/02_silver.ipynb` dans l'ordre. Chaque règle calcule le nombre de lignes restantes et retirées sur le jeu réellement lu depuis Bronze. Les résultats ne sont pas préremplis, car le fichier source peut évoluer entre deux exécutions.

> **Résultats historiques :** le tableau ci-dessous provient d'une exécution antérieure sur un Bronze de 12 302 768 lignes. Le CSV local examiné depuis s'interrompt au milieu de l'enregistrement 6 151 385 ; ces chiffres ne décrivent donc pas ce fichier et doivent être recalculés après une ingestion complète.

| Règle | Justification | Lignes retirées | Lignes restantes |
|---|---|---:|---:|
| Départ — Bronze | Nombre de lignes avant nettoyage | 0 | 12 302 768 |
| R1 — doublons exacts | Une même ligne source ne doit être conservée qu'une fois | 0 | 12 302 768 |
| R2 — trajectoire absente | La trajectoire est nécessaire pour rattacher le comptage à un axe | 8 | 12 302 760 |
| R3 — date absente, illisible ou antérieure à 1900 | Une date plausible est indispensable à l'analyse temporelle | 190 | 12 302 570 |
| R4 — identifiant de site absent | Sans identifiant, le comptage ne peut pas être localisé | 0 | 12 302 570 |
| R5 — mode absent | Le mode est nécessaire aux comparaisons multimodales | 0 | 12 302 570 |
| R6 — comptage absent ou non numérique | La mesure doit pouvoir être interprétée comme un entier | 286 | 12 302 284 |
| R7 — comptage négatif | Une valeur négative n'est pas physiquement interprétable | 0 | 12 302 284 |
| R8 — complétion des attributs descriptifs | Compléter par site/trajectoire sans retirer de ligne ; laisser les valeurs inconnues nulles | 0 | 12 302 284 |
| Total — Silver | Nombre de lignes après les règles R1 à R7 | 484 | 12 302 284 |

La règle R3 rejette aussi les dates antérieures à 1900 : Bronze contient quatre horodatages parsés en année 0001, dont deux restent après R2. Ces dates sont incompatibles avec la période de comptage observée (2011–2026).

Résultats historiques de `work/02_silver.ipynb` : 43 290 noms de site, 43 288 coordonnées, 0 type de voie et 0 sens de circulation récupérés. Après complétion, il reste respectivement 3 274 742, 3 364 868, 3 318 032 et 3 318 032 valeurs inconnues dans ces champs. Ces nombres doivent être recalculés avec le prochain Bronze complet.

## Valeurs élevées

Le notebook calcule un seuil exploratoire égal au 99,9e percentile de chaque mode et ajoute le booléen `aberrant_q999`. Les lignes signalées restent dans Silver : ce seuil ne constitue pas, à lui seul, une preuve d'erreur et ne justifie pas une suppression automatique.

## Comparaison visuelle

Le notebook distingue l'effet du nettoyage Bronze → Silver d'un exemple de perception : les mêmes totaux Silver sont affichés une fois avec un axe tronqué trompeur, puis avec un axe commençant à zéro pour comparer correctement les longueurs des barres.

## Limites d'interprétation

- Un volume de comptages élevé ne signifie pas nécessairement qu'un axe est saturé : la capacité, la durée de collecte et la couverture des capteurs ne sont pas intégrées dans ces agrégats.
- Les valeurs sans coordonnées restent utilisables dans les analyses temporelles, mais pas dans une carte.
- Les catégories de mode sont nettoyées des espaces superflus sans fusionner des libellés différents sans vérification métier.
