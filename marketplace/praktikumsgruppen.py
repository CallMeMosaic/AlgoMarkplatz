"""Übersicht über den Dateiinhalt:

Implementiert die Disjoint-Set-Datenstruktur (Union-Find) mit `SetNode` und `Praktikumsgruppen`.
Ermöglicht das Zusammenfassen von Benutzern in Praktikumsgruppen (Gruppenbildung,
Union, Find mit Pfadkomprimierung).
"""

# Status: FINAL, dgaida2, 15.10.2024

# Definiert die Klassen Praktikumsgruppen und SetNode, implementiert als Menge von disjunkten Mengen (Praktikum 3) oder als Dictionary (Praktikum 1 und 2)
#
from typing import Any, List, Union, Optional
import warnings


class SetNode:
    """Klasse zur Repräsentation eines Knotens in einer Disjoint-Set-Struktur."""

    def __init__(self) -> None:
        """Initialisiert einen SetNode als eigene Wurzel mit Gewicht 1."""
        self._parent: SetNode = self
        self._weight: int = 1
        self._praktikumsgruppe: Optional[int] = None

    def parent(self) -> "SetNode":
        """Gibt den Elternknoten zurück."""
        return self._parent

    def get_praktikumsgruppe(self) -> Optional[int]:
        """Gibt die Praktikumsgruppennummer zurück."""
        return self._praktikumsgruppe

    def set_praktikumsgruppe(self, groupnum: int) -> None:
        """Setzt die Praktikumsgruppennummer."""
        self._praktikumsgruppe = groupnum


class Praktikumsgruppen(dict):
    # COMMENTS BY ME
    """
    This is an ADT of Type: Dictionary as it saves a key (user_id) and a value (object of type User)
                                                            Datastructure: Is a HashTable, as it inherits the implementation from python's dict, which
                                                            implements the dict class as a HasTable. To be Specific it uses Open Addressing. Since
                                                            it inherits directly from the python dict, it is also efficiently implemented using C.

                                                             Θ(1) for Insertion, Deletion and Lookup.
                                                             Θ(n) if collision or expansion needed.
                                                             Generally grabbing an item is instantaneous Θ(n)

    """


    """Klasse zur Repräsentation einer Sammlung disjunkter Mengen (Praktikumsgruppen).

    In Praktikum 1 und 2: Dictionary containing all students. Die Klasse user.Users erbt von dieser Klasse.
    In Praktikum 3: Class representing a collection of disjoint sets for grouping users into practical groups.

    Methods:
        find(node): Finds the root of the set containing the node, with path compression.
        find_byid(user_id, return_id=False): Finds the root of the set containing the user by ID.
        union(user_id1, user_id2): Unions the sets containing the two users.
        create_groups(user_ids, groupnumbers): Creates groups from the provided user IDs and group numbers.
        get_groupmembers(user_id): Gets the members of the group containing the user.
        print_ds(): Prints the disjoint set structure.

    Attributes:
        None (erbt von dict).
    """

    # *** CONSTRUCTORS ***
    def __init__(self) -> None:
        """Initialisiert eine neue Praktikumsgruppen-Instanz.

        Args:
            None

        Raises:
            None
        """
        super().__init__()

    # *** PUBLIC methods ***

    def find(self, node: SetNode) -> SetNode:
        """Findet die Wurzel eines Knotens mit Pfadkomprimierung."""

        if node._parent is not node:
            node._parent = self.find(node._parent)

        return node._parent

    def union(self, user_id1: str, user_id2: str) -> None:
        """Vereinigt die Gruppen zweier Benutzer mithilfe von Weighted Quick-Union."""

        if user_id1 not in self:
            raise KeyError(f"User {user_id1} existiert nicht!")

        if user_id2 not in self:
            raise KeyError(f"User {user_id2} existiert nicht!")

        root1 = self.find(self[user_id1])
        root2 = self.find(self[user_id2])

        # Beide Benutzer sind bereits in derselben Gruppe
        if root1 is root2:
            return

        # Der Baum mit dem größeren Gewicht wird zur neuen Wurzel
        if root1._weight >= root2._weight:
            root2._parent = root1
            root1._weight += root2._weight
        else:
            root1._parent = root2
            root2._weight += root1._weight

    def find_byid(self, user_id: str, return_id: bool = False) -> Union[Any, str]:
        """Findet die Wurzel der Praktikumsgruppe eines Benutzers anhand seiner ID."""

        if user_id not in self:
            raise KeyError(f"User {user_id} existiert nicht!")

        root = self.find(self[user_id])

        if return_id:
            for uid, user in self.items():
                if user is root:
                    return uid

        return root

    def create_groups(self, user_ids: List[str], groupnumbers: List[int]) -> None:
        """Erstellt Praktikumsgruppen anhand der übergebenen Gruppennummern."""

        if len(user_ids) != len(groupnumbers):
            raise ValueError("Die Listen müssen gleich lang sein!")

        # Alle Benutzer zunächst wieder zu einzelnen Gruppen machen
        for user in self.values():
            user._parent = user
            user._weight = 1

        # Speichert für jede Gruppennummer den ersten gefundenen Benutzer
        group_representatives = {}

        for user_id, groupnumber in zip(user_ids, groupnumbers):

            if user_id not in self:
                warnings.warn(
                    f"User {user_id} ist nicht im Dictionary vorhanden!"
                )
                continue

            if groupnumber not in group_representatives:
                group_representatives[groupnumber] = user_id

            else:
                first_user = group_representatives[groupnumber]
                self.union(first_user, user_id)



    # *** PUBLIC GET methods ***

    def get_groupmembers(self, user_id: str) -> List[str]:
        """Gibt alle Benutzer zurück, die in derselben Gruppe sind."""

        if not isinstance(user_id, str):
            raise TypeError("Die Benutzer-ID muss ein String sein!")

        if user_id not in self:
            raise KeyError(f"User {user_id} existiert nicht!")

        target_root = self.find(self[user_id])

        group_members = []

        for uid, user in self.items():
            if self.find(user) is target_root:
                group_members.append(uid)

        return group_members


    def print_ds(self) -> None:
        """Gibt die Disjoint-Set-Struktur aus.

        Funktioniert erst, wenn Sie in Praktikum 3 die Methode parent() in SetNode implementiert haben.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        for user_id, user in self.items():
            print(user_id, self[user_id].parent().id())


