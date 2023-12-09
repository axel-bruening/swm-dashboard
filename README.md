# SWM-Dashboard

SWM-Dashboard ist ein Streamlit-basiertes Projekt für die grafische Aufbereitung von KPI aus der TG Wissensmanagement des IAT.

## Installation

### Lokale Installation

1. Klone das Repository:

    ```bash
    git clone https://github.com/axel-bruening/swm-dashboard.git
    cd swm-dashboard
    ```

2. Installiere die erforderlichen Pakete mit pip:

    ```bash
    pip install -r requirements.txt
    ```

3. Führe die Anwendung aus:

    ```bash
    streamlit run home.py
    ```

    Öffne deinen Webbrowser und gehe zu [http://localhost:8501](http://localhost:8501), um das Dashboard zu sehen.

### Verwendung mit Docker

1. Baue das Docker-Image:

    ```bash
    docker build -t swm-dashboard-app .
    ```

2. Starte den Docker-Container:

    ```bash
    docker run -p 8501:8501 swm-dashboard-app
    ```

    Öffne deinen Webbrowser und gehe zu [http://localhost:8501](http://localhost:8501), um das Dashboard zu sehen.

## Beitrag

Wenn Sie zur Entwicklung beitragen möchten, lesen Sie bitte unsere [Beitragshinweise](CONTRIBUTING.md).

## Anforderungen

Alle erforderlichen Pakete und deren Versionen sind in der `requirements.txt`-Datei aufgeführt. Sie können sie mit dem folgenden Befehl installieren:

```bash
pip install -r requirements.txt