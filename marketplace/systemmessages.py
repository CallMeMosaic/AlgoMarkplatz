"""Übersicht über den Dateiinhalt:

Definiert die Klasse SystemMessages.
Verwaltet Systemnachrichten in einer Warteschlange und zeigt diese nacheinander
über GUI-Callbacks oder direkte Tkinter-Label-Aktualisierungen an.
"""

# Status: FINAL, dgaida2, 15.10.2024

# Definiert die Klasse SystemMessages
# über die Methode push() können Nachrichten in der Warteschlange gespeichert werden.
# Nachrichten in der Warteschlange werden nacheinander in dem tk.Label _lbl_sysmessage
# für 3 Sekunden angezeigt (die letzte Nachricht für 15 Sekunden), bis keine Nachrichten mehr in der
# Warteschlange existieren.
# in der GUI werden diese Nachrichten oben links angezeigt.

from typing import Any, Callable, Optional


class SystemMessages:
    """Verwaltet Benachrichtigungsmeldungen des Systems über Callbacks oder Tkinter-Widgets.

    Attributes:
        _queue (list): Die Warteschlange für ausstehende Systemnachrichten.
        _lbl_sysmessage (Optional[Any]): Tkinter-Label zur Anzeige (falls vorhanden).
        _update_callback (Optional[Callable[[str, str], None]]): Callback zur Aktualisierung des Textes und Hintergrunds.
        _after_callback (Optional[Callable[[int, Callable], None]]): Callback zur Zeitverzögerung (Timer).
        _displaying (bool): Status, ob gerade eine Nachricht angezeigt wird.
    """

    # *** CONSTRUCTORS ***
    def __init__(self, target: Optional[Any] = None,
                 update_callback: Optional[Callable[[str, str], None]] = None,
                 after_callback: Optional[Callable[[int, Callable], None]] = None) -> None:
        """Initialisiert die SystemMessages-Klasse.

        Args:
            target (Optional[Any]): Tkinter-Label oder kompatibles Objekt zur Nachrichtenanzeige.
            update_callback (Optional[Callable[[str, str], None]]): Funktion zur Aktualisierung von Text und Farbe.
            after_callback (Optional[Callable[[int, Callable], None]]): Funktion zur Timer-Steuerung.

        Raises:
            None
        """
        self._queue: list = []
        self._lbl_sysmessage = target if (target is not None and hasattr(target, "config")) else None
        if self._lbl_sysmessage is not None:
            self._update_callback = lambda text, bg: self._lbl_sysmessage.config(text=text, bg=bg)
            self._after_callback = lambda ms, fn: self._lbl_sysmessage.after(ms, fn)
        else:
            self._update_callback = update_callback
            self._after_callback = after_callback
        self._displaying: bool = False

    # *** PUBLIC SET methods ***

    # *** PUBLIC methods ***

    def push(self, message: str) -> None:
        """Fügt eine neue Nachricht zur Warteschlange hinzu und startet bei Bedarf die Anzeige.

        Args:
            message (str): Die anzuzeigende Systemnachricht.

        Returns:
            None

        Raises:
            None
        """
        self._queue.append(message)
        if not self._displaying:
            self._display_next_message()

    # *** PUBLIC GET methods ***

    # *** PUBLIC STATIC methods ***

    # *** PRIVATE methods ***

    def _display_next_message(self) -> None:
        """Interne Methode zur schrittweisen Anzeige der nächsten Nachricht aus der Warteschlange.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        if not self._queue:
            self._displaying = False
            if self._lbl_sysmessage is not None:
                default_bg = '#F1F5F9'
                try:
                    if hasattr(self._lbl_sysmessage, "master") and hasattr(self._lbl_sysmessage.master, "cget"):
                        default_bg = self._lbl_sysmessage.master.cget("bg")
                    elif hasattr(self._lbl_sysmessage, "master") and "bg" in self._lbl_sysmessage.master.keys():
                        default_bg = self._lbl_sysmessage.master["bg"]
                except Exception:
                    default_bg = '#F1F5F9'
                if self._update_callback:
                    self._update_callback("-", default_bg)
            elif self._update_callback:
                self._update_callback("-", "#F1F5F9")
            return

        self._displaying = True
        message = self._queue.pop(0)
        if self._update_callback:
            self._update_callback(message, "#93C5FD")

        if len(self._queue) == 0:
            display_time = 15  # 15 seconds for the last message
        else:
            display_time = 3  # 3 seconds for other messages

        if self._after_callback:
            self._after_callback(display_time * 1000, self._display_next_message)

    # *** PUBLIC methods to return class properties ***

    # *** PRIVATE variables ***
