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
        """
        Einfache Methode, um die _is_end_of_word Eigenschaft eines Knotens zu verändernt. Die wird benötigt, wenn ein Knoten
        durch ein neues Wort zu einem möglichen Ende eines Wortes wird.

        :return: None
        """

        self._is_end_of_word = True


    # *** PUBLIC methods to return class properties ***

    def is_end_of_word(self) -> bool:
        """
        Einfache Methode, welche den Wert der _is_end_of_word Eigenschaft zurückgibt, da diese per Konvention nicht erreichbar sein soll.

        :return: True, wenn Endknoten eines Wortes, sonst False.
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
        """
        Das Einfügen eines Knotens in den Trie erfolgt durch das Durchlaufen des
        Wortes in einzelnen Buchstaben.Dabei wird der Trie durchiteriert, sollte ein Knoten nicht bereits existieren,
        so wird er erstellt.
        Sobald das Wort durchiteriert wurde, wird der Buchstabe, der gerade erreicht wurde, als ein EndOfWord Knoten markiert.

        :param word: Das Wort, welches Hinzugefügt werden soll.
        :return: None.
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
        """
        Nimmt eine Prefix entgegen und durchsucht den Trie nach möglichen Endungen für das gegebene Prefix.
        Iteriert durch die Buchstaben des Prefixes bis das Ende des Prefixes erreicht wurde.
        Ruft nach erreichen des Endes die Hilfsmethode _find_words auf und gibt eine Liste aller möglichen Endungen mit dem Prefix zusammen aus.
        Sollte das Prfix nicht existieren, wird eine leere Liste ausgegebne.

        :param prefix: Das eingegebene Wort, für welches die möglichen Endungen gesucht werden sollen.
        :return: Eine Liste aller möglichen Endungen des Prefixes oder eine leere Liste, falls das Prefix nicht im Trie vorhanden ist.
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
        """
        Dient als Hilfsmethode zur Ermittlung aller möglichen Endungen eines gegebenen Prefixes im Trie.
        Checkt als erstes, ob das Prefix selbst ein valides Wort im Trie ist, wenn dies der Fall ist wird es in die Liste appended.
        Danach wird rekursiv über alle Kinder des Knotens iteriert um die möglichen Endungen zu finden, dabei wird das Prefix immer um den Char des momentatnen
        Knotens ergänzt, sollte das Resultat eine Endung sein, wird es zur Liste appended.
        Gibt am Ende die Liste aller gefundenen Endunge aus.

        :param node: Der Startknoten für die Sucht (Das Prefix endet hier).
        :param prefix: Die Zeichenkette des Prefixes.
        :return: Liste aller gefundenen Endungen.
        """

        words: List[str] = []
        if node.is_end_of_word():
            words.append(prefix)
        for char, next_node in node.children.items():
            words.extend(Trie._find_words(next_node, prefix + char))
        return words
