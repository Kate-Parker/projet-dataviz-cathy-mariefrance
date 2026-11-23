# Pannes fréquentes

- **Port déjà occupé** : vérifier les conteneurs en cours avec `docker compose ps`.
  La configuration Delta isolée utilise des ports différents ; voir le README.
- **Fichier CSV introuvable ou déjà présent** : lancer le script de téléchargement
  depuis la racine. `--force` remplace le CSV existant après validation : conserver
  une copie si les données actuelles doivent être préservées.
- **Delta indisponible** : utiliser l'image Spark compatible de la configuration
  isolée. Ne pas écrire du Delta sur les anciennes tables Parquet.
- **Bronze existe déjà** : l'ingestion refuse de l'écraser. Utiliser un nouveau
  projet Compose isolé plutôt que supprimer ou remplacer les données existantes.
- **`MALFORMED_CSV_RECORD` dans Bronze** : le CSV contient une ligne dont le
  nombre de champs est incorrect. Le notebook s'arrête pour éviter d'altérer
  silencieusement les données ; conserver le fichier et télécharger une nouvelle
  copie officielle dans un emplacement séparé pour comparaison.
- **Table PostgreSQL absente** : exécuter Bronze, Silver, Gold puis le notebook
  d'export PostgreSQL dans le même environnement avant d'ouvrir les dashboards.
- **Modification de la base ou du mot de passe PostgreSQL sans effet** : ces
  paramètres sont initialisés seulement à la création du volume. Ne pas supprimer
  le volume existant ; consulter la section PostgreSQL du README.
- **Première session Spark lente** : les dépendances Java sont téléchargées au
  premier démarrage. Vérifier la connexion réseau et les messages dans Jupyter.
- **Console RustFS inaccessible** : ouvrir
  `http://localhost:9001/rustfs/console/` (ou le port isolé `19001`).
