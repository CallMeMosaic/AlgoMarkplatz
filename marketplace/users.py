"""Übersicht über den Dateiinhalt:

Die Klasse Users verwaltet alle Benutzer des Online-Marktplatzes.
Sie erbt von `Praktikumsgruppen` und liest Benutzer- sowie Freundschaftsdaten
aus den CSV-Dateien (`user.csv`, `friends.csv`) ein. Sie stellt Methoden zur
Passwortüberprüfung, Freundschaftsempfehlung, Abstands- und Verbindungsberechnung bereit.
"""

# Status: FINAL, dgaida2, 15.10.2024

# definiert die Klasse Users.
# Users ist eine Menge von disjunkten Mengen (nur für drittes Praktikum) von der Klasse User,
# damit man Users in Praktikumsgruppen einsortieren kann. Für das erste und zweite Praktikum ist die Klasse
# Praktikumsgruppe lediglich ein Dictionary
# in der Klasse werden die csv-Dateien user.csv und friends.csv gelesen.

from typing import Any, Dict, List, Optional, Tuple, Union
import ast
from collections import deque
import csv
import math
from pathlib import Path

from scipy.optimize import check_grad

import marketplace.user
import marketplace.praktikumsgruppen

import networkx as nx
import osmnx as ox


class Users(marketplace.praktikumsgruppen.Praktikumsgruppen):
    # COMMENT:
    """
    Users extends the class Praktikumsgruppen. This is an ADT of Type: Dictionary as it saves a key (user_id) and a value (object of type User)
                                                            Datastructure: Is a HashTable, as it inherits the implementation from python's dict, which
                                                            implements the dict class as a HasTable. To be Specific it uses Open Addressing. Since
                                                            it inherits directly from the python dict, it is also efficiently implemented using C.

                                                             Θ(1) for Insertion, Deletion and Lookup.
                                                             Θ(n) if collision or expansion needed.
                                                             Generally grabbing an item is instantaneous Θ(n)
    """
    """Klasse zur Verwaltung aller registrierten Benutzer und ihrer Freundschaften.

    Attributes:
        _groupnumbers (List[int]): Liste der Gruppennummern der eingelesenen Benutzer.
    """

    map_graph = None

    # *** CONSTRUCTORS ***
    def __init__(self, csvfile: str, *args: Any) -> None:
        """Initialisiert das Users-Objekt und liest Daten aus CSV-Dateien ein.

        Args:
            csvfile (str): Pfad zur Benutzer-CSV-Datei (z. B. 'user.csv').
            *args (Any): Variable Argumente.

        Raises:
            FileNotFoundError: Falls die CSV-Datei nicht gefunden wurde.
        """
        super().__init__()

        self._read_users_from_csvfile(csvfile)
        self._read_friends_csv('friends.csv')

        # erstelle Praktikumsgruppen als Menge disjunkter Mengen bzw. als dictionary (1. und 2. Praktikum)
        super().create_groups(list(self.keys()), self._groupnumbers)

        # Der Straßengraph wird erst für eine gültige Distanzabfrage geladen.

    # *** PUBLIC SET methods ***

    # *** PUBLIC methods ***

    def add(self,
            user_id: str,
            password: str,
            name_family: str = "",
            name_first: str = "",
            gps_coord: Tuple[Optional[float],
            Optional[float]] = (None, None),
            address: str = ""
            ) -> None:
        """Adds the given user with user_id to the internal dictionary.

        Args:
            user_id (str): GM-ID / unique user identifier.
            password (str): Password of user.
            name_family (str, optional): Family name of user. Defaults to "".
            name_first (str, optional): First name of user. Defaults to "".
            gps_coord (tuple, optional): (latitude, longitude) coordinates. Defaults to (None, None).
            address (str, optional): Address string corresponding to GPS coordinates. Defaults to "".
        """
        self[user_id] = marketplace.user.User(user_id, password, name_family, name_first, gps_coord, address)

    def load_graph(self) -> None:
        """Lädt den Fahrstraßengraphen einmalig aus GraphML oder von OpenStreetMap.

        Ein bereits gesetzter Graph wird unverändert weiterverwendet. Ohne Cache
        wird wie im Projektbeispiel das Gebiet um Gummersbach (dist=5000) geladen.
        Download- und Dateifehler werden an den Aufrufer weitergegeben.
        """
        if self.map_graph is not None:
            return

        # GraphML erhält Kantenlängen und parallele Straßen; OSM-XML ist kein GraphML.
        graph_path = Path('nrw_map_graph.graphml')
        if graph_path.is_file():
            self.map_graph = ox.load_graphml(graph_path)
        else:
            filter = '["highway"~"motorway|motorway_link|trunk|trunk_link|primary|primary_link"|secondary|secondary_link]'
            # Explanation:
            """
            This filters for motorways (which are Autobahnen), trunk roads (which are like some bundesstraßen), primary road
            (whihc most bundesstraßen are labeled as on OSM) and their corresponding linkages so that a route can be established.
            Anything small is left out for loading time and size of the graph.
            """

            map_graph = ox.graph.graph_from_place(
                'North Rhine-Westphalia',
                network_type='drive',
                custom_filter=filter
            )
            ox.save_graphml(map_graph, graph_path)
            self.map_graph = map_graph

    def calc_distance_between_users(self, user_id1: str, user_id2: str) -> float:
        """Berechnet die kürzeste Fahrstrecke im geladenen Straßennetz.

        Die GPS-Punkte werden auf die nächsten Straßenknoten abgebildet; Wege
        vom Wohnort zu diesen Knoten zählen nicht mit. Einbahnstraßen werden
        berücksichtigt, daher können Hin- und Rückweg verschieden lang sein.
        Der Standardgraph deckt nur Gummersbach ab, nicht ganz NRW. Auch Punkte
        außerhalb werden auf diesen Graphen abgebildet; für solche Wohnorte
        muss ein ausreichend großer Graph als map_graph bereitgestellt werden.

        Args:
            user_id1: ID des ersten Benutzers
            user_id2: ID des zweiten Benutzers

        Returns:
            float: Minimale Summe der Straßenkantenlängen in Metern.
                  Gibt unendlich zurück, falls Benutzer oder gültige Koordinaten
                  fehlen oder kein gerichteter Pfad gefunden wird.
        """
        if user_id1 not in self or user_id2 not in self:
            return float('inf')

        user1 = self[user_id1]
        user2 = self[user_id2]

        # GPS-Koordinaten abrufen (Breitengrad, Längengrad)
        origin_point = user1.gps_coords()  # (lat, lon)
        destination_point = user2.gps_coords()  # (lat, lon)

        # Fehlende oder ungültige GPS-Daten vor Graphzugriff und Knotensuche abfangen.
        for point in (origin_point, destination_point):
            try:
                if (point is None or len(point) != 2
                        or not all(math.isfinite(value) for value in point)
                        or not (-90 <= point[0] <= 90 and -180 <= point[1] <= 180)):
                    return float('inf')
            except (TypeError, ValueError):
                return float('inf')

        self.load_graph()

        try:
            # Nächste Knoten im Graphen finden (nearest_nodes erwartet lon, lat)
            origin = ox.distance.nearest_nodes(
                self.map_graph,
                origin_point[1],  # Längengrad
                origin_point[0]   # Breitengrad
            )
            destination = ox.distance.nearest_nodes(
                self.map_graph,
                destination_point[1],
                destination_point[0]
            )

            # Kürzesten Pfad berechnen
            shortest_path = ox.routing.shortest_path(
                self.map_graph,
                origin,
                destination,
                weight='length'
            )
            # OSMnx liefert bei nicht erreichbarem Ziel None statt einer Knotenliste.
            if shortest_path is None:
                return float('inf')

            # Bei parallelen Kanten zählt wie bei der Routensuche die kürzeste Kante.
            distance_m = nx.path_weight(self.map_graph, shortest_path, weight='length')
            return float(distance_m)

        except (nx.NetworkXNoPath, ValueError) as e:
            # Beispielsweise getrennte Komponenten oder ein leerer Graph.
            print(f"Warnung: Kein Pfad zwischen {user_id1} und {user_id2} gefunden: {e}")
            return float('inf')


    # *** PUBLIC GET methods ***

    def get_name_of_user(self, user_id: str) -> str:
        """Gibt den vollständigen Namen des Benutzers zurück.

        Args:
            user_id (str): Benutzer-ID.

        Returns:
            str: Name des Benutzers.

        Raises:
            KeyError: Falls die `user_id` nicht existiert.
        """
        node = self[user_id]
        return node.name()

    def num_users(self) -> int:
        """Gibt die Gesamtanzahl registrierter Benutzer zurück.

        Args:
            None

        Returns:
            int: Anzahl der Benutzer.

        Raises:
            None
        """
        return len(self.keys())

    def password_valid(self, user_id: str, password: str) -> bool:
        """Prüft, ob das Passwort für den angegebenen Benutzer gültig ist.

        Args:
            user_id (str): Benutzer-ID.
            password (str): Passwort.

        Returns:
            bool: `True`, wenn Passwort korrekt, sonst `False`.

        Raises:
            KeyError: Falls die `user_id` nicht existiert.
        """
        return self[user_id].password_valid(password)

    def get_user_pretty_print_for_list(self, user_id: str) -> str:
        """Erstellt eine formatierte Repräsentation eines Benutzers für Listboxen.

        Args:
            user_id (str): Benutzer-ID.

        Returns:
            str: Der formatierte Benutzer-String inkl. Praktikumsgruppen-Info.

        Raises:
            KeyError: Falls `user_id` nicht existiert.
        """
        return (self[user_id].pretty_print() + "\t in Praktikumsgruppe repräsentiert durch: " +
                str(self.find_byid(user_id, True)))

    def get_friends_andgroupmembers_pretty_print(self, user_id: str) -> List[str]:
        """Returns list of friends and group members for the given user_id that is shown on GUI.

        Args:
            user_id (str): usually the current user id

        Returns:
            List[str]: Liste formatierter Strings.

        Raises:
            KeyError: Falls `user_id` nicht existiert.
        """
        friends = self[user_id].friends()
        friend_names = [self.get_user_pretty_print_for_list(friend) for friend in friends]

        group_members = self.get_groupmembers(user_id)
        if group_members is None:
            return friend_names

        # entferne mich selbst aus der Gruppe, da ich ja weiß, dass ich (user_id) in der Gruppe bin
        if user_id in group_members:
            group_members.remove(user_id)

        group_members_pp = [self.get_user_pretty_print_for_list(member) for member in group_members]
        return friend_names + group_members_pp

    def get_mutual_friends(self, user_id: str) -> Dict[str, int]:
        """Ermittelt gemeinsame Freunde (Freunde von Freunden) und deren Häufigkeit.

        Args:
            user_id (str): usually the current user id

        Returns:
            Dict[str, int]: dictionary with friends of the friends of given user_id together with the information with how many friends of user_id these friends are friends with

        Raises:
            KeyError: Falls `user_id` nicht existiert.
        """
        friends = self[user_id].friends()
        mutual_friends_count: Dict[str, int] = {}

        for friend in friends:
            friend_friends = self[friend].friends()
            for mutual_friend in friend_friends:
                if mutual_friend != user_id and mutual_friend not in friends:
                    if mutual_friend in mutual_friends_count:
                        mutual_friends_count[mutual_friend] += 1
                    else:
                        mutual_friends_count[mutual_friend] = 1

        return mutual_friends_count

    def suggest_friends(self, user_id: str, num_common_friends: int = 2,
                        distance_threshold: float = 10000.0, pretty_print: bool = True) -> List[str]:
        """
        Suggests users to the given user_id based on mutual friends and geographic proximity.

        Author:
            CallMeMosaic

        Recommendations are generated in two distinct prioritized parts:
        (1) Common friends: Users who are friends with at least `num_common_friends` of the target user's direct friends,
            ordered descending by the number of mutual connections.
        (2) Nearby connected friends: Users living within `distance_threshold` who are reachable via the social network
            graph (see `are_users_connected`), ordered ascending by geographic distance.

        Args:
            user_id (str): GM-ID of the user for whom suggestions should be generated.
            num_common_friends (int): Minimum number of shared friends required for mutual friend recommendations. Defaults to 2.
            distance_threshold (float): Maximum driving distance in meters for nearby friend recommendations.
                Defaults to 10000 (10 km); this is a road-distance cutoff, not a coordinate difference in degrees.
            pretty_print (bool): If True, returns formatted display strings for each user; otherwise returns user IDs. Defaults to True.

        Returns:
            List[str]: Combined list of suggested friend identifiers or pretty-printed strings,
                       with top mutual connections first followed by closest nearby connected users.

        Raises:
            KeyError: If `user_id` does not exist in the user database.
        """

        # Step 1: Compute frequencies of mutual friends (friends of friends)
        mutual_friends_count = self.get_mutual_friends(user_id)

        # Step 2: Filter and sort candidates with sufficient mutual friends (Part 1)
        # Select candidates having at least `num_common_friends` shared connections
        common_friends = [
            friend_id for friend_id, count in mutual_friends_count.items()
            if count >= num_common_friends
                        ]

        # Sort candidates in descending order of mutual friend count (highest overlap first)
        common_friends.sort(key=lambda fid: mutual_friends_count[fid], reverse=True)

        # Step 3: Identify nearby connected candidates in the network (Part 2)
        # Retrieve direct friends and keep a set of already suggested users to prevent duplicates
        direct_friends = self[user_id].friends()
        suggested_set = set(common_friends)

        nearby_candidates: List[Tuple[str, float]] = []
        for other_id in self:
            # Exclude self, existing direct friends, and users already added in part 1
            if other_id == user_id or other_id in direct_friends or other_id in suggested_set:
                continue

            # Calculate driving distance in meters between target user and candidate
            dist = self.calc_distance_between_users(user_id, other_id)

            # Check if candidate is geographically close and connected in the friendship graph
            if dist < distance_threshold:
                if self.are_users_connected(user_id, other_id):
                    nearby_candidates.append((other_id, dist))

        # Sort nearby candidates in ascending order by distance (closest neighbor first)
        nearby_candidates.sort(key=lambda item: item[1])
        nearby_friends = [other_id for other_id, _ in nearby_candidates]

        # Step 4: Concatenate both prioritized recommendation lists
        suggested_friends = common_friends + nearby_friends

        # Step 5: Format output if pretty-printing is requested
        if pretty_print:
            suggested_friends = [self[friend].pretty_print() for friend in suggested_friends]

        return suggested_friends

    def are_users_connected(self, user_id1: str, user_id2: str, degree: int = 3) -> bool:
        """
        Determines whether two users are connected in the friendship network up to a given degree.

        Author:
            CallMeMosaic

        Traverses the friendship graph using Breadth-First Search (BFS) to identify whether
        a connection path exists between `user_id1` and `user_id2` within `degree` steps.

        Args:
            user_id1 (str): GM-ID of the starting user.
            user_id2 (str): GM-ID of the target user.
            degree (int): Maximum allowable friendship degree (path length). Defaults to 3.

        Returns:
            bool: True if a path of length <= degree exists between the users, False otherwise.

        Raises:
            None
        """

        # Validate that both user IDs exist in the user database
        if user_id1 not in self or user_id2 not in self:
            return False

        # Negative degrees are invalid for network traversal
        if degree < 0:
            return False

        # A user is connected to themselves at degree 0 or higher
        if user_id1 == user_id2:
            return True

        # Initialize BFS queue with (current_user_id, current_degree) and track visited users
        queue = deque([(user_id1, 0)])
        visited = {user_id1}

        # Perform Breadth-First Search exploration
        while queue:
            current, d = queue.popleft()

            # Expand neighbors only if we have not reached the maximum exploration depth
            if d < degree:
                if current in self:
                    # Explore all immediate friends of the current user
                    for neighbor in self[current].friends():
                        # Target found within the allowed degree
                        if neighbor == user_id2:
                            return True

                        # Enqueue unvisited neighbors for the next layer of BFS traversal
                        if neighbor not in visited and neighbor in self:
                            visited.add(neighbor)
                            queue.append((neighbor, d + 1))

        # No connection path found within the specified degree
        return False

    # *** PUBLIC STATIC methods ***

    # *** PRIVATE methods ***

    def _read_users_from_csvfile(self, csvfile: str) -> None:
        """
        Read the given csvfile that contains all students that want to do the Praktikum in this semester
        including their GM-ID, Names and number of their Praktikumsgruppe

        :param csvfile: csv file that has to be created at the beginning of the semester containing all students
        in this semester
        """
        with open(csvfile, newline='', encoding='utf-8-sig') as f:
            csvreader = csv.reader(f)
            # Skip header row
            next(csvreader)

            # private member variable containing the Praktikumsgruppe number of the students in the order that the
            # students are read from the csv file
            self._groupnumbers = []

            for row in csvreader:
                user_id, name_family, name_first, password, groupnum, gps_coords, address = row
                # macht aus String wieder das Tuple mit long und lat Koordinaten
                # (literal_eval statt eval, damit aus der CSV-Datei kein beliebiger Code ausgeführt werden kann)
                gps_coords_tuple = ast.literal_eval(gps_coords)
                self.add(user_id, password, name_family, name_first, gps_coords_tuple, address)
                self._groupnumbers.append(int(groupnum))

    def _read_friends_csv(self, file_path: str) -> None:
        """
        Funktion, um die friends.csv-Datei einzulesen und ein Dictionary zu erstellen
        :param file_path: path to friends.csv file
        """
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            csvreader = csv.reader(f)
            next(csvreader)  # Überspringe die Header-Zeile
            for row in csvreader:
                user_id = row[0]
                friends = row[1].split(', ')
                self[user_id].friends_add_list(friends)
                for friend in friends:  # gehe alle Freunde durch und füge user_id ebenfalls als Freund hinzu
                    self[friend].friends_add(user_id)

    # *** PUBLIC methods to return class properties ***

    # *** PRIVATE variables ***
