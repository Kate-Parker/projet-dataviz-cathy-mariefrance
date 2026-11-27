#!/bin/sh
set -eu

URL='https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/comptage-multimodal-comptages/exports/csv?delimiter=%3B&use_labels=true'
METADATA_URL='https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/comptage-multimodal-comptages'
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
OUTPUT="$ROOT/data/raw/comptage_multimodal_comptages.csv"
FORCE=0

usage() {
    cat <<'EOF'
Usage: telecharger_donnees.sh [--output FILE] [--force]

Télécharge l'export CSV officiel des comptages multimodaux de Paris.
Par défaut, écrit data/raw/comptage_multimodal_comptages.csv.
--force remplace le fichier cible s'il existe déjà.
EOF
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        --output)
            if [ "$#" -lt 2 ]; then
                echo "Erreur : --output attend un chemin." >&2
                exit 2
            fi
            OUTPUT=$2
            shift 2
            ;;
        --force)
            FORCE=1
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Option inconnue : $1" >&2
            usage >&2
            exit 2
            ;;
    esac
done

if python3 -c 'import sys; sys.exit(sys.version_info.major != 3)' >/dev/null 2>&1; then
    PYTHON=python3
elif python -c 'import sys; sys.exit(sys.version_info.major != 3)' >/dev/null 2>&1; then
    PYTHON=python
else
    echo "Erreur : Python 3 est nécessaire pour valider le téléchargement." >&2
    exit 1
fi

case "$OUTPUT" in
    /*) ;;
    *) OUTPUT="$PWD/$OUTPUT" ;;
esac

OUTPUT_DIR=$(dirname -- "$OUTPUT")
mkdir -p "$OUTPUT_DIR"

if [ -e "$OUTPUT" ] && [ "$FORCE" -ne 1 ]; then
    echo "Erreur : $OUTPUT existe déjà. Utilisez --force pour le remplacer." >&2
    exit 1
fi

TEMP_FILE=$(mktemp "${OUTPUT}.XXXXXX")
METADATA_FILE=$(mktemp "${OUTPUT}.metadata.XXXXXX")
cleanup() {
    rm -f "$TEMP_FILE" "$METADATA_FILE"
}
trap cleanup 0 HUP INT TERM

if ! curl --fail --location --silent --show-error \
    --connect-timeout 20 --retry 2 --retry-delay 2 \
    --output "$METADATA_FILE" "$METADATA_URL"; then
    echo "Erreur : impossible de lire les métadonnées du jeu de données." >&2
    exit 1
fi

if ! curl --fail --location --silent --show-error \
    --connect-timeout 20 --speed-limit 1024 --speed-time 120 --retry 2 --retry-delay 2 \
    --user-agent 'projet-dataviz-comptages-paris/1.0' \
    --output "$TEMP_FILE" "$URL"; then
    echo "Erreur : le téléchargement du CSV a échoué." >&2
    exit 1
fi

if [ ! -s "$TEMP_FILE" ]; then
    echo "Erreur : l'export CSV téléchargé est vide." >&2
    exit 1
fi

if ! "$PYTHON" - "$TEMP_FILE" "$METADATA_FILE" <<'PY'
import csv
import json
import sys

colonnes_attendues = [
    "Identifiant trajectoire",
    "Identifiant site",
    "Nom du site",
    "Date et heure de comptage",
    "Mode déplacement",
    "Nombre de véhicules",
    "Type voie",
    "Sens de circulation",
    "Trajectoire",
    "Coordonnées Géo",
]

try:
    with open(sys.argv[2], encoding="utf-8") as fichier:
        metadonnees = json.load(fichier)
    nombre_attendu = metadonnees.get("metas", {}).get("default", {}).get("records_count")
    if not isinstance(nombre_attendu, int) or isinstance(nombre_attendu, bool):
        raise ValueError("Nombre de lignes absent des métadonnées de l'API.")

    with open(sys.argv[1], encoding="utf-8-sig", newline="") as fichier:
        lecteur = csv.reader(fichier, delimiter=";", strict=True)
        entetes = next(lecteur, None)
        if entetes != colonnes_attendues:
            print(
                "Erreur : les colonnes reçues ne correspondent pas au schéma "
                f"attendu par le notebook Bronze : {entetes!r}",
                file=sys.stderr,
            )
            sys.exit(1)
        nombre_lignes = 0
        for numero, ligne in enumerate(lecteur, start=2):
            if len(ligne) != len(colonnes_attendues):
                raise ValueError(
                    f"Ligne CSV {numero} : {len(ligne)} champs reçus, "
                    f"{len(colonnes_attendues)} attendus."
                )
            nombre_lignes += 1
        if nombre_lignes != nombre_attendu:
            raise ValueError(
                f"{nombre_lignes:,} lignes reçues, {nombre_attendu:,} annoncées par l'API."
            )
        if nombre_lignes < 2_000_000:
            print("Erreur : moins de 2 000 000 lignes de données.", file=sys.stderr)
            sys.exit(1)
        print(f"CSV validé : {nombre_lignes:,} lignes, 10 champs par ligne.")
except (OSError, UnicodeError, csv.Error, json.JSONDecodeError, ValueError) as erreur:
    print(f"Erreur : impossible de valider le CSV : {erreur}", file=sys.stderr)
    sys.exit(1)
PY
then
    exit 1
fi

if [ "$FORCE" -eq 1 ]; then
    mv -f "$TEMP_FILE" "$OUTPUT"
else
    if ! ln "$TEMP_FILE" "$OUTPUT"; then
        echo "Erreur : $OUTPUT existe déjà. Utilisez --force pour le remplacer." >&2
        exit 1
    fi
    rm -f "$TEMP_FILE"
fi

echo "CSV téléchargé et vérifié : $OUTPUT"
