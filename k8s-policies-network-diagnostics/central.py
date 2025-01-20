from typing import Any

from vantage6.algorithm.tools.util import info, warn, error
from vantage6.algorithm.tools.decorators import algorithm_client
from vantage6.algorithm.client import AlgorithmClient


@algorithm_client
def central(
    client: AlgorithmClient, sleep_time:int
) -> Any:

    """ Central part of the algorithm """
    organizations = client.organization.list()
    org_ids = [organization.get("id") for organization in organizations]

    # Define input parameters for a subtask
    info("Defining input parameters")
    input_ = {
        "method": "partial",
        "kwargs": {
            "sleep_time": sleep_time,
        }
    }

    # create a subtask for all organizations in the collaboration.
    info("Creating subtask for all organizations in the collaboration")
    task = client.task.create(
        input_=input_,
        organizations=org_ids,
        name="Network diagnostics",
        description="Network diagnostics"
    )


    # wait for node to return results of the subtask.
    info("Waiting for results")
    results = client.wait_for_results(task_id=task.get("id"))
    info("Results obtained!")


    # return the final results of the algorithm
    return results
