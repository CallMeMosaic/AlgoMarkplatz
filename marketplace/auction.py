"""Übersicht über den Dateiinhalt:

Diese Datei definiert die Klasse Auction.
In einer Auktion wird ein Artikel (Item) von einem Verkäufer an einen Höchstbietenden
versteigert. Bietvorgänge, Mindestgebote, Verfallszeiten und Porto werden hier verwaltet.
"""

# Status: FINAL, dgaida2, 16.10.2024

# Definiert die Klasse Auction.
# In einer Auktion wird ein Item, das von einem User versteigert wird (seller_id), an einen anderen User versteigert
# (purchaser_id). Es können mehrere User bei einer Auktion bieten, diese werden im Heap _users_bidding gespeichert

from typing import Any, List, Optional, Set, Tuple
import heapq
import marketplace.user
import marketplace.item
import marketplace.stack
import random
from datetime import datetime, timedelta


class Auction:
    """Klasse zur Repräsentation einer Auktion auf dem Marktplatz.

    Attributes:
        _id (str): Auktions-ID.
        _item (marketplace.item.Item): Der zu versteigernde Artikel.
        _seller_id (str): Benutzer-ID des Verkäufers.
        _purchaser_id (Optional[str]): Benutzer-ID des Käufers / Höchstbietenden.
        _auction_ends (datetime): Auslaufzeitpunkt der Auktion.
        _recommended2users (Set[str]): Menge von Benutzer-IDs, denen die Auktion empfohlen wurde.
        _users_bidding (List[Tuple[float, str]]): Min-Heap der Gebote (-gebotsbetrag, user_id).
        _bids_ordered (marketplace.stack.Stack): Chronologischer Stapel aller Gebote (user_id, bid_amount).
    """

    # *** CONSTRUCTORS ***
    def __init__(self, auction_id: str, user_id: str, item: marketplace.item.Item) -> None:
        """Standard-Konstruktor zur Erstellung einer Auktion.

        Args:
            auction_id (str): Die eindeutige Auktions-ID.
            user_id (str): Die Verkäufer-ID.
            item (marketplace.item.Item): Das zu verkaufende Item.

        Raises:
            None
        """
        self._id: str = auction_id

        self._item: marketplace.item.Item = item

        self._seller_id: str = user_id
        self._purchaser_id: Optional[str] = None       # noch hat niemand das Produkt gekauft

        # Uhrzeit inklusive datum, wann Auktion ausläuft (bis zu 30 Minuten = 1800 Sekunden).
        self._auction_ends: datetime = datetime.now() + timedelta(seconds=random.randint(45, 1800))

        # Menge von Nutzern, der diese Auktion empfohlen wird
        # auctions recommended to user because its friends are also interested, or because user has already bought or is
        # currently bidding on similar products
        self._recommended2users: Set[str] = set()

        # use a heap to add a new customer with its bid (heapq implements a min heap)
        self._users_bidding: List[Tuple[float, str]] = []

        # bids of all users on this auction in the order in which they were done. the last bid
        # is on top of the stack
        self._bids_ordered: marketplace.stack.Stack = marketplace.stack.Stack()

    # *** PUBLIC SET methods ***

    def set_purchaser_id(self) -> Optional[str]:
        """Setzt die Käufer-ID auf den Höchstbietenden, wenn die Auktion abgelaufen ist.

        Args:
            None

        Returns:
            Optional[str]: Die Benutzer-ID des Käufers oder 'Kein Bieter'.

        Raises:
            ValueError: Wenn die Auktion noch nicht abgelaufen ist.
        """
        if self.expired():
            self._purchaser_id = self.get_highest_bidder()
        else:
            raise ValueError("set_purchaser_id() darf noch nicht aufgerufen werden, da Auktion noch nicht zu Ende ist!")

        return self._purchaser_id

    def recommend2user(self, user_id: str) -> None:
        """Fügt einen Benutzer zur Empfehlungsliste für diese Auktion hinzu.

        Args:
            user_id (str): Die ID des Benutzers.

        Returns:
            None

        Raises:
            None
        """
        self._recommended2users.add(user_id)

    # *** PUBLIC methods ***

    def bid(self, user: marketplace.user.User, bid_amount: float) -> bool:
        """Platziert ein Gebot eines Benutzers für diese Auktion.

        Args:
            user (marketplace.user.User): Der bietende Benutzer.
            bid_amount (float): Der Gebotsbetrag in Euro.

        Returns:
            bool: `True`, wenn das Gebot erfolgreich abgegeben wurde, sonst `False`.

        Raises:
            None
        """
        # auf abgelaufene oder bereits abgewickelte Auktionen darf nicht mehr geboten werden
        if self.expired() or self.sold():
            return False

        if bid_amount > user.balance():         # has user enough money?
            return False

        if bid_amount < self._item.value_min():     # is bid_amount above the minimum bid?
            return False

        user_id = user.id()

        portofee = self.calculate_portofee()

        # check whether user already bid before. If yes then check if new bid is higher than previous one.
        # if higher, then decrease balance only by the difference between both bids
        # muss dann auch in _bids_ordered den entsprechenden eintrag löschen und in _users_bidding auch oder dort den
        # betrag und den heap aktualisieren

        old_bid = self.get_bid_of_user(user_id)

        if old_bid is None or old_bid < bid_amount:

            if old_bid is not None:     # dann gibt es schon ein Gebot von user_id
                # altes Gebot aus dem Heap löschen und weiter unten das neue Gebot in den Heap schreiben.
                # bliebe das alte Gebot im Heap, könnte get_bid_of_user() das alte, niedrigere Gebot liefern und
                # bei Auktionsende würde jedes alte Gebot erneut erstattet. Ein Element aus der Mitte eines Heaps
                # zu löschen und den Heap neu aufzubauen kostet O(n), s. auch:
                # https://docs.python.org/3/library/heapq.html#priority-queue-implementation-notes
                self._users_bidding[:] = [(value, id_bidder) for value, id_bidder in self._users_bidding
                                          if id_bidder != user_id]
                heapq.heapify(self._users_bidding)

                # Porto wurde schon im ersten Gebot abgezogen, deshalb muss es nicht nochmal abgezogen werden
                portofee = 0.0

                for item in list(self._bids_ordered):
                    if item[0] == user_id:
                        self._bids_ordered.remove(item)

            else:
                old_bid = 0.0     # setze old_bid von None auf 0, um unten damit rechnen zu können

            # TODO: bisher ist es so, dass user direkt sein bid_amount bietet und nicht bid_amount als
            #  maximalgebot gesehen wird
            #  und nur so viel geboten wird, wie nötig ist, bspw. 1 € über aktuelles max-gebot
            heapq.heappush(self._users_bidding, (-bid_amount, user_id))

            self._bids_ordered.push((user_id, bid_amount))

            user.decrease_balance(bid_amount + portofee - old_bid)

            # eine auktion, die user empfohlen wurde, muss jetzt nicht mehr empfohlen werden, da user
            # ja jetzt bietet
            if self.is_recommended2user(user_id):
                self._recommended2users.remove(user_id)

            return True
        else:
            return False

    def calculate_portofee(self) -> float:
        """Berechnet Porto für die Lieferung der Bestellung. Porto ist abhängig von Distanz zwischen Käufer und Verkäufer.

        Args:
            None

        Returns:
            float: Die Portogebühr in Euro.

        Raises:
            None
        """
        # TODO students (optionale Aufgabe in Praktikum 3): porto (fee) berechnen
        
        return 0.0

    # *** PUBLIC GET methods ***

    def sold(self) -> bool:
        """Prüft, ob die Auktion bereits abgewickelt/verkauft wurde.

        Args:
            None

        Returns:
            bool: `True`, wenn `_purchaser_id` gesetzt ist, sonst `False`.

        Raises:
            None
        """
        return self._purchaser_id is not None

    def sold_success(self) -> bool:
        """Prüft, ob die Auktion erfolgreich an einen echten Käufer verkauft wurde.

        Args:
            None

        Returns:
            bool: `True`, wenn `_purchaser_id` gesetzt und ungleich 'Kein Bieter' ist.

        Raises:
            None
        """
        return self._purchaser_id is not None and self._purchaser_id != "Kein Bieter"

    def expired(self) -> bool:
        """Prüft, ob die Auktion abgelaufen ist.

        Args:
            None

        Returns:
            bool: `True`, wenn die aktuelle Zeit das Auktionsende erreicht oder überschritten hat.

        Raises:
            None
        """
        return datetime.now() >= self._auction_ends

    def pretty_print(self, with_sold_by: bool = True, user_id: Optional[str] = None) -> str:
        """Formatiert die Auktionsdetails als String für die Listboxen.

        Args:
            with_sold_by (bool): Gibt an, ob der Verkäufer angezeigt werden soll.
            user_id (Optional[str]): Falls angegeben, wird auch das eigene Gebot des Benutzers dargestellt.

        Returns:
            str: Der formatierte Auktions-String.

        Raises:
            None
        """
        if with_sold_by:
            return "ID: {0} Name: {1} Mindestgebot: {2} € \tHöchstes Gebot: {3} € \tAuktionsende: {4} \tVerkäufer: {5}".format(
                self._id.ljust(15), self._item.name().ljust(30), self._item.value_min(),
                self.get_highest_bid(),
                marketplace.auction.Auction.format_datetime(self._auction_ends), self._seller_id.ljust(10))
        elif user_id is not None:
            return "ID: {0} Name: {1} Mindestgebot: {2} € \tHöchstes Gebot: {3} € \tIhr Gebot: {4} € \tAuktionsende: {5}".format(
                self._id.ljust(15), self._item.name().ljust(30), self._item.value_min(),
                self.get_highest_bid(), self.get_bid_of_user(user_id),
                marketplace.auction.Auction.format_datetime(self._auction_ends))
        else:
            return "ID: {0} Name: {1} Mindestgebot: {2} € \tHöchstes Gebot: {3} € \tAuktionsende: {4}".format(
                self._id.ljust(15), self._item.name().ljust(30), self._item.value_min(),
                self.get_highest_bid(),
                marketplace.auction.Auction.format_datetime(self._auction_ends))

    def get_highest_bid(self) -> float:
        """Gibt das Höchstgebot in Euro zurück.

        Args:
            None

        Returns:
            float: Das höchste abgegebene Gebot in Euro.

        Raises:
            None
        """
        if not self._users_bidding:
            return 0.0
        return -self._users_bidding[0][0]  # Negative because we use a min-heap

    def get_highest_bidder(self) -> str:
        """Gibt die Benutzer-ID des Höchstbietenden zurück.

        Args:
            None

        Returns:
            str: Die Benutzer-ID oder 'Kein Bieter'.

        Raises:
            None
        """
        if not self._users_bidding:
            return "Kein Bieter"
        return self._users_bidding[0][1]

    def get_item_name(self) -> str:
        """Gibt den Namen des Artikels zurück.

        Args:
            None

        Returns:
            str: Name des Artikels.

        Raises:
            None
        """
        return self._item.name()

    def get_item_value_min(self) -> float:
        """Gibt das Mindestgebot des Artikels zurück.

        Args:
            None

        Returns:
            float: Mindestgebot in Euro.

        Raises:
            None
        """
        return self._item.value_min()

    def get_item_description(self) -> str:
        """Gibt die Beschreibung des Artikels zurück.

        Args:
            None

        Returns:
            str: Artikelbeschreibung.

        Raises:
            None
        """
        return self._item.description()

    def get_time_left(self) -> float:
        """Berechnet die verbleibende Zeit der Auktion in Sekunden.

        Args:
            None

        Returns:
            float: Verbleibende Sekunden.

        Raises:
            None
        """
        return (self._auction_ends - datetime.now()).total_seconds()

    def is_user_bidding(self, user_id: str) -> bool:
        """Prüft, ob der angegebene Benutzer für diese Auktion bietet.

        Args:
            user_id (str): Die zu prüfende Benutzer-ID.

        Returns:
            bool: `True`, wenn der Benutzer mitbietet, sonst `False`.

        Raises:
            None
        """
        return any(id_bidder == user_id for _, id_bidder in self._users_bidding)

    def is_any_bidder(self) -> bool:
        """Prüft, ob für die Auktion mindestens ein Gebot vorliegt.

        Args:
            None

        Returns:
            bool: `True`, wenn Gebote vorhanden sind, sonst `False`.

        Raises:
            None
        """
        return bool(self._users_bidding)

    def get_bid_of_user(self, user_id: str) -> Optional[float]:
        """Gibt das Gebot eines bestimmten Benutzers in dieser Auktion zurück.

        Args:
            user_id (str): Die Benutzer-ID.

        Returns:
            Optional[float]: Das Gebot in Euro oder `None`, falls der Benutzer nicht bietet.

        Raises:
            None
        """
        # minuszeichen wegen min-heap
        return next((-value for value, id_bidder in self._users_bidding if id_bidder == user_id), None)

    def is_recommended2user(self, user_id: str) -> bool:
        """Prüft, ob die Auktion dem Benutzer empfohlen wurde (und entfernt sie ggf., falls der Nutzer bereits bietet).

        Args:
            user_id (str): Die Benutzer-ID.

        Returns:
            bool: `True`, wenn dem Benutzer empfohlen, sonst `False`.

        Raises:
            None
        """
        if self.is_user_bidding(user_id) and user_id in self._recommended2users:
            self._recommended2users.remove(user_id)
        # auction soll nur empfohlen werden, wenn user_id nicht schon auf Auktion bietet
        return user_id in self._recommended2users  # and not self.is_user_bidding(user_id)

    def get_last_bid(self) -> Optional[Tuple[str, float]]:
        """Gibt das zeitlich letzte Gebot auf den Stapel zurück.

        Args:
            None

        Returns:
            Optional[Tuple[str, float]]: Das letzte Gebot (user_id, bid_amount) oder `None`.

        Raises:
            None
        """
        return self._bids_ordered.peek()

    # *** PUBLIC STATIC methods ***

    @staticmethod
    def get_id_from_pretty_print(printed_auction: str) -> str:
        """Extrahiert die Auktions-ID aus dem formatierten Listbox-Text.

        Args:
            printed_auction (str): Der formatierte String einer Auktion.

        Returns:
            str: Die extrahierte Auktions-ID.

        Raises:
            IndexError: Falls das Format nicht den Erwartungen entspricht.
        """
        printed_auction_split = printed_auction.split("Name: ")
        return printed_auction_split[0][4:].rstrip()

    @staticmethod
    def format_datetime(dt: datetime) -> str:
        """Formatiert ein Datetime-Objekt in einen lesbaren String ("heute, ...", "morgen, ...").

        Args:
            dt (datetime): Das zu formatierende Datetime-Objekt.

        Returns:
            str: Der formatierte Datums-String.

        Raises:
            None
        """
        now = datetime.now()
        today = now.date()
        tomorrow = today + timedelta(days=1)
        dt_date = dt.date()

        if dt_date == today:
            return dt.strftime("heute, %H:%M Uhr")
        elif dt_date == tomorrow:
            return dt.strftime("morgen, %H:%M Uhr")
        else:
            delta = (dt_date - today).days
            return dt.strftime(f"in {delta} Tagen, %H:%M Uhr")

    # *** PRIVATE methods ***

    # *** PUBLIC methods to return class properties ***

    def id(self) -> str:
        """Gibt die Auktions-ID zurück.

        Args:
            None

        Returns:
            str: Auktions-ID.

        Raises:
            None
        """
        return self._id

    def seller_id(self) -> str:
        """Gibt die Verkäufer-ID zurück.

        Args:
            None

        Returns:
            str: Verkäufer-ID.

        Raises:
            None
        """
        return self._seller_id

    def purchaser_id(self) -> Optional[str]:
        """Gibt die Käufer-ID zurück.

        Args:
            None

        Returns:
            Optional[str]: Käufer-ID oder `None`.

        Raises:
            None
        """
        return self._purchaser_id

    def auction_ends(self) -> datetime:
        """Gibt den Endzeitpunkt der Auktion zurück.

        Args:
            None

        Returns:
            datetime: Endzeitpunkt.

        Raises:
            None
        """
        return self._auction_ends

    def item(self) -> marketplace.item.Item:
        """Gibt das Auktions-Item zurück.

        Args:
            None

        Returns:
            marketplace.item.Item: Artikel-Objekt.

        Raises:
            None
        """
        return self._item

    def users_bidding(self) -> List[Tuple[float, str]]:
        """Gibt den Min-Heap der Bietenden zurück.

        Args:
            None

        Returns:
            List[Tuple[float, str]]: Bietende-Heap.

        Raises:
            None
        """
        return self._users_bidding

    def recommended2users(self) -> Set[str]:
        """Gibt die Menge der empfohlenen Benutzer zurück.

        Args:
            None

        Returns:
            Set[str]: Menge von Benutzer-IDs.

        Raises:
            None
        """
        return self._recommended2users

    def bid_count(self) -> int:
        """Gibt die Anzahl der Nutzer zurück, die auf diese Auktion bieten.

        Jeder Nutzer hat genau einen Eintrag (sein aktuelles Gebot) im Heap `_users_bidding`.

        Args:
            None

        Returns:
            int: Anzahl bietender Nutzer.

        Raises:
            None
        """
        return len(self._users_bidding)

    # *** PRIVATE variables ***
