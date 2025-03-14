import httpx
import pandas as pd
from loguru import logger
from bs4 import BeautifulSoup
import re
from typing import Set, List


def fetch_boss_names() -> pd.Series:
    """Fetch boss names from Tibia Wiki and return as a pandas Series."""
    url = "https://tibia.fandom.com/wiki/Bosses"

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        with httpx.Client(timeout=15.0) as client:
            logger.info(f"Fetching bosses from {url}")
            response = client.get(url, headers=headers)
            response.raise_for_status()

            # Parse the HTML
            soup = BeautifulSoup(response.text, "html.parser")

            # Find the "Bosses" h2 heading - handling the span structure
            bosses_heading = soup.find("span", {"id": "Bosses"})
            if bosses_heading:
                bosses_heading = bosses_heading.parent

            # Fallback method if the above doesn't work
            if not bosses_heading:
                for h2 in soup.find_all("h2"):
                    if h2.find("span") and h2.get_text().strip() == "Bosses":
                        bosses_heading = h2
                        break

            # Final fallback
            if not bosses_heading:
                logger.error("Could not find 'Bosses' heading")
                return pd.Series([], name="boss_name")

            # Find the first table after the Bosses heading
            boss_table = None
            current = bosses_heading
            while current and not boss_table:
                current = current.find_next()
                if (
                    current
                    and current.name == "table"
                    and "wikitable" in current.get("class", [])
                ):
                    boss_table = current
                    break

            if not boss_table:
                logger.error("Could not find table after Bosses heading")
                return pd.Series([], name="boss_name")

            boss_names = set()
            for row in boss_table.select("tr"):
                cells = row.select("td")
                if cells:
                    boss_name = cells[0].get_text(strip=True)
                    boss_name = re.sub(r"\[.*?\]", "", boss_name).strip()
                    if boss_name:
                        boss_names.add(boss_name)

            logger.info(f"Found {len(boss_names)} bosses")
            return pd.Series(list(boss_names), name="boss_name")

    except httpx.RequestError as e:
        logger.error(f"Error fetching URL: {e}")
        return pd.Series([], name="boss_name")
    except Exception as e:
        logger.error(f"Error processing boss data: {e}")
        return pd.Series([], name="boss_name")


def fetch_creatures_names() -> pd.Series:
    """Fetch creature names from Tibia Wiki and return as a pandas Series."""
    url = "https://tibia.fandom.com/wiki/List_of_Creatures"

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        with httpx.Client(timeout=15.0) as client:
            logger.info(f"Fetching creatures from {url}")
            response = client.get(url, headers=headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Find the "List of Creatures" h3 heading - handling the span structure
            creatures_heading = soup.find("span", {"id": "List_of_Creatures"})
            if creatures_heading:
                creatures_heading = creatures_heading.parent

            # Fallback method if the above doesn't work
            if not creatures_heading:
                for h3 in soup.find_all("h3"):
                    if h3.find("span") and h3.get_text().strip() == "List of Creatures":
                        creatures_heading = h3
                        break

            # Final fallback
            if not creatures_heading:
                logger.error("Could not find 'List of Creatures' heading")
                return pd.Series([], name="creature_name")

            # Find the first table after the List of Creatures heading
            creatures_table = None
            current = creatures_heading
            while current and not creatures_table:
                current = current.find_next()
                if (
                    current
                    and current.name == "table"
                    and "wikitable" in current.get("class", [])
                ):
                    creatures_table = current
                    break

            if not creatures_table:
                logger.error("Could not find table after List of Creatures heading")
                return pd.Series([], name="creature_name")

            # Extract creature names from the first column of each row
            creature_names: List[str] = []
            for row in creatures_table.select("tr"):
                cells = row.select("td")
                if cells:
                    # The creature name is in the first column
                    creature_name = cells[0].get_text(strip=True)
                    creature_name = re.sub(r"\[.*?\]", "", creature_name).strip()
                    if creature_name:
                        creature_names.append(creature_name)

            logger.info(f"Found {len(creature_names)} creatures")
            return pd.Series(creature_names, name="creature_name")

    except httpx.RequestError as e:
        logger.error(f"Error fetching URL: {e}")
        return pd.Series([], name="creature_name")
    except Exception as e:
        logger.error(f"Error processing creature data: {e}")
        return pd.Series([], name="creature_name")


if __name__ == "__main__":
    # Fetch and save bosses
    bosses_series = fetch_boss_names()
    print(f"Bosses found: {len(bosses_series)}")
    print(bosses_series.head(10))
    bosses_series.to_frame().to_parquet(
        "boss_names.parquet", engine="pyarrow", compression="snappy"
    )

    # Fetch and save creatures
    creatures_series = fetch_creatures_names()
    print(f"Creatures found: {len(creatures_series)}")
    print(creatures_series.head(10))
    creatures_series.to_frame().to_parquet(
        "creature_names.parquet", engine="pyarrow", compression="snappy"
    )
