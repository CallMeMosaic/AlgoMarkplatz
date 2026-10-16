"""Übersicht über den Dateiinhalt:

Implementiert den ADT Stack (Stapel) auf Basis einer Python-Liste.
Ermöglicht Standard-Stapeloperationen wie Push, Pop, Peek sowie Hilfsmethoden.
"""

# Status: FINAL, dgaida2, 15.10.2024

# Implementiert den ADT Stack (Stapel) mit der Datenstruktur: Python-Liste (dynamisches Array)

from typing import Any, Optional


class Stack(list):
    """Klasse zur Repräsentation eines Stapels (Stack ADT) basierend auf einer Liste.

    Attributes:
        None (erbt von list).
    """

    # *** CONSTRUCTORS ***
    def __init__(self) -> None:
        """Standard-Konstruktor zur Initialisierung des Stapels.

        Args:
            None

        Raises:
            None
        """
        super().__init__()

    # *** PUBLIC methods ***

    def push(self, item: Any) -> None:
        """Fügt ein Element oben auf den Stapel.

        Args:
            item (Any): Das hinzuzufügende Element.

        Returns:
            None

        Raises:
            None
        """
        self.append(item)

    # laut Vorlesung gibt es diese Methode nicht in einem Stack
    def update(self, item: Any, item_new: Any) -> None:
        """Ersetzt ein bestehendes Element im Stapel durch ein neues Element.

        Args:
            item (Any): Das zu suchende Element.
            item_new (Any): Das neue Element.

        Returns:
            None

        Raises:
            None
        """
        for i, myitem in enumerate(self):
            if myitem == item:
                self[i] = item_new

    # *** PUBLIC GET methods ***

    # Die Methode pop() wird bereits durch die parent Klasse list implementiert

    def peek(self) -> Optional[Any]:
        """Gibt das oberste Element des Stapels zurück, ohne es zu entfernen.

        Args:
            None

        Returns:
            Optional[Any]: Das oberste Element oder `None`, wenn der Stapel leer ist.

        Raises:
            None
        """
        if self.is_empty():
            return None
        return self[-1]

    def is_empty(self) -> bool:
        """Überprüft, ob der Stapel leer ist.

        Args:
            None

        Returns:
            bool: `True`, wenn der Stapel leer ist, sonst `False`.

        Raises:
            None
        """
        return len(self) == 0

    def size(self) -> int:
        """Gibt die Anzahl der Elemente im Stapel zurück.

        Args:
            None

        Returns:
            int: Anzahl der Elemente im Stapel.

        Raises:
            None
        """
        return len(self)
