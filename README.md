# Online-Marktplatz Praktikum

Dieses Verzeichnis enthält die Codebasis und Dokumentation für das Praktikum im Modul Algorithmik.

## Projektübersicht

Der Online-Marktplatz ist eine Python-Anwendung mit einer Tkinter-GUI, die Kernkonzepte aus Datenstrukturen und Algorithmen demonstriert (Mengen, Trees, Heaps, Hashtabellen, Graphen etc.).

## Installation und Abhängigkeiten

Das Projekt benötigt Python (>= 3.11) sowie externe Bibliotheken wie `osmnx` für geografische Distanz- und Routenberechnungen. Sie können die Abhängigkeiten entweder über `pip` oder über eine Anaconda/Conda-Umgebung installieren.

### Option 1: Installation über Pip

1. Stellen Sie sicher, dass Python 3.11 oder neuer installiert ist.  
1. Installieren Sie die erforderlichen Pakete mit `pip`:  

```bash
pip install -r requirements.txt
```

Alternativ können Sie das Paket im Editier-Modus installieren:

```bash
pip install -e .
```

### Option 2: Installation über Anaconda / Conda

Falls Sie Anaconda oder Miniconda verwenden, können Sie die bereitgestellte `environment.yml` nutzen:

1. Erstellen Sie die Conda-Umgebung:  

```bash
conda env create -f environment.yml
```

1. Aktivieren Sie die Umgebung:  

```bash
conda activate marketplace
```

## Aufgabenstellung und Dokumentation

Die vollständige Aufgabenstellung sowie Beschreibungen zu allen drei Teilprojekten finden Sie im Ordner `docs/`:

- [Aufgabenstellung Übersicht](docs/index.md)  
- [GUI Benutzerhandbuch (User Manual)](docs/gui_user_manual.md)  
- [Teilprojekt 1: Projektanalyse und Verständnis](docs/teilprojekt_1.md)  
- [Teilprojekt 2: Erweiterung der Artikel- und Auktionsverwaltung](docs/teilprojekt_2.md)  
- [Teilprojekt 3: Freundesverwaltung, Gebotsagenten und Empfehlungssystem](docs/teilprojekt_3.md)  

## Anwendung starten

Um die Anwendung zu starten, führen Sie im entpackten Ordner `marketplace` (dort liegen auch `user.csv`, `friends.csv` und `auctions.csv`) folgenden Befehl aus:

```bash
python gui_marketplace.py
```

Standardmäßig können Sie sich mit Ihrer GM-ID und dem Passwort `abcde` anmelden.

## Tests ausführen

Eigene Unit-Tests für Ihre Implementierungen können Sie im Ordner `tests/` anlegen (Dateinamen `test_*.py`) und mit `pytest` ausführen:

```bash
pytest tests/
```
