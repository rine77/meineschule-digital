# meineschule-digital

Inoffizieller Python-Client für [MeineSchule.digital](https://meineschule.digital).

Die Bibliothek meldet sich mit einem vorhandenen Benutzerkonto an und liest
Daten, auf die dieses Konto Zugriff hat. Sie ist unabhängig von Home Assistant
nutzbar. Eine mögliche Home-Assistant-Integration wird als eigenes Projekt
entwickelt und verwendet diese Bibliothek als Abhängigkeit.

> [!NOTE]
> Dieses Projekt ist inoffiziell und steht in keiner Verbindung zum Anbieter
> von MeineSchule.digital.

## Funktionen

- Anmeldung mit Benutzername und Passwort
- Auslesen von Home.InfoPoint
- Noten, Fehlzeiten und Bemerkungen
- Unterrichtseinträge und Hausaufgaben
- Individueller Stundenplan für den ausgewählten Schüler
- Ermittlung von Hausaufgaben-Zieldaten aus einem ausdrücklich genannten
  „zum“-Datum oder aus der nächsten angezeigten Fachstunde
- Ausschluss von Fächern, die zwar im Plan erscheinen, vom Kind aber nicht
  besucht werden

## Voraussetzungen und Installation

Benötigt wird Python 3.11 oder neuer. Installiere die veröffentlichte Version von PyPI:

    pip install "meineschule-digital==0.1.2"

Alternativ kannst du das Repository klonen und lokal installieren:

    git clone https://github.com/rine77/meineschule-digital.git
    cd meineschule-digital
    python -m venv .venv
    source .venv/bin/activate
    pip install .

Für die Entwicklung einschließlich Tests:

    pip install -e ".[test]"
    pytest -q

## Zugangsdaten und Schulpfad

Für die Nutzung brauchst du Benutzername, Passwort und den technischen
Schulpfad. Bei dieser Beispieladresse:

    https://meineschule.digital/beispiel-gymnasium/hip

ist `beispiel-gymnasium` der Schulpfad. Übergib diese Angaben aus der
Konfiguration deiner Anwendung. Die Bibliothek speichert keine Zugangsdaten.

Für lokale Versuche gibt es `.env.example` und das Beispiel unter
`examples/read_home_info.py`. Kopiere die Beispieldatei nach `.env` und trage
dort deine eigenen Werte ein. `.env` wird von Git ignoriert. Das Beispiel
benötigt zusätzlich:

    pip install python-dotenv
    python examples/read_home_info.py

## Verwendung

Der Client arbeitet asynchron und verwendet eine `aiohttp.ClientSession`:

    import asyncio
    import os

    import aiohttp

    from meineschule_digital import MeineSchuleClient

    async def main():
        async with aiohttp.ClientSession() as session:
            client = MeineSchuleClient(session)
            await client.login(
                os.environ["MSD_USERNAME"],
                os.environ["MSD_PASSWORD"],
            )

            info = await client.get_home_info(
                os.environ["MSD_SCHOOL"]
            )
            print(f"Noten: {len(info.grades)}")
            print(f"Bemerkungen: {len(info.remarks)}")

    asyncio.run(main())

`get_home_info()` liefert den angezeigten Schülernamen sowie Noten,
Fehlzeiten, Bemerkungen und Unterrichtseinträge. Für Noten und Bemerkungen
stehen außerdem `get_grades()` und `get_remarks()` als Einzelzugriffe bereit.

### Noten

Eine Note enthält Fach, Datum, Wert, Bemerkung und den Text der Spalte
`Information`. Dieser Text wird **unverändert übernommen**. Die Bibliothek
leitet daraus keine Gewichtung oder Bewertungskategorie ab und berechnet
keinen Notendurchschnitt.

### Hausaufgaben

`get_homework()` verbindet die Einträge aus Home.InfoPoint mit dem
individuellen Stundenplan:

    from datetime import date, timedelta

    heute = date.today()
    aufgaben = await client.get_homework(
        "beispiel-gymnasium",
        heute - timedelta(days=7),
        heute + timedelta(days=7),
        excluded_subjects={"er"},
    )

Jede Aufgabe enthält das Aufgabedatum (`assigned_date`), das Fach
(`subject`), den vollständigen Text (`text`), ein mögliches Zieldatum
(`due_date`) und dessen Herkunft (`due_date_source`):

| Herkunft | Bedeutung |
| --- | --- |
| `explicit` | Im Aufgabentext steht ein Datum in der Form `zum DD.MM.JJJJ`. |
| `schedule` | Das Datum wurde aus der nächsten nicht ausgefallenen Fachstunde ermittelt. |
| `unknown` | Innerhalb der abgefragten Planwochen war keine verlässliche Zuordnung möglich. |

Die Datumsspalte auf Home.InfoPoint bezeichnet den Tag, an dem die Aufgabe
eingetragen wurde. Sie ist **nicht automatisch das Zieldatum**.

Mit `excluded_subjects` kannst du schülerbezogen Fächer ausschließen, die
trotzdem im Stundenplan oder bei den Hausaufgaben angezeigt werden. Für
einen Schüler, der Ethik (`Et`) statt evangelischer Religion (`ER`) besucht,
kann beispielsweise `{"er"}` übergeben werden. Fachkürzel werden ohne
Beachtung der Groß- und Kleinschreibung verglichen.

## Fehler

Ein fehlgeschlagener Login oder eine abgelaufene Sitzung löst
`AuthenticationError` aus. Ein verweigerter Planabruf löst
`PermissionError` aus. Unerwartete Antworten und ungültige Parameter
können `ValueError` auslösen. Netzwerkfehler werden von `aiohttp`
weitergegeben.

## Grenzen

Die Bibliothek nutzt die Weboberfläche von MeineSchule.digital. Änderungen
an deren HTML oder JSON können Anpassungen des Clients erforderlich machen.
Ein Zieldatum aus dem Stundenplan wird nur ermittelt, wenn die benötigten
Planwochen erfolgreich abgefragt wurden. Schulspezifische Angaben werden
als Rohdaten weitergegeben und nicht inhaltlich interpretiert.

Eine ausführlichere Beschreibung der Datenfelder und Methoden findest du
in der [Anwenderdokumentation](docs/usage.md).

## Datenschutz

Committe keine Passwörter, Session-Cookies, HAR-Dateien oder unbearbeiteten
HTML- und JSON-Antworten mit Schülerdaten. Verwende für Tests ausschließlich
erfundene oder vollständig anonymisierte Daten.

## Lizenz

MIT – siehe [LICENSE](LICENSE).
