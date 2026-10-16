---
nav_exclude: true
---

# Online-Marktplatz: Projektbeschreibung und Aufgabenstellung

## Projektbeschreibung

Der Online-Marktplatz, den Sie entwickeln werden, soll eine voll funktionsfähige Plattform zum Kaufen und Verkaufen von Artikeln bieten. Nutzer können Artikel einstellen, auf Artikel bieten, Artikel kaufen und verkaufen sowie mit anderen Nutzern interagieren. Die Plattform bietet eine Vielzahl von Funktionen, um den Kauf- und Verkaufsprozess zu erleichtern und die Nutzererfahrung zu verbessern.

## Features des Marktplatzes

- **Benutzerverwaltung:** Registrierung, Login, Logout, Profilverwaltung.  
- **Freundesverwaltung:** Freunde hinzufügen und entfernen, Anzeige gemeinsamer Freunde.  
- **Artikelverwaltung:** Artikel hinzufügen, löschen, suchen und anzeigen.  
- **Auktionsverwaltung:** Bieten auf Artikel, Anzeige von Geboten, Anzeige gewonnener und verkaufter Artikel.  
- **Empfehlungssystem:** Anzeige empfohlener Artikel basierend auf dem Benutzerverhalten.  

## Übersicht der Teilprojekte

Das Projekt ist in drei Teilprojekte unterteilt, wobei Sie eine bereits implementierte Rohversion des Marktplatzes in Python erhalten. Zu den drei Praktikumsterminen stellen Sie das jeweilige Teilprojekt vor.

- [GUI Benutzerhandbuch (User Manual)](gui_user_manual.md)  
- [Teilprojekt 1: Projektanalyse und Verständnis](teilprojekt_1.md)  
- [Teilprojekt 2: Erweiterung der Artikel- und Auktionsverwaltung](teilprojekt_2.md)  
- [Teilprojekt 3: Freundesverwaltung, Gebotsagenten und Empfehlungssystem](teilprojekt_3.md)  

## Struktur des Rohprojekts

### Dateien, die Sie bearbeiten werden

- `praktikumsgruppen.py`: Sortiert Nutzer in Praktikumsgruppen ein. Editieren Sie im 1. und 3. Praktikum.  
- `max_heap.py`: Speichert die Auktionen in einem Heap. Editieren Sie im 2. Praktikum.  
- `users.py`: Definiert einen Container für alle Nutzer der Plattform. Editieren Sie im 3. Praktikum.  
- `auctions.py`: Definiert Container für alle Auktionen. Editieren Sie im 2. Praktikum.  
- `transactions.py`: Speichert die getätigten Transaktionen in eine Hashtabelle. Editieren Sie im 1. Praktikum.  
- `auctionapp_init.py`: Initialisiert die GUI. Editieren Sie im 1. Praktikum (`initialize_trie()`, `show_suggestions()`).  
- `simulator.py`: Simuliert Kauf- und Verkaufvorgänge sowie Bewertungen auf dem Marktplatz. Editieren Sie im 2. Praktikum (`randomly_rate_users()`).  
- `auction.py`: Definiert eine Auktion. Editieren Sie im 3. Praktikum, falls Sie die optionale Portoberechnung umsetzen.  

### Dateien, die Sie sich ansehen können

- `item.py`: Definiert ein Produkt, das ersteigert werden kann.  
- `stack.py`: Implementierung eines Stacks.  
- `user.py`: Definiert einen Nutzer des Marktplatzes.  
- `systemmessages.py`: Anzeige von Systemnachrichten auf der GUI.  
- `trie.py`: Implementierung der Datenstruktur Trie.  
- `avl_tree.py`: Implementierung eines AVL-Baums.  

### Unterstützende Dateien

- `gui_marketplace.py`: Enthält die main. Mit `python gui_marketplace.py` starten Sie die Anwendung.  

## Abschluss

Nach Abschluss der drei Teilprojekte sollten Sie eine umfassende, funktionsfähige und benutzerfreundliche Online-Marktplatz-Plattform entwickelt haben. Durch diese Aufteilung in drei Teilprojekte können Sie schrittweise die Komplexität des Projekts bewältigen und Ihre Kenntnisse in Datenstrukturen und Algorithmen vertiefen. Jedes Teilprojekt baut auf dem vorherigen auf und führt neue Konzepte ein, die für die erfolgreiche Implementierung des gesamten Systems notwendig sind.

Viel Erfolg!
