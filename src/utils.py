import time

from airflow.api.client.local_client import Client
from typing import Any, Callable, Iterable
    

class BaseTimeoutDecoratorClass:
    """ A base class for implementing retry-on-timeout decorators.

    Attributes:
        retries (int): The number of times to retry the function 
                       before raising an exception.
        wait (float): The number of seconds to wait between retries.
        error (Exception): The type of exception to catch and retry on.
    """
    def __init__(self, retries: int, wait: float, error: Exception):
        self.retries = retries
        self.wait = wait
        self.error = error

    def __call__(self, func: Callable) -> Callable:
        def wrapped(*args, **kwargs):
            for i in range(self.retries + 1):
                try:
                    result = func(*args, **kwargs)
                    return result
                except self.error as err:
                    time.sleep(self.wait)
                    if i == self.retries:
                        raise err
        return wrapped


def batch_data(data: Iterable[Any], n: int) -> Iterable[Any]:
    """ Splits an iterable into batches of a specified size.
    Args:
        data (Iterable[Any]): The iterable to be batched.
        n (int): The batch size.
    Yields:
        Iterable[Any]: An iterator that yields batches of size 
            n from the input iterable.
    """
    for idx in range(0, len(data), n):
        yield data[idx : idx + n]


def kill_airflow_job(dag_id: str) -> None:
    """ Permanently kill the pipelines airflow job.
    Args:
        dag_id (str): The ID of the DAG to kill the job for.
    """
    client = Client(None, None)
    for dag_run in client.get_dag_runs(dag_id):
        if dag_run.state == 'running':
            client.trigger_dag(
                dag_id=dag_id, 
                run_id=dag_run.run_id, 
                conf={'kill_signal': 'SIGINT'}
            )
