import openai

from typing import List, Dict, Any
from utils import batch_data, BaseTimeoutDecoratorClass
from openai.error import APIError, Timeout

from config import OPENAI_EMBEDDING_BATCH, OPENAI_KEY, OPENAI_MODEL


def get_text_embeddings(data: List[str]) -> Dict[str, Any]:
    """ Generates text embeddings for a list of input texts using 
        the OpenAI API. It creates an input prompt for each input 
        text and submits the prompt to the API to generate an embedding. 
    Args:
        data (List[Dict[str, Any]]): List of dictionaries containing 
            metadata of data attributes.
    Returns:
        List[Dict[str, Any]]: A List of text embedding dictionaries
    """
    embeddings = []
    prompts = construct_text_embedding_prompt(data)
    for prompt_batch in batch_data(prompts, OPENAI_EMBEDDING_BATCH):
        embeddings += embedding_api(prompt_batch)
    return embeddings


def construct_text_embedding_prompt(data: List[Dict[str, Any]]) -> List[str]:
    """ Takes a list of dictionaries containing metadata of
        data attributes and constructs a list of prompts by 
        concatenating the name, type, description, and tags of each attribute.
    Args:
        data (List[Dict[str, Any]]): List of dictionaries containing 
            metadata of data attributes.
    Returns:
        prompts (List[str]): List of prompts constructed by concatenating 
            the name, type, description, and tags of each attribute.
    """
    prompts = []
    for attr in data:
        prompts.append(" ".join([
            attr["name"],
            attr["type"],
            attr["description"],
            ", ".join(attr["tags"])
        ]))
    return prompts


class RetryOnOpenAI_ApiError(BaseTimeoutDecoratorClass):
    """ A decorator for retrying a function when a OpenAI 
        API error (APIError or Timeout) occurs.
    """
    def __init__(self, retries, wait):
        super().__init__(retries, wait, (APIError, Timeout))
    

@RetryOnOpenAI_ApiError(retries=10, wait=1)
def embedding_api(embedding_prompts):
    """ """
    openai.api_key = OPENAI_KEY
    response = openai.Embedding.create(
        input=embedding_prompts,
        model=OPENAI_MODEL
    )
    return response["data"]