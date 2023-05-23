import json

from google.cloud import storage
from google.oauth2.service_account import Credentials
from google.api_core.exceptions import TooManyRequests
from utils import BaseTimeoutDecoratorClass
from typing import Dict, Any

from config import GS_BUCKET, GS_PROJECT_ID, GS_SERVICE_KEY


class RetryOnGcpTimeoutError(BaseTimeoutDecoratorClass):
    """ A decorator for retrying a function when a GCP 
        timeout error (TooManyRequests) occurs.
    """
    def __init__(self, retries, wait):
        super().__init__(retries, wait, TooManyRequests)


class GCP_Client:
    """
    A class for interacting with Google Cloud Storage.

    Attributes:
        client (google.cloud.storage.client.Client): A client object for
            interacting with the Google Cloud Storage API.
        bucket (google.cloud.storage.bucket.Bucket): A bucket object for
            accessing files within a specific bucket.
    """


    def __init__(self) -> None:
        """ Initializes a new instance of the GCP_Client class. """
        creds = Credentials.from_service_account_file(GS_SERVICE_KEY)
        self.client = storage.Client(project=GS_PROJECT_ID, credentials=creds)
        self.bucket = self.client.get_bucket(GS_BUCKET)


    @RetryOnGcpTimeoutError(retries=20, wait=0.2)
    def check_file_exists(self, file_name: str) -> bool:
        """ Checks if a file with the given name exists in the GCP bucket.
        Args:
            file_name (str): The name of the file to check.
        Returns:
            bool: True if the file exists, False otherwise.
        """
        blob = self.bucket.blob(file_name)
        return blob.exists()


    @RetryOnGcpTimeoutError(retries=20, wait=0.2)
    def load_file(self, json_file: str) -> Dict[str, Any]:
        """ Loads a JSON file from the GCP bucket.
        Args:
            json_file (str): The name of the JSON file to load.
        Returns:
            Dict[str, Any]: A dictionary containing the contents of the JSON file.
        """
        blob = self.bucket.blob(json_file)
        file_str = blob.download_as_string()
        return json.loads(file_str)


    @RetryOnGcpTimeoutError(retries=100, wait=0.2)
    def upload_file(
        self, data: Dict[str, Any], file_name: str, overwrite: bool = True) -> None:
        """ Uploads a JSON file to the GCP bucket.
        Args:
            data (Dict[str, Any]): A dictionary containing the 
                    data to be uploaded.
            file_name (str): The name of the file to upload.
            overwrite (bool, optional): If True, overwrite the file 
                    if it already exists. If False and the file already 
                    exists, raise an AssertionError. Defaults to True.
        """
        if not overwrite:
            assert not self.check_file_exists(file_name)
        data = json.dumps(data)
        blob = self.bucket.blob(file_name)
        blob.upload_from_string(
            data, content_type="application/json"
        )
