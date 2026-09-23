# MeineSchule.digital Python-Client verwenden

`meineschule-digital` ist eine inoffizielle Python-Bibliothek zum Lesen von
Daten aus MeineSchule.digital. Sie kann unabhängig von Home Assistant in
eigenen Python-Anwendungen verwendet werden.

Die Bibliothek meldet sich mit einem MeineSchule.digital-Konto an und liest
Daten, auf die dieses Konto Zugriff hat. Sie benötigt Python 3.11 oder neuer.

## Installation

Benötigt wird Python 3.11 oder neuer. Installiere Version `0.1.0` direkt
von GitHub:

    pip install "git+https://github.com/rine77/meineschule-digital.git@v0.1.0"

Oder klone das Repository und installiere es lokal:

    git clone https://github.com/rine77/meineschule-digital.git
    cd meineschule-digital
    pip install .

## Zugangsdaten und Schulpfad

Für die Anmeldung werden Benutzername und Passwort benötigt. Für die Abfragen
wird außerdem der technische Schulpfad gebraucht: Bei einer Adresse wie

    https://meineschule.digital/beispiel-gymnasium/hip

lautet er `beispiel-gymnasium`.

Die Bibliothek speichert diese Werte nicht. Übergib sie aus der Konfiguration
deiner Anwendung. Hinterlege Passwörter nicht direkt im Python-Quellcode.

## Grundlegender Aufruf

Die Bibliothek verwendet `aiohttp` und wird asynchron aufgerufen:

    import asyncio
    import aiohttp

    from meineschule_digital import MeineSchuleClient

    async def main():
        async with aiohttp.ClientSession() as session:
            client = MeineSchuleClient(session)
            await client.login("BENUTZERNAME", "PASSWORT")

            info = await client.get_home_info("beispiel-gymnasium")
            print(f"Noten: {len(info.grades)}")
            print(f"Bemerkungen: {len(info.remarks)}")

    asyncio.run(main())

Die Platzhalter für Benutzername und Passwort dienen nur zur Veranschaulichung.
Ein vollständiges lokales Beispiel mit `.env` liegt im Repository unter
`examples/read_home_info.py`.

## Home.InfoPoint

`get_home_info(school_slug)` liefert ein `HomeInfo`-Objekt mit:

- `student`: angezeigter Schülername
- `grades`: Noten
- `absences`: Fehlzeiten
- `remarks`: Bemerkungen
- `lessons`: Unterrichtseinträge mit Hausaufgabentexten

Für einen Einzelzugriff stehen `get_grades(school_slug)` und
`get_remarks(school_slug)` bereit. Jede dieser Methoden ruft die Seite erneut
ab. Wenn du mehrere Datenarten benötigst, verwende einmal `get_home_info()`.

Eine Note enthält `subject`, `date`, `value`, `remark` und `information`.
`information` ist der unveränderte Text der gleichnamigen Spalte. Die
Bibliothek deutet diesen Text nicht als Gewichtung oder Bewertungskategorie
und berechnet keinen Notendurchschnitt.

Eine Bemerkung enthält `date`, `text`, `subject`, `type` und `author`.

## Stundenplan

`get_schedule(school_slug, day, excluded_subjects=...)` liest die Planwoche,
in die `day` fällt. `day` ist ein `datetime.date`. Ein Unterrichtseintrag
enthält Datum, Stundennummer, Fach und die Angabe `cancelled`.

    from datetime import date

    lessons = await client.get_schedule(
        "beispiel-gymnasium",
        date.today(),
        excluded_subjects={"er"},
    )

`excluded_subjects` ist optional. Damit können Fächer ausgeblendet werden,
die im Plan erscheinen, aber vom betreffenden Kind nicht besucht werden.
Der Vergleich der Fachkürzel berücksichtigt Groß- und Kleinschreibung nicht.

Für mehrere Wochen gibt es `get_schedule_weeks()`. Die Methode liefert
`(lessons, covered_weeks)`; `covered_weeks` enthält die Montage der
erfolgreich abgefragten Wochen.

## Hausaufgaben und Zieldaten

`get_homework()` kombiniert Home.InfoPoint mit dem Stundenplan:

    from datetime import date, timedelta

    today = date.today()
    homework = await client.get_homework(
        "beispiel-gymnasium",
        today - timedelta(days=7),
        today + timedelta(days=7),
        excluded_subjects={"er"},
    )

Jeder `HomeworkItem` enthält:

- `assigned_date`: Tag, an dem die Aufgabe eingetragen wurde
- `subject`: Fachkürzel
- `text`: vollständiger Aufgabentext
- `due_date`: ermitteltes Zieldatum oder `None`
- `due_date_source`: `explicit`, `schedule` oder `unknown`

Steht im Text `zum DD.MM.JJJJ`, wird dieses Datum als `explicit` übernommen.
Andernfalls sucht die Bibliothek die nächste nicht ausgefallene Stunde des
Fachs in den abgefragten Planwochen (`schedule`). Reichen die Plandaten nicht
für eine verlässliche Zuordnung, bleibt `due_date` bei `None` (`unknown`).

`from_date` bezieht sich auf das Aufgabedatum. `until_date` begrenzt die
Suche im Stundenplan; es begrenzt nicht ausdrücklich genannte Zieldaten.
Pro Aufruf können höchstens zwölf Planwochen abgefragt werden.

## Fehlerbehandlung

Ein fehlgeschlagener Login oder eine abgelaufene Sitzung löst
`AuthenticationError` aus. Ein verweigerter Zugriff auf eine Planwoche löst
`PermissionError` aus. Bei unerwarteten Antwortformaten oder ungültigen
Parametern kann `ValueError` auftreten. HTTP- und Verbindungsfehler von
`aiohttp` werden an die aufrufende Anwendung weitergegeben.

## Grenzen

Die Bibliothek verwendet die Weboberfläche von MeineSchule.digital. Ändert
sich deren HTML- oder JSON-Struktur, kann ein Update der Bibliothek nötig
werden. Schulspezifische Inhalte wie die Notenspalte `information` werden
als Daten weitergegeben und nicht interpretiert.
