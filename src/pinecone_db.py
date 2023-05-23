import uuid
import pinecone

from typing import List, Dict, Any
from utils import batch_data

from config import (
    PINECONE_ENV, PINECONE_INDEX, PINECONE_KEY, PINECONE_UPSERT_BATCH
)

def pinecone_upsert_data(
        pinecone_data: List[Dict[str, Any]], namespace: str) -> None:
    """ Upserts data to a Pinecone index in batches.
    Args:
        pinecone_data (List[Dict[str, Any]]): The data to be upserted, 
            where each element is a dictionary representing a vector.
        namespace (str): The namespace of the Pinecone index.
    """
    pinecone.init(api_key=PINECONE_KEY, environment=PINECONE_ENV)
    pinecone_index = pinecone.Index(PINECONE_INDEX)
    for pinecone_batch in batch_data(pinecone_data, PINECONE_UPSERT_BATCH):
        pinecone_index.upsert(pinecone_batch, namespace=namespace)
    

def create_pinecone_data(
        metadata_list: List[Dict[str, Any]], 
        embedding_list: Dict[str, Any]) -> List[Dict[str, Any]]:
    """ Creates Pinecone data from metadata and embeddings.
    Args:
        metadata_list (List[Dict[str, Any]]): A list of dictionaries 
            containing metadata for each vector.
        embedding_list (Dict[str, Any]): A dictionary containing embeddings.
    Returns:
        pinecone_data (List[Dict[str, Any]]): A list of dictionaries 
            representing Pinecone data, where each dictionary contains 
            an id, metadata, and values key-value pair.
    """
    pinecone_data = []
    for idx, metadata in enumerate(metadata_list):
        attr_id = uuid.uuid4().hex
        metadata["id"] = attr_id
        pinecone_data.append({
            "id": attr_id,
            "metadata": metadata,
            "values": embedding_list[idx]["embedding"]
        })
    return pinecone_data