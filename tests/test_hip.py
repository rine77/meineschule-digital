from datetime import date

from meineschule_digital.parsers.hip import parse_hip


def test_parse_grades_and_lessons():
    html = """
    <div class="main withschoolmenu">
      <h2>Beispiel, Alex</h2>
      <h3>Noten</h3>
      <h4>de - Deutsch</h4>
      <table>
        <tr><th>Datum</th><th>Note</th><th>Bemerkung</th><th>Information</th></tr>
        <tr><td>14.09.2026</td><td>2</td><td>Vortrag</td><td>Noten,Einfach</td></tr>
      </table>
      <h3>Unterricht</h3>
      <table>
        <tr><th>Datum</th><th>Fach</th><th>Hausaufgaben</th></tr>
        <tr><td>22.09.2026</td><td>et</td><td>Mindmap zum 06.10.2026</td></tr>
      </table>
    </div>
    """
    result = parse_hip(html)

    assert result.student == "Beispiel, Alex"
    assert len(result.grades) == 1
    assert result.grades[0].subject == "de - Deutsch"
    assert result.grades[0].date == date(2026, 9, 14)
    assert result.grades[0].value == "2"
    assert len(result.lessons) == 1
    assert result.lessons[0].homework == "Mindmap zum 06.10.2026"


def test_parse_absences_and_remarks_without_summary_rows():
    html = """
    <div class="main withschoolmenu">
      <h2>Beispiel, Alex</h2>
      <h3>Fehlzeiten</h3>
      <table>
        <tr><th>Datum</th><th>Bemerkung</th></tr>
        <tr><td>11.09.2026</td><td>Tag (Entschuldigt)</td></tr>
      </table>
      <h4>Zusammenfassung</h4>
      <table>
        <tr><th></th><th>Entschuldigt</th><th>Unentschuldigt</th></tr>
        <tr><td>Fehltage</td><td>1</td><td>0</td></tr>
      </table>
      <h3>Bemerkungen</h3>
      <table>
        <tr><th>Datum</th><th>Bemerkung</th><th>Fach</th><th>Typ</th><th>Benutzer</th></tr>
        <tr>
          <td>09.09.2026</td><td>Beispieltext</td><td>de - Deutsch</td>
          <td>Hinweis</td><td>Muster, Lea</td>
        </tr>
      </table>
    </div>
    """
    result = parse_hip(html)

    assert len(result.absences) == 1
    assert result.absences[0].date == date(2026, 9, 11)
    assert result.absences[0].remark == "Tag (Entschuldigt)"

    assert len(result.remarks) == 1
    assert result.remarks[0].text == "Beispieltext"
    assert result.remarks[0].subject == "de - Deutsch"
    assert result.remarks[0].type == "Hinweis"
    assert result.remarks[0].author == "Muster, Lea"


def test_homework_due_date_is_distinct_from_entry_date():
    html = """
    <div class="main withschoolmenu">
      <h2>Beispiel, Alex</h2>
      <h3>Unterricht</h3>
      <table>
        <tr><th>Datum</th><th>Fach</th><th>Hausaufgaben</th></tr>
        <tr><td>22.09.2026</td><td>et</td>
            <td>Mindmap zum 06.10.2026</td></tr>
        <tr><td>16.09.2026</td><td>la</td>
            <td>Vokabeln wiederholen</td></tr>
      </table>
    </div>
    """
    result = parse_hip(html)

    assert result.lessons[0].date == date(2026, 9, 22)
    assert result.lessons[0].due_date == date(2026, 10, 6)
    assert result.lessons[0].homework == "Mindmap zum 06.10.2026"

    assert result.lessons[1].date == date(2026, 9, 16)
    assert result.lessons[1].due_date is None


def test_grade_preserves_information_as_raw_text():
    html = """
    <div class="main withschoolmenu">
      <h2>Beispiel, Alex</h2>
      <h3>Noten</h3>
      <h4>en - Englisch</h4>
      <table>
        <tr><th>Datum</th><th>Note</th><th>Bemerkung</th><th>Information</th></tr>
        <tr><td>03.09.2026</td><td>3</td>
            <td>Vokabeltest</td><td>Noten,keine Wertung</td></tr>
      </table>
    </div>
    """
    grade = parse_hip(html).grades[0]

    assert grade.subject == "en - Englisch"
    assert grade.value == "3"
    assert grade.remark == "Vokabeltest"
    assert grade.information == "Noten,keine Wertung"
