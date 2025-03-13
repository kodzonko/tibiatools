from loguru import logger
import pandas as pd
import re
from datetime import datetime
import spacy

nlp = spacy.load("en_core_web_sm")


def is_valid_entry(text: str) -> bool:
    """Check if a line is a valid combat log entry (starts with a timestamp)."""
    return bool(text) and text[0].isdigit()


def extract_date(text: str) -> str | None:
    """
    Extract date from Server Log header string and return in yyyy-mm-dd format.

    Args:
        text: String containing the log header text

    Returns:
        Formatted date string (YYYY-MM-DD) or None if extraction fails
    """
    # Sample input: "Channel Server Log saved Tue Feb 25 15:00:47 2025"
    pattern = r"Channel Server Log saved (\w{3} \w{3} \d{1,2} \d{2}:\d{2}:\d{2} \d{4})"
    match = re.search(pattern, text)

    if match:
        date_str = match.group(1)
        try:
            # Parse the date using the appropriate format
            date_obj = datetime.strptime(date_str, "%a %b %d %H:%M:%S %Y")
            # Return formatted date string
            return date_obj.strftime("%Y-%m-%d")
        except ValueError:
            logger.error(f"Could not parse date: {date_str}")
            return None
    return None


def extract_target_and_action(text: str) -> tuple[str, str] | tuple[None, None]:
    """Extract action type using regex pattern matching."""
    # Compile regex pattern once (more efficient for repeated use)
    patterns = {
        r"\b(loses|lose)\b": "ATTACK",
        r"\bhealed\b": "HEAL",
        r"\bgained\b": "GAIN",
        r"\bdropped\b": "LOOT",
    }

    for pattern, action_type in patterns.items():
        if finding := re.search(pattern, text):
            subject = text[: finding.start()].strip()
            return subject, action_type

    return None, None


def extract_actor(text: str) -> str:
    """Extract the actor from a given text."""

    if "due to your" in text or "yourself" in text:
        return "You"

    # Check for "attack by" pattern with optional "critical"
    attack_by_pattern = r"(?:critical )?attack by ([^\.]+)\."
    if match := re.search(attack_by_pattern, text):
        return match.group(1).strip()

    # Original pattern as fallback
    if "due to an attack by" in text:
        return text.split("an attack by")[1].strip()

    if "himself" in text:
        return extract_target_and_action(text)[0] or "OTHER"

    return "OTHER"


def parse_server_log(file_path: str) -> pd.DataFrame:
    """Parse Tibia combat log file into a structured DataFrame."""

    # Read the file and split into timestamp and message
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    filter_words = {"saved", "poisoned", "using", "appended", "looted"}

    timestamps = []
    messages = []

    date_ = "1900-01-01"
    for line in lines:
        if line.startswith("Channel Server Log saved"):
            date_ = extract_date(line)
            continue
        if is_valid_entry(line) and not any(word in line for word in filter_words):
            timestamps.append(f"{date_} {line[:8]}")
            messages.append(line[9:].strip())

    # Create DataFrame
    df = pd.DataFrame({"timestamp": timestamps, "message": messages})

    # Convert timestamp to datetime
    df["timestamp"] = pd.to_datetime(df["timestamp"], format="%Y-%m-%d %H:%M:%S")

    # Extract actions from messages
    df[["target", "action"]] = pd.DataFrame(
        df["message"].apply(extract_target_and_action).tolist()
    )

    df["actor"] = df["message"].apply(extract_actor)

    return df


if __name__ == "__main__":
    text = "Zamulosh loses 334 hitpoints due to an attack by Night Ghoustt."
    verb = extract_target_and_action(text)
    print(f"Found verb: {verb}")  # Output: Found verb: loses
