# home.py
import pandas as pd
import plotly.express as px
import streamlit as st

# -- Konfiguration der Streamlit-Seite
st.set_page_config(
    page_title="SWM Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.sidebar.image("https://bilder.sponet.de/iks/IAT_Logo_RGB.png")
st.sidebar.header("Willkommen auf dem interaktiven Dashboard von SWM! 📊📈", divider="rainbow")
st.sidebar.markdown("Hier erhalten Sie auf einen Blick wertvolle Einblicke und Datenvisualisierungen zu wichtigen "
                    "Kennzahlen das Fachbereichs. Mit den folgenden Optionen können die Daten entsprechend gefiltert "
                    "werden.")


@st.cache_data
def get_sponet_export_csv():
    sponet_raw_df = pd.read_csv('C:/Users/bruening/Desktop/QMQS-All.csv', sep=';', header=None)
    # sponet_raw_df = pd.read_csv('//iat/iks/db/exporte/SPONET-QMQS/QMQS-All.csv', sep=';', header=None)
    sponet_raw_df.columns = ['ID', 'ZS-Titel', 'originaler Titel', 'ausgewertet von', 'ausgewertet am', 'ZS-Auswerter',
                             'ZS-korrigiert am', 'Deskriptoren', 'Tagging']
    return sponet_raw_df


@st.cache_data
def fetch_journals_from_raw(_sponet_raw_df):
    return _sponet_raw_df.drop(
        columns=['ID', 'originaler Titel', 'ausgewertet von', 'ausgewertet am', 'Deskriptoren',
                 'Tagging']).drop_duplicates()


@st.cache_data
def fetch_records_from_raw(_sponet_raw_df):
    sponet_records_raw_df = _sponet_raw_df.drop(
        columns=['ID', 'ZS-Titel', 'originaler Titel', 'ZS-Auswerter', 'ZS-korrigiert am',
                 'Deskriptoren', 'Tagging'])
    sponet_records_raw_df['ausgewertet am'] = pd.to_datetime(sponet_records_raw_df['ausgewertet am'])
    sponet_records_raw_df.rename(columns={'ausgewertet von': 'auswerter', 'ausgewertet am': 'datum'}, inplace=True)
    return sponet_records_raw_df


@st.cache_data
def fetch_topics_per_year_from_raw(_sponet_raw_df):
    sponet_topics_raw_df = _sponet_raw_df.drop(
        columns=['ID', 'ZS-Titel', 'originaler Titel', 'ausgewertet von', 'ZS-Auswerter', 'ZS-korrigiert am',
                 'Tagging'])
    sponet_topics_raw_df['ausgewertet am'] = pd.to_datetime(sponet_topics_raw_df['ausgewertet am'])
    sponet_topics_raw_df.rename(columns={'ausgewertet am': 'datum'}, inplace=True)

    sponet_topics_raw_df['Jahr'] = sponet_topics_raw_df['datum'].dt.year
    deskriptoren = sponet_topics_raw_df['Deskriptoren'].str.split(';', expand=True)
    sponet_topics_raw_df = pd.concat([sponet_topics_raw_df, deskriptoren], axis=1)

    # Verarbeiten Sie die Daten, um sie in das gewünschte Format zu bringen
    topics_per_year_df = sponet_topics_raw_df.melt(id_vars=['Jahr'], value_vars=list(sponet_topics_raw_df.columns[7:]))
    topics_per_year_df = topics_per_year_df[topics_per_year_df['value'].notnull()]
    topics_per_year_df = topics_per_year_df.groupby(['Jahr', 'value']).size().unstack().fillna(0)
    return topics_per_year_df


@st.cache_data
def fetch_tagging_per_year_from_raw(_sponet_raw_df):
    sponet_tagging_raw_df = _sponet_raw_df.drop(
        columns=['ID', 'ZS-Titel', 'originaler Titel', 'ausgewertet von', 'ZS-Auswerter', 'ZS-korrigiert am',
                 'Deskriptoren'])
    sponet_tagging_raw_df['ausgewertet am'] = pd.to_datetime(sponet_tagging_raw_df['ausgewertet am'])
    sponet_tagging_raw_df.rename(columns={'ausgewertet am': 'datum'}, inplace=True)

    sponet_tagging_raw_df['Jahr'] = sponet_tagging_raw_df['datum'].dt.year
    deskriptoren = sponet_tagging_raw_df['Deskriptoren'].str.split(';', expand=True)
    sponet_tagging_raw_df = pd.concat([sponet_tagging_raw_df, deskriptoren], axis=1)

    # Verarbeiten Sie die Daten, um sie in das gewünschte Format zu bringen
    taggings_per_year_df = sponet_tagging_raw_df.melt(id_vars=['Jahr'],
                                                      value_vars=list(sponet_tagging_raw_df.columns[7:]))
    taggings_per_year_df = taggings_per_year_df[taggings_per_year_df['value'].notnull()]
    taggings_per_year_df = taggings_per_year_df.groupby(['Jahr', 'value']).size().unstack().fillna(0)
    return taggings_per_year_df


def zscore(x, window):
    r = x.rolling(window=window)
    m = r.mean().shift(1)
    s = r.std(ddof=0).shift(1)
    z = (x - m) / s
    return z


@st.cache_data
def get_filtered_records(records, date_von, date_bis, auswerter):
    if date_von and date_bis:
        records = records[
            (records['datum'] >= pd.to_datetime(date_von)) &
            (records['datum'] <= pd.to_datetime(date_bis))]

    if auswerter:
        records = records[records['auswerter'].isin(auswerter)]

    return records


def prepare_bar_chart(data, x, y, color, x_label, y_label):
    barchart = px.bar(data, x=x, y=y, color=color, labels={x: x_label, y: y_label})
    barchart.update_layout(barmode='group')
    return barchart


# -- Zeitschriften oder Auswertungen
option_kpi = st.sidebar.selectbox("Wähle aus den folgenden Optionen", ["Zeitschriften", "Auswertungen", "Themen"])
sponet_df = get_sponet_export_csv()

match option_kpi:
    case "Auswertungen":
        # -- Verbinde und lade alle Nachweise
        df_records = fetch_records_from_raw(sponet_df)

        # -- Datum von, bis basierend auf min, max Auswertungsdatum der Rohdaten
        date_von_records_auswerter = st.sidebar.date_input(
            "Von", pd.to_datetime(df_records['datum'].min()), format="DD.MM.YYYY")
        date_bis_records_auswerter = st.sidebar.date_input(
            "Bis", pd.to_datetime(df_records['datum'].max()), format="DD.MM.YYYY")
        # -- Auswerter basierend auf gewählter Betrachtungszeitraum
        df_records = df_records[
            (df_records['datum'] >= pd.to_datetime(date_von_records_auswerter)) &
            (df_records['datum'] <= pd.to_datetime(date_bis_records_auswerter))]
        # -- Nur eindeutige Auswerter für Dropdownmenü
        df_records_unique_auswerter = df_records[df_records['auswerter'].str.len() > 0]['auswerter'].unique()
        option_records_auswerter = st.sidebar.multiselect("Wähle einen Auswerter", df_records_unique_auswerter)

        filtered_df_records = get_filtered_records(
            df_records, date_von_records_auswerter, date_bis_records_auswerter, option_records_auswerter)

        st.subheader(
            f"🔑 Key facts für den Zeitraum **{date_von_records_auswerter}** bis **{date_bis_records_auswerter}**")

        st.markdown(f"- 📕 Nachweise: **{len(filtered_df_records)}**")
        st.markdown(f"- 👩‍💻 Personen: **{len(filtered_df_records['auswerter'].unique())}**")
        st.divider()

        c11, c12 = st.columns([3, 1])
        with c11:
            st.subheader("📊 Summe über gewählten Zeitraum")
            absolut_filtered_df_records = filtered_df_records['auswerter'].value_counts().reset_index()
            absolut_filtered_df_records.columns = ['Auswerter', 'Anzahl']
            fig = prepare_bar_chart(
                absolut_filtered_df_records, x='Auswerter', y='Anzahl', color=None, x_label='Auswerter',
                y_label='Anzahl')
            st.plotly_chart(fig, theme="streamlit", use_container_width=True)
        with c12:
            st.dataframe(absolut_filtered_df_records, use_container_width=True, hide_index=True)
            st.caption(
                f"Absolute Anzahl Erfassungen pro Auswerter für den Zeitraum {date_von_records_auswerter} "
                f"bis {date_bis_records_auswerter}.")

        st.divider()
        c21, c22 = st.columns([3, 1])
        with c21:
            st.subheader("📈 Monatliche Entwicklung für den gewählten Zeitraum")
            monthly_filtered_df_records = filtered_df_records.groupby(
                [filtered_df_records['auswerter'], pd.Grouper(key='datum', freq='M')]).size().reset_index(name='count')
            monthly_filtered_df_records.columns = ['Auswerter', 'Datum', 'Anzahl']
            fig = prepare_bar_chart(monthly_filtered_df_records, x='Datum', y='Anzahl', color='Auswerter',
                                    x_label='Monat', y_label='Auswertungen')
            st.plotly_chart(fig, theme="streamlit", use_container_width=True)

        with c22:
            st.dataframe(monthly_filtered_df_records, use_container_width=True, hide_index=True)
            st.caption(
                f"Anteilige monatliche Anzahl Erfassungen pro Auswerter für den Zeitraum {date_von_records_auswerter} "
                f"bis {date_bis_records_auswerter}.")

        st.divider()
        c31, c32 = st.columns([3, 1])
        with c31:
            st.subheader("📈 Quartalsweise Entwicklung für den gewählten Zeitraum")
            quarterly_filtered_df_records = filtered_df_records.groupby(
                [filtered_df_records['auswerter'], pd.Grouper(key='datum', freq='Q')]).size().reset_index(name='count')
            quarterly_filtered_df_records.columns = ['Auswerter', 'Datum', 'Anzahl']
            fig = prepare_bar_chart(quarterly_filtered_df_records, x='Datum', y='Anzahl', color='Auswerter',
                                    x_label='Quartal', y_label='Auswertungen')
            st.plotly_chart(fig, theme="streamlit", use_container_width=True)
        with c32:
            st.dataframe(quarterly_filtered_df_records, use_container_width=True, hide_index=True)
            st.caption(
                f"Anteilige quartalsweise Anzahl Erfassungen pro Auswerter für den Zeitraum {date_von_records_auswerter} "
                f"bis {date_bis_records_auswerter}.")

        st.divider()
        c41, c42 = st.columns([3, 1])
        with c41:
            st.subheader("📈📉 Erfassungstrend der Hilfskräfte")
            query_hiwis = 'prakt-swm'
            monthly_filtered_hiwi_df_records = monthly_filtered_df_records[
                monthly_filtered_df_records['Auswerter'].str.contains(query_hiwis, case=False, regex=True)]
            monthly_filtered_hiwi_df_records.columns = ['Auswerter', 'Datum', 'Anzahl']
            fig = prepare_bar_chart(monthly_filtered_hiwi_df_records, x='Datum', y='Anzahl', color='Auswerter',
                                    x_label='Monat', y_label='Auswertungen')
            fig.add_hrect(y0=0, y1=60, line_width=0, fillcolor="red", opacity=0.1)
            fig.add_hline(y=120, line_dash="dot",
                          annotation_text="SOLL für 40h",
                          annotation_position="bottom right")
            st.plotly_chart(fig, theme="streamlit", use_container_width=True)

        with c42:
            st.dataframe(monthly_filtered_hiwi_df_records, use_container_width=True, hide_index=True)
            st.caption(
                f"Anteilige monatliche Anzahl Erfassungen pro Auswerter für den Zeitraum {date_von_records_auswerter} "
                f"bis {date_bis_records_auswerter}.")

    case "Zeitschriften":
        # -- Verbinde und lade alle Zeitschriften
        df_journals = fetch_journals_from_raw(sponet_df)

        # -- Nur eindeutige Erfasser von Zeitschriften für Dropdownmenü
        df_journals_unique_auswerter = df_journals[df_journals['ZS-Auswerter'].str.len() > 0]['ZS-Auswerter'].unique()
        option_journals_auswerter = st.sidebar.multiselect("Wähle einen Auswerter", df_journals_unique_auswerter)
        toggle_journals_all = st.sidebar.toggle("Alle erfassten Zeitschriften", False,
                                                disabled=any(option_journals_auswerter))

        # -- Filtere die Zeitschriftendaten nach den ausgewählten optionen
        if any(option_journals_auswerter):
            filtered_df_journals = df_journals[df_journals['ZS-Auswerter'].isin(option_journals_auswerter)]

        elif not toggle_journals_all:
            filtered_df_journals = df_journals[df_journals['ZS-Auswerter'].str.len() > 0]

        else:
            filtered_df_journals = df_journals

        st.subheader(
            f"🔑 Key facts über ausgewerteten Zeitschriften in SPONET")

        st.markdown(
            f"- 📕 Zeitschriften: insgesamt **{len(df_journals)}** und davon **{len(filtered_df_journals['ZS-Auswerter'])}** in regelmäßiger Beobachtung")
        st.markdown(f"- 👩‍💻 Personen: **{len(filtered_df_journals['ZS-Auswerter'].unique())}**")
        st.divider()

        col1, col2 = st.columns([2, 2])
        with col1:
            st.subheader("📊 Zeitschriftenverteilung")
            # Anzahl der Einträge pro Autor aggregieren
            autor_count = filtered_df_journals['ZS-Auswerter'].value_counts(dropna=False).reset_index()
            autor_count.columns = ['Auswerter', 'Anzahl']

            fig = px.pie(autor_count, names='Auswerter', values='Anzahl')
            st.plotly_chart(fig, theme="streamlit", use_container_width=True)

        with col2:
            st.dataframe(filtered_df_journals, use_container_width=True, hide_index=True)
            st.caption(f"Zeitschriften pro Auswerter.")

    case "Themen":
        df_topics = fetch_topics_per_year_from_raw(sponet_df)
        st.dataframe(df_topics)

        df_topics_trending = zscore(df_topics, 3)
        st.dataframe(df_topics_trending)

        fig = px.line(df_topics_trending, x=df_topics_trending.index, y=df_topics_trending.columns, log_x=True,
                      log_y=True)
        # Legen Sie die Achsentitel fest
        fig.update_xaxes(title_text="Jahr")
        fig.update_yaxes(title_text="Anzahl")
        # Legen Sie den Diagrammtitel fest
        fig.update_layout(title_text="Anzahl der Deskriptoren pro Jahr (Linienchart)")
        # Zeigen Sie das Diagramm an
        st.plotly_chart(fig, theme="streamlit", use_container_width=True)

    case _:
        st.write("Not defined")
