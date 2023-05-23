import re
import json
import sys
import base64

import numpy as np

from typing import List, Dict, Any
from geopy import distance
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from config import DEFAULT_DURATION


def compute_distance(
        lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """ Computes the distance in kilometers between two sets of coordinates.
    Returns:
        float: The distance in kilometers between the two sets of coordinates.
    """
    coords_1 = (lat1, lng1)
    coords_2 = (lat2, lng2)
    return distance.geodesic(coords_1, coords_2).km


def decode_base64(base64_string: str) -> str:
    """ Decodes a base64-encoded string and removes the 
        first and last four characters.
    Args:
        base64_string (str): The base64-encoded string to decode.
    Returns:
        str: The decoded string.
    """
    return base64.b64decode(base64_string).decode("utf-8")[4:-4]


def parse_attr_ids_response(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """ Parses a response containing attraction IDs and names.
    Args:
        data (List[Dict[str, Any]]): A list of dictionaries 
            representing the JSON response.
    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing 
            the attraction IDs and names.
    """
    results = []
    for item in data[0]["data"]["Result"][0]["sections"]:
        if item["__typename"] == "WebPresentation_SingleFlexCardSection":
            results.append({
                "id": item["singleFlexCardContent"]["saveId"]["id"],
                "name": item["singleFlexCardContent"]["cardTitle"]["text"]
            })
    return results


def extract_activity_duration(text: str) -> int:
    """ Extracts the duration of an activity from a string. 
        The function searches the string for any sequences of 
        digits and calculates the average duration in minutes 
        rounded to the nearest 5 minutes.
    Args:
        text (str): The text to extract the duration from.
    Returns:
        int: The duration of the activity in minutes.
    """
    digits = re.findall(r'\d+', text)
    digits = [int(digit) for digit in digits]
    if "hour" in text.lower():
        return 5 * round(60 * np.mean(digits) / 5)
    elif "minute" in text.lower() or "min" in text.lower():
        return 5 * round(np.mean(digits) / 5)
    else:
        raise Exception


def parse_activity_duration(data: List[Dict[str, Any]]) -> int:
    """ Parses the JSON response to extract the duration of the activity. 
        If no duration is found, the default duration is returned.
    Args:
        data (List[Dict[str, Any]]): A list of dictionaries 
            representing the JSON response.
    Returns:
        int: The duration of the activity in minutes.
    """
    items = data[0]["data"]["Result"][0]["detailSectionGroups"] \
                [1]["about"]["primary"]["content"]
    for item in items:
        try:
            if (item["__typename"] == "WebPresentation_AboutContentWeb" and
                item["identifier"] == "DURATION"):
                return extract_activity_duration(
                    item["item"]["text"]["text"]
                )
        except:
            pass
    return DEFAULT_DURATION


def parse_business_description(data: List[Dict[str, Any]]) -> str:
    """ Parses the JSON response to extract the description of the 
        business. If no description is found, an exception is raised.
    Args:
        data (List[Dict[str, Any]]): A list of dictionaries 
            representing the JSON response.
    Returns:
        str: The description of the business.
    """
    for item in data[0]["data"]["Result"][0]["detailSectionGroups"]:
        if item["__typename"] == "WebPresentation_AttractionAboutSectionGroup":
            try:
                description = item["about"]["primary"]["about"]
                description = decode_base64(description).replace("\n", "")
                return description
            except:
                pass
    raise Exception
    

def parse_business_tags(data: List[Dict[str, Any]]) -> List[str]:
    """ Parses the JSON response to extract the tags 
        associated with the business. If no tags are found, 
        an empty list is returned.
    Args:
        data (List[Dict[str, Any]]): A list of dictionaries 
            representing the JSON response.
    Returns:
        List[str]: A list of tags associated with the business.
    """
    for item in data[0]["data"]["Result"][0]["detailSectionGroups"][0]["detailSections"]:
        try:
            tags = item["tags"]["text"]
            return [tag.strip() for tag in tags.split("•")]
        except:
            pass
    return []


def parse_business_website(data: List[Dict[str, Any]]) -> str:
    """ Parses the JSON response to extract the website of 
        the business. If no website URL is found, an empty 
        string is returned.
    Args:
        data (List[Dict[str, Any]]): A list of dictionaries 
            representing the JSON response.
    Returns:
        str: The website URL of the business.
    """
    for item in data[0]["data"]["Result"][0]["detailSectionGroups"][0]["detailSections"]:
        if item.get("__typename", "") == "WebPresentation_PoiOverviewWeb":
            try:
                for link in item["contactLinks"]:
                    if (link["__typename"] == "WebPresentation_ContactLink" and
                        link["linkType"] == "WEBSITE"):
                        website = decode_base64(link["link"]["externalUrl"])
                        return website
            except:
                pass
    return ""


def parse_business_hours(data: List[Dict[str, Any]]) -> str:
    """ Parses the JSON response to extract the hours 
        of operation of the business. If no hours of 
        operation are found, an empty string is returned.
    Args:
        data (List[Dict[str, Any]]): A list of dictionaries 
            representing the JSON response.
    Returns:
        str: The hours of operation of the business as a JSON string.
    """
    for item in data[0]["data"]["Result"][0]["detailSectionGroups"][0]["detailSections"]:
        if item.get("__typename", "") == "WebPresentation_PoiHoursWeb":
            try:
                hours = {}
                for section in item["poiHours"]['fullSchedule']:
                    hours[section["day"]["text"]] = section["intervals"]
                return json.dumps(hours)
            except:
                continue
    return ""