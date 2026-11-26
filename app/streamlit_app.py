import os

import altair as alt
import pandas as pd
import psycopg
import streamlit as st


st.set_page_config(page_title="Mobilité à Paris", layout="wide")
st.title("Comptages multimodaux à Paris")
st.markdown(
    "Explorez les volumes et les horaires observés pour identifier les sites à examiner. "
    "Un volume élevé ne mesure pas à lui seul la saturation : la durée de collecte "
    "et la capacité des voies ne sont pas connues."
)


@st.cache_data(ttl=60)
def charger_tables():
    noms = (
        "gold_sites_classement",
        "gold_serie_mensuelle",
        "gold_heatmap_heure_jour",
        "gold_kpi",
    )
    tables = {}
    with psycopg.connect(
        host=os.environ["PG_HOST"],
        dbname=os.environ["PG_DB"],
        user=os.environ["PG_USER"],
        password=os.environ["PG_PASSWORD"],
        connect_timeout=5,
    ) as connexion:
        with connexion.cursor() as curseur:
            for nom in noms:
                curseur.execute(psycopg.sql.SQL("SELECT * FROM {}").format(psycopg.sql.Identifier(nom)))
                colonnes = [col.name for col in curseur.description]
                tables[nom] = pd.DataFrame(curseur.fetchall(), columns=colonnes)
    return tables


try:
    tables = charger_tables()
except psycopg.Error as erreur:
    st.error(f"Impossible de lire les tables Gold dans PostgreSQL : {erreur}")
    st.info("Exécutez d'abord les notebooks Gold et d'export PostgreSQL.")
    st.stop()

sites = tables["gold_sites_classement"]
mensuel = tables["gold_serie_mensuelle"]
profil = tables["gold_heatmap_heure_jour"]
kpi = tables["gold_kpi"]
if any(table.empty for table in (sites, mensuel, profil, kpi)):
    st.error("Une table Gold est vide. Vérifiez la production et l'export Gold.")
    st.stop()

st.header("Vue d'ensemble")
st.caption("Les cinq indicateurs ci-dessous couvrent toute la période et tous les modes, indépendamment des filtres.")
colonnes = st.columns(5)
for colonne, (_, indicateur) in zip(colonnes, kpi.sort_values("kpi_id").iterrows()):
    valeur = indicateur["valeur_texte"]
    if pd.isna(valeur):
        nombre = f'{indicateur["valeur_numerique"]:,.2f}'.rstrip("0").rstrip(".")
        valeur = f'{nombre} {indicateur["unite"]}'
    colonne.metric(indicateur["libelle"], str(valeur), help=indicateur["definition"])

st.sidebar.header("Filtres")
annees = sorted(int(a) for a in mensuel["annee"].dropna().unique())
modes = sorted(mensuel["mode_deplacement"].dropna().unique())
annees_choisies = st.sidebar.multiselect("Années", annees, default=annees)
modes_choisis = st.sidebar.multiselect("Modes", modes, default=modes)
if not annees_choisies or not modes_choisis:
    st.warning("Sélectionnez au moins une année et un mode.")
    st.stop()

series = mensuel[mensuel["annee"].isin(annees_choisies) & mensuel["mode_deplacement"].isin(modes_choisis)].copy()
classement = sites[sites["annee"].isin(annees_choisies) & sites["mode_deplacement"].isin(modes_choisis)].copy()
if series.empty or classement.empty:
    st.warning("Aucun comptage pour cette sélection.")
    st.stop()

st.header("Comment les volumes évoluent-ils ?")
st.caption("Sommes mensuelles relevées ; les variations peuvent aussi refléter la couverture des capteurs.")
series["date"] = pd.to_datetime(dict(year=series["annee"], month=series["mois"], day=1))
st.altair_chart(
    alt.Chart(series).mark_line(point=True).encode(
        x=alt.X("date:T", title="Mois"),
        y=alt.Y("total_usagers:Q", title="Véhicules comptés"),
        color=alt.Color("mode_deplacement:N", title="Mode"),
        tooltip=["date:T", "mode_deplacement:N", "total_usagers:Q", "nb_sites_actifs:Q"],
    ).interactive(),
    use_container_width=True,
)

st.header("Quels sites examiner ?")
st.caption("Classement par volume cumulé sur la sélection, tous types de voie confondus.")
classement["site"] = classement["nom_du_site"].fillna("Site " + classement["identifiant_site"].astype(str))
top = (classement.groupby(["identifiant_site", "site"], as_index=False)["total_usagers"]
       .sum().nlargest(10, "total_usagers"))
st.altair_chart(
    alt.Chart(top).mark_bar().encode(
        x=alt.X("total_usagers:Q", title="Véhicules comptés"),
        y=alt.Y("site:N", sort="-x", title="Site"),
        tooltip=["identifiant_site:N", "site:N", "total_usagers:Q"],
    ).interactive(),
    use_container_width=True,
)

st.subheader("Carte des sites aux volumes les plus élevés")
sites_cartographiables = classement.dropna(subset=["latitude", "longitude"]).copy()
sites_cartographiables = sites_cartographiables[
    sites_cartographiables["latitude"].between(-90, 90)
    & sites_cartographiables["longitude"].between(-180, 180)
]
carte = (sites_cartographiables
         .groupby(["identifiant_site", "site", "latitude", "longitude"], as_index=False)["total_usagers"]
         .sum().nlargest(10, "total_usagers"))
if carte.empty:
    st.warning("Aucun site de cette sélection ne possède de coordonnées valides.")
else:
    st.caption(
        f"Les 10 sites cartographiables les plus élevés parmi "
        f"{sites_cartographiables['identifiant_site'].nunique()} sites géolocalisés. "
        "Les sites sans coordonnées restent présents dans le classement, mais pas sur la carte."
    )
    st.map(
        carte,
        latitude="latitude",
        longitude="longitude",
        size="total_usagers",
        color="#3B82F6",
        zoom=11,
    )
    site_a_examiner = carte.iloc[0]
    st.info(
        f"**Piste d'analyse :** examiner d'abord « {site_a_examiner['site']} », "
        f"qui présente le volume cumulé le plus élevé parmi les sites cartographiables "
        f"({site_a_examiner['total_usagers']:,.0f} véhicules comptés). "
        "Comparer les périodes et durées de mesure, puis vérifier la couverture des capteurs "
        "et la capacité de la voie avant toute décision d'aménagement."
    )

st.header("À quels moments les comptages sont-ils élevés ?")
st.caption("Profil calculé sur toutes les années ; seul le filtre de mode s'applique à ce graphique.")
profil = profil[profil["mode_deplacement"].isin(modes_choisis)]
jours = {1: "Dim", 2: "Lun", 3: "Mar", 4: "Mer", 5: "Jeu", 6: "Ven", 7: "Sam"}
profil = profil.copy()
profil["jour"] = profil["jour_semaine"].map(jours)
st.altair_chart(
    alt.Chart(profil).mark_rect().encode(
        x=alt.X("heure:O", title="Heure"),
        y=alt.Y("jour:N", sort=list(jours.values()), title="Jour"),
        color=alt.Color("moyenne_par_heure:Q", title="Moyenne / site-heure"),
        column=alt.Column("mode_deplacement:N", title="Mode"),
        tooltip=["mode_deplacement:N", "jour:N", "heure:O", "moyenne_par_heure:Q", "nb_sites_heures_mesurees:Q"],
    ),
    use_container_width=True,
)
