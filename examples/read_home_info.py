import asyncio
import os
from collections import Counter
from datetime import date, timedelta

import aiohttp
from dotenv import load_dotenv

from meineschule_digital.client import MeineSchuleClient


async def main() -> None:
    load_dotenv()

    username = os.getenv("MSD_USERNAME")
    password = os.getenv("MSD_PASSWORD")
    school = os.getenv("MSD_SCHOOL")

    if not all((username, password, school)):
        raise SystemExit(
            "MSD_USERNAME, MSD_PASSWORD und MSD_SCHOOL müssen gesetzt sein"
        )

    excluded = {
        value.strip().casefold()
        for value in os.getenv("MSD_EXCLUDED_SUBJECTS", "").split(",")
        if value.strip()
    }

    today = date.today()

    async with aiohttp.ClientSession() as session:
        client = MeineSchuleClient(session)
        await client.login(username, password)

        info = await client.get_home_info(school)
        homework = await client.get_homework(
            school,
            today - timedelta(days=7),
            today + timedelta(days=7),
            excluded_subjects=excluded,
        )

    sources = Counter(item.due_date_source for item in homework)

    print(f"Noten: {len(info.grades)}")
    print(f"Fehlzeiten: {len(info.absences)}")
    print(f"Bemerkungen: {len(info.remarks)}")
    print(f"Relevante Hausaufgaben: {len(homework)}")
    print(f"Zieldatum ausdrücklich: {sources['explicit']}")
    print(f"Zieldatum aus Stundenplan: {sources['schedule']}")
    print(f"Zieldatum unbekannt: {sources['unknown']}")


if __name__ == "__main__":
    asyncio.run(main())
