# generic_helper.py

import re

def get_str_from_tech_dict(tech_dict: dict) -> str:
    """
    Converts a dictionary of tech items to a string format.
    Example: {"Laptop": 2, "Phone": 1} -> "2 Laptop, 1 Phone"
    """
    result = ", ".join([f"{int(value)} {key}" for key, value in tech_dict.items()])
    return result

def extract_session_id(session_str: str) -> str:
    """
    Extracts the session ID from a session string.
    Example: "/sessions/12345/contexts/" -> "12345"
    """
    match = re.search(r"/sessions/(.*?)/contexts/", session_str)
    if match:
        return match.group(1)  # Return only the session ID

    return ""
