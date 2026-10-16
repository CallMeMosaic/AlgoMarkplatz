"""Übersicht über den Dateiinhalt:

Implementiert die Dataclass `Transaction` und die Hashtabellen-Klasse `Transactions`
zur Erfassung und Zählung von Kaufabwicklungs-Transaktionen und Hash-Kollisionen.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass(frozen=True)
class Transaction:
    """Dataclass zur Repräsentation einer durchgeführten Verkaufstransaktion.

    Attributes:
        seller (str): Name des Verkäufers.
        buyer (str): Name des Käufers.
        price (float): Verkaufspreis in Euro.
        timestamp (datetime): Zeitstempel der Transaktion.
        product_name (str): Name des verkauften Produkts.
    """
    seller: str
    buyer: str
    price: float
    timestamp: datetime
    product_name: str

    def __repr__(self) -> str:
        """Gibt eine kompakte String-Repräsentation der Transaktion zurück.

        Args:
            None

        Returns:
            str: Formatierte Zeichenkette.

        Raises:
            None
        """
        # Compact representation for printing
        ts = self.timestamp.isoformat(timespec="seconds")
        return (f"Transaction(seller={self.seller!r}, buyer={self.buyer!r}, "
                f"price={self.price}, timestamp={ts}, product_name={self.product_name!r})")


class Transactions:
    """Hashtabelle zur Speicherung von Transaktionen und Erfassung von Hash-Kollisionen.

    Attributes:
        _capacity (int): Kapazität/Anzahl der Buckets der Hashtabelle.
        _buckets (List[List[Transaction]]): Liste der Buckets für Transaktionen.
        _size (int): Gesamtanzahl gespeicherter Transaktionen.
        _collisions (int): Gesamtzahl aufgetretener Hash-Kollisionen.
    """
    """
    Intentionally naive hash table
    - Uses a deliberately bad hash function (default: first letter of product name).
    - Counts total collisions since creation.
    """
    
    def __init__(self, capacity: int = 128) -> None:
        """Initialisiert die Transactions-Hashtabelle mit einer bestimmten Kapazität.

        Args:
            capacity (int): Kapazität (Anzahl Buckets). Defaults to 128.

        Raises:
            ValueError: Wenn `capacity` <= 0 ist.
        """
        if capacity <= 0:
            raise ValueError("capacity must be > 0")
        self._capacity: int = capacity
        self._buckets: List[List[Transaction]] = [[] for _ in range(capacity)]
        self._size: int = 0
        self._collisions: int = 0

    # *** PUBLIC METHODS ***

    def insert(self, tx: Transaction) -> None:
        """Fügt eine Transaktion ein und zählt Kollisionen, wenn der Ziel-Bucket nicht leer ist.

        Args:
            tx (Transaction): Die einzufügende Transaktion.

        Returns:
            None

        Raises:
            None
        """
        idx = self._hash_fn(tx)
        bucket = self._buckets[idx]
        if len(bucket) > 0:
            self._collisions += 1
        bucket.append(tx)
        self._size += 1

    # *** PUBLIC GET METHODS ***

    def get_collisions(self) -> int:
        """Gibt die Gesamtzahl aufgetretener Kollisionen seit Erstellung zurück.

        Args:
            None

        Returns:
            int: Anzahl der Kollisionen.

        Raises:
            None
        """
        return self._collisions

    def get_capacity(self) -> int:
        """Gibt die Kapazität (Anzahl der Buckets) der Hashtabelle zurück.

        Args:
            None

        Returns:
            int: Kapazität der Hashtabelle.

        Raises:
            None
        """
        return self._capacity

    def get_size(self) -> int:
        """Gibt die Gesamtanzahl eingefügter Transaktionen zurück.

        Args:
            None

        Returns:
            int: Anzahl gespeicherter Transaktionen.

        Raises:
            None
        """
        return self._size

    # *** PRIVATE METHODS ***

    # TODO: Erstellt eine bessere Hashfunktion, welche möglichst wenig Kollisionen generiert
    def _hash_fn(self, tx: Transaction) -> int:
        """Hashfunktion zur Bestimmung des Bucket-Index einer Transaktion.

        Args:
            tx (Transaction): Die Transaktion.

        Returns:
            int: Der berechnete Bucket-Index.

        Raises:
            None
        """
        # Deliberately bad key function:
        # Use ONLY the first character of the product name.
        if not tx.product_name:
            return 0
        first = tx.product_name[0].lower()
        # Map 'a'..'z' to 0..25, everything else also squeezed into the table
        return (ord(first) - ord('a')) % self._capacity
