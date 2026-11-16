# Couche Silver — qualité et préparation

## Objectif

La couche Silver transforme les données Bronze en observations typées, contrôlées et directement exploitables pour les analyses temporelles et géographiques. Le notebook lit `s3a://datalake/bronze/comptage_multimodal_paris` et écrit `s3a://datalake/silver/comptage_multimodal_paris`.

Les champs descriptifs manquants (`nom_du_site`, `type_voie`, `sens_de_circulation`, `coordonnees_geo`) ne sont pas un motif de suppression : ils sont complétés à partir des autres observations du site ou de la trajectoire, lorsque c'est possible. Sinon, ils restent nuls. Cela évite de perdre des comptages qui restent utiles aux analyses temporelles.

## Règles de qualité

Exécuter les cellules de `work/02_silver.ipynb` dans l'ordre. Chaque règle calcule le nombre de lignes restantes et retirées sur le jeu réellement lu depuis Bronze. Les résultats ne sont pas préremplis, car le fichier source peut évoluer entre deux exécutions.

| Règle | Justification | Lignes retirées | Lignes restantes |
|---|---|---:|---:|
| Départ — Bronze | Nombre de lignes avant nettoyage | À calculer | — |
| R1 — doublons exacts | Une même ligne source ne doit être conservée qu'une fois | À calculer | À calculer |
| R2 — trajectoire absente | La trajectoire est nécessaire pour rattacher le comptage à un axe | À calculer | À calculer |
| R3 — date absente ou illisible | Une date valide est indispensable à l'analyse temporelle | À calculer | À calculer |
| R4 — identifiant de site absent | Sans identifiant, le comptage ne peut pas être localisé | À calculer | À calculer |
| R5 — mode absent | Le mode est nécessaire aux comparaisons multimodales | À calculer | À calculer |
| R6 — comptage absent ou non numérique | La mesure doit pouvoir être interprétée comme un entier | À calculer | À calculer |
| R7 — comptage négatif | Une valeur négative n'est pas physiquement interprétable | À calculer | À calculer |
| R8 — complétion des attributs descriptifs | Compléter par site/trajectoire sans retirer de ligne ; laisser les valeurs inconnues nulles | 0 | À calculer |
| Total — Silver | Nombre de lignes après les règles R1 à R7 | À calculer | À calculer |

Copier les valeurs affichées par la dernière cellule de `work/02_silver.ipynb` dans ce tableau après exécution. La complétion R8 rapporte séparément le nombre de valeurs descriptives récupérées.

## Valeurs élevées

Le notebook calcule un seuil exploratoire égal au 99,9e percentile de chaque mode et ajoute le booléen `aberrant_q999`. Les lignes signalées restent dans Silver : ce seuil ne constitue pas, à lui seul, une preuve d'erreur et ne justifie pas une suppression automatique.

## Limites d'interprétation

- Un volume de comptages élevé ne signifie pas nécessairement qu'un axe est saturé : la capacité, la durée de collecte et la couverture des capteurs ne sont pas intégrées dans ces agrégats.
- Les valeurs sans coordonnées restent utilisables dans les analyses temporelles, mais pas dans une carte.
- Les catégories de mode sont nettoyées des espaces superflus sans fusionner des libellés différents sans vérification métier.
