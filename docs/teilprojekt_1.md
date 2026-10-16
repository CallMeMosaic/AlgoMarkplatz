---
nav_exclude: true
---

# Teilprojekt 1: Projektanalyse und Verständnis

[Zurück zur Übersicht](index.md)

## Ziele

- Vertraut machen mit dem bestehenden Code.  
- Beantwortung grundlegender Fragen zum Code und den verwendeten Datenstrukturen.  

## Aufgaben

### 1. Code-Analyse

- Laden Sie die bereitgestellte Rohversion des Online-Marktplatzes herunter, starten Sie das Programm mit `python gui_marketplace.py` und testen Sie das Programm. Ihr Nutzername ist Ihre GM-ID und das Passwort ist `abcde`.  
- Machen Sie sich mit der Struktur und den Hauptkomponenten des Projekts vertraut. Schauen Sie sich dafür insbesondere diese Dateien an:  
  1. `user.py`, `praktikumsgruppen.py`, `users.py`  
  2. `auction.py`, `auctions.py`, `item.py`, `stack.py`  
  3. `systemmessages.py`, `trie.py`  

### 2. Analyse der ADTs und Datenstrukturen

- In welcher Datenstruktur sind die Nutzer des Marktplatzes gespeichert? Schauen Sie sich dafür `users.py` und `praktikumsgruppen.py` an. Erweitern Sie die Klasse `SetNode` in `praktikumsgruppen.py` um die private Membervariable `_praktikumsgruppe` und implementieren Sie die Methoden `create_groups()` und `get_groupmembers()` in `praktikumsgruppen.py`.  
- Welche Laufzeit hat aufgrund der gewählten Datenstruktur ein Zugriff auf einen bestimmten Nutzer des Marktplatzes? Welche Laufzeit hat die Methode `get_groupmembers()` in Abhängigkeit der Anzahl Nutzer des Marktplatzes?  
- In welchem ADT werden alle Auktionen gespeichert und als welche Datenstruktur wird er implementiert? (s. `auctions.py`)  
- Welcher ADT wird in der Klasse `systemmessages.py` genutzt und warum? Als welche Datenstruktur wird der ADT implementiert?  
- Wie wird gespeichert in welcher Reihenfolge die Gebote auf eine Auktion abgegeben wurden? Wie erhält man das zuletzt abgegebene Gebot? (s. `auction.py`)  
- Wenn Sie nach einem Produkt suchen, werden Ihnen in einem Tooltip Autoergänzungsvorschläge angezeigt, auf die Sie klicken können. Die Datenstruktur dahinter ist ein Trie, s. `trie.py`. Informieren Sie sich über Tries (s. Vorlesungsfolien). Erweitern Sie die Initialisierung des Tries so, dass Sie im Suchfeld auch nach Nutzer-IDs suchen können (s. `auctionapp_init.py`: `initialize_trie()`).  
- Diese Autoergänzung kann auch durch einen AVL-Baum implementiert werden. Schauen Sie sich die Klasse `AVLTree` in `avl_tree.py` an und dort insbesondere die Methode `find_most_likely_words()`. Ändern Sie die Methode `show_suggestions()` in `auctionapp_init.py`, sodass die Vorschläge vom AVL-Baum genutzt werden. Können Sie Unterschiede in der Laufzeit zwischen der Trie- und der AVL-Baum-Implementierung feststellen?  

### 3. Hashfunktion verbessern

- Transaktionen (Verkäufer, Käufer, Preis, Zeitstempel, Produktname) werden in einer eigenen Hashtabelle gespeichert. Schauen Sie sich die implementierte Hashtabelle in `transactions.py` mit ihrer Hashfunktion an. Wie funktioniert die Hashfunktion? Was passiert bei einer Kollision?  
- Aktuell sorgt die Hashfunktion für viele Kollisionen. Verbessern Sie die Hashfunktion in der Klasse `Transactions` (s. `transactions.py`), sodass deutlich weniger Kollisionen passieren. Die Kollisionen werden alle 30 Sekunden über die Systemnachrichten mitgeteilt. Als Kollision zählt jedes Einfügen in einen Bucket, der bereits belegt ist. Die Hashtabelle hat 1024 Buckets: Überlegen Sie, wie viele Kollisionen bei n Transaktionen selbst mit einer idealen Hashfunktion zu erwarten sind.  

### 4. Dokumentation

- Erstellen Sie eine kurze Präsentation, in der die oben gestellten Fragen beantwortet werden.  
- Optional: Fügen Sie Kommentare im Code hinzu, um den Zweck und die Funktionsweise der Hauptfunktionen zu erklären.  
- Laden Sie den Code als ZIP-Datei und die Folien als PDF in Ihrer Gruppe hoch. Wir werden uns beides ansehen. Sie müssen es nicht im Praktikum präsentieren.  
