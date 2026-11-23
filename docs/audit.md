# Audit du cahier des charges

Cet audit compare les contenus des branches distantes `main`, `silver` et `feature/gold-aggregats`, ainsi que les changements locaux sur `silver`. Il ne constitue pas un test complet depuis un clone.

## Livrables

| Exigence | État et éléments vérifiés |
|---|---|
| Dépôt et `.gitignore` | Présents sur les trois branches. Les accès des collaborateurs et les règles GitHub ne sont pas vérifiés faute d'authentification. |
| Téléchargement du CSV | Présent sur `main` ; repris sur `silver` sans fusion. Le téléchargement complet depuis un nouveau clone reste à tester. |
| RustFS, PostgreSQL, Jupyter | Présents sur les trois branches. Sur `silver`, les services locaux ont été démarrés ; la console RustFS et Adminer répondent et la connexion PostgreSQL à `nyctaxi` fonctionne. |
| Ingestion Bronze | Un notebook est présent sur chaque branche. La dernière exécution utilise Parquet en repli, pas Delta : l'exigence Delta n'est donc pas démontrée. Le notebook ajoute une colonne de provenance aux données brutes. |
| Ontologie et trois requêtes SPARQL | Ontologie et requêtes présentes. La version de `main` interroge un extrait réel de Bronze ; l'exécution complète de ces requêtes n'a pas été vérifiée ici. |
| Persona et question métier | Présents sur `silver`, avec la limite : un comptage ne mesure pas à lui seul la saturation. |
| Silver : typage et bilan des règles | Présents et exécutés localement ; résultats dans `silver.md`. |
| Exploration Silver | Notebook présent et exécuté localement. |
| Graphique naïf puis corrigé | Ajouté localement à la suite de la comparaison Bronze/Silver, avec explication de l'axe tronqué. La nouvelle cellule a été testée sur des données d'exemple ; le notebook complet reste à réexécuter avec elle. |
| Agrégats Gold et fiches KPI | Tables et cinq fiches présents sur `silver` ; agrégats exécutés et vérifiés localement. La branche Gold contient en plus une série quotidienne. |
| Export Gold vers PostgreSQL | Code présent sur `feature/gold-aggregats`, pas sur `silver` ; aucune exportation de tables Gold n'a été validée ici. La base locale `nyctaxi` ne contient pas encore ces tables. |
| Dashboard Streamlit avec récit et filtres | Aucun fichier d'application ni service Compose Streamlit dans les branches auditées. |
| Test complet clone → téléchargement → Compose → notebooks → dashboard | Non réalisé ; impossible de le valider complètement sans dashboard fonctionnel et export PostgreSQL vérifié. |
| Organisation complémentaire | `seances/`, `mon_travail/`, `plan-b/` et configuration Grafana absents des branches auditées. `.env.example` a été ajouté localement sur `silver` ; les notebooks sont rangés dans `work/`. |
| Fuseki et Superset | Aucun service Fuseki ni Superset trouvé dans les fichiers Compose des branches auditées. |

## Points d'attention pour le groupe

- Les branches divergent : `main` apporte notamment le téléchargement et une version actualisée des requêtes sémantiques ; `feature/gold-aggregats` apporte notamment l'export PostgreSQL. Aucune fusion n'a été effectuée.
- Les configurations PostgreSQL des branches distantes ne sont pas toutes cohérentes. Sur la branche locale `silver`, Compose et l'URL JDBC utilisent désormais `PG_DB`, avec `nyctaxi` par défaut. Un volume PostgreSQL déjà initialisé ne crée pas automatiquement une nouvelle base.
- Le code partagé fixe le fuseau Spark à `America/New_York` ; vérifier ce choix avec les horodatages de la source parisienne avant de conclure sur les heures de pointe.
- Les adresses de services ne prouvent pas que les livrables applicatifs ou sémantiques sont complets. La disponibilité du serveur SPARQL, de Superset et du dashboard reste à mettre en place et à tester.
