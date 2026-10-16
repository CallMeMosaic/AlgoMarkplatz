"""Übersicht über den Dateiinhalt:

Implementiert die Simulator-Klasse zur Erzeugung zufälliger Hintergrundaktivitäten
(Gebote abgeben, neue Auktionen anlegen, Benutzer bewerten) in der Anwendung.
"""

# Status: Not FINAL, dgaida2, 15.10.2024

from typing import Any
import threading
import random
import time
import marketplace.users


class Simulator:
    """Klasse zur Simulation von Benutzeraktivitäten (Bieten, Verfehlen, Erstellen, Bewerten).

    Attributes:
        stop_simulation (bool): Flag zum Stoppen laufender Simulationszyklen.
    """

    def __init__(self) -> None:
        """Initialisiert eine neue Simulator-Instanz.

        Args:
            None

        Raises:
            None
        """
        self.stop_simulation: bool = False

    def place_random_bids(self, auctions: Any, current_user_id: str, num_auctions: int = 10) -> None:
        """Gibt zufällige Gebote für aktive Auktionen durch andere Benutzer ab.

        Args:
            auctions (Any): Die Auctions-Instanz.
            current_user_id (str): ID des aktuellen Benutzers.
            num_auctions (int): Anzahl zufälliger Gebote.

        Returns:
            None

        Raises:
            None
        """
        if self.stop_simulation:
            return

        users = auctions.users()

        user_ids = [user_id for user_id in users.keys() if user_id != current_user_id]

        auctions._place_random_bids(num_auctions, user_ids, True, current_user_id)

        # auction_ids = list(auctions.keys())
        #
        # for _ in range(num_auctions):
        #     random_user = random.choice(user_ids)
        #     random_auction = random.choice(auction_ids)
        #
        #     min_bid = auctions.get_item_value_min(random_auction)
        #
        #     random_bid = min_bid + random.randint(1, 50)
        #     auctions.bid_in_auction(random_auction, users[random_user], random_bid)
        #
        #     # prüfen, ob Angebot des curent_user überboten wurde, falls er in dieser Auktion bietet und
        #     # falls ja, dann systemnachricht ausgeben.
        #     bid_by_current_customer = auctions.get_bid_of_user(random_auction, current_user_id)
        #     if bid_by_current_customer is not None and bid_by_current_customer < random_bid:
        #         print('Angebot von current_user wurde überboten')
        #         print('Letzte Auktion kam von Nutzer {0}, das steht auch im Stapel: {1}'.format(
        #             random_user, auctions.get_last_bid(random_auction)))

        # threading.Timer(30, self.place_random_bids, args=(auctions, current_user_id)).start()

    def create_random_auctions(self, auctions: Any, current_user_id: str) -> None:
        """Erstellt zufällige neue Auktionen im System.

        Args:
            auctions (Any): Die Auctions-Instanz.
            current_user_id (str): ID des aktuellen Benutzers.

        Returns:
            None

        Raises:
            None
        """
        if self.stop_simulation:
            return

        user_ids = [user_id for user_id in auctions.users().keys() if user_id != current_user_id]

        for _ in range(5):
            random_user = random.choice(user_ids)
            item_name = "Kartoffelschäler"
            description = ""
            value_min = 1.0
            auctions.add_new_auction(random_user, item_name, description, value_min)

        # threading.Timer(30, self.create_random_auctions, args=(auctions, current_user_id)).start()

    def randomly_rate_users(self, users: marketplace.users.Users, current_user_id: str) -> None:
        """Vergibt zufällige Sterne-Bewertungen an Benutzer.

        Args:
            users (marketplace.users.Users): Die Users-Instanz.
            current_user_id (str): ID des aktuellen Benutzers.

        Returns:
            None

        Raises:
            None
        """
        if self.stop_simulation:
            return

        user_ids = [user_id for user_id in users.keys() if user_id != current_user_id]

        for _ in range(35):
            random_user = random.choice(user_ids)
            stars = random.randint(1, 5)
            # TODO for students (Praktikum 2): damit Ihre Datenstruktur für den am besten bewerteten User aktuell
            #  bleibt, muss sie nach jeder Bewertung aktualisiert werden. Dafür dürfen Sie diese Methode anpassen.
            users[random_user].rate_user(stars)

    def stop(self) -> None:
        """Stoppt die Ausführung der Simulation.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        self.stop_simulation = True
