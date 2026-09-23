from datetime import datetime

from bs4 import BeautifulSoup, Tag

from meineschule_digital.models import Grade, HomeInfo, Lesson


def _date(value: str):
    return datetime.strptime(value.strip(), "%d.%m.%Y").date()


def _cells(row: Tag) -> list[str]:
    return [cell.get_text(" ", strip=True) for cell in row.find_all("td", recursive=False)]


def parse_hip(html: str) -> HomeInfo:
    soup = BeautifulSoup(html, "html.parser")
    main = soup.select_one(".main.withschoolmenu")
    if main is None:
        raise ValueError("Home.InfoPoint-Inhalt nicht gefunden")

    heading = main.find("h2")
    if heading is None:
        raise ValueError("Schülername nicht gefunden")

    result = HomeInfo(student=heading.get_text(" ", strip=True))
    section = ""
    subject = ""

    for element in main.children:
        if not isinstance(element, Tag):
            continue

        if element.name == "h3":
            section = element.get_text(" ", strip=True)
            subject = ""
        elif element.name == "h4" and section == "Noten":
            subject = element.get_text(" ", strip=True)
        elif element.name == "table":
            for row in element.find_all("tr", recursive=False):
                cells = _cells(row)
                if section == "Noten" and subject and len(cells) == 4:
                    result.grades.append(
                        Grade(subject, _date(cells[0]), cells[1], cells[2], cells[3])
                    )
                elif section == "Unterricht" and len(cells) == 3:
                    result.lessons.append(
                        Lesson(_date(cells[0]), cells[1], cells[2])
                    )

    return result
