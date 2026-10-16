"""Übersicht über den Dateiinhalt:

Implementiert die Klassen `TrieNode` und `Trie` zur effizienten Präfix-Suche
und Autovervollständigung von Wörtern (z. B. Produktnamen).
"""

# Status: FINAL, dgaida2, 15.10.2024
# Definiert die Klasse Trie. class is used to look for all words that start with a given prefix.

from typing import Dict, List, Optional


class TrieNode:
    """Ein Knoten in der Trie-Datenstruktur.

    Attributes:
        children (Dict[str, TrieNode]): Wörterbuch, das Zeichen auf Kind-TrieNodes abbildet.
        _is_end_of_word (bool): Flag, das angibt, ob der Knoten das Ende eines Wortes darstellt.
    """

    # *** CONSTRUCTORS ***
    def __init__(self) -> None:
        """Initialisiert einen TrieNode mit leerem Kind-Wörterbuch und is_end_of_word=False.

        Args:
            None

        Raises:
            None
        """
        self.children: Dict[str, TrieNode] = {}
        self._is_end_of_word: bool = False

    # *** PUBLIC SET methods ***

    def set_is_end_of_word(self) -> None:
        """Setzt das Flag _is_end_of_word auf True.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        self._is_end_of_word = True

    # *** PUBLIC methods to return class properties ***

    def is_end_of_word(self) -> bool:
        """Gibt zurück, ob dieser Knoten das Ende eines Wortes markiert.

        Args:
            None

        Returns:
            bool: `True`, wenn Endknoten eines Wortes, sonst `False`.

        Raises:
            None
        """
        return self._is_end_of_word


class Trie:
    """Trie-Datenstruktur zum Speichern und Durchsuchen von Zeichenketten.

    Attributes:
        _root (TrieNode): Die Wurzel des Tries.
    """

    # *** CONSTRUCTORS ***
    def __init__(self) -> None:
        """Initialisiert einen neuen Trie mit einer Wurzel.

        Args:
            None

        Raises:
            None
        """
        self._root: TrieNode = TrieNode()

    # *** PUBLIC methods ***

    def insert(self, word: str) -> None:
        """Fügt ein Wort in den Trie ein.

        Args:
            word (str): Das einzufügende Wort.

        Returns:
            None

        Raises:
            None
        """
        word = word.lower()
        node = self._root
        for char in word:           # for each character of the word
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.set_is_end_of_word()

    # *** PUBLIC GET methods ***

    def search(self, prefix: str) -> List[str]:
        """Sucht nach allen Wörtern im Trie, die mit dem angegebenen Präfix beginnen.

        Args:
            prefix (str): Das Suchpräfix.

        Returns:
            List[str]: Liste aller passenden Wörter.

        Raises:
            None
        """
        prefix = prefix.lower()
        node = self._root
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]
        return Trie._find_words(node, prefix)

    # *** PRIVATE methods ***

    @staticmethod
    def _find_words(node: TrieNode, prefix: str) -> List[str]:
        """Rekursive Hilfsmethode zur Ermittlung aller Wörter ab einem gegebenen Knoten.

        Args:
            node (TrieNode): Der Ausgangsknoten.
            prefix (str): Das bis zum Knoten gebildete Präfix.

        Returns:
            List[str]: Liste der ab diesem Knoten gefundenen Wörter.

        Raises:
            None
        """
        words: List[str] = []
        if node.is_end_of_word():
            words.append(prefix)
        for char, next_node in node.children.items():
            words.extend(Trie._find_words(next_node, prefix + char))
        return words
