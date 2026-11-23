# Audit du cahier des charges

Cet audit compare les contenus des branches distantes `main`, `silver` et `feature/gold-aggregats`, ainsi que les changements locaux sur `silver`. Il ne constitue pas un test complet depuis un clone.

## Livrables

| Exigence | État et éléments vérifiés |
|---|---|
| Dépôt et `.gitignore` | Présents sur les trois branches. Les accès des collaborateurs et les règles GitHub ne sont pas vérifiés faute d'authentification. |
| Téléchargement du CSV | Présent sur `main` ; repris sur `silver` sans fusion. Le téléchargement complet depuis un nouveau clone reste à tester. |
| RustFS, PostgreSQL, Jupyter | Présents sur les trois branches. Sur `silver`, les services locaux ont été démarrés ; la console RustFS et Adminer répondent et la connexion PostgreSQL à `nyctaxi` fonctionne. |
| Ingestion Bronze | Un notebook est présent sur chaque branche. La dernière exécution utilise Parquet en repli, pas Delta : l'exigence Delta n'est donc pas démontrée. Le notebook ajoute une colonne de provenance aux données brutes. |
| Ontologie et trois requêtes SPARQL | Sur `silver`, les trois requêtes ont été exécutées sur un extrait de 200 observations Silver de janvier 2025. Les autres branches ne sont pas modifiées. |
| Persona et question métier | Présents sur `silver`, avec la limite : un comptage ne mesure pas à lui seul la saturation. |
| Silver : typage et bilan des règles | Présents et exécutés localement ; résultats dans `silver.md`. |
| Exploration Silver | Notebook présent et exécuté localement. |
| Graphique naïf puis corrigé | Ajouté localement à la suite de la comparaison Bronze/Silver, avec explication de l'axe tronqué. La nouvelle cellule a été testée sur des données d'exemple ; le notebook complet reste à réexécuter avec elle. |
| Agrégats Gold et fiches KPI | Tables et cinq fiches présents sur `silver` ; agrégats exécutés et vérifiés localement. La branche Gold contient en plus une série quotidienne. |
| Export Gold vers PostgreSQL | Notebook d'export exécuté sur `silver` : 2 888 lignes pour les sites, 572 pour la série mensuelle, 1 347 pour le profil et 5 KPI, vérifiés après relecture. La branche Gold propose également son propre export. |
| Dashboard Streamlit avec récit et filtres | Application et service du profil `app` ajoutés sur `silver`. |
| Dashboard Grafana | Service du profil `bi`, source PostgreSQL et tableau de bord provisionnés sur `silver` ; les six requêtes ont retourné des données sur l'exécution locale. |
| Test complet clone → téléchargement → Compose → notebooks → dashboard | Non réalisé depuis un clone neuf. |
| Organisation complémentaire | `seances/`, `mon_travail/` et `plan-b/` absents des branches auditées. `.env.example` et la configuration Grafana ont été ajoutés localement sur `silver` ; les notebooks sont rangés dans `work/`. |
| Fuseki et Superset | Aucun service Fuseki ni Superset trouvé dans les fichiers Compose des branches auditées. |

## Points d'attention pour le groupe

- Les branches divergent : `main` apporte notamment le téléchargement et une version actualisée des requêtes sémantiques ; `feature/gold-aggregats` apporte notamment l'export PostgreSQL. Aucune fusion n'a été effectuée.
- Les configurations PostgreSQL des branches distantes ne sont pas toutes cohérentes. Sur la branche locale `silver`, Compose et l'URL JDBC utilisent désormais `PG_DB`, avec `nyctaxi` par défaut. Un volume PostgreSQL déjà initialisé ne crée pas automatiquement une nouvelle base.
- Le code partagé fixe le fuseau Spark à `America/New_York` ; vérifier ce choix avec les horodatages de la source parisienne avant de conclure sur les heures de pointe.
- Les adresses de services ne prouvent pas que les livrables applicatifs ou sémantiques sont complets. Un serveur SPARQL Fuseki et Superset ne sont pas configurés ; les requêtes SPARQL sont exécutées avec RDFLib dans le notebook.
