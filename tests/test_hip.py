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
