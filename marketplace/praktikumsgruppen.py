"""Übersicht über den Dateiinhalt:

Implementiert die Disjoint-Set-Datenstruktur (Union-Find) mit `SetNode` und `Praktikumsgruppen`.
Ermöglicht das Zusammenfassen von Benutzern in Praktikumsgruppen (Gruppenbildung,
Union, Find mit Pfadkomprimierung).
"""

# Status: FINAL, dgaida2, 15.10.2024

# Definiert die Klassen Praktikumsgruppen und SetNode, implementiert als Menge von disjunkten Mengen (Praktikum 3) oder als Dictionary (Praktikum 1 und 2)
#
from typing import Any, List, Optional, Union
import warnings


class SetNode:
    """Klasse zur Repräsentation eines Knotens in einer Disjoint-Set-Struktur (Union-Find).

    Attributes:+
        _parent (SetNode): Zeiger auf den Eltern-Knoten (self bei Wurzeln).
        _weight (int): Anzahl der Knoten im Teilbaum.
    """

    # TODO for students: die Klasse user.User erbt von SetNode. diese Klasse wird eigentlich erst in Praktikum 3 benötigt.
    #     für Praktikum 1 und 2 müsste User nicht von dieser Klasse erben

    # *** CONSTRUCTORS ***
    def __init__(self) -> None:
        """Initialisiert einen SetNode als eigene Wurzel mit Gewicht 1.

        Args:
            None

        Raises:
            None
        """

        # Creates the private variable _praktikumsgruppe (which is an int as declared at the very bottom of users.py get_from_cvs method
        self._praktikumsgruppe: Optional[int] = None # Saves the groupnumber assigned to this node.

    def get_praktikumsgruppe(self) -> Optional[int]:
            """
            custom getter for the _praktikumsgruppe private variable.

            :param self: Needed to access the variable
            :return: Returns an int if the variable has a value, otherwise it returns None.
            """

            return self._praktikumsgruppe


    def set_praktikumsgruppe(self, groupnum: int) -> None:
            """
            custom setter for the private variable _praktikumsgruppe.
            Needed to change it's value later on, as a Node shouldn't have to have on upon initialization (As far as I understand)

            :param self: Needed to access the variable itself.
            :param groupnum: The Integer number which the _praktikumsgruppe variable will be set to
            :return: None because it is a setter
            """

            self._praktikumsgruppe = groupnum

            # TODO: werden nur für Praktikum 3 benötigt
            self._parent: SetNode = self   # parent Knoten des SetNode Objekts. self bedeutet, dass der Knoten ein Wurzelknoten ist
            self._weight: int = 1      # Gewicht (Anzahl Knoten) des (Teil-)Baumes, der in dem SetNode Objekt verwurzelt ist

        # Alternative: Rank-based Quick Union
        # self._rank = 0

    # *** PUBLIC SET methods ***

    # TODO: implementieren Sie in Praktikum 3 die benötigten Methoden

    # *** PUBLIC methods to return class properties ***

    # TODO: implementieren Sie in Praktikum 3 die benötigten Methoden

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

    # TODO in Praktikum 3: implement find(node), find_byid(user_id, return_id=False) and 
    #  union(user_id1, user_id2)

    def find_byid(self, user_id: str, return_id: bool = False) -> Union[Any, str]:
        """Findet die Wurzel der Praktikumsgruppe eines Benutzers anhand seiner ID.

        TODO students: die Methode existiert in der Studierendenversion nur aus Kompatibilitätsgründen und wird im 3. Praktikum implementiert

        Args:
            user_id (str): Benutzer-ID.
            return_id (bool): Wenn `True`, wird die Benutzer-ID der Wurzel zurückgegeben.

        Returns:
            Union[Any, str]: Das Wurzelobjekt oder dessen ID.

        Raises:
            KeyError: Falls `user_id` nicht im Wörterbuch existiert.
        """
        return user_id

    def create_groups(self, user_ids: List[str], groupnumbers: List[int]) -> None:
        """
        This method iterates through two lists user_ids and groupnumbers, which should be of identical size.
        The lists are intended to be generated from a CSV file using the method _read_users_from_csvfile() method from users.py.
        If this is true, the elements in both lists correspond to the same user and therefore the lists can be iterated through
        simultaneously without any checks.

        The result of this method's execution is, that each user gets assigned their corresponding group according using the
        variable's custom setter method.

        :param: user_ids
        :type: List[str]
        :description: This list would be each user's id. The list should be generated from the above stated method.

        :param: groupnumbers
        :type: List[int]
        :description: This list would be each user's group's number. This list should be generated from the above stated method.


        :return: None

        :raises: Raises a warning when the user is not in the dictionary (Should never happen)

        Docstring edited by CallMeMosaic
        """



        for u, groupnum in zip(user_ids, groupnumbers):

            # Zip is used in this case, as the read_from_csv method creates lists of identical size from a CSV file
            # This means that each element in one of those lists, corresponds to an item at the same index of any other of those lists
            # Due to this the zip() method is used to create one iterable list of sets to iterate through.
            if u in self:


                self[u].set_praktikumsgruppe(groupnum)


            else:
                warnings.warn("User is not in underlying dictionary. THIS SHOULD NOT BE HAPPENING!")


    # *** PUBLIC GET methods ***

    def get_groupmembers(self, user_id: str) -> List[str]:
        """
        Searches for all users with the same group_id as the user_id handed in parameter and returns a list of all of them.
        Also makes sure that user_id is according to the hinted type.

        :param: user_id
        :type: String
        :description: The ID of the user whose group to find.

        :return: List[str] / Empty List
        :description: Returns a List of all users in the user's group or an empty list if the user has no group/ is alone in a group.

        :raises: KeyError if the user_id is not in the dict
        :raises: TypeError if the wrong type was entered for user_id

        Runtime:
        Θ(n) as the entire dictionary is iterated through once.
        Ω(1) as it can happen that the user is not found or has no group, which reults in outputting nothing.+++++++++++++++++^^

        Docstring edited by CallMeMosaic
        """

        # Check if the user is even in the dictionary

        if user_id not in self:
            raise KeyError(f"User {user_id} is not item of underlying dict!")


        # Make sure the entered variable is according to type hint

        if isinstance(user_id, String) or user_id is None:
            raise TypeError(f"Parameter type missmatch. Expected type was 'String' got: {type(user_id)}!")


        # Assign the group's id of the targeted user to a temporary variable

        targeted_group = self[user_id].get_praktikumsgruppe()

        if targeted_group is None:
            print("User has no Praktikumsgruppe")
            return []


        # Iterate through the users of the dict and add all users user_id with the same group to the list

        group_members = []

        for id, user_object in self.items():
            # usage of self.items() here so that the object to iterate through contains the key-value-pairs of the dict
            # instead of just the keys, as it would be when iterating through self.

            if user_object.get_praktikumsgruppe() == targeted_group:

                group_members.append(id)

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

    # *** PUBLIC STATIC methods ***

    # *** PRIVATE methods ***

    # *** PUBLIC methods to return class properties ***

    # *** PRIVATE variables ***
