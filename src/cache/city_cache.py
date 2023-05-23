import os
import sys
import json

from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from config import CACHE_FILENAME, BASE_FILEPATH
CACHE_FILEPATH = os.path.join(BASE_FILEPATH, CACHE_FILENAME)


class CityCache:
    """ A class for iterating over a cache of city information.

    Attributes:
        cache (List[Dict[str, Any]]): A list of dictionaries containing 
            city information. Each dictionary should have "name", "type", 
            and "processed" keys.
        num_processed (int): The number of cities that have been 
            processed so far.
    """

    def __init__(self, cities_per_job):
        """ Initializes a new instance of the CityCache class. 
        Args:
            cities_per_job (int): The number of cities to process 
                per airflow job
        """
        self.cities_per_job = cities_per_job
        with open(CACHE_FILEPATH, "r") as file:
            self.cache = json.load(file)
        self.num_processed = 0
    

    def __iter__(self):
        """ Iterates over a set number of cities in the cache that 
            have not been processed. Update 'processed' field once 
            city attractions have been scraped. Mark as 'success' if 
            no errors raised and stored in pinecone
        Yields:
            Tuple[str, str]: A tuple containing the name and type of a city.
        """
        for idx, city_info in enumerate(self.cache):
            processed = city_info["processed"]
            if not processed:
                self.cache[idx]["processed"] = True
                self.cache[idx]["success"] = False
                self.update_cache()
                yield city_info
                self.cache[idx]["success"] = True
                self.update_cache()
                self.num_processed += 1
                if self.num_processed == self.cities_per_job :
                    return


    def cache_complete(self) -> bool:
        """ Checks if all cities in the cache have been processed.
        Returns:
            bool: True if all cities have been processed, False otherwise.
        """
        for info in self.cache:
            if not info["processed"]:
                return False
        return True


    def update_cache(self) -> None:
        """ Writes the current state of the cache to a file. """
        with open(CACHE_FILENAME, "w") as file:
            json.dump(self.cache, file, indent=4)
            
