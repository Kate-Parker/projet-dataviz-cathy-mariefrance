# Fiches des indicateurs Gold

Les indicateurs sont calculés dans `gold_kpi` par `work/03_gold.ipynb`. Ils portent sur les observations Silver pour lesquelles `aberrant_q999 = false`. Ils décrivent les comptages disponibles, pas le nombre de personnes ni la capacité des voies.

## 1. Total des véhicules comptés

- **Question :** quel volume de comptages est présent dans le jeu de données retenu ?
- **Calcul :** somme de `nombre_vehicules` sur les observations Silver non signalées, tous modes, sites et périodes confondus.
- **Unité :** véhicules comptés.
- **Usage :** donner un ordre de grandeur global et vérifier la cohérence des agrégats.
- **Visualisation :** une carte affiche le total et des barres horizontales présentent sa répartition par mode, sur toute la période et indépendamment des filtres.
- **Limite :** ce cumul dépend de la durée de mesure et de la couverture des capteurs; ce n'est ni un nombre de personnes uniques ni un indicateur de saturation.

## 2. Nombre de sites actifs

- **Question :** combien de sites ont contribué aux comptages retenus ?
- **Calcul :** nombre d'identifiants de site distincts (`identifiant_site`) ayant au moins une observation non signalée.
- **Unité :** sites.
- **Usage :** contextualiser la couverture spatiale des données.
- **Limite :** un site actif peut n'avoir été mesuré que pendant une partie de la période.

## 3. Mode au volume compté le plus élevé

- **Question :** quel mode totalise le plus de comptages dans les données retenues ?
- **Calcul :** somme de `nombre_vehicules` par `mode_deplacement`, puis choix du total maximal. En cas d'égalité, le libellé de mode est départagé par ordre alphabétique.
- **Unité :** mode.
- **Usage :** repérer le mode qui domine les volumes mesurés de ce jeu de données.
- **Limite :** la comparaison reste sensible aux sites et durées de collecte disponibles pour chaque mode.

## 4. Part du mode principal

- **Question :** quelle part du total revient au mode principal ?
- **Calcul :** `100 × total_du_mode_principal / total_tous_modes`.
- **Unité :** pourcentage.
- **Usage :** compléter le classement des modes par un indicateur de poids relatif.
- **Limite :** cette part est calculée sur les comptages observés, pas sur l'ensemble des déplacements réels de la ville.

## 5. Heure de pointe moyenne

- **Question :** quelle heure de la journée présente le total moyen par site le plus élevé ?
- **Calcul :** addition des modes pour chaque site et heure civile mesurée, puis moyenne de ces totaux par heure locale (`Europe/Paris`). L'heure ayant la plus grande moyenne est retenue; en cas d'égalité, l'heure la plus précoce est choisie.
- **Unité :** heure locale, de 0 à 23.
- **Usage :** identifier un créneau à examiner dans le profil temporel et le dashboard.
- **Limite :** c'est une moyenne des site-heures disponibles, sans correction de la capacité ni de la couverture; elle ne représente pas une heure de pointe universelle.

## Conventions communes

- Les observations signalées par le seuil exploratoire Silver `aberrant_q999` sont exclues des agrégats Gold, mais restent dans Silver.
- Une moyenne par heure est calculée sur les heures site-mode effectivement observées. Les heures sans mesure ne sont pas inventées.
- Les résultats doivent être lus avec le nombre de sites et d'heures mesurés; un volume cumulé élevé ne suffit pas à conclure qu'un axe est saturé.
