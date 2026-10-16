"""Übersicht über den Dateiinhalt:

Diese Datei definiert die Basisklasse `AuctionAppInit` für die grafische Benutzeroberfläche (GUI)
des Online-Marktplatzes. Sie enthält alle Methoden zur Erstellung und Verwaltung der Tkinter-Widgets,
Frame-Strukturen, Event-Handling sowie die Anbindung an die Datenstrukturen (Trie, AVL-Baum, Auktionen).
"""

# Status: Not FINAL, dgaida2, 15.10.2024

# Definiert die Basis Klasse für Klasse AuctionApp.
# In dieser Klasse werden alle GUI Elemente erstellt. Die wichtigste Methode ist create_widgets()

from typing import Any, List, Optional, Tuple, Union
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from collections import Counter

import marketplace.auctions
import sys

THEME = {
    "bg_app": "#F1F5F9",
    "bg_card": "#FFFFFF",
    "fg_text": "#0F172A",
    "fg_muted": "#475569",
    "primary": "#2563EB",
    "primary_hover": "#1D4ED8",
    "primary_fg": "#FFFFFF",
    "border": "#CBD5E1",
    "select_bg": "#2563EB",
    "select_fg": "#FFFFFF",
    "font_normal": ("Segoe UI" if sys.platform == "win32" else "Helvetica", 10),
    "font_bold": ("Segoe UI" if sys.platform == "win32" else "Helvetica", 10, "bold"),
    "font_title": ("Segoe UI" if sys.platform == "win32" else "Helvetica", 11, "bold"),
}
import marketplace.user
import marketplace.trie
import marketplace.auction
import marketplace.systemmessages
import marketplace.avl_tree
from marketplace import avl_tree


class ToolTip:
    """Erzeugt einen Tooltip für ein Tkinter-Widget beim Mouseover."""

    def __init__(self, widget: tk.Widget, text: str) -> None:
        self.widget = widget
        self.text = text
        self.tip_window: Optional[tk.Toplevel] = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event: Optional[tk.Event] = None) -> None:
        if self.tip_window or not self.text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            tw,
            text=self.text,
            justify=tk.LEFT,
            background="#FFFFE1",
            foreground="#0F172A",
            relief=tk.SOLID,
            borderwidth=1,
            font=("Segoe UI" if sys.platform == "win32" else "Helvetica", 9, "normal"),
        )
        label.pack(ipadx=4, ipady=2)

    def hide_tip(self, event: Optional[tk.Event] = None) -> None:
        if self.tip_window:
            try:
                if self.tip_window.winfo_exists():
                    self.tip_window.destroy()
            except tk.TclError:
                pass
            self.tip_window = None


class AuctionAppInit:
    """Basisklasse zur Initialisierung und Verwaltung der GUI-Elemente der Auktions-Anwendung.

    Attributes:
        root (tk.Tk): Das Hauptfenster der Tkinter-Anwendung.
        _auctions (marketplace.auctions.Auctions): Die Auktions-Verwaltungsinstanz.
        _users (marketplace.users.Users): Die Benutzer-Verwaltungsinstanz.
        _current_user (Optional[marketplace.user.User]): Der aktuell angemeldete Benutzer.
        trie (marketplace.trie.Trie): Trie zur Autovervollständigung der Produktsuche.
        avl_tree (marketplace.avl_tree.AVLTree): AVL-Baum zur Suche häufiger Suchbegriffe.
        tooltip (Optional[tk.Toplevel]): Das Tooltip-Fenster für Suchvorschläge.
    """

    def __init__(self, root: tk.Tk) -> None:
        """Initialisiert die AuctionAppInit-Klasse und baut die Benutzeroberfläche auf.

        Args:
            root (tk.Tk): Das Tkinter-Hauptfenster.

        Raises:
            Exception: Wenn die Initialisierung der Komponenten fehlschlägt.
        """
        self.root = root
        self.root.title("Online-Marktplatz für Auktionen")

        self.setup_theme()

        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        self._auctions = marketplace.auctions.Auctions("auctions.csv")
        self._users = self._auctions.users()

        # der aktuell eingeloggte user
        self._current_user: Optional[marketplace.user.User] = None

        # erstelle gui
        self.create_widgets()

        self.root.bind("<Configure>", self.update_tooltip_position)
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

        # füge alle Auktionen zur Liste der Auktionen hinzu
        self.add_items2all_items_list()

        self.trie = marketplace.trie.Trie()
        self.avl_tree = avl_tree.AVLTree()

        self.tooltip: Optional[tk.Toplevel] = None
        self.initialize_trie()

        self.enable_widgets(False)  # Initially disable all widgets

    def setup_theme(self) -> None:
        """Richtet das TTK Style-Theme und Hintergrundfarben für die Anwendung ein."""
        self.root.configure(bg=THEME["bg_app"])

        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("TFrame", background=THEME["bg_app"])
        style.configure("Card.TFrame", background=THEME["bg_card"], relief="solid", borderwidth=1, bordercolor=THEME["border"])
        style.configure("TLabel", background=THEME["bg_app"], foreground=THEME["fg_text"], font=THEME["font_normal"])
        style.configure("Header.TLabel", background=THEME["bg_app"], foreground=THEME["fg_text"], font=THEME["font_title"])
        style.configure("CardHeader.TLabel", background=THEME["bg_card"], foreground=THEME["fg_text"], font=THEME["font_title"])

        style.configure(
            "TButton",
            font=THEME["font_bold"],
            background=THEME["primary"],
            foreground=THEME["primary_fg"],
            borderwidth=0,
            padding=6,
        )
        style.map(
            "TButton",
            background=[("active", THEME["primary_hover"]), ("disabled", "#E2E8F0")],
            foreground=[("disabled", "#94A3B8")],
        )

        style.configure(
            "Vertical.TScrollbar",
            troughcolor=THEME["bg_app"],
            bordercolor=THEME["border"],
            background="#CBD5E1",
            arrowcolor=THEME["fg_muted"],
        )

    def _style_entry(self, entry: tk.Entry) -> None:
        entry.configure(
            bg=THEME["bg_card"],
            fg=THEME["fg_text"],
            insertbackground=THEME["fg_text"],
            relief="solid",
            bd=1,
            highlightthickness=1,
            highlightbackground=THEME["border"],
            highlightcolor=THEME["primary"],
            font=THEME["font_normal"],
        )

    def _style_button(self, button: tk.Button) -> None:
        button.configure(
            bg=THEME["primary"],
            fg=THEME["primary_fg"],
            activebackground=THEME["primary_hover"],
            activeforeground=THEME["primary_fg"],
            disabledforeground="#CBD5E1",
            font=THEME["font_bold"],
            relief="flat",
            bd=0,
            padx=10,
            pady=4,
            cursor="hand2",
        )

    def _style_listbox(self, listbox: tk.Listbox) -> None:
        listbox.configure(
            bg=THEME["bg_card"],
            fg=THEME["fg_text"],
            selectbackground=THEME["select_bg"],
            selectforeground=THEME["select_fg"],
            font=THEME["font_normal"],
            relief="solid",
            bd=1,
            highlightthickness=0,
        )

    def _style_label(self, label: tk.Label, is_header: bool = False) -> None:
        label.configure(
            bg=THEME["bg_app"],
            fg=THEME["fg_text"],
            font=THEME["font_title"] if is_header else THEME["font_normal"],
        )

    def _style_radiobutton(self, radio: tk.Radiobutton) -> None:
        radio.configure(
            bg=THEME["bg_app"],
            fg=THEME["fg_text"],
            selectcolor=THEME["bg_card"],
            activebackground=THEME["bg_app"],
            activeforeground=THEME["fg_text"],
            font=THEME["font_normal"],
        )

    def create_frame_useraccount(self) -> None:
        """Erstellt das Frame für Benutzerkonto-Aktionen (Login, Registrierung, Logout, Account-Details).

        Args:
            None

        Returns:
            None
        """
        self.frame_useraccount = ttk.Frame(self.root)
        self.frame_useraccount.grid(row=0, column=6, padx=5, pady=5, sticky="ew")

        # Nutzername Label und Entry
        self.lbl_username = tk.Label(self.frame_useraccount, text="User-ID:")
        self.lbl_username.grid(row=0, column=0, padx=(5, 2), pady=5, sticky="e")
        self._style_label(self.lbl_username)

        self.username_entry = tk.Entry(self.frame_useraccount)
        self.username_entry.grid(row=0, column=1, padx=(0, 5), pady=5, sticky="ew")
        self.username_entry.insert(0, "")
        self._style_entry(self.username_entry)
        ToolTip(self.username_entry, "Geben Sie Ihre User-ID ein")

        # Passwort Label und Entry
        self.lbl_password = tk.Label(self.frame_useraccount, text="Passwort:")
        self.lbl_password.grid(row=0, column=2, padx=(5, 2), pady=5, sticky="e")
        self._style_label(self.lbl_password)

        self.password_entry = tk.Entry(self.frame_useraccount, show='*')
        self.password_entry.grid(row=0, column=3, padx=(0, 5), pady=5, sticky="ew")
        self.password_entry.insert(0, "")
        self._style_entry(self.password_entry)
        ToolTip(self.password_entry, "Geben Sie Ihr Passwort ein")

        self.login_btn = tk.Button(self.frame_useraccount, text="Einloggen", command=self.login)
        self.login_btn.grid(row=0, column=4, padx=5, pady=5, sticky="ew")
        self._style_button(self.login_btn)
        ToolTip(self.login_btn, "Klicken Sie hier, um sich einzuloggen")

        self.register_btn = tk.Button(self.frame_useraccount, text="Registrieren", command=self.register)
        self.register_btn.grid(row=0, column=5, padx=5, pady=5, sticky="ew")
        self._style_button(self.register_btn)
        ToolTip(self.register_btn, "Neues Benutzerkonto registrieren")

        lbl_spacer = tk.Label(self.frame_useraccount, text="     ")
        lbl_spacer.grid(row=0, column=6, padx=5, pady=5, sticky="ew")
        self._style_label(lbl_spacer)

        self.logout_btn = tk.Button(self.frame_useraccount, text="Logout", command=self.logout)
        self.logout_btn.grid(row=0, column=7, padx=5, pady=5, sticky="ew")
        self._style_button(self.logout_btn)
        ToolTip(self.logout_btn, "Vom Marktplatz abmelden")

        self.account_btn = tk.Button(self.frame_useraccount, text="Mein Account", command=self.my_account)
        self.account_btn.grid(row=0, column=8, padx=5, pady=5, sticky="ew")
        self._style_button(self.account_btn)
        ToolTip(self.account_btn, "Details des eigenen Benutzerkontos anzeigen")

        self.frame_useraccount.columnconfigure(0, weight=0)
        self.frame_useraccount.columnconfigure(1, weight=1)
        self.frame_useraccount.columnconfigure(2, weight=0)
        self.frame_useraccount.columnconfigure(3, weight=1)
        self.frame_useraccount.columnconfigure(4, weight=1)
        self.frame_useraccount.columnconfigure(5, weight=1)
        self.frame_useraccount.columnconfigure(6, weight=0)
        self.frame_useraccount.columnconfigure(7, weight=1)
        self.frame_useraccount.columnconfigure(8, weight=1)

    def create_frame_systemmessage(self) -> None:
        """Erstellt das Frame zur Anzeige von Systemnachrichten.

        Args:
            None

        Returns:
            None
        """
        self.frame_systemmessage = ttk.Frame(self.root)
        self.frame_systemmessage.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.frame_systemmessage.columnconfigure(0, weight=1)
        self.frame_systemmessage.columnconfigure(1, weight=2)

        lbl_title = tk.Label(self.frame_systemmessage, text="Systemnachricht: ")
        lbl_title.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self._style_label(lbl_title, is_header=True)

        self.lbl_sysmessage = tk.Label(self.frame_systemmessage, text="-")
        self.lbl_sysmessage.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self._style_label(self.lbl_sysmessage)

        self.system_messages = marketplace.systemmessages.SystemMessages(self.lbl_sysmessage)
        self._auctions.set_system_messages(self.system_messages)

    def create_frame_myauctions(self) -> None:
        """Erstellt das Frame zur Anzeige eigener Auktionen, Gebote und Empfehlungen.

        Args:
            None

        Returns:
            None
        """
        self.frame_myauctions = ttk.Frame(self.frame_left)
        self.frame_myauctions.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        self.frame_myauctions.rowconfigure(1, weight=1)
        self.frame_myauctions.columnconfigure(0, weight=1)

        # Liste mit Auktionen
        lbl_title = tk.Label(self.frame_myauctions, text="Meine Auktionen")
        lbl_title.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky="ew")
        self._style_label(lbl_title, is_header=True)

        self.item_listbox = tk.Listbox(self.frame_myauctions, width=110)
        self.item_listbox.grid(row=1, column=0, rowspan=7, columnspan=3, padx=5, pady=5, sticky="nsew")
        self.item_listbox.bind('<<ListboxSelect>>', self.on_item_listbox_select)
        self._style_listbox(self.item_listbox)

        self.add_item_btn = tk.Button(self.frame_myauctions, text="Auktion hinzufügen", command=self.add_item_widget)
        self.add_item_btn.grid(row=1, column=4, padx=5, pady=5, sticky="ew")
        self._style_button(self.add_item_btn)
        ToolTip(self.add_item_btn, "Eine neue Auktion erstellen")

        self.delete_item_btn = tk.Button(self.frame_myauctions, text="Auktion löschen", command=self.delete_item)
        self.delete_item_btn.grid(row=2, column=4, padx=5, pady=5, sticky="ew")
        self._style_button(self.delete_item_btn)
        ToolTip(self.delete_item_btn, "Ausgewählte eigene Auktion löschen")

        self.view_option = tk.StringVar(value="offered")

        self.show_bids_radio = tk.Radiobutton(self.frame_myauctions, text="Meine Gebote", variable=self.view_option,
                                              value="bids",
                                              command=self.add_myitems2items_list)
        self.show_bids_radio.grid(row=9, column=0, padx=5, pady=5, sticky="nsew")
        self._style_radiobutton(self.show_bids_radio)
        ToolTip(self.show_bids_radio, "Auktionen anzeigen, auf die Sie geboten haben")

        self.show_won_items_radio = tk.Radiobutton(self.frame_myauctions, text="Gewonnene Auktionen",
                                                   variable=self.view_option,
                                                   value="won", command=self.add_myitems2items_list)
        self.show_won_items_radio.grid(row=9, column=1, padx=5, pady=5, sticky="nsew")
        self._style_radiobutton(self.show_won_items_radio)
        ToolTip(self.show_won_items_radio, "Auktionen anzeigen, die Sie gewonnen haben")

        self.show_offered_items_radio = tk.Radiobutton(self.frame_myauctions, text="Angebotene Artikel",
                                                       variable=self.view_option,
                                                       value="offered", command=self.add_myitems2items_list)
        self.show_offered_items_radio.grid(row=10, column=0, padx=5, pady=5, sticky="nsew")
        self._style_radiobutton(self.show_offered_items_radio)
        ToolTip(self.show_offered_items_radio, "Auktionen anzeigen, die Sie anbieten")

        self.show_recommended_items_radio = tk.Radiobutton(self.frame_myauctions, text="Empfohlene Auktionen",
                                                           variable=self.view_option, value="recommended",
                                                           command=self.add_myitems2items_list)
        self.show_recommended_items_radio.grid(row=10, column=1, padx=5, pady=5, sticky="nsew")
        self._style_radiobutton(self.show_recommended_items_radio)
        ToolTip(self.show_recommended_items_radio, "Empfohlene Auktionen anzeigen")

        self.show_sold_items_radio = tk.Radiobutton(self.frame_myauctions, text="Verkaufte Artikel",
                                                    variable=self.view_option, value="sold",
                                                    command=self.add_myitems2items_list)
        self.show_sold_items_radio.grid(row=9, column=2, padx=5, pady=5, sticky="nsew")
        self._style_radiobutton(self.show_sold_items_radio)
        ToolTip(self.show_sold_items_radio, "Auktionen anzeigen, die Sie erfolgreich verkauft haben")

    def create_frame_friends(self) -> None:
        """Erstellt das Frame für die Verwaltung von Freunden und Gruppenmitgliedern.

        Args:
            None

        Returns:
            None
        """
        self.frame_friends = ttk.Frame(self.frame_left)
        self.frame_friends.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        self.frame_friends.rowconfigure(1, weight=1)
        self.frame_friends.columnconfigure(0, weight=1)
        self.frame_friends.columnconfigure(1, weight=1)

        # Liste meiner Freunde
        lbl_friends = tk.Label(self.frame_friends, text="Meine Freunde und Gruppenmitglieder", justify='left')
        lbl_friends.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self._style_label(lbl_friends, is_header=True)

        self.friends_listbox = tk.Listbox(self.frame_friends, width=50)
        self.friends_listbox.grid(row=1, column=0, rowspan=7, padx=5, pady=5, sticky="nsew")
        self.friends_listbox.bind('<<ListboxSelect>>', self.on_friends_listbox_select)
        self._style_listbox(self.friends_listbox)

        self.btn_add_friend = tk.Button(self.frame_friends, text="Freund hinzufügen", command=self.add_friend)
        self.btn_add_friend.grid(row=1, column=4, padx=5, pady=5, sticky="nsew")
        self._style_button(self.btn_add_friend)
        ToolTip(self.btn_add_friend, "Nutzer zur Freundesliste hinzufügen")

        self.remove_friend_btn = tk.Button(self.frame_friends, text="Freund entfernen", command=self.remove_friend)
        self.remove_friend_btn.grid(row=2, column=4, padx=5, pady=5, sticky="nsew")
        self._style_button(self.remove_friend_btn)
        ToolTip(self.remove_friend_btn, "Ausgewählten Freund aus der Liste entfernen")

        lbl_mutual = tk.Label(self.frame_friends, text="User mit denen meine Freunde befreundet sind")
        lbl_mutual.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        self._style_label(lbl_mutual, is_header=True)

        self.mutual_friends_listbox = tk.Listbox(self.frame_friends, width=50)
        self.mutual_friends_listbox.grid(row=1, column=1, rowspan=7, padx=5, pady=5, sticky="nsew")
        self._style_listbox(self.mutual_friends_listbox)

    def create_frame_search_bid(self) -> None:
        """Erstellt das Frame für die Produktsuche und die Ansicht aller Auktionen.

        Args:
            None

        Returns:
            None
        """
        # Frame to contain search and bid btn.
        self.frame_search_bid = ttk.Frame(self.root)
        self.frame_search_bid.grid(row=5, column=6, padx=5, pady=5, sticky="nsew")

        self.frame_search_bid.rowconfigure(2, weight=1)
        self.frame_search_bid.columnconfigure(0, weight=1)

        # Liste mit allen Artikeln und Suche
        self.search_entry = tk.Entry(self.frame_search_bid)
        self.search_entry.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        self._style_entry(self.search_entry)
        # self.search_entry.insert(0, "Suchbegriff")
        self.search_entry.bind('<KeyRelease>', self.show_suggestions)
        ToolTip(self.search_entry, "Suchbegriff für Artikel eingeben")

        self.search_btn = tk.Button(self.frame_search_bid, text="Suchen", command=self.search_items)
        self.search_btn.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self._style_button(self.search_btn)
        ToolTip(self.search_btn, "Auktionen nach Suchbegriff filtern")

        # Frame to contain the listbox and scrollbar.
        self.frame = ttk.Frame(self.frame_search_bid)
        self.frame.grid(row=2, column=0, rowspan=12, columnspan=12, padx=5, pady=5, sticky="nsew")
        # Create a scrollbar with vertical orientation.
        self.scrollbar = ttk.Scrollbar(self.frame, orient=tk.VERTICAL)

        lbl_all = tk.Label(self.frame_search_bid, text="Alle Auktionen", justify='left')
        lbl_all.grid(row=0, column=0, columnspan=12, padx=5, pady=5, sticky="ew")
        self._style_label(lbl_all, is_header=True)

        self.all_items_listbox = tk.Listbox(self.frame, width=140, height=30,
                                            yscrollcommand=self.scrollbar.set)
        self._style_listbox(self.all_items_listbox)
        # Bind the <<ListboxSelect>> event to the on_listbox_select function
        self.all_items_listbox.bind('<<ListboxSelect>>', self.on_listbox_select)
        # Link it to the listbox.
        self.scrollbar.config(command=self.all_items_listbox.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.all_items_listbox.pack()

    def create_frame_auction_detail(self, listbox: str = "all_items") -> None:
        """Erstellt das Detail-Frame für eine ausgewählte Auktion.

        Args:
            listbox (str): Angabe, aus welcher Listbox das Element ausgewählt wurde ("all_items" oder "item").

        Returns:
            None

        Raises:
            ValueError: Wenn `listbox` weder 'all_items' noch 'item' entspricht.
        """
        if listbox == "all_items":
            selected = self.all_items_listbox.curselection()
        elif listbox == "item":
            selected = self.item_listbox.curselection()
        else:
            raise ValueError("listbox must be 'all_items' or 'item'")

        # Frame löschen, wenn er existiert
        if hasattr(self, 'frame_auction_detail'):
            for widget in self.frame_auction_detail.winfo_children():
                widget.destroy()
            self.frame_auction_detail.grid_forget()

        self.frame_auction_detail = ttk.Frame(self.frame_search_bid)
        self.frame_auction_detail.grid(row=14, column=0, rowspan=4, columnspan=12, padx=5, pady=5, sticky="nsew")

        if selected:
            if listbox == "all_items":
                auction_desc = self.all_items_listbox.get(selected)
            elif listbox == "item":
                auction_desc = self.item_listbox.get(selected)
            else:
                raise ValueError("listbox must be 'all_items' or 'item'")

            auction_id = marketplace.auction.Auction.get_id_from_pretty_print(auction_desc)

            # Auktion-ID
            auction_id_label = tk.Label(self.frame_auction_detail, text=f"Auktion-ID: {auction_id}")
            auction_id_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
            self._style_label(auction_id_label)

            # Produktname
            item_name = self._auctions.get_item_name(auction_id)
            item_name_label = tk.Label(self.frame_auction_detail, text=f"Produktname: {item_name}")
            item_name_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
            self._style_label(item_name_label)

            # Produktbeschreibung
            item_description = self._auctions.get_item_description(auction_id)
            item_description_label = tk.Label(self.frame_auction_detail,
                                              text=f"Produktbeschreibung: {item_description}")
            item_description_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
            self._style_label(item_description_label)

            # Mindestgebot
            min_value = self._auctions.get_item_value_min(auction_id)
            min_value_label = tk.Label(self.frame_auction_detail, text=f"Mindestgebot: {min_value:.2f} €")
            min_value_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")
            self._style_label(min_value_label)

            # Höchstes Gebot
            highest_bid = self._auctions.get_highest_bid(auction_id)
            highest_bid_label = tk.Label(self.frame_auction_detail, text=f"Höchstes Gebot: {highest_bid:.2f} €")
            highest_bid_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")
            self._style_label(highest_bid_label)

            # Höchstbietender
            highest_bidder = self._auctions.get_highest_bidder(auction_id)
            highest_bidder_label = tk.Label(self.frame_auction_detail, text=f"Höchstbietender: {highest_bidder}")
            highest_bidder_label.grid(row=1, column=1, padx=5, pady=5, sticky="w")
            self._style_label(highest_bidder_label)

            # Ende der Auktion in
            time_left = self._auctions.get_time_left(auction_id)
            time_left_label = tk.Label(self.frame_auction_detail, text=f"Ende der Auktion in: {time_left:.0f} s")
            time_left_label.grid(row=2, column=1, padx=5, pady=5, sticky="w")
            self._style_label(time_left_label)

            # Verkäufer
            seller_id = self._auctions.get_seller_id(auction_id)
            seller_id_label = tk.Label(self.frame_auction_detail, text=f"Verkäufer: {seller_id}")
            seller_id_label.grid(row=4, column=0, padx=5, pady=5, sticky="w")
            self._style_label(seller_id_label)

            self.bid_amount_entry = tk.Entry(self.frame_auction_detail)
            self.bid_amount_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
            self.bid_amount_entry.insert(0, "50")
            self._style_entry(self.bid_amount_entry)
            ToolTip(self.bid_amount_entry, "Gebotsbetrag in Euro eingeben")

            self.bid_btn = tk.Button(self.frame_auction_detail, text="Bieten", command=self.place_bid)
            self.bid_btn.grid(row=4, column=1, padx=5, pady=5, sticky="ew")
            self._style_button(self.bid_btn)
            ToolTip(self.bid_btn, "Gebot für die ausgewählte Auktion abgeben")

    def create_widgets(self) -> None:
        """Erstellt alle untergeordneten Widgets und Frames der Benutzeroberfläche.

        Args:
            None

        Returns:
            None
        """
        self.create_frame_systemmessage()

        self.create_frame_useraccount()

        self.root.rowconfigure(5, weight=1)
        self.root.columnconfigure(6, weight=1)

        # placeholder
        # tk.Label(self.root, text="     ").grid(row=4, column=2, padx=5, pady=5)

        self.frame_left = ttk.Frame(self.root)
        self.frame_left.grid(row=5, column=0, padx=5, pady=5, sticky="nsew")

        self.frame_left.rowconfigure(0, weight=1)
        self.frame_left.columnconfigure(0, weight=1)

        self.create_frame_myauctions()

        self.create_frame_friends()

        self.create_frame_search_bid()

        self.create_frame_auction_detail()

    # *** FUNCTION HANDLES invoked by tk widget items ***

    def add_myitems2items_list(self) -> None:
        """Befüllt die Listbox 'Meine Auktionen' basierend auf der ausgewählten Option (angebotene, gewonnene, etc.).

        Args:
            None

        Returns:
            None
        """
        self.item_listbox.delete(0, tk.END)
        value = self.view_option.get()

        if self._current_user is None:
            return

        user_id = self._current_user.id()
        user_id_pass: Optional[str] = None

        if value == 'offered':
            auctions = self._auctions.get_auctions_offered(user_id)
        elif value == 'won':
            auctions = self._auctions.get_auctions_won(user_id)
        elif value == 'bids':
            auctions = self._auctions.get_auctions_bid_in(user_id)
            user_id_pass = user_id
        elif value == 'recommended':
            auctions = self._auctions.get_auctions_is_recommended(user_id)
        elif value == 'sold':
            auctions = self._auctions.get_auctions_sold(user_id)
        else:
            auctions = []

        for auction_id in auctions:
            self.item_listbox.insert(tk.END, self._auctions[auction_id].pretty_print(False, user_id_pass))

    def on_listbox_select(self, event: tk.Event) -> None:
        """Event-Handler bei Auswahl einer Auktion in der Liste aller Auktionen.

        Args:
            event (tk.Event): Das Tkinter-Event-Objekt.

        Returns:
            None
        """
        self.create_frame_auction_detail(listbox="all_items")

    def on_friends_listbox_select(self, event: tk.Event) -> None:
        """Event-Handler bei Auswahl eines Freundes in der Freundesliste.

        Args:
            event (tk.Event): Das Tkinter-Event-Objekt.

        Returns:
            None
        """
        # Get the selected index
        selected_index = self.friends_listbox.curselection()
        if selected_index:
            self.remove_friend_btn.config(state=tk.NORMAL)
        else:
            self.remove_friend_btn.config(state=tk.DISABLED)

    def on_item_listbox_select(self, event: tk.Event) -> None:
        """Event-Handler bei Auswahl einer Auktion in der Liste 'Meine Auktionen'.

        Args:
            event (tk.Event): Das Tkinter-Event-Objekt.

        Returns:
            None
        """
        # Get the selected index
        selected_index = self.item_listbox.curselection()
        value = self.view_option.get()

        if selected_index and value == 'offered':
            self.delete_item_btn.config(state=tk.NORMAL)
        elif selected_index and value == 'bids':
            self.create_frame_auction_detail(listbox="item")
        elif selected_index and value == 'recommended':
            self.create_frame_auction_detail(listbox="item")
        else:
            self.delete_item_btn.config(state=tk.DISABLED)

    def my_account(self) -> None:
        """Öffnet ein Fenster mit Detailinformationen zum aktuell angemeldeten Benutzerkonto.

        Args:
            None

        Returns:
            None
        """
        if self._current_user:
            account_info = tk.Toplevel(self.root)
            account_info.title("Mein Account")
            account_info.configure(bg=THEME["bg_app"])

            lbl1 = tk.Label(account_info, text="Nutzername:")
            lbl1.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
            self._style_label(lbl1)

            lbl2 = tk.Label(account_info, text=self._current_user.name())
            lbl2.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
            self._style_label(lbl2)

            lbl3 = tk.Label(account_info, text="Passwort:")
            lbl3.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
            self._style_label(lbl3)

            lbl4 = tk.Label(account_info, text=self._current_user.password())
            lbl4.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
            self._style_label(lbl4)

            lbl5 = tk.Label(account_info, text="ID:")
            lbl5.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
            self._style_label(lbl5)

            lbl6 = tk.Label(account_info, text=self._current_user.id())
            lbl6.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
            self._style_label(lbl6)

            lbl7 = tk.Label(account_info, text="Budget:")
            lbl7.grid(row=3, column=0, padx=5, pady=5, sticky="ew")
            self._style_label(lbl7)

            lbl8 = tk.Label(account_info, text=f"{self._current_user.balance():.2f} €")
            lbl8.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
            self._style_label(lbl8)
        else:
            messagebox.showerror("Fehler", "Kein Nutzer eingeloggt")

    def login(self) -> None:
        """Führt den Login-Vorgang für die eingegebenen Benutzerdaten durch.

        Args:
            None

        Returns:
            None
        """
        userid = self.username_entry.get()
        password = self.password_entry.get()

        if userid in self._users and self._users.password_valid(userid, password):
            self._current_user = self._users.get(userid)

            self.system_messages.push("Erfolgreich eingeloggt.")

            self._auctions.start_simulation_init(userid)

            # erst Widgets aktivieren, dann Listen füllen: in eine deaktivierte Listbox fügt Tk nichts ein
            self.enable_widgets()
            self.update_lists()
        else:
            messagebox.showerror("Login Fehler", "Ungültiger Benutzername oder Passwort")

    def register(self) -> None:
        """Registriert einen neuen Benutzer mit den eingegebenen Zugangsdaten.

        Args:
            None

        Returns:
            None
        """
        userid = self.username_entry.get()
        password = self.password_entry.get()

        if userid not in self._users:
            self._users.add(userid, password)
            messagebox.showinfo("Erfolg",
                                f"Registrierung des Nutzers {userid} erfolgreich! Loggen Sie sich bitte ein.")
        else:
            messagebox.showerror("Fehler", f"Benutzername {userid} bereits vergeben")

    def add_friend(self) -> None:
        """Öffnet einen Dialog zur Eingabe einer Freund-ID und fügt diesen der Freundesliste hinzu.

        Args:
            None

        Returns:
            None
        """
        if self._current_user is None:
            return
        friend_id = AuctionAppInit.simple_input("Freund hinzufügen", "GM-ID des Nutzers:")
        if friend_id:
            friend = self._users.get_user_pretty_print_for_list(friend_id)
            self._current_user.friends_add(friend_id)
            self.friends_listbox.insert(tk.END, friend)

            self._auctions.get_auctions_friends_offer(self._current_user.id())
            self._auctions.get_auctions_friends_bid_in(self._current_user.id())

    def remove_friend(self) -> None:
        """Entfernt den in der Freundesliste ausgewählten Freund.

        Args:
            None

        Returns:
            None
        """
        if self._current_user is None:
            return
        selected_friend_index = self.friends_listbox.curselection()
        if selected_friend_index:
            friend_name = self.friends_listbox.get(selected_friend_index)

            friend_id = marketplace.user.User.get_id_from_pretty_print(friend_name)

            # lösche Freund nur, wenn er ein Freund ist. da in der Liste auch Gruppenmitglieder sind, die nicht
            # unbedingt auch Freunde sein müssen
            if self._current_user.is_friend(friend_id):
                # freund aus freundesliste von _current_user löschen
                success = self._current_user.friends_delete(friend_id)

                self.friends_listbox.delete(selected_friend_index)

                self._auctions.get_auctions_friends_offer(self._current_user.id())
                self._auctions.get_auctions_friends_bid_in(self._current_user.id())

    def search_items(self) -> None:
        """Filtert die Auktionen in der Übersicht basierend auf dem Suchbegriff.

        Args:
            None

        Returns:
            None
        """
        search_term = self.search_entry.get()

        # wieder alle Auktionen anzeigen
        self.add_items2all_items_list()
        
        if search_term == "":
            return

        results = [item for item in self.all_items_listbox.get(0, tk.END) if search_term.lower() in item.lower()]
        self.all_items_listbox.delete(0, tk.END)
        for item in results:
            self.all_items_listbox.insert(tk.END, item)
        self.hide_tooltip()

    def add_item_widget(self) -> None:
        """Öffnet ein Fenster zur Erstellung einer neuen Auktion.

        Args:
            None

        Returns:
            None
        """
        new_item_widget = tk.Toplevel(self.root)
        new_item_widget.title("Artikel hinzufügen")
        new_item_widget.configure(bg=THEME["bg_app"])

        lbl_name = tk.Label(new_item_widget, text="Name:")
        lbl_name.grid(row=0, column=0, padx=5, pady=5)
        self._style_label(lbl_name)

        self.new_article_name = tk.Entry(new_item_widget)
        self.new_article_name.grid(row=0, column=1, padx=5, pady=5)
        self.new_article_name.insert(0, "Produktname")
        self._style_entry(self.new_article_name)

        lbl_desc = tk.Label(new_item_widget, text="Beschreibung:")
        lbl_desc.grid(row=1, column=0, padx=5, pady=5)
        self._style_label(lbl_desc)

        self.new_article_description = tk.Entry(new_item_widget)
        self.new_article_description.grid(row=1, column=1, padx=5, pady=5)
        self._style_entry(self.new_article_description)

        lbl_min = tk.Label(new_item_widget, text="Mindestgebot (€):")
        lbl_min.grid(row=2, column=0, padx=5, pady=5)
        self._style_label(lbl_min)

        self.new_min_value = tk.Entry(new_item_widget)
        self.new_min_value.grid(row=2, column=1, padx=5, pady=5)
        self.new_min_value.insert(0, "1")
        self._style_entry(self.new_min_value)

        ok_button = tk.Button(new_item_widget, text="OK", command=lambda: self.add_new_auction(new_item_widget))
        ok_button.grid(row=3, column=0, columnspan=2, pady=10)
        self._style_button(ok_button)

    def delete_item(self) -> None:
        """Löscht die aktuell in 'Meine Auktionen' ausgewählte Auktion.

        Args:
            None

        Returns:
            None
        """
        selected = self.item_listbox.curselection()
        if selected:
            auction_desc = self.item_listbox.get(selected)
            auction_id = marketplace.auction.Auction.get_id_from_pretty_print(auction_desc)

            success = self._auctions.delete(auction_id)

            if success:
                self.item_listbox.delete(selected)

                index = self.search_auction_id_in_all_items_listbox(auction_id)
                # index = self.all_items_listbox.get(0, tk.END).index(auction_desc)
                if index is not None:
                    self.all_items_listbox.delete(index)

                self.system_messages.push("Auktion erfolgreich gelöscht.")
            else:
                self.system_messages.push("Auktion darf nicht gelöscht werden, da User darauf bieten.")

    def place_bid(self) -> None:
        """Gibt ein Gebot für die aktuell ausgewählte Auktion ab.

        Args:
            None

        Returns:
            None

        Raises:
            ValueError: Wenn der eingegebene Gebotsbetrag keine gültige Zahl ist.
        """
        if self._current_user is None:
            return
        bid_amount = self.bid_amount_entry.get()
        selected = self.all_items_listbox.curselection()
        value = self.view_option.get()
        is_all_items_listbox = True

        # habe len(selected) == 0 ergänzt, da selected ein leeres tuple ist, wenn in all_items_listbox nichts
        # selektiert ist
        if (selected is None or len(selected) == 0) and (value == 'recommended' or value == 'bids'):
            selected = self.item_listbox.curselection()
            is_all_items_listbox = False

        if bid_amount and selected:
            if is_all_items_listbox:
                auction_desc = self.all_items_listbox.get(selected)
            else:
                auction_desc = self.item_listbox.get(selected)

            auction_id = marketplace.auction.Auction.get_id_from_pretty_print(auction_desc)
            try:
                amount_val = float(bid_amount)
            except ValueError:
                messagebox.showerror("Fehler", "Ungültiger Gebotsbetrag")
                return

            success = self._auctions.bid_in_auction(auction_id, self._current_user, amount_val)

            if not success:
                messagebox.showerror("Fehler",
                                     "Nicht genügend Guthaben, Ihr Gebot ist unter dem Mindestgebot bzw. nicht höher "
                                     "als Ihr bisheriges Gebot, oder die Auktion ist bereits beendet")
            else:
                self.update_listbox_item(selected, auction_id)
                self.system_messages.push("Gebot erfolgreich abgegeben für {0}.".format(
                    self._auctions[auction_id].get_item_name()))
        else:
            print('place_bid fails: ', bid_amount, selected, is_all_items_listbox, value)

    def show_suggestions(self, event: tk.Event) -> None:
        """Zeigt Autovervollständigungsvorschläge für das Suchfeld an.

        Args:
            event (tk.Event): Das Tastatur-Event.

        Returns:
            None
        """
        search_text = self.search_entry.get()
        if search_text:
            suggestions = self.trie.search(search_text)
            # TODO for students (Praktikum 1): nutzen Sie hier die Vorschläge des AVL-Baums und vergleichen Sie
            #  die Laufzeit mit der des Tries
            # avl_suggestions = self.avl_tree.find_most_likely_words(search_text)
            self.show_tooltip(suggestions)
        else:
            self.hide_tooltip()

    def on_select(self, event: tk.Event) -> None:
        """Übernimmt den in der Vorschlagsliste ausgewählten Begriff in das Suchfeld.

        Args:
            event (tk.Event): Das Auswahl-Event.

        Returns:
            None
        """
        widget = event.widget
        selected = widget.get(widget.curselection())
        self.search_entry.delete(0, tk.END)
        self.search_entry.insert(0, selected)
        self.hide_tooltip()

    def logout(self) -> None:
        """Meldet den aktuellen Benutzer ab und deaktiviert steuerbare Widgets.

        Args:
            None

        Returns:
            None
        """
        self._current_user = None
        self.enable_widgets(False)

    # *** PRIVATE METHODS ***

    def enable_widgets(self, enable: bool = True) -> None:
        """Aktiviert oder deaktiviert interaktive Benutzeroberflächenelemente.

        Args:
            enable (bool): `True`, um Widgets zu aktivieren; `False`, um sie zu deaktivieren.

        Returns:
            None
        """
        widgets = [
            self.add_item_btn, self.delete_item_btn, self.show_bids_radio,
            self.show_won_items_radio, self.show_offered_items_radio, self.show_recommended_items_radio,
            self.friends_listbox, self.btn_add_friend, self.remove_friend_btn,
            self.search_entry, self.search_btn, self.all_items_listbox,
            self.logout_btn, self.account_btn, self.show_sold_items_radio
        ]
        for widget in widgets:
            # bid_btn is set to NORMAL in method on_listbox_select below
            if (enable and widget is not self.remove_friend_btn
                    and widget is not self.delete_item_btn):
                widget.config(state=tk.NORMAL)
            else:
                widget.config(state=tk.DISABLED)

    def update_lists(self) -> None:
        """Aktualisiert alle Listen in der Benutzeroberfläche (Auktionen, Freunde, gegenseitige Freunde).

        Args:
            None

        Returns:
            None
        """
        self.add_myitems2items_list()

        self.add_myfriends2friends_list()
        self.add_users2mutualfriends_list()

    def add_myfriends2friends_list(self) -> None:
        """Aktualisiert die Freundesliste in der Benutzeroberfläche.

        Args:
            None

        Returns:
            None
        """
        if self._current_user is None:
            return
        self.friends_listbox.delete(0, tk.END)

        friends = self._users.get_friends_andgroupmembers_pretty_print(self._current_user.id())

        self.friends_listbox.insert(0, *friends)

        self._auctions.get_auctions_friends_offer(self._current_user.id())
        self._auctions.get_auctions_friends_bid_in(self._current_user.id())

    def add_users2mutualfriends_list(self) -> None:
        """Aktualisiert die Liste der vorgeschlagenen Freunde (Freunde von Freunden).

        Args:
            None

        Returns:
            None
        """
        if self._current_user is None:
            return
        self.mutual_friends_listbox.delete(0, tk.END)

        mutual_friends = self._users.suggest_friends(self._current_user.id(), 3)

        self.mutual_friends_listbox.insert(0, *mutual_friends)

    def update_listbox_item(self, selected_index: Any, auction_id: int) -> None:
        """Aktualisiert den Text einer spezifischen Auktion in der Listbox.

        Args:
            selected_index (Any): Der Index des Eintrags in der Listbox.
            auction_id (int): Die ID der zu aktualisierenden Auktion.

        Returns:
            None
        """
        # Get the selected index
        if selected_index:
            # Get the new value from the user
            new_value = self._auctions[auction_id].pretty_print()
            if new_value:
                # Delete the old entry
                self.all_items_listbox.delete(selected_index)
                # Insert the new entry at the same position
                self.all_items_listbox.insert(selected_index, new_value)

    def add_items2all_items_list(self) -> None:
        """Befüllt die Listbox 'Alle Auktionen' neu und stellt die bisherige Auswahl wieder her.

        Args:
            None

        Returns:
            None
        """
        # speichern welches Element in der Liste ausgewählt war, damit es auch am Ende der
        # Funktion wieder ausgewählt werden kann
        selected_index = self.all_items_listbox.curselection()
        if selected_index:
            auction_desc = self.all_items_listbox.get(selected_index)

            auction_id_before = marketplace.auction.Auction.get_id_from_pretty_print(auction_desc)
        else:
            auction_id_before = None

        # alle Elemente in Liste löschen und Auktionen die nicht ausgelaufen sind, wieder
        # in liste einfügen
        self.all_items_listbox.delete(0, tk.END)

        for auction_id, auction in list(self._auctions.items()):
            if not auction.expired():
                self.all_items_listbox.insert(tk.END, auction.pretty_print())

        # wenn vor dem Löschvorgang ein Element in der Liste ausgewählt war, dieses wieder auswählen,
        # wenn Element noch in Liste existiert
        if auction_id_before:
            self.search_auction_id_in_all_items_listbox(auction_id_before)

    def search_auction_id_in_all_items_listbox(self, auction_id_searching: int) -> Optional[int]:
        """Sucht nach einer Auktions-ID in der Listbox aller Auktionen und wählt diese aus.

        Args:
            auction_id_searching (int): Die zu suchende Auktions-ID.

        Returns:
            Optional[int]: Der Index des Elements in der Listbox oder None.
        """
        item_found: Optional[int] = None

        for item in range(self.all_items_listbox.size()):
            auction_desc = self.all_items_listbox.get(item)

            auction_id = marketplace.auction.Auction.get_id_from_pretty_print(auction_desc)

            if auction_id == auction_id_searching:
                self.all_items_listbox.select_set(item)
                item_found = item
                break

        return item_found

    def add_new_auction(self, widget: tk.Toplevel) -> None:
        """Fügt eine neue Auktion hinzu und schließt den Erstellungs-Dialog.

        Args:
            widget (tk.Toplevel): Das Dialogfenster zur Erstellung der Auktion.

        Returns:
            None

        Raises:
            ValueError: Wenn das Mindestgebot ungültig ist.
        """
        if self._current_user is None:
            return
        item_name = self.new_article_name.get()
        description = self.new_article_description.get()
        value_min = self.new_min_value.get()

        user_id = self._current_user.id()

        # Aufrufen der Methode add_new_auction der Auktionsklasse
        auction = self._auctions.add_new_auction(user_id, item_name, description, float(value_min))

        # hier nur einfügen, wenn gerade die liste mit den angezeigten Angeboten gezeigt wird
        if self.view_option.get() == 'offered':
            self.item_listbox.insert(tk.END, auction.pretty_print(False))

        # Füge neues Item an der richtigen Stelle in all_items_listbox ein, sortiert nach verbleibender Zeit
        new_time_left = auction.get_time_left()
        inserted = False
        for idx in range(self.all_items_listbox.size()):
            existing_desc = self.all_items_listbox.get(idx)
            existing_id = marketplace.auction.Auction.get_id_from_pretty_print(existing_desc)
            if existing_id in self._auctions:
                existing_time_left = self._auctions.get_time_left(existing_id)
                if existing_time_left > new_time_left:
                    self.all_items_listbox.insert(idx, auction.pretty_print())
                    inserted = True
                    break

        if not inserted:
            self.all_items_listbox.insert(tk.END, auction.pretty_print())

        self.system_messages.push("Neue Auktion erfolgreich erstellt.")

        # neuen Produktnamen auch für die Autovervollständigung verfügbar machen
        self.rebuild_trie()

        # Schließen des Fensters
        widget.destroy()

    # *** TRIE: für Autovervollständigung bei Suche nach Produkten in Liste ***

    def initialize_trie(self) -> None:
        """Initialisiert den Trie und den AVL-Baum mit den Produktnamen aus den Auktionen.

        Args:
            None

        Returns:
            None
        """
        # TODO for students (Praktikum 1): fügen Sie auch die Nutzer-IDs in den Trie ein, damit im Suchfeld
        #  auch nach Nutzer-IDs gesucht werden kann
        product_names = self._auctions.get_all_item_names()

        counter = Counter(product_names)
        tuple_list = list(counter.items())

        for product_name, count in tuple_list:
            self.trie.insert(product_name)
            self.avl_tree.insert(product_name, count)

    def rebuild_trie(self) -> None:
        """Baut Trie und AVL-Baum neu auf, damit auch neu erstellte Auktionen vorgeschlagen werden.

        Args:
            None

        Returns:
            None
        """
        self.trie = marketplace.trie.Trie()
        self.avl_tree = avl_tree.AVLTree()
        self.initialize_trie()

    def show_tooltip(self, suggestions: List[str]) -> None:
        """Erstellt und zeigt ein Tooltip-Fenster mit Suchvorschlägen an.

        Args:
            suggestions (List[str]): Liste der anzuzeigenden Suchvorschläge.

        Returns:
            None
        """
        if self.tooltip:
            self.tooltip.destroy()

        # Calculate the height and width of the Listbox based on content
        max_height = 10  # Maximum number of items to show before adding a scrollbar
        num_items = min(len(suggestions), max_height)  # Limit the number of visible items

        if num_items > 0:
            # Create a new tooltip window
            self.tooltip = tk.Toplevel(self.root)
            self.tooltip.wm_overrideredirect(True)  # Remove window decorations

            # Calculate the position to display the tooltip
            x, y, _, _ = self.search_entry.bbox("insert")
            x += self.search_entry.winfo_rootx()
            y += self.search_entry.winfo_rooty() + 25
            self.tooltip.geometry(f"+{x}+{y}")  # Set initial position

            # Create the Listbox for suggestions
            listbox = tk.Listbox(self.tooltip)
            listbox.pack()
            self._style_listbox(listbox)

            # Add suggestions to the Listbox
            for suggestion in suggestions:
                listbox.insert(tk.END, suggestion)

            listbox.bind("<<ListboxSelect>>", self.on_select)

            # Determine the maximum width needed for the suggestions
            max_width = max(len(s) for s in suggestions) + 2  # Add padding to width

            # Set height and width of the Listbox to accommodate the suggestions
            listbox.config(height=num_items, width=max_width)
            listbox.update_idletasks()  # Update Listbox geometry calculations

            # Correctly calculate width and height of the Listbox after updates
            width = listbox.winfo_reqwidth()  # Use winfo_reqwidth() to get requested width
            height = listbox.winfo_reqheight()  # Use winfo_reqheight() to get requested height

            # Update tooltip size based on Listbox size
            self.tooltip.geometry(f"{width}x{height}+{x}+{y}")

    def hide_tooltip(self) -> None:
        """Versteckt das Tooltip-Fenster für Suchvorschläge.

        Args:
            None

        Returns:
            None
        """
        if self.tooltip:
            try:
                if self.tooltip.winfo_exists():
                    self.tooltip.destroy()
            except tk.TclError:
                pass
            self.tooltip = None

    def update_tooltip_position(self, event: tk.Event) -> None:
        """Aktualisiert die Position des Tooltips beim Anpassen der Fenstergröße oder -position.

        Args:
            event (tk.Event): Das Konfigurations-Event.

        Returns:
            None
        """
        if self.tooltip:
            try:
                if self.tooltip.winfo_exists():
                    x, y, _, _ = self.search_entry.bbox("insert")
                    x += self.search_entry.winfo_rootx()
                    y += self.search_entry.winfo_rooty() + 25
                    self.tooltip.geometry(f"+{x}+{y}")
                else:
                    self.tooltip = None
            except tk.TclError:
                self.tooltip = None

    # *** PRIVATE STATIC METHODS ***

    def _on_closing(self) -> None:
        """Stoppt laufende Simulationen und schließt das Hauptfenster.

        Args:
            None

        Returns:
            None
        """
        # Signal the thread to stop
        self._auctions.stop_simulation()

        self.root.destroy()

    @staticmethod
    def simple_input(title: str, prompt: str) -> Optional[str]:
        """Öffnet einen einfachen Eingabedialog und gibt die Benutzereingabe zurück.

        Args:
            title (str): Der Titel des Dialogfensters.
            prompt (str): Die Aufforderungsnachricht im Dialogfenster.

        Returns:
            Optional[str]: Der eingegebene Text oder `None`, wenn abgebrochen wurde.
        """
        return simpledialog.askstring(title, prompt)
