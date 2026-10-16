"""Übersicht über den Dateiinhalt:

Die Klasse Auctions verwaltet alle Auktionen im Marktplatz in einem Wörterbuch (dict).
Sie stellt Methoden zum Hinzufügen, Bieten, Löschen, Suchen, Empfehlen und Abwickeln
abgelaufener Auktionen bereit und steuert im Hintergrund einen Simulator-Thread.
"""

# Status: Not FINAL, dgaida2, 15.10.2024

# Die Klasse Auctions speichert alle Auktionen in einem Dictionary

from typing import Any, Dict, List, Optional, Tuple, Union
import marketplace.auction
import marketplace.item
import marketplace.users
import marketplace.simulator
from marketplace.max_heap import MaxHeap
from marketplace.transactions import Transaction, Transactions
from datetime import datetime
import random
import threading
import csv


# wenn man nur produkte ersteigern möchte, die in einem
# preissegment sind, dann AVL-Baum sinnvoll. am besten dann alle Auktionen sowohl in Hashtabelle als auch in
# AVL Baum speichern und je nachdem ob preissegment-filter in gui genutzt wird (müsste noch hinzugefügt
# werden zu gui), nutzt man entweder AVL-Baum oder Hashtabelle.
class Auctions(dict):

    # COMMENTS BY ME
    """
    Same thing here, this class inherits from dict, which is pythons own implementation of the ADT dictionary.
    Since it directly inherits from the python dict, it is also implemented as a HashTable datastructure written in C
    using OpenAddressing.

    How to find newest auction:
    look at current counter value -1 and add an "a" infront of it.
    Insert as key into the dictionary.
    Whabam there's your newest auction.

    Output in order:
    Insert "a" + n into the dictionary until you hit the current counter value.
    Whabam that's all items.

    """


    """Klasse zur Verwaltung des Wörterbuchs aller Auktionen.

    Attributes:
        _id_next_auction (int): Zähler für die Generierung fortlaufender Auktions-IDs.
        _heap (Optional[marketplace.max_heap.MaxHeap]): Max-Heap der Auktionen zur Ermittlung der Top-Auktion.
        _heap_users_rated (Optional[Any]): Heap für bewertete Benutzer.
        _transactions (Transactions): Speichert abgeschlossene Transaktionen.
        _users (marketplace.users.Users): Benutzer-Verwaltungsinstanz.
        _my_simulator (marketplace.simulator.Simulator): Simulatorsinstanz für Hintergrundaktivitäten.
        _stop_event (threading.Event): Signal-Event zum Stoppen des Simulators.
        _system_messages (Optional[Any]): SystemMessage-Instanz für Benachrichtigungen.
    """

    # *** CONSTRUCTORS ***
    def __init__(self, csvfile: str, *args: Any) -> None:
        """Initialisiert das Auctions-Objekt und lädt vorhandene Auktionen aus der CSV-Datei.

        Args:
            csvfile (str): Pfad zur CSV-Datei mit Auktionsdaten.
            *args (Any): Variable Argumente.

        Raises:
            FileNotFoundError: Falls die CSV-Datei nicht existiert.
        """
        super().__init__(self)

        self._id_next_auction: int = 0

        # für erstes Praktikum auf None setzen und für 2. Praktikum auf MaxHeap()
        try:
            self._heap: Optional[MaxHeap] = MaxHeap()  # None
        except NotImplementedError:
            self._heap = None

        # TODO for students: für 2. Praktikum: erstelle hier ein MaxHeap, um den besten User/Verkäufer mit der Methode
        #  get_top_rated_user() (s.u.) in konstanter Zeit zurück geben zu können. auf der GUI gibt es noch keinen Button
        #  mit dem Sie andere Nutzer bewerten können. das wird alles simuliert in simulator.py. Sie können von jedem
        #  User über die Methode user.User.get_rating_stars_mean() die mittlere Anzahl Sterne abfragen.
        #  Nach jeder Bewertung muss die Datenstruktur aktualisiert werden, s. simulator.Simulator.randomly_rate_users().
        self._heap_users_rated: Optional[Any] = None

        # 1024 Buckets: in 30 Minuten entstehen einige hundert Transaktionen. Bei nur 128 Buckets wären ab der
        # 129. Transaktion Kollisionen unvermeidbar und der Effekt einer besseren Hashfunktion kaum sichtbar.
        self._transactions: Transactions = Transactions(1024)

        self._users: marketplace.users.Users = marketplace.users.Users("user.csv")

        self._read_auctions_from_csvfile(csvfile)

        self._place_random_bids(num_bids=10 * self._users.num_users())

        self._my_simulator: marketplace.simulator.Simulator = marketplace.simulator.Simulator()

        self._stop_event: threading.Event = threading.Event()
        self._system_messages: Optional[Any] = None

        # self._start_simulator()

    # *** PUBLIC SET methods ***

    def set_system_messages(self, system_messages: Any) -> None:
        """Setzt das Objekt für Systemnachrichten.

        Args:
            system_messages (Any): Die SystemMessages-Instanz.

        Returns:
            None

        Raises:
            None
        """
        self._system_messages = system_messages

    # *** PUBLIC methods ***

    def add_new_auction(self, user_id: str, item_name: str, description: str = "", value_min: float = 1.0) -> marketplace.auction.Auction:
        """Erstellt eine neue Auktion und fügt sie dem Wörterbuch hinzu.

        Args:
            user_id (str): ID des Verkäufers.
            item_name (str): Name des Produkts.
            description (str): Beschreibung des Produkts.
            value_min (float): Mindestgebot in Euro.

        Returns:
            marketplace.auction.Auction: Die neu erstellte Auktion.

        Raises:
            None
        """
        item = marketplace.item.Item(item_name, description, float(value_min))

        auction, auction_id = self._new_auction(user_id, item)

        self[auction_id] = auction

        return auction

    def bid_in_auction(self, auction_id: str, user: Any, bid_amount: float) -> bool:
        """Gibt ein Gebot für die angegebene Auktions-ID ab.

        Args:
            auction_id (str): Auktions-ID.
            user (Any): Der bietende Benutzer.
            bid_amount (float): Gebotsbetrag in Euro.

        Returns:
            bool: `True`, wenn das Gebot erfolgreich war, sonst `False`.

        Raises:
            None
        """
        if auction_id in self:
            success = self[auction_id].bid(user, float(bid_amount))
            if success and self._heap is not None:
                self._heap.update_bidders(auction_id, self[auction_id].bid_count())
            return bool(success)
        return False

    def delete(self, auction_id: str) -> bool:
        """Löscht eine Auktion, sofern noch niemand darauf geboten hat.

        Args:
            auction_id (str): Auktions-ID.

        Returns:
            bool: `True`, wenn das Löschen erfolgreich war, sonst `False`.

        Raises:
            KeyError: Wenn die `auction_id` nicht im Wörterbuch existiert.
        """
        # funktioniert nur, wenn noch niemand auf diese Auktion geboten hat, sonst kann man Auktion nicht löschen
        # muss dann auch item in self[auction_id] löschen, bzw. muss das?
        if not self[auction_id].is_any_bidder():
            del self[auction_id]
            return True
        else:
            return False

    def start_simulation_init(self, current_user_id: str, duration: int = 1800) -> None:
        """Startet die Hintergrund-Simulation von Aktivitäten für 30 Minuten (1800 Sekunden).

        Args:
            current_user_id (str): ID des angemeldeten Benutzers.
            duration (int): Maximale Simulationsdauer in Sekunden (Standard: 1800).

        Returns:
            None

        Raises:
            None
        """
        self._start_simulator(current_user_id, elapsed_seconds=0, max_duration=duration)

    def stop_simulation(self) -> None:
        """Stoppt den Simulator-Thread und den Timer.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        self._stop_event.set()

        if hasattr(self, '_timer') and self._timer.is_alive():
            self._timer.cancel()

    def __delitem__(self, key: str) -> None:
        """Löscht ein Element aus dem Wörterbuch und entfernt es aus dem Max-Heap.

        Args:
            key (str): Auktions-ID.

        Returns:
            None

        Raises:
            KeyError: Wenn der Key nicht existiert.
        """
        super().__delitem__(key)
        if self._heap is not None:
            self._heap.remove(key)

    # wird bei self[auction_id] = auction aufgerufen
    def __setitem__(self, key: str, value: marketplace.auction.Auction) -> None:
        """Setzt eine Auktion im Wörterbuch und fügt sie dem Max-Heap hinzu.

        Args:
            key (str): Auktions-ID.
            value (marketplace.auction.Auction): Auktions-Objekt.

        Returns:
            None

        Raises:
            None
        """
        super().__setitem__(key, value)
        if self._heap is not None:
            self._heap.add_auction(value.id(), value.bid_count())

    # *** PUBLIC GET methods ***

    def get_time_left(self, auction_id: str) -> float:
        """Gibt die verbleibende Zeit einer Auktion in Sekunden zurück.

        Args:
            auction_id (str): Auktions-ID.

        Returns:
            float: Verbleibende Sekunden.

        Raises:
            KeyError: Wenn `auction_id` nicht vorhanden ist.
        """
        return self[auction_id].get_time_left()

    def get_auction_ends(self, auction_id: str) -> datetime:
        """Gibt den Auktions-Endzeitpunkt zurück.

        Args:
            auction_id (str): Auktions-ID.

        Returns:
            datetime: Auslaufzeitpunkt.

        Raises:
            KeyError: Wenn `auction_id` nicht vorhanden ist.
        """
        return self[auction_id].auction_ends()

    def get_seller_id(self, auction_id: str) -> str:
        """Gibt die Verkäufer-ID einer Auktion zurück.

        Args:
            auction_id (str): Auktions-ID.

        Returns:
            str: Verkäufer-ID.

        Raises:
            KeyError: Wenn `auction_id` nicht vorhanden ist.
        """
        return self[auction_id].seller_id()

    def get_purchaser_id(self, auction_id: str) -> Optional[str]:
        """Gibt die Käufer-ID einer Auktion zurück.

        Args:
            auction_id (str): Auktions-ID.

        Returns:
            Optional[str]: Käufer-ID.

        Raises:
            KeyError: Wenn `auction_id` nicht vorhanden ist.
        """
        return self[auction_id].purchaser_id()

    def get_item(self, auction_id: str) -> marketplace.item.Item:
        """Gibt das Item einer Auktion zurück.

        Args:
            auction_id (str): Auktions-ID.

        Returns:
            marketplace.item.Item: Das Artikel-Objekt.

        Raises:
            KeyError: Wenn `auction_id` nicht vorhanden ist.
        """
        return self[auction_id].item()

    def get_item_name(self, auction_id: str) -> str:
        """Gibt den Artikelnamen einer Auktion zurück.

        Args:
            auction_id (str): Auktions-ID.

        Returns:
            str: Name des Artikels.

        Raises:
            KeyError: Wenn `auction_id` nicht vorhanden ist.
        """
        return self[auction_id].get_item_name()

    def get_all_item_names(self) -> List[str]:
        """Gibt eine Liste aller Artikelnamen aller Auktionen zurück.

        Args:
            None

        Returns:
            List[str]: Liste der Artikelnamen.

        Raises:
            None
        """
        return [self.get_item_name(auction_id) for auction_id in self]

    def get_item_description(self, auction_id: str) -> str:
        """Gibt die Artikelbeschreibung einer Auktion zurück.

        Args:
            auction_id (str): Auktions-ID.

        Returns:
            str: Beschreibung des Artikels.

        Raises:
            KeyError: Wenn `auction_id` nicht vorhanden ist.
        """
        return self[auction_id].get_item_description()

    def get_item_value_min(self, auction_id: str) -> float:
        """Gibt das Mindestgebot einer Auktion zurück.

        Args:
            auction_id (str): Auktions-ID.

        Returns:
            float: Mindestgebot in Euro.

        Raises:
            KeyError: Wenn `auction_id` nicht vorhanden ist.
        """
        return self[auction_id].get_item_value_min()

    def get_users_bidding(self, auction_id: str) -> List[Tuple[float, str]]:
        """Gibt die Liste der Bietenden einer Auktion zurück.

        Args:
            auction_id (str): Auktions-ID.

        Returns:
            List[Tuple[float, str]]: Gebote-Min-Heap.

        Raises:
            KeyError: Wenn `auction_id` nicht vorhanden ist.
        """
        return self[auction_id].users_bidding()

    def get_highest_bid(self, auction_id: str) -> float:
        """Gibt das Höchstgebot einer Auktion zurück.

        Args:
            auction_id (str): Auktions-ID.

        Returns:
            float: Höchstes Gebot in Euro.

        Raises:
            KeyError: Wenn `auction_id` nicht vorhanden ist.
        """
        return self[auction_id].get_highest_bid()

    def get_highest_bidder(self, auction_id: str) -> str:
        """Gibt die Benutzer-ID des Höchstbietenden zurück.

        Args:
            auction_id (str): Auktions-ID.

        Returns:
            str: Benutzer-ID des Höchstbietenden.

        Raises:
            KeyError: Wenn `auction_id` nicht vorhanden ist.
        """
        return self[auction_id].get_highest_bidder()

    def get_auctions_offered(self, user_id: str) -> List[str]:
        """Gibt alle aktiven Auktions-IDs zurück, die vom Benutzer angeboten werden.

        Args:
            user_id (str): Benutzer-ID.

        Returns:
            List[str]: Liste der Auktions-IDs.

        Raises:
            None
        """
        return [auction_id for auction_id, auction in list(self.items())
                if auction.seller_id() == user_id and not auction.sold()]

    def get_auctions_bid_in(self, user_id: str) -> List[str]:
        """Gibt alle Auktions-IDs zurück, in denen der Benutzer mitbietet.

        Args:
            user_id (str): Benutzer-ID.

        Returns:
            List[str]: Liste der Auktions-IDs.

        Raises:
            None
        """
        return [auction_id for auction_id, auction in list(self.items())
                if auction.is_user_bidding(user_id) and not auction.sold()]

    def get_auctions_sold(self, user_id: str) -> List[str]:
        """Gibt alle Auktions-IDs zurück, die erfolgreich vom Benutzer verkauft wurden.

        Args:
            user_id (str): Benutzer-ID.

        Returns:
            List[str]: Liste der Auktions-IDs.

        Raises:
            None
        """
        return [auction_id for auction_id, auction in list(self.items())
                if auction.seller_id() == user_id and auction.sold_success()]

    def get_auctions_won(self, user_id: str) -> List[str]:
        """Gibt alle Auktions-IDs zurück, die vom Benutzer gewonnen wurden.

        Args:
            user_id (str): Benutzer-ID.

        Returns:
            List[str]: Liste der Auktions-IDs.

        Raises:
            None
        """
        return [auction_id for auction_id, auction in list(self.items()) if auction.purchaser_id() == user_id]

    def get_auctions_is_recommended(self, user_id: str) -> List[str]:
        """Gibt alle dem Benutzer empfohlenen Auktions-IDs zurück.

        Args:
            user_id (str): Benutzer-ID.

        Returns:
            List[str]: Liste der Auktions-IDs.

        Raises:
            None
        """
        return [auction_id for auction_id, auction in list(self.items())
                if auction.is_recommended2user(user_id) and not auction.sold()]

    def get_is_user_bidding(self, auction_id: str, user_id: str) -> bool:
        """Prüft, ob der Benutzer in der Auktion mitbietet.

        Args:
            auction_id (str): Auktions-ID.
            user_id (str): Benutzer-ID.

        Returns:
            bool: `True`, wenn der Benutzer bietet, sonst `False`.

        Raises:
            KeyError: Wenn `auction_id` nicht vorhanden ist.
        """
        return self[auction_id].is_user_bidding(user_id)

    def get_bid_of_user(self, auction_id: str, user_id: str) -> Optional[float]:
        """Gibt das Gebot des Benutzers in der Auktion zurück.

        Args:
            auction_id (str): Auktions-ID.
            user_id (str): Benutzer-ID.

        Returns:
            Optional[float]: Gebot in Euro oder `None`.

        Raises:
            KeyError: Wenn `auction_id` nicht vorhanden ist.
        """
        return self[auction_id].get_bid_of_user(user_id)

    def get_last_bid(self, auction_id: str) -> Optional[Tuple[str, float]]:
        """Gibt das letzte Gebot auf den Stapel der Auktion zurück.

        Args:
            auction_id (str): Auktions-ID.

        Returns:
            Optional[Tuple[str, float]]: Letztes Gebot oder `None`.

        Raises:
            KeyError: Wenn `auction_id` nicht vorhanden ist.
        """
        return self[auction_id].get_last_bid()

    def get_transactions_collisions(self) -> int:
        """Gibt die Anzahl der Kollisionen in den Transaktionen zurück.

        Args:
            None

        Returns:
            int: Anzahl der Kollisionen.

        Raises:
            None
        """
        return self._transactions.get_collisions()

    def get_transactions_size(self) -> int:
        """Gibt die Anzahl gespeicherter Transaktionen zurück.

        Args:
            None

        Returns:
            int: Anzahl Transaktionen.

        Raises:
            None
        """
        return self._transactions.get_size()

    def get_auctions_friends_offer(self, user_id: str) -> None:
        """Empfiehlt dem Benutzer Auktionen, die von seinen Freunden angeboten werden.

        Args:
            user_id (str): Benutzer-ID.

        Returns:
            None

        Raises:
            KeyError: Falls die `user_id` nicht in den Benutzern existiert.
        """
        friends = self._users[user_id].friends()
        friends_auctions: Dict[str, int] = {}

        for friend_id in friends:
            auctions_friend = self.get_auctions_offered(friend_id)
            for auction_id in auctions_friend:
                if auction_id in friends_auctions:
                    friends_auctions[auction_id] += 1
                else:
                    friends_auctions[auction_id] = 1

        if friends_auctions:  # friends_actions could also be empty, then max throws an error
            max_auction = max(friends_auctions, key=lambda k: friends_auctions[k])

            # empfehle max_auction an user
            self[max_auction].recommend2user(user_id)

    def get_auctions_friends_bid_in(self, user_id: str) -> None:
        """Empfiehlt dem Benutzer Auktionen, in denen seine Freunde bieten.

        Args:
            user_id (str): Benutzer-ID.

        Returns:
            None

        Raises:
            KeyError: Falls die `user_id` nicht in den Benutzern existiert.
        """
        friends = self._users[user_id].friends()
        friends_auctions: Dict[str, int] = {}

        for friend_id in friends:
            auctions_friend = self.get_auctions_bid_in(friend_id)
            for auction_id in auctions_friend:
                if auction_id in friends_auctions:
                    friends_auctions[auction_id] += 1
                else:
                    friends_auctions[auction_id] = 1

        if friends_auctions:  # friends_actions could also be empty, then max throws an error
            max_auction = max(friends_auctions, key=lambda k: friends_auctions[k])

            # empfehle max_auction an user
            self[max_auction].recommend2user(user_id)

    def get_top_auction(self, with_num_bids: bool = False) -> Optional[Union[Tuple[int, str], str]]:
        """Gibt die Auktion mit den meisten Geboten aus dem Max-Heap zurück.

        Args:
            with_num_bids (bool): Ob die Anzahl der Gebote mit zurückgegeben werden soll.

        Returns:
            Optional[Union[Tuple[int, str], str]]: Top-Auktion oder `None`.

        Raises:
            None
        """
        if not self._heap:
            return None
        if with_num_bids:
            return self._heap.get_auction_with_max_bidders()
        else:
            res = self._heap.get_auction_with_max_bidders()
            return res[1] if res else None

    # TODO for students: in 2. Praktikum: nutze diese Methode und passe diese evtl. an
    def get_top_rated_user(self, with_num_stars: bool = False) -> Optional[Union[List[Any], str]]:
        """Gibt den am besten bewerteten Benutzer zurück.

        Args:
            with_num_stars (bool): Ob die Sterne-Anzahl mit zurückgegeben werden soll.

        Returns:
            Optional[Union[List[Any], str]]: Benutzer-ID oder `[max_stars, max_user]`.

        Raises:
            None
        """
        # TODO for students: do not use this part
        # stupid brute force implementation
        max_user: Optional[str] = None
        max_stars: float = 0.0
        for user_id, user in self._users.items():
            stars_mean = user.get_rating_stars_mean()
            if stars_mean > max_stars:
                max_stars = stars_mean
                max_user = user_id

        if with_num_stars:
            return [max_stars, max_user]
        else:
            return max_user

        # TODO for students: instead use and probably change this
        # if not self._heap_users_rated:
        #     return None
        # if with_num_stars:
        #     return self._heap_users_rated.get_top_user()
        # else:
        #     return self._heap_users_rated.get_top_user()[1]

    def get_active_auctions(self) -> Dict[str, marketplace.auction.Auction]:
        """Gibt alle nicht abgewickelten/nicht verkauften Auktionen zurück.

        Args:
            None

        Returns:
            Dict[str, marketplace.auction.Auction]: Wörterbuch aktiver Auktionen.

        Raises:
            None
        """
        auctions_active = {}
        for auction_id, auction in list(self.items()):
            if not auction.sold():
                auctions_active[auction_id] = auction

        return auctions_active

    # *** PUBLIC STATIC methods ***

    @staticmethod
    def sort_time_left(auctions_dict: Dict[str, marketplace.auction.Auction]) -> Dict[str, marketplace.auction.Auction]:
        """Sortiert ein Wörterbuch von Auktionen aufsteigend nach Auslaufzeit.

        Args:
            auctions_dict (Dict[str, marketplace.auction.Auction]): Zu sortierendes Wörterbuch.

        Returns:
            Dict[str, marketplace.auction.Auction]: Das sortierte Wörterbuch.

        Raises:
            None
        """
        # Sortiere das dict nach _time_left der Items in absteigender Reihenfolge
        return dict(sorted(auctions_dict.items(), key=lambda x: x[1].auction_ends(), reverse=False))

    # *** PRIVATE methods ***

    def _new_auction(self, user_id: str, item: marketplace.item.Item) -> Tuple[marketplace.auction.Auction, str]:
        auction_id = self._create_new_auction_id()

        auction = marketplace.auction.Auction(auction_id, user_id, item)

        return auction, auction_id

    def _create_new_auction_id(self) -> str:
        auction_id = "a" + str(self._id_next_auction)
        self._id_next_auction += 1
        return auction_id

    def _read_auctions_from_csvfile(self, csvfile: str) -> None:
        auctions = {}

        with open(csvfile, newline='', encoding='utf-8-sig') as f:
            csvreader = csv.reader(f)
            # Skip header row
            next(csvreader)

            for row in csvreader:
                item_name, description, user_id, value_min = row

                # self.add_new_auction(user_id, item_name, description, float(value_min))
                item = marketplace.item.Item(item_name, description, float(value_min))
                auction, auction_id = self._new_auction(user_id, item)

                auctions[auction_id] = auction

        auctions = marketplace.auctions.Auctions.sort_time_left(auctions)

        for auction in auctions:
            self[auction] = auctions[auction]

    def _place_random_bids(self, num_bids: int = 10, user_ids: Optional[List[str]] = None,
                           show_message: bool = False, current_user_id: Optional[str] = None) -> None:
        """

        :param num_bids:
        :param user_ids:
        :param show_message:
        :param current_user_id:
        """
        if user_ids is None:
            user_ids = list(self._users.keys())

        # biete nur auf solche Auktionen die noch nicht beendet sind!
        auctions_active = self.get_active_auctions()

        auction_ids = list(auctions_active)

        # Sicherstellen, dass es genügend Auktionen gibt, um 10 zufällige Gebote zu platzieren
        if len(auction_ids) < num_bids:
            raise ValueError(f"Nicht genügend Auktionen vorhanden, um {num_bids} zufällige Gebote zu platzieren.")

        for _ in range(num_bids):
            random_user = random.choice(user_ids)
            random_auction = random.choice(auction_ids)

            min_bid = self.get_item_value_min(random_auction)

            random_bid = min_bid + random.randint(1, 50)  # Zufälliger Betrag über dem Mindestgebot

            bid_by_current_customer = None
            if show_message and current_user_id is not None:
                bid_by_current_customer = self.get_bid_of_user(random_auction, current_user_id)

            success = self.bid_in_auction(random_auction, self._users[random_user], random_bid)

            if show_message and success:
                # prüfen, ob Angebot des current_user überboten wurde, falls er in dieser Auktion bietet und
                # falls ja, dann systemnachricht ausgeben.
                if bid_by_current_customer is not None and bid_by_current_customer < random_bid:
                    item_name = self.get_item_name(random_auction)
                    if self._system_messages is not None:
                        self._system_messages.push(f"Ihr Angebot für {item_name} wurde überboten.")
                    print('Angebot von current_user wurde überboten')
                    print('Letzte Auktion kam von Nutzer {0}, das steht auch im Stapel: {1}'.format(
                        random_user, self.get_last_bid(random_auction)))

    def _start_simulator(self, current_user_id: str, elapsed_seconds: int = 0, max_duration: int = 1800) -> None:
        if self._stop_event.is_set() or elapsed_seconds >= max_duration:
            return

        self._my_simulator.place_random_bids(self, current_user_id)

        self._my_simulator.create_random_auctions(self, current_user_id)

        self._my_simulator.randomly_rate_users(self._users, current_user_id)

        next_elapsed = elapsed_seconds + 30
        if next_elapsed < max_duration:
            timer = threading.Timer(30, self._start_simulator, args=(current_user_id, next_elapsed, max_duration))
            timer.start()
            self._timer = timer

    def _set_purchaser_id(self, auction_id: str) -> bool:
        """
        :param auction_id:
        :return:
        """
        # setze Verkäufer
        purchaser_id = self[auction_id].set_purchaser_id()
        seller_id = self[auction_id].seller_id()
        highest_bid = self[auction_id].get_highest_bid()

        if self._heap is not None:
            self._heap.remove(auction_id)

        if purchaser_id is not None and purchaser_id != "Kein Bieter":
            self._transactions.insert(Transaction(seller=self._users[seller_id].name(), 
                                                  buyer=self._users[purchaser_id].name(), 
                                                  price=highest_bid, 
                                                  timestamp=datetime.now(), 
                                                  product_name=self[auction_id].get_item_name()))

        # purchaser_id kann auch "Kein Bieter" oder None sein.
        if purchaser_id in self._users:
            # dem Verkäufer wird der Verkaufspreis überwiesen
            self._users[seller_id].increase_balance(highest_bid)

            # muss allen Aktionären, die nicht gewonnen haben das Geld zurückerstatten,
            # da dieses bereits beim Bieten von Balance abgezogen wurde, oder ich verkleinere balance
            # erst beim Verkauf. führt dazu, dass man Schulden machen könnte
            for (bid_of_user, user_id) in self[auction_id].users_bidding():
                if user_id != purchaser_id:
                    # minus sign, da Angebot negativ ist, wg. min-heap
                    self._users[user_id].increase_balance(-bid_of_user)

            return True
        else:  # dann ist Auktion ausgelaufen, aber es gab keinen Käufer
            return False

    # ...............

    def handle_expired_auction(self, auction_id: str) -> bool:
        """Behandelt das Auslaufen einer Auktion und wickelt die Bezahlung/Kauf ab.

        Args:
            auction_id (str): Auktions-ID.

        Returns:
            bool: `True`, wenn ein Käufer gesetzt und der Kauf abgewickelt wurde, sonst `False`.

        Raises:
            KeyError: Wenn `auction_id` nicht existiert.
        """
        # Hier kommt die Logik, was passieren soll, wenn eine Auktion ausläuft
        if not self[auction_id].sold():
            return self._set_purchaser_id(auction_id)
        else:
            return False

    # *** PUBLIC methods to return class properties ***

    def id_next_auction(self) -> int:
        """Gibt den aktuellen Zählerstand für Auktions-IDs zurück.

        Args:
            None

        Returns:
            int: Nächste Auktions-ID.

        Raises:
            None
        """
        return self._id_next_auction

    def users(self) -> marketplace.users.Users:
        """Gibt die Benutzer-Verwaltung zurück.

        Args:
            None

        Returns:
            marketplace.users.Users: Die Users-Instanz.

        Raises:
            None
        """
        return self._users

    # *** PRIVATE variables ***
