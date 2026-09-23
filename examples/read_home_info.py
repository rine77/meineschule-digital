import asyncio
import os

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

    async with aiohttp.ClientSession() as session:
        client = MeineSchuleClient(session)
        await client.login(username, password)
        info = await client.get_home_info(school)

    print("Home.InfoPoint erfolgreich gelesen")
    print(f"Noten: {len(info.grades)}")
    print(f"Fehlzeiten: {len(info.absences)}")
    print(f"Bemerkungen: {len(info.remarks)}")
    print(f"Unterrichtseinträge: {len(info.lessons)}")


if __name__ == "__main__":
    asyncio.run(main())
