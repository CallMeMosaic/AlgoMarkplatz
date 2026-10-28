"""Übersicht über den Dateiinhalt:

Implementiert den MaxHeap zur effizienten Verwaltung von Auktionen basierend
auf der Anzahl der abgegebenen Gebote. Die Auktion mit den meisten Geboten
befindet sich an der Spitze des Heaps.
"""
# Status: FINAL, dgaida2, 15.10.2024

# Die Klasse MaxHeap implementiert einen Max-Heap

from typing import Dict, List, Optional, Tuple


class MaxHeap:
    """Klasse zur Repräsentation eines Max-Heaps für Auktionen.

    Attributes:
        heap (List[Tuple[int, str]]): Liste von (bid_count, auction_id) Tupeln.
        auction_map (Dict[str, Tuple[int, int]]): Hash-Map (auction_id -> (bid_count, heap_index)).
    """

    def __init__(self) -> None:
        """Initialisiert eine neue MaxHeap-Instanz.

        Args:
            None

        Raises:
            None
        """
        self.heap: List[Tuple[int, str]] = []
        self.auction_map: Dict[str, Tuple[int, int]] = {}

    # *** PUBLIC methods ***

    def add_auction(self, auction_id: str, bid_count: int) -> None:
        """Fügt eine neue Auktion zum Max-Heap hinzu.

        Args:
            auction_id (str): Auktions-ID.
            bid_count (int): Gebotsanzahl.

        Returns:
            None

        Raises:
            ValueError: Wenn die Auktion bereits im Heap existiert.
        """
        if auction_id in self.auction_map:
            raise ValueError("Auktion existiert bereits")

        # Neues Element ans Ende setzen und nach oben sortieren
        self.heap.append((bid_count, auction_id))
        index = len(self.heap) - 1
        self.auction_map[auction_id] = (bid_count, index)
        self._heapify_up(index)

    def update_bidders(self, auction_id: str, new_bid_count: int) -> None:
        """Aktualisiert die Gebotsanzahl einer existierenden Auktion im Heap.

        Args:
            auction_id (str): Auktions-ID.
            new_bid_count (int): Neue Gebotsanzahl.

        Returns:
            None

        Raises:
            ValueError: Wenn die Auktion nicht im Heap existiert.
        """
        if auction_id not in self.auction_map:
            raise ValueError("Auktion existiert nicht")

        old_bid_count, index = self.auction_map[auction_id]
        self.heap[index] = (new_bid_count, auction_id)
        self.auction_map[auction_id] = (new_bid_count, index)

        if new_bid_count > old_bid_count:
            self._heapify_up(index)
        elif new_bid_count < old_bid_count:
            self._heapify_down(index)

    def remove(self, auction_id: str) -> None:
        """Entfernt eine Auktion aus dem Max-Heap.

        Args:
            auction_id (str): Auktions-ID.

        Returns:
            None

        Raises:
            ValueError: Wenn die Auktion nicht im Heap existiert.
        """
        if auction_id not in self.auction_map:
            raise ValueError("Auktion existiert nicht")

        _, index = self.auction_map[auction_id]
        last = len(self.heap) - 1

        if index != last:
            # Zu entfernendes Element mit dem letzten tauschen
            self._swap(index, last)

        self.heap.pop()
        del self.auction_map[auction_id]

        # Das nachgerückte Element kann nach oben oder unten wandern müssen
        if index < len(self.heap):
            self._heapify_up(index)
            self._heapify_down(index)

    def get_auction_with_max_bidders(self) -> Optional[Tuple[int, str]]:
        """Gibt die Auktion mit den meisten Geboten an der Spitze des Heaps zurück.

        Args:
            None

        Returns:
            Optional[Tuple[int, str]]: Tupel aus (bid_count, auction_id) oder `None`.

        Raises:
            None
        """
        if not self.heap:
            return None
        return self.heap[0][0], self.heap[0][1]

    def get_auction_bidders(self, auction_id: str) -> Optional[int]:
        """Gibt die Gebotsanzahl einer Auktion zurück.

        Args:
            auction_id (str): Auktions-ID.

        Returns:
            Optional[int]: Gebotsanzahl oder `None`, falls nicht vorhanden.

        Raises:
            None
        """
        if auction_id in self.auction_map:
            return self.auction_map[auction_id][0]
        return None

    # *** PRIVATE methods ***

    def _swap(self, i: int, j: int) -> None:
        """ Hilfsfunktion zum Tauschen von zwei Auktionen im Max-Heap.
            Aktualisiert ebenfalls die Position der Auktionen in der auction_map.

        Args:
            i: Index der ersten Auktion im Max-Heap.
            j: Index der zweiten Auktion im Max-Heap.
        """
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]

        bid_i, id_i = self.heap[i]
        bid_j, id_j = self.heap[j]
        self.auction_map[id_i] = (bid_i, i)
        self.auction_map[id_j] = (bid_j, j)

    def _heapify_up(self, index: int) -> None:
        """ Führt das Heapify-Up-Verfahren durch, um die Heap-Eigenschaft nach oben hin wiederherzustellen.

        Args:
            index: Der Index des Elements, das nach oben "heapified" werden soll.
        """
        while index > 0:
            parent = (index - 1) // 2
            if self.heap[index][0] > self.heap[parent][0]:
                self._swap(index, parent)
                index = parent
            else:
                break

    def _heapify_down(self, index: int) -> None:
        """ Führt das Heapify-Down-Verfahren durch, um die Heap-Eigenschaft nach unten hin wiederherzustellen.

        Args:
            index: Der Index des Elements, das nach unten "heapified" werden soll.
        """
        size = len(self.heap)
        while True:
            left = 2 * index + 1
            right = 2 * index + 2
            largest = index

            if left < size and self.heap[left][0] > self.heap[largest][0]:
                largest = left
            if right < size and self.heap[right][0] > self.heap[largest][0]:
                largest = right

            if largest == index:
                break

            self._swap(index, largest)
            index = largest