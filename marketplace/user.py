"""Übersicht über den Dateiinhalt:

Diese Datei definiert die Klasse User.
Ein User repräsentiert einen Teilnehmer am Marktplatz (Käufer und Verkäufer).
Ein User besitzt Zugangsdaten, Name, ein Budget (Balance), eine Freundesliste,
Wohnortdaten (GPS & Adresse) sowie Bewertungen und erbt von SetNode für Praktikumsgruppen.
"""

# Status: FINAL, dgaida2, 15.10.2024

# definiert die Klasse User.
# user ist ein Aktionär auf dem Online-Marktplatz. Kann sowohl Produkte kaufen als auch verkaufen.
# Ein user hat auch Freunde.
# ihm können deshalb auch Produkte/Auktionen vorgeschlagen werden. Beispielsweise solche,
# die seine Freunde interessieren.
# Ein Nutzer wird über seine ID identifiziert. Ein Nutzer hat ein Budget (balance), das sich verkleinert, wenn User
# etwas verkauft und das sich vergrößert, wenn User etwas verkauft.
# Nutzer wohnt an einer zufälligen GPS-Koordinate, für die der Wohnort als String zurückgegeben werden kann.
# (wird in drittes Praktikum benötigt)

# Nur für dritten Praktikumstermin:
# User erbt von der Klasse SetNode, SetNode ist ein Knoten in einer disjunkten Menge, definiert in Praktikumsgruppen,
# damit ist User ein Mitglied einer Praktikumsgruppe

from typing import Any, List, Optional, Set, Tuple
import marketplace.praktikumsgruppen


class User(marketplace.praktikumsgruppen.SetNode):
    """Klasse zur Repräsentation eines Benutzers auf dem Marktplatz.

    Attributes:
        _id (str): Benutzer-ID.
        _password (str): Passwort des Benutzers.
        _name_first (str): Vorname des Benutzers.
        _name_family (str): Nachname des Benutzers.
        _friends (Set[str]): Menge der Benutzer-IDs von Freunden.
        _balance (float): Guthaben des Benutzers in Euro.
        _gps_coords (Tuple[float, float]): Breitengrad und Längengrad des Wohnorts.
        _address (str): Adresse/Wohnort-String.
        _rating_stars (List[int]): Liste der erhaltenen Sterne-Bewertungen.
    """

    # *** CONSTRUCTORS ***
    def __init__(self, user_id: str, password: str, name_family: str, name_first: str,
                 gps_coord: Tuple[float, float], address: str) -> None:
        """Standard-Konstruktor zur Initialisierung eines Benutzers.

        Args:
            user_id (str): Eindeutige Benutzer-ID.
            password (str): Passwort des Benutzers.
            name_family (str): Nachname des Benutzers.
            name_first (str): Vorname des Benutzers.
            gps_coord (Tuple[float, float]): GPS-Koordinaten des Wohnorts (Lat, Lon).
            address (str): Textuelle Adresse des Benutzers.

        Raises:
            None
        """
        super().__init__()

        self._id: str = user_id
        self._password: str = password

        self._name_first: str = name_first
        self._name_family: str = name_family

        self._friends: Set[str] = set()              # friends of user

        self._balance: float = 500.0           # amount of money user has in Euros

        # Tupel mit Längen- und Breitengrad des erfundenen Wohnorts des Users.
        self._gps_coords: Tuple[float, float] = gps_coord

        # Adresse, die zur GPS-Koordinate gehört
        self._address: str = address

        self._rating_stars: List[int] = []

    # *** PUBLIC SET methods ***

    def decrease_balance(self, amount: float) -> None:
        """Verringert das Guthaben des Benutzers um den angegebenen Betrag.

        Args:
            amount (float): Der abzuziehende Betrag in Euro.

        Returns:
            None

        Raises:
            None
        """
        self._balance -= amount

    def increase_balance(self, amount: float) -> None:
        """Erhöht das Guthaben des Benutzers um den angegebenen Betrag.

        Args:
            amount (float): Der hinzuzufügende Betrag in Euro.

        Returns:
            None

        Raises:
            None
        """
        self._balance += amount

    # *** PUBLIC methods ***

    def password_valid(self, password: str) -> bool:
        """Überprüft, ob das eingegebene Passwort korrekt ist.

        Args:
            password (str): Das zu prüfende Passwort.

        Returns:
            bool: `True`, wenn das Passwort mit `_password` übereinstimmt, sonst `False`.

        Raises:
            None
        """
        return password == self._password

    def friends_add_list(self, friend_ids: List[str]) -> None:
        """Fügt eine Liste von Benutzer-IDs zur Freundesliste hinzu.

        Args:
            friend_ids (List[str]): Liste hinzuzufügender Freundes-IDs.

        Returns:
            None

        Raises:
            None
        """
        for friend_id in friend_ids:
            self._friends.add(friend_id)

    def friends_add(self, friend_id: str) -> None:
        """Fügt eine einzelne Benutzer-ID zur Freundesliste hinzu.

        Args:
            friend_id (str): Die hinzuzufügende Freundes-ID.

        Returns:
            None

        Raises:
            None
        """
        self._friends.add(friend_id)

    def friends_delete(self, friend_id: str) -> None:
        """Entfernt eine Benutzer-ID aus der Freundesliste.

        Args:
            friend_id (str): Die zu entfernende Freundes-ID.

        Returns:
            None

        Raises:
            KeyError: Falls die `friend_id` nicht in der Freundesliste existiert.
        """
        self._friends.remove(friend_id)

    def rate_user(self, stars: int) -> None:
        """Fügt eine Sterne-Bewertung für den Benutzer hinzu.

        Args:
            stars (int): Bewertung in Sternen (z. B. 1 bis 5).

        Returns:
            None

        Raises:
            None
        """
        self._rating_stars.append(stars)

    # *** PUBLIC GET methods ***

    def pretty_print(self) -> str:
        """Gibt eine formatierte Zeichenkette mit Benutzer-ID, Name und Wohnort zurück.

        Args:
            None

        Returns:
            str: Der formatierte Benutzer-String.

        Raises:
            None
        """
        return "ID: {0} Name: {1} Wohnort: {2}".format(self._id.ljust(15), self.name(),
                                                       self.address())

    @staticmethod
    def get_id_from_pretty_print(pretty_print_text: str) -> str:
        """Extrahiert die Benutzer-ID aus einer formatierten Benutzer-Zeichenkette.

        Args:
            pretty_print_text (str): Die formatierte Zeichenkette.

        Returns:
            str: Die extrahierte Benutzer-ID.

        Raises:
            IndexError: Falls der String kein erwartet formatierter Benutzer-Text ist.
        """
        splits = pretty_print_text.split(" ")
        return splits[1]

    def is_friend(self, user_id: str) -> bool:
        """Prüft, ob der angegebene Benutzer in der Freundesliste enthalten ist.

        Args:
            user_id (str): Die zu prüfende Benutzer-ID.

        Returns:
            bool: `True`, wenn der Benutzer ein Freund ist, sonst `False`.

        Raises:
            None
        """
        return user_id in self._friends

    def get_rating_stars_mean(self) -> float:
        """Berechnet den Notendurchschnitt (Mittelwert) der bisherigen Sterne-Bewertungen.

        Args:
            None

        Returns:
            float: Durchschnittliche Sterneanzahl oder 0.0 bei fehlenden Bewertungen.

        Raises:
            None
        """
        mean = 0.0
        for star in self._rating_stars:
            mean += star

        if len(self._rating_stars) >= 1:
            mean /= len(self._rating_stars)

        return mean

    # *** PUBLIC STATIC methods ***

    # *** PRIVATE methods ***

    # *** PUBLIC methods to return class properties ***

    def balance(self) -> float:
        """Gibt das aktuelle Guthaben des Benutzers zurück.

        Args:
            None

        Returns:
            float: Guthaben in Euro.

        Raises:
            None
        """
        return self._balance

    def name(self) -> str:
        """Gibt den vollen Namen des Benutzers (Vorname + Nachname) zurück.

        Args:
            None

        Returns:
            str: Vollständiger Name.

        Raises:
            None
        """
        return f"{self._name_first} {self._name_family}"

    def id(self) -> str:
        """Gibt die Benutzer-ID zurück.

        Args:
            None

        Returns:
            str: Benutzer-ID.

        Raises:
            None
        """
        return self._id

    def password(self) -> str:
        """Gibt das Passwort des Benutzers zurück.

        Args:
            None

        Returns:
            str: Passwort.

        Raises:
            None
        """
        return self._password

    def friends(self) -> Set[str]:
        """Gibt die Menge aller Freundes-IDs zurück.

        Args:
            None

        Returns:
            Set[str]: Menge der Freundes-IDs.

        Raises:
            None
        """
        return self._friends

    def gps_coords(self) -> Tuple[float, float]:
        """Gibt die GPS-Koordinaten des Benutzers zurück.

        Args:
            None

        Returns:
            Tuple[float, float]: Längen- und Breitengrad des Wohnorts.

        Raises:
            None
        """
        return self._gps_coords

    def address(self) -> str:
        """Gibt die Adresse des Benutzers zurück.

        Args:
            None

        Returns:
            str: Wohnadresse.

        Raises:
            None
        """
        return self._address

    # *** PRIVATE variables ***
