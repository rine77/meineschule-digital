from datetime import date, datetime

from bs4 import BeautifulSoup, Tag

from meineschule_digital.models import (
    Absence,
    Grade,
    HomeInfo,
    Lesson,
    StudentRemark,
)


def _date(value: str) -> date:
    return datetime.strptime(value.strip(), "%d.%m.%Y").date()


def _cells(row: Tag) -> list[str]:
    return [
        cell.get_text(" ", strip=True)
        for cell in row.find_all("td", recursive=False)
    ]


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
    subsection = ""

    for element in main.children:
        if not isinstance(element, Tag):
            continue

        if element.name == "h3":
            section = element.get_text(" ", strip=True)
            subject = ""
            subsection = ""
        elif element.name == "h4":
            if section == "Noten":
                subject = element.get_text(" ", strip=True)
            else:
                subsection = element.get_text(" ", strip=True)
        elif element.name == "table":
            for row in element.find_all("tr", recursive=False):
                cells = _cells(row)

                if section == "Noten" and subject and len(cells) == 4:
                    result.grades.append(
                        Grade(
                            subject=subject,
                            date=_date(cells[0]),
                            value=cells[1],
                            remark=cells[2],
                            information=cells[3],
                        )
                    )
                elif section == "Fehlzeiten" and not subsection and len(cells) == 2:
                    result.absences.append(
                        Absence(date=_date(cells[0]), remark=cells[1])
                    )
                elif section == "Bemerkungen" and len(cells) == 5:
                    result.remarks.append(
                        StudentRemark(
                            date=_date(cells[0]),
                            text=cells[1],
                            subject=cells[2],
                            type=cells[3],
                            author=cells[4],
                        )
                    )
                elif section == "Unterricht" and len(cells) == 3:
                    result.lessons.append(
                        Lesson(
                            date=_date(cells[0]),
                            subject=cells[1],
                            homework=cells[2],
                        )
                    )

    return result
