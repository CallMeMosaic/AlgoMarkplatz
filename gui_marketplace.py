"""Übersicht über den Dateiinhalt:

Hauptdatei zur Ausführung der Marktplatz GUI-Anwendung (`AuctionApp`).
Erbt von `AuctionAppInit` und erweitert die Anwendung um einen periodischen
Timer (alle 30 Sekunden), der abgelaufene Auktionen prüft, Top-Auktionen und
Top-User ermittelt sowie die Ansichten der Benutzeroberfläche aktualisiert.
"""

# Status: Not FINAL, dgaida2, 15.10.2024

# main file

from typing import Any
import tkinter as tk
import threading

from auctionapp_init import AuctionAppInit


class AuctionApp(AuctionAppInit):
    """Hauptklasse der Auktions-GUI-Anwendung. Erbt von `AuctionAppInit`.

    Attributes:
        root (tk.Tk): Das Hauptfenster der Tkinter-Anwendung.
    """

    # *** CONSTRUCTORS ***
    def __init__(self, root: tk.Tk) -> None:
        """Initialisiert die AuctionApp und startet den periodischen Update-Timer.

        Args:
            root (tk.Tk): Das Tkinter-Hauptfenster.

        Raises:
            Exception: Wenn die Initialisierung der Oberklasse fehlschlägt.
        """
        super().__init__(root)

        self.start_update_timer()

    # *** Alle 30 Sekunden wird überprüft welche Auktionen abgelaufen sind und die Listen werden aktualisiert ***

    def update_listboxes(self) -> None:
        """Prüft abgelaufene Auktionen, pusht Systemnachrichten und aktualisiert alle Listboxen.

        Diese Methode wird alle 30 Sekunden über `root.after` erneut aufgerufen.

        Args:
            None

        Returns:
            None
        """
        self._check_auctions_expiry()

        top_auction = self._auctions.get_top_auction(True)

        if top_auction is not None:
            self.system_messages.push(
                "Die TOP Auktion mit {0} Geboten ist Auktion {1} in der man ein {2} für aktuell {3} € ersteigern kann.".format(
                    top_auction[0], top_auction[1], self._auctions.get_item_name(top_auction[1]),
                    self._auctions.get_highest_bid(top_auction[1])
                ))

        top_user = self._auctions.get_top_rated_user(True)

        # top_user[1] ist None, solange noch niemand bewertet wurde
        if top_user is not None and top_user[1] is not None:
            self.system_messages.push("Der am besten bewertete User mit {0:.1f} Sternen ist user {1}.".format(
                    top_user[0], top_user[1])
                )

        # der Simulator erstellt laufend neue Auktionen, deren Produktnamen sollen auch vorgeschlagen werden
        self.rebuild_trie()

        # Aktualisieren Sie alle Listboxen hier
        self.add_items2all_items_list()
        self.search_items()

        if self._current_user:
            self.update_lists()

        self.system_messages.push("Beim Speichern von {1} Transaktionen traten {0} Kollisionen auf.".format(
            self._auctions.get_transactions_collisions(), self._auctions.get_transactions_size()))

        # Wiederhole die Aktualisierung alle 30 Sekunden (30000 Millisekunden)
        self.root.after(30000, self.update_listboxes)

    def start_update_timer(self) -> None:
        """Startet den Update-Timer zur periodischen Aktualisierung der Benutzeroberfläche.

        Args:
            None

        Returns:
            None
        """
        # Starte den Timer zur Aktualisierung der Listboxen
        self.update_listboxes()

    # *** PRIVATE METHODS ***

    def _check_auctions_expiry(self) -> None:
        """Prüft im Hintergrund alle Auktionen auf Ablauf und informiert die beteiligten Nutzer.

        Args:
            None

        Returns:
            None
        """
        for auction_id, auction in list(self._auctions.items()):
            # gehe alle Auktionen durch, die abgelaufen sind, aber noch nicht als verkauft gelten. das sind Auktionen,
            # bei denen der neue Käufer noch nicht eingetragen ist. der Käufer wird in handle_expired_auction() gesetzt.
            # da wir über jede Auktion nur einmal informieren wollen, ist die Abfrage auction.sold wichtig
            if auction.expired() and not auction.sold():
                success = self._auctions.handle_expired_auction(auction_id)

                if self._current_user is not None:

                    if auction.seller_id() == self._current_user.id():
                        if success:
                            self.system_messages.push(
                                "Ihr {0} wurde gerade erfolgreich für {1:.2f} € versteigert.".format(
                                    auction.get_item_name(), auction.get_highest_bid()))
                        else:
                            self.system_messages.push(
                                "Ihre Auktion für {0} ist ausgelaufen, hat aber keinen Käufer gefunden.".format(
                                    auction.get_item_name()))

                    if auction.purchaser_id() == self._current_user.id():
                        self.system_messages.push(
                            "Sie haben {0} gerade erfolgreich für {1:.2f} € ersteigert.".format(
                                auction.get_item_name(), auction.get_highest_bid()))

                    if auction.is_user_bidding(self._current_user.id()):
                        if auction.purchaser_id() != self._current_user.id():
                            self.system_messages.push(
                                "Die Auktion für {0} wurde gerade beendet, allerdings wurde Ihr Angebot überboten.".format(
                                    auction.get_item_name()))

    # *** ... ***


if __name__ == "__main__":
    root = tk.Tk()
    app = AuctionApp(root)
    root.mainloop()
