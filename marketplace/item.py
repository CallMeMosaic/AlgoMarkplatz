"""Übersicht über den Dateiinhalt:

Diese Datei definiert die Klasse Item.
Sie beschreibt ein Produkt, das über den Marktplatz ersteigert oder verkauft werden kann.
Ein Produkt besitzt einen Namen, eine Beschreibung sowie ein Mindestgebot.
"""

# Status: FINAL, dgaida2, 15.10.2024

# Definiert die Klasse Item.
# Die Klasse beschreibt ein Produkt, das über den Marktplatz über eine Auktion ersteigert/verkauft werden kann.
# Ein Produkt hat einen Namen, eine Beschreibung und ein Wert für ein Mindestgebot. Der Besitzer des Produkts
# wird über die Auktion definiert, da der Besitzer in der Auktion ja wechselt. die eindeutige Identifizierung eines
# Produkts erfolgt über die id der zugehörigen Auktion, deshalb hat diese Klasse keine id.

from typing import Any


class Item:
    """Klasse zur Repräsentation eines Artikels auf dem Marktplatz.

    Attributes:
        _name (str): Name des Artikels.
        _description (str): Satz, der den Artikel beschreibt.
        _value_min (float): Mindestgebot in € für den Artikel.
    """

    # *** CONSTRUCTORS ***
    def __init__(self, name: str, description: str, value_min: float) -> None:
        """Standard-Konstruktor für ein Item.

        Args:
            name (str): Name des Artikels.
            description (str): Beschreibung des Artikels.
            value_min (float): Mindestgebot in € für den Artikel.

        Raises:
            None
        """
        self._name: str = name
        self._description: str = description

        self._value_min: float = float(value_min)

    # *** PUBLIC SET methods ***

    # *** PUBLIC methods ***

    # *** PUBLIC GET methods ***

    # *** PUBLIC STATIC methods ***

    # *** PRIVATE methods ***

    # *** PUBLIC methods to return class properties ***

    def name(self) -> str:
        """Gibt den Namen des Artikels zurück.

        Args:
            None

        Returns:
            str: Name des Artikels.

        Raises:
            None
        """
        return self._name

    def description(self) -> str:
        """Gibt die Beschreibung des Artikels zurück.

        Args:
            None

        Returns:
            str: Beschreibung des Artikels.

        Raises:
            None
        """
        return self._description

    def value_min(self) -> float:
        """Gibt das Mindestgebot des Artikels zurück.

        Args:
            None

        Returns:
            float: Mindestgebot in € für den Artikel.

        Raises:
            None
        """
        return self._value_min

    # *** PRIVATE variables ***
