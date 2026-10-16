"""Übersicht über den Dateiinhalt:

Implementiert die Datenstrukturen `AVLTree` (AVL-Baum) und `Node` (Baum-Knoten).
Ein AVL-Baum ist ein selbstbalancierender binärer Suchbaum, der effiziente Einfüge-,
Such-, Lösch- und Präfix-Vorschlagsoperationen in O(log n) ermöglicht.
"""

# Status: FINAL, dgaida2, 15.10.2024

# Die Klasse AVLTree implementiert einen AVL-Baum

from typing import Any, Dict, List, Optional, Union


class Node:
    """Klasse zur Repräsentation eines Knotens in einem AVL-Baum.

    Attributes:
        key (Optional[str]): Der Schlüsselwert des Knotens (z.B. Produktname).
        values (List[str]): Liste der zugehörigen Werte/Pfade.
        left_child (Optional[Node]): Linkes Kind des Knotens.
        right_child (Optional[Node]): Rechtes Kind des Knotens.
        parent (Optional[Node]): Zeiger auf den Eltern-Knoten.
        height (int): Höhe des Knotens im Baum.
    """

    def __init__(self, key: Optional[str] = None) -> None:
        """Initialisiert einen AVL-Baum-Knoten.

        Args:
            key (Optional[str]): Der Schlüssel für den Knoten.

        Raises:
            None
        """
        self.key: Optional[str] = key
        self.values: List[str] = []
        self.left_child: Optional[Node] = None
        self.right_child: Optional[Node] = None
        self.parent: Optional[Node] = None  # pointer to parent Node in tree
        self.height: int = 1  # height of Node in tree (max dist. to leaf) NEW FOR AVL

    def add_value(self, path: Any) -> None:
        """Fügt einen Wert/Pfad zur Liste der Knotenwerte hinzu.

        Args:
            path (Any): Der hinzuzufügende Wert.

        Returns:
            None

        Raises:
            None
        """
        self.values.append(path)

    def get_value(self) -> List[str]:
        """Gibt die Liste der gespeicherten Knotenwerte zurück.

        Args:
            None

        Returns:
            List[str]: Liste der Werte.

        Raises:
            None
        """
        return self.values


class AVLTree:
    """Klasse zur Repräsentation eines selbstbalancierenden AVL-Baums.

    Attributes:
        root (Optional[Node]): Die Wurzel des AVL-Baums.
    """

    def __init__(self) -> None:
        """Standard-Konstruktor für den AVL-Baum.

        Args:
            None

        Raises:
            None
        """
        self.root: Optional[Node] = None

    def __repr__(self) -> str:
        """Gibt eine visuelle Baumstruktur als String zurück.

        Args:
            None

        Returns:
            str: Die String-Darstellung des Baums.

        Raises:
            None
        """
        if self.root is None:
            return ''
        content = '\n'  # to hold final string
        cur_nodes: List[Optional[Node]] = [self.root]  # all nodes at current level
        cur_height = self.root.height  # height of nodes at current level
        sep = ' ' * (2 ** (cur_height - 1))  # variable sized separator between elements
        while True:
            cur_height += -1  # decrement current height
            if len(cur_nodes) == 0:
                break
            cur_row = ' '
            next_row = ''
            next_nodes: List[Optional[Node]] = []

            if all(n is None for n in cur_nodes):
                break

            for n in cur_nodes:
                if n is None:
                    cur_row += '   ' + sep
                    next_row += '   ' + sep
                    next_nodes.extend([None, None])
                    continue

                if n.key is not None:
                    buf = ' ' * int((5 - len(str(n.key))) / 2)
                    cur_row += '%s%s%s' % (buf, str(n.key), buf) + sep
                else:
                    cur_row += ' ' * 5 + sep

                if n.left_child is not None:
                    next_nodes.append(n.left_child)
                    next_row += ' /' + sep
                else:
                    next_row += '  ' + sep
                    next_nodes.append(None)

                if n.right_child is not None:
                    next_nodes.append(n.right_child)
                    next_row += ' \\' + sep
                else:
                    next_row += '  ' + sep
                    next_nodes.append(None)

            content += (cur_height * '   ' + cur_row + '\n' + cur_height * '   ' + next_row + '\n')
            cur_nodes = next_nodes
            sep = ' ' * int(len(sep) / 2)  # cut separator size in half
        return content

    def insert(self, key: str, value: Any) -> Node:
        """Fügt einen neuen Knoten in den AVL-Baum ein oder aktualisiert ihn.

        Args:
            key (str): Der Schlüssel (in Kleinbuchstaben konvertiert).
            value (Any): Der mit dem Schlüssel assoziierte Wert.

        Returns:
            Node: Der neu erstellte oder aktualisierte Knoten.

        Raises:
            None
        """
        """
            Insert a new Node into the Tree. If the key already exists the associated Node will be updated.

            Return:
            -------
            If the Key does not exist return new Node.
            If the Key does exist return the Node that has been updated.
        """

        if self.root is None:
            new_node = self.create_new_node(key.lower(), value)
            self.root = new_node
            return new_node
        else:
            return self._insert(key.lower(), value, self.root)

    def _insert(self, key: str, value: Any, cur_node: Node) -> Node:
        if cur_node.key is not None and key < cur_node.key:
            if cur_node.left_child is None:
                new_node = self.create_new_node(key, value)
                cur_node.left_child = new_node
                cur_node.left_child.parent = cur_node  # set parent
                self._inspect_insertion(cur_node.left_child)
                return new_node
            else:
                return self._insert(key, value, cur_node.left_child)
        elif cur_node.key is not None and key > cur_node.key:
            if cur_node.right_child is None:
                new_node = self.create_new_node(key, value)
                cur_node.right_child = new_node
                cur_node.right_child.parent = cur_node  # set parent
                self._inspect_insertion(cur_node.right_child)
                return new_node
            else:
                return self._insert(key, value, cur_node.right_child)
        else:
            updated_node = self.update_node(cur_node, value)
            return updated_node

    def print_tree(self) -> None:
        """Druckt alle Schlüssel und Höhen der Knoten Inorder aus.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        if self.root is not None:
            self._print_tree(self.root)

    def _print_tree(self, cur_node: Optional[Node]) -> None:
        if cur_node is not None:
            self._print_tree(cur_node.left_child)
            print('%s, h=%d' % (str(cur_node.key), cur_node.height))
            self._print_tree(cur_node.right_child)

    def height(self) -> int:
        """Berechnet die Gesamthöhe des AVL-Baums.

        Args:
            None

        Returns:
            int: Die maximale Höhe des Baums.

        Raises:
            None
        """
        if self.root is not None:
            return self._height(self.root, 0)
        else:
            return 0

    def _height(self, cur_node: Optional[Node], cur_height: int) -> int:
        if cur_node is None:
            return cur_height
        left_height = self._height(cur_node.left_child, cur_height + 1)
        right_height = self._height(cur_node.right_child, cur_height + 1)
        return max(left_height, right_height)

    def find(self, key: str) -> Optional[Node]:
        """Sucht nach einem Knoten mit dem angegebenen Schlüssel.

        Args:
            key (str): Der gesuchte Schlüssel.

        Returns:
            Optional[Node]: Der gefundene Knoten oder `None`.

        Raises:
            None
        """
        if self.root is not None:
            return self._find(key.lower(), self.root)
        else:
            return None

    def _find(self, key: str, cur_node: Optional[Node]) -> Optional[Node]:
        if cur_node is None or cur_node.key is None:
            return None
        if key == cur_node.key:
            return cur_node
        elif key < cur_node.key and cur_node.left_child is not None:
            return self._find(key, cur_node.left_child)
        elif key > cur_node.key and cur_node.right_child is not None:
            return self._find(key, cur_node.right_child)
        return None

    # TODO for students: Schauen Sie sich diese Methode ganz genau an. Wie wird der AVL-Baum durchlaufen? Zeichnen Sie
    #  am besten einen AVL-Baum und gehen Sie mit dieser Methode Schritt für Schritt durch diesen Baum
    def find_most_likely_words(self, prefix: str) -> List[str]:
        """Findet alle Wörter/Schlüssel, die mit dem angegebenen Präfix beginnen.

        Args:
            prefix (str): Das Suchpräfix.

        Returns:
            List[str]: Sortierte Liste passender Wörter nach Wert absteigend.

        Raises:
            None
        """
        words_dict: Dict[str, Any] = dict()
        start_word = prefix.lower()
        # end_word ist das kleinste Wort, das nicht mehr mit prefix beginnt (z. B. 'cd' -> 'ce').
        # bei leerem Präfix passen alle Wörter
        end_word = start_word[:-1] + str(chr(ord(start_word[-1]) + 1)) if start_word else chr(0x10FFFF)

        if self.root is not None and self.root.key is not None:
            if start_word <= self.root.key < end_word:
                words_dict[self.root.key] = self.root.values[0]
                self._find_most_likely_words(self.root.left_child, words_dict, start_word, end_word)
                self._find_most_likely_words(self.root.right_child, words_dict, start_word, end_word)
            elif self.root.key < start_word:
                self._find_most_likely_words(self.root.right_child, words_dict, start_word, end_word)
            elif self.root.key >= end_word:
                self._find_most_likely_words(self.root.left_child, words_dict, start_word, end_word)

        # Liste der Wörter sortiert nach Value absteigend
        sorted_words = [product for product, count in sorted(words_dict.items(), key=lambda x: x[1], reverse=True)]
        return sorted_words

    def _find_most_likely_words(self, node: Optional[Node], words_dict: dict, start_word: str, end_word: str) -> None:
        if node is not None and node.key is not None:
            if start_word <= node.key < end_word:
                words_dict[node.key] = node.values[0]
                self._find_most_likely_words(node.left_child, words_dict, start_word, end_word)
                self._find_most_likely_words(node.right_child, words_dict, start_word, end_word)
            elif node.key < start_word:
                self._find_most_likely_words(node.right_child, words_dict, start_word, end_word)
            elif node.key >= end_word:
                self._find_most_likely_words(node.left_child, words_dict, start_word, end_word)

    def delete_key(self, key: str) -> None:
        """Löscht einen Schlüssel aus dem AVL-Baum.

        Args:
            key (str): Der zu löschende Schlüssel.

        Returns:
            None

        Raises:
            None
        """
        return self.delete_node(self.find(key))

    def delete_node(self, node: Optional[Node]) -> None:
        """Löscht einen bestimmten Knoten aus dem AVL-Baum und stellt die Balancierung wieder her.

        Args:
            node (Optional[Node]): Der zu löschende Knoten.

        Returns:
            None

        Raises:
            None
        """
        # -----
        # Improvements since prior lesson

        # Protect against deleting a Node not found in the tree
        if node is None or node.key is None or self.find(node.key) is None:
            print("Node to be deleted not found in the tree!")
            return None

        # -----

        # returns the Node with min key in tree rooted at input Node
        def min_key_node(n: Node) -> Node:
            current = n
            while current.left_child is not None:
                current = current.left_child
            return current

        # returns the number of children for the specified Node
        def num_children(n: Node) -> int:
            num_child = 0
            if n.left_child is not None:
                num_child += 1
            if n.right_child is not None:
                num_child += 1
            return num_child

        # get the parent of the Node to be deleted
        node_parent = node.parent

        # get the number of children of the Node to be deleted
        node_children = num_children(node)

        # break operation into different cases based on the
        # structure of the tree & Node to be deleted

        # CASE 1 (Node has no children)
        if node_children == 0:
            if node_parent is not None:
                # remove reference to the Node from the parent
                if node_parent.left_child == node:
                    node_parent.left_child = None
                else:
                    node_parent.right_child = None
            else:
                self.root = None

        # CASE 2 (Node has a single child)
        if node_children == 1:
            # get the single child Node
            child = node.left_child if node.left_child is not None else node.right_child
            if node_parent is not None:
                # replace the Node to be deleted with its child
                if node_parent.left_child == node:
                    node_parent.left_child = child
                else:
                    node_parent.right_child = child
            else:
                self.root = child

            # correct the parent pointer in Node
            if child is not None:
                child.parent = node_parent

        # CASE 3 (Node has two children)
        if node_children == 2:
            # get the inorder successor of the deleted Node
            if node.right_child is not None:
                successor = min_key_node(node.right_child)

                # copy the inorder successor's key to the Node formerly
                # holding the key we wished to delete
                node.key = successor.key

                # delete the inorder successor now that it's key was
                # copied into the other Node
                self.delete_node(successor)

                # exit function so we don't call the _inspect_deletion twice
                return

        if node_parent is not None:
            # fix the height of the parent of current Node
            node_parent.height = 1 + max(self.get_height(node_parent.left_child),
                                         self.get_height(node_parent.right_child))

            # begin to traverse back up the tree checking if there are
            # any sections which now invalidate the AVL balance rules
            self._inspect_deletion(node_parent)

    def search(self, key: str) -> bool:
        """Prüft, ob ein Schlüssel im AVL-Baum vorhanden ist.

        Args:
            key (str): Der zu suchende Schlüssel.

        Returns:
            bool: `True`, wenn der Schlüssel existiert, sonst `False`.

        Raises:
            None
        """
        if self.root is not None:
            return self._search(key.lower(), self.root)
        else:
            return False

    def _search(self, key: str, cur_node: Optional[Node]) -> bool:
        if cur_node is None or cur_node.key is None:
            return False
        if key == cur_node.key:
            return True
        elif key < cur_node.key and cur_node.left_child is not None:
            return self._search(key, cur_node.left_child)
        elif key > cur_node.key and cur_node.right_child is not None:
            return self._search(key, cur_node.right_child)
        return False

    def _inspect_insertion(self, cur_node: Node, path: Optional[List[Node]] = None) -> None:
        if path is None:
            path = []
        if cur_node.parent is None:
            return
        path = [cur_node] + path

        left_height = self.get_height(cur_node.parent.left_child)
        right_height = self.get_height(cur_node.parent.right_child)

        if abs(left_height - right_height) > 1:
            path = [cur_node.parent] + path
            self._rebalance_node(path[0], path[1], path[2])
            return

        new_height = 1 + cur_node.height
        if new_height > cur_node.parent.height:
            cur_node.parent.height = new_height

        self._inspect_insertion(cur_node.parent, path)

    def _inspect_deletion(self, cur_node: Optional[Node]) -> None:
        if cur_node is None:
            return

        left_height = self.get_height(cur_node.left_child)
        right_height = self.get_height(cur_node.right_child)

        if abs(left_height - right_height) > 1:
            y = self.taller_child(cur_node)
            if y is not None:
                x = self.taller_child(y)
                if x is not None:
                    self._rebalance_node(cur_node, y, x)

        self._inspect_deletion(cur_node.parent)

    def _rebalance_node(self, z: Node, y: Node, x: Node) -> None:
        if y == z.left_child and x == y.left_child:
            self._right_rotate(z)
        elif y == z.left_child and x == y.right_child:
            self._left_rotate(y)
            self._right_rotate(z)
        elif y == z.right_child and x == y.right_child:
            self._left_rotate(z)
        elif y == z.right_child and x == y.left_child:
            self._right_rotate(y)
            self._left_rotate(z)
        else:
            raise Exception('_rebalance_node: z,y,x Node configuration not recognized!')

    def _right_rotate(self, z: Node) -> None:
        sub_root = z.parent
        y = z.left_child
        if y is None:
            return
        t3 = y.right_child
        y.right_child = z
        z.parent = y
        z.left_child = t3
        if t3 is not None:
            t3.parent = z
        y.parent = sub_root
        if y.parent is None:
            self.root = y
        else:
            if y.parent.left_child == z:
                y.parent.left_child = y
            else:
                y.parent.right_child = y
        z.height = 1 + max(self.get_height(z.left_child),
                           self.get_height(z.right_child))
        y.height = 1 + max(self.get_height(y.left_child),
                           self.get_height(y.right_child))

    def _left_rotate(self, z: Node) -> None:
        sub_root = z.parent
        y = z.right_child
        if y is None:
            return
        t2 = y.left_child
        y.left_child = z
        z.parent = y
        z.right_child = t2
        if t2 is not None:
            t2.parent = z
        y.parent = sub_root
        if y.parent is None:
            self.root = y
        else:
            if y.parent.left_child == z:
                y.parent.left_child = y
            else:
                y.parent.right_child = y
        z.height = 1 + max(self.get_height(z.left_child),
                           self.get_height(z.right_child))
        y.height = 1 + max(self.get_height(y.left_child),
                           self.get_height(y.right_child))

    @staticmethod
    def get_height(cur_node: Optional[Node]) -> int:
        """Gibt die Höhe eines bestimmten Knotens zurück.

        Args:
            cur_node (Optional[Node]): Der Knoten.

        Returns:
            int: Höhe des Knotens oder 0 bei `None`.

        Raises:
            None
        """
        if cur_node is None:
            return 0
        return cur_node.height

    def taller_child(self, cur_node: Node) -> Optional[Node]:
        """Gibt das Kind mit der größeren Höhe zurück.

        Args:
            cur_node (Node): Der Eltern-Knoten.

        Returns:
            Optional[Node]: Das höhere Kind-Knoten-Objekt.

        Raises:
            None
        """
        left = self.get_height(cur_node.left_child)
        right = self.get_height(cur_node.right_child)
        return cur_node.left_child if left >= right else cur_node.right_child

    @staticmethod
    def create_new_node(key: str, path_to_image: Any) -> Node:
        """Erstellt einen neuen Knoten und fügt ihm einen Wert hinzu.

        Args:
            key (str): Der Schlüssel.
            path_to_image (Any): Der einzufügende Wert.

        Returns:
            Node: Der erstellte Knoten.

        Raises:
            None
        """
        new_node = Node(key)
        new_node.add_value(path_to_image)
        return new_node

    @staticmethod
    def update_node(node_to_update: Node, path_to_image: Any) -> Node:
        """Fügt einem bestehenden Knoten einen weiteren Wert hinzu.

        Args:
            node_to_update (Node): Der zu aktualisierende Knoten.
            path_to_image (Any): Der hinzuzufügende Wert.

        Returns:
            Node: Der aktualisierte Knoten.

        Raises:
            None
        """
        node_to_update.add_value(path_to_image)
        return node_to_update
