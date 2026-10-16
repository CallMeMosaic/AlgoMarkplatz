---
nav_exclude: true
---

# Teilprojekt 3: Freundesverwaltung, Gebotsagenten und Empfehlungssystem

[Zurück zur Übersicht](index.md)

## Ziele

- Implementierung und Verbesserung der Freundesverwaltung.  
- Einführung von intelligenten Gebotsagenten, die strategisch und optimiert bieten.  
- Entwicklung eines Empfehlungssystems basierend auf dem Nutzerverhalten.  

## Aufgaben

### 1. Freundesverwaltung

- Implementieren Sie eine Funktion, die dem Nutzer solche Nutzer als Freunde vorschlägt, die mit möglichst vielen seiner Freunde befreundet sind (s. `users.py`, `suggest_friends()`).  
- Schreiben Sie eine Funktion, die prüft, ob zwei Nutzer irgendwie über deren Freundesnetzwerk (ersten, zweiten, dritten Grades) verbunden sind (s. `users.py`, `are_users_connected()`).  
- Wie Sie evtl. bereits gesehen haben, haben wir für jeden Nutzer einen zufälligen Wohnort in NRW (oder in der Nähe) generiert. Berechnen Sie den Abstand von dem Wohnort Ihres Users zu dem Wohnort aller anderen Nutzer, mit denen Sie über mehrere Ecken befreundet sind, um sich weitere Nutzer als potenzielle Freunde empfehlen zu lassen. Der Abstand soll der Abstand sein, den Sie mit einem Fahrzeug zwischen beiden Wohnorten zurücklegen müssen. Nutzen Sie dafür die Bibliothek [osmnx](https://osmnx.readthedocs.io/en/stable/).  
- Beispiel-Code für `osmnx`:  

```python
import networkx as nx
import osmnx as ox

map_graph = ox.graph.graph_from_address(
    'Steinmüllerallee 1, Gummersbach, Germany', dist=5000, network_type='drive'
)
origin_point = (50.985108, 7.542490)  # Breiten- und Längengrad
destination_point = (51.022255, 7.562705)
origin = ox.distance.nearest_nodes(map_graph, origin_point[1], origin_point[0])
destination = ox.distance.nearest_nodes(
    map_graph, destination_point[1], destination_point[0]
)
shortest_path = ox.routing.shortest_path(
    map_graph, origin, destination, weight='length'
)
distance_m = nx.path_weight(map_graph, shortest_path, weight='length')  # Länge in Metern
```

- Hinweis: Die Wohnorte liegen über ganz NRW und Umgebung verteilt. Ein Straßengraph für dieses Gebiet ist sehr groß, der Download dauert lange und braucht viel Arbeitsspeicher. Laden Sie den Graphen deshalb nur einmal, speichern Sie ihn lokal (`ox.save_graphml()` / `ox.load_graphml()`) und berechnen Sie Distanzen nur für die Nutzer, die Sie tatsächlich benötigen. Für große Gebiete kann es außerdem helfen, nur größere Straßen zu laden (Parameter `custom_filter`).  

### 2. Portoberechnung (optionale Aufgabe)

- Das Porto für den Versand der Artikel sei proportional zu der Distanz zwischen Verkäufer und Käufer. Berechnen Sie für die Auktionen, auf die der Nutzer gerade bietet, das Porto (0,1 € pro 5 km) und geben Sie das Porto bei der Anzeige der Auktionen, auf die der Nutzer gerade bietet, an. Die Methode `calculate_portofee()` in `auction.py` kennt bisher weder den Käufer noch die Wohnorte, ihre Signatur dürfen Sie deshalb anpassen.  

### 3. Verwaltung der Studierenden in Praktikumsgruppen

- Schauen Sie sich die Datei `praktikumsgruppen.py` an und implementieren Sie die Klasse `Praktikumsgruppen` als Menge von disjunkten Mengen. Nutzen Sie weighted Quick-Union mit Pfadverkürzung.  
- Bei dieser Implementierung können Sie die `SetNode`-Klasse nutzen. In dieser können Sie die in Praktikum 1 hinzugefügte Membervariable `_praktikumsgruppe` wieder auskommentieren. Sie müssen auch die Methoden `create_groups()` und `get_groupmembers()` in `praktikumsgruppen.py` neu implementieren.  
- Erläutern Sie, wie zwei Praktikumsgruppen zusammengelegt werden können. Was passiert in der Menge der disjunkten Menge?  

### 4. Dokumentation

- Erstellen Sie eine kurze Präsentation, in der Sie die oben gestellten Fragen beantworten und Ihren Code präsentieren.  
- Laden Sie den Code als ZIP-Datei und die Folien als PDF in Ihrer Gruppe hoch. Wir werden uns beide ansehen. Sie müssen es nicht im Praktikum präsentieren.  
