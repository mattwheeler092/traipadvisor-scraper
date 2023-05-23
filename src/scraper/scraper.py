import json
import aiohttp
import asyncio
import base64
import math
import sys
import requests
import logging

from typing import List, Dict, Optional, Tuple
from tenacity import retry, stop_after_attempt, wait_fixed
from functools import reduce
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from config import (
    MIN_DISTANCE, 
    TRIPADVISOR_API_URL,
    DEFAULT_RATING,
    DEFAULT_REVIEW_COUNT
)

from .utils.request import (
    load_attr_id_request_json,
    load_attr_detail_request_json,
    load_city_id_request_json,
    load_headers_json
)

from .utils.response import (
    parse_attr_ids_response,
    parse_activity_duration,
    parse_business_description,
    parse_business_hours,
    parse_business_tags,
    parse_business_website,
    compute_distance
)

class TripAdvisorScraper:
    """ A scraper for extracting information about attractions 
        in a city from TripAdvisor.
    """

    def __init__(self, city_info: Dict, max_attr: Optional[int] = None):
        """ Initialize a new instance of the TripAdvisorScraper class.
        Args:
            city_info (Dict): A dictionary containing information 
                    about the city.
            max_attr (Optional[int], optional): The maximum number of 
                    attractions to fetch. Defaults to None.
        """
        self.city = city_info["city"]
        self.state = "" if city_info["state"] is None else city_info["state"]
        self.country = city_info["country"]
        self.lat = city_info["lat"]
        self.lng = city_info["lng"]

        self.headers = load_headers_json()
        self.city_id = self.get_city_id()

        self.max_attr = self.get_max_attr()
        if max_attr is not None:
            self.max_attr = min(self.max_attr, max_attr)

        self.max_pages = math.ceil(self.max_attr / 30)
        self.attr_ids = None


    def get_city_id(self) -> Optional[int]:
        """
        Get the TripAdvisor ID for the city.

        Returns:
            Optional[int]: The TripAdvisor ID for the city, or None if not found.
        """
        city_request = ', '.join([self.city, self.country])
        request = load_city_id_request_json(city_request)
        response = self.get_sync_request(request)
        for item in response[0]['data']['Typeahead_autocomplete']['results']:
            if item["__typename"] == "Typeahead_LocationItem":
                try:
                    item_lat = item["details"]["latitude"]
                    item_lng = item["details"]["longitude"]
                    dist = compute_distance(
                        self.lat, self.lng, item_lat, item_lng
                    )
                    if dist < MIN_DISTANCE:
                        return item["locationId"]
                except KeyError:
                    continue
        msg = f"No city_id found for {self.city}"
        logging.log(logging.WARNING, msg)


    def get_max_attr(self) -> int:
        """ Get the maximum number of attractions to fetch.
        Returns:
            int: The maximum number of attractions to fetch.
        """
        if self.city_id is None:
            return
        request = load_attr_id_request_json(self.city_id, 0)
        response = self.get_sync_request(request)
        for item in response[0]['data']['Result'][0]['sections'][::-1]:
            if item["__typename"] == 'WebPresentation_PaginationLinksList':
                return item.get("totalResults", 30)
            

    async def get_attr_details(self) -> List[Dict]:
        """ Get the details for the attractions.
        Returns:
            List[Dict]: A list of dictionaries containing the details 
                    for the attractions. 
        """
        tasks = []
        await self.get_attr_ids()
        async with aiohttp.ClientSession(headers=self.headers) as session:
            for attr_id in self.attr_ids[:self.max_attr]:
                request = load_attr_detail_request_json(attr_id["id"])
                tasks.append(self.get_async_request(session, request))
            data = await asyncio.gather(*tasks)
        data = self.format_attr_details(data)
        return data
    

    async def get_attr_ids(self) -> None:
        """ Asynchronously fetch and store the attraction IDs 
            in self.attr_ids. 
        """
        if self.attr_ids is None:
            tasks = []
            async with aiohttp.ClientSession(headers=self.headers) as session:
                for page in range(self.max_pages):
                    request = load_attr_id_request_json(self.city_id, page)
                    tasks.append(self.get_async_request(session, request))
                data = await asyncio.gather(*tasks)
            self.attr_ids = reduce(lambda x, y: x + y, [
                parse_attr_ids_response(item) for item in data
            ])
    

    def format_attr_details(self, data: List[Dict]) -> List[Dict]:
        """ Format the attraction details.
        Args:
            data (List[Dict]): The raw attraction details.
        Returns:
            List[Dict]: The formatted attraction details.
        """
        details = []
        for idx, item in enumerate(data):
            try:
                details.append({
                    "tripadvisor_id": self.attr_ids[idx]["id"],
                    "name": self.attr_ids[idx]["name"],
                    **self.parse_attr_details_response(item)
                })
            except:
                continue
        return details        
    

    def extract_lat_lng(self, data: List[Dict]) -> Tuple[float, float]:
        """ Extract latitude and longitude from the given data.
        Args:
            data (List[Dict]): The data containing latitude and 
                    longitude information.
        Returns:
            Tuple[float, float]: The latitude and longitude.
        """
        try:
            info = data[0]["data"]["Result"][0]["detailSectionGroups"]\
                       [3]["staticMap"]["center"]
            return info["latitude"], info["longitude"]
        except:
            return self.lat, self.lng
        

    def parse_attr_details_response(self, data: Dict) -> Dict:
        """ Parse the attraction details response.
        Args:
            data (Dict): The raw attraction details.
        Returns:
            Dict: The parsed attraction details.
        """
        general = json.loads(data[0]["data"]["Result"][0]["container"]["jsonLd"])
        latitude, longitude = self.extract_lat_lng(data)
        result = {
            "type": general.get("@type", ""),
            "address": general.get("address", {}).get("streetAddress", ""),
            "city": self.city,
            "state": self.state,
            "country": self.country,
            "zip_code": general.get("address", {}).get("postalCode", ""),
            "rating": general.get("aggregateRating", {}) \
                            .get("ratingValue", DEFAULT_RATING),
            "review_count": general.get("aggregateRating", {}) \
                            .get("reviewCount", DEFAULT_REVIEW_COUNT),
            "image_url": general.get("image", ""),
            "latitude": latitude,
            "longitude": longitude,
            "description": parse_business_description(data),
            "activity_duration": parse_activity_duration(data),
            "website": parse_business_website(data),
            "tags": parse_business_tags(data),
            "hours": parse_business_hours(data)
        }
        if result["rating"] is not None:
            result["rating"] = float(result["rating"])

        if result["review_count"] is not None:
            result["review_count"] = int(result["review_count"])

        return result


    @retry(stop=stop_after_attempt(5), wait=wait_fixed(2))
    async def get_async_request(
        self, session: aiohttp.ClientSession, request: Dict) -> Dict:
        """ Asynchronously send an HTTP request.
        Args:
            session (aiohttp.ClientSession): The aiohttp ClientSession 
                    to use for the request. request (Dict): The request data.
        Returns:
            Dict: The JSON response from the request.
        """
        async_session = session.post(
            TRIPADVISOR_API_URL, headers=self.headers, json=request
        )
        async with async_session as response:
            return await response.json()


    @retry(stop=stop_after_attempt(5), wait=wait_fixed(2))
    def get_sync_request(self, request: Dict) -> Dict:
        """ Synchronously send an HTTP request.
        Args:
            request (Dict): The request data.
        Returns:
            Dict: The JSON response from the request.
        """
        response = requests.post(
            TRIPADVISOR_API_URL, headers=self.headers, json=request
        )
        return response.json()