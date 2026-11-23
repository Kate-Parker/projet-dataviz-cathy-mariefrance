# Audit du cahier des charges

Cet audit compare les contenus des branches distantes `main`, `silver` et `feature/gold-aggregats`, ainsi que les changements sur `silver`. Il ne constitue pas un test complet depuis un clone.

## Livrables

| Exigence | État et éléments vérifiés |
|---|---|
| Dépôt et `.gitignore` | Présents sur les trois branches. Les collaborateurs visibles sont Kate-Parker et EFMFL ; Laminendao n'apparaît pas dans la liste accessible. Les invitations et règles ne sont pas vérifiées. |
| Téléchargement du CSV | L'en-tête réellement reçu de l'API correspond aux libellés attendus, et Silver accepte aussi les noms techniques du CSV local. L'ancien délai de 300 secondes a interrompu trois téléchargements ; il a été remplacé par un contrôle de débit. La protection, `--force` et le rejet d'un en-tête invalide ont été testés avec un export simulé. Un téléchargement complet depuis un nouveau clone reste à vérifier. |
| RustFS, PostgreSQL, Jupyter | Présents sur les trois branches. Sur `silver`, les services locaux ont été démarrés ; la console RustFS et Adminer répondent et la connexion PostgreSQL à `nyctaxi` fonctionne. |
| Ingestion Bronze | Sur `silver`, le notebook exige Delta, conserve les colonnes d'origine et refuse de remplacer un chemin existant. Une configuration Spark compatible et un lac isolé ont été ajoutés. Un extrait de 100 lignes réelles a été écrit et relu en Delta avec ses dix colonnes, avec les noms techniques puis avec les libellés officiels. Le CSV local a déclenché une erreur de ligne mal formée ; un traitement complet sur l'export officiel reste à vérifier. Les anciennes données Parquet ne sont pas migrées. |
| Ontologie et trois requêtes SPARQL | Sur `silver`, les trois requêtes ont été exécutées sur un extrait de 200 observations Silver de janvier 2025. Les autres branches ne sont pas modifiées. |
| Persona et question métier | Présents sur `silver`, avec la limite : un comptage ne mesure pas à lui seul la saturation. |
| Silver : typage et bilan des règles | Présents et exécutés localement ; résultats dans `silver.md`. |
| Exploration Silver | Notebook présent et exécuté localement. |
| Graphique naïf puis corrigé | Ajouté localement à la suite de la comparaison Bronze/Silver, avec explication de l'axe tronqué. La nouvelle cellule a été testée sur des données d'exemple ; le notebook complet reste à réexécuter avec elle. |
| Agrégats Gold et fiches KPI | Tables et cinq fiches présents sur `silver` ; agrégats exécutés et vérifiés localement. La branche Gold contient en plus une série quotidienne. |
| Export Gold vers PostgreSQL | Notebook d'export exécuté sur `silver` : 2 888 lignes pour les sites, 572 pour la série mensuelle, 1 347 pour le profil et 5 KPI, vérifiés après relecture. La branche Gold propose également son propre export. |
| Dashboard Streamlit avec récit et filtres | Application et service du profil `app` ajoutés sur `silver`. |
| Dashboard Grafana | Service du profil `bi`, source PostgreSQL et tableau de bord provisionnés sur `silver` ; les six requêtes ont retourné des données sur l'exécution locale. |
| Test complet clone → téléchargement → Compose → notebooks → dashboard | Le clonage GitHub de `silver` et la validation de la configuration Compose ont réussi. L'enchaînement complet depuis ce clone n'est pas encore validé. |
| Organisation complémentaire | Sur `silver`, les dossiers `seances/`, `mon_travail/` et `plan-b/` décrivent les livrables existants et les travaux manquants ; le plan B Colab autonome reste à réaliser. Une capture du graphique Streamlit et un guide de pannes sont présents. |
| Fuseki et Superset | Un service Fuseki optionnel est configuré sur `silver`. L'ontologie et l'extrait du notebook ont été chargés dans un jeu isolé ; une requête y a compté 200 observations. Ce n'est pas le graphe complet. Superset n'est pas configuré. |

## Points d'attention pour le groupe

- Les branches divergent : `main` apporte notamment le téléchargement et une version actualisée des requêtes sémantiques ; `feature/gold-aggregats` apporte notamment l'export PostgreSQL. Aucune fusion n'a été effectuée.
- Les configurations PostgreSQL des branches distantes ne sont pas toutes cohérentes. Sur la branche locale `silver`, Compose et l'URL JDBC utilisent désormais `PG_DB`, avec `nyctaxi` par défaut. Un volume PostgreSQL déjà initialisé ne crée pas automatiquement une nouvelle base.
- Le CSV local contient au moins une ligne mal formée. Les tableaux et captures issus de l'ingestion antérieure doivent être recalculés depuis un export vérifié avant d'être utilisés pour une conclusion métier.
- Le code partagé fixe le fuseau Spark à `America/New_York` ; vérifier ce choix avec les horodatages de la source parisienne avant de conclure sur les heures de pointe.
- Les adresses de services ne prouvent pas que les livrables applicatifs ou sémantiques sont complets. Le notebook exécute ses requêtes avec RDFLib ; l'export vers Fuseki concerne seulement l'extrait sélectionné.
