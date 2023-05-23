import os
import json
import sys

from typing import List, Dict
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from config import (
    REQUEST_ATTR_DETAILS_JSON,
    REQUEST_ATTR_ID_JSON,
    REQUEST_CITY_ID_JSON,
    REQUEST_HEADER_JSON,
    BASE_FILEPATH
)

REQUEST_ATTR_ID_FILEPATH = os.path.join(BASE_FILEPATH, REQUEST_ATTR_ID_JSON)
REQUEST_ATTR_DETAILS_FILEPATH = os.path.join(BASE_FILEPATH, REQUEST_ATTR_DETAILS_JSON)
REQUEST_CITY_ID_FILEPATH = os.path.join(BASE_FILEPATH, REQUEST_CITY_ID_JSON)
REQUEST_HEADER_FILEPATH = os.path.join(BASE_FILEPATH, REQUEST_HEADER_JSON)


def load_attr_id_request_json(
        city_id: str, page: int, num_attr: int=30) -> List[Dict]:
    """ Load the JSON request template for requesting a list 
        of attractions from TripAdvisor.
    Args:
        city_id (str): The unique ID of the city or region for 
                which attractions are being requested.
        page (int): The page number of the results to retrieve.
        num_attr (int, optional): The number of attractions to 
                retrieve per page. Defaults to 30.
    Returns:
        List[Dict]: A list of dictionaries representing the JSON request.
    """
    with open(REQUEST_ATTR_ID_FILEPATH, "r") as file:
        request = json.load(file)
    pagee = str(page * num_attr)
    request[0]["variables"]["request"]["routeParameters"]["geoId"] = city_id
    request[0]["variables"]["request"]["routeParameters"]["pagee"] = pagee
    request[0]["variables"]["route"]["params"]["geoId"] = city_id
    request[0]["variables"]["route"]["params"]["pagee"] = pagee
    return request


def load_attr_detail_request_json(attr_id: str) -> List[Dict]:
    """ Loads an attraction detail request JSON from a file and 
        replaces the content ID with the given attribute ID.
    Args:
        attr_id (str): The ID of the attraction to request details for.
    Returns:
        List[Dict]: A list of dictionaries representing the JSON request.
    """
    with open(REQUEST_ATTR_DETAILS_FILEPATH, "r") as file:
        request = json.load(file)
    request[0]["variables"]["request"]["routeParameters"]["contentId"] = attr_id
    return request


def load_city_id_request_json(city: str) -> List[Dict]:
    """ Load the JSON request template for requesting information 
        about a city or region from TripAdvisor.
    Args:
        city (str): The name of the city or region for 
                which information is being requested.
    Returns:
        List[Dict]: A list of dictionaries representing the JSON request.
    """
    with open(REQUEST_CITY_ID_FILEPATH, "r") as file:
        request = json.load(file)
    request[0]["variables"]["request"]["query"] = city
    return request


def load_headers_json() -> Dict:
    """ Load the headers for sending HTTP requests to TripAdvisor's API.
    Returns:
        Dict: A dictionary containing the necessary headers.
    """
    with open(REQUEST_HEADER_FILEPATH, "r") as file:
        headers = json.load(file)
    return headers