import os
import sys
from typing import Any
from loguru import logger
from utils.env import get_env_project_id, check_application_credentials, check_compute_engine_service_account_email, check_storage_service_account_email, check_service_account_oauth_token
from shared.entities.gcp_project import GCPProject
from google.api_core.extended_operation import ExtendedOperation

# Check parameters
def check_gcp_params(args):
    # check project id 
    if args.project_id is None:
        logger.info("Project ID not provided in command line arguments")
        logger.info("Checking environment variables")
        try:
            args.project_id = get_env_project_id()
        except Exception as e:
            logger.error(e)
            exit(1)
    # check compute service account 
    try:
        check_compute_engine_service_account_email()
    except Exception as e:
        logger.error(e)
        exit(1)

    # check storage service account
    try:
        check_storage_service_account_email()
    except Exception as e:
        logger.error(e)
        exit(1)

    # check authentication 
    if args.authentication_type == "service-account":
        logger.info("Authentication type set to use service account")
        logger.info("Checking environment variable")
        try:
            check_application_credentials()
            return GCPProject(args.project_id, auth_type="service-account")
        except Exception as e:
            logger.error(e)
            exit(1)
    elif args.authentication_type == "oauth":
        logger.info("Authentication type set to use oauth")
        logger.info("Checking environment variable")
        try:
            check_service_account_oauth_token()
            return GCPProject(args.project_id, auth_type="oauth", service_token=os.environ.get("SERVICE_ACCOUNT_OAUTH_TOKEN"))
        except Exception as e:
            logger.error(e)
            exit(1)

def wait_for_extended_operation(
    operation: ExtendedOperation, verbose_name: str = "operation", timeout: int = 1000
) -> Any:
    """
    This method will wait for the extended (long-running) operation to
    complete. If the operation is successful, it will return its result.
    If the operation ends with an error, an exception will be raised.
    If there were any warnings during the execution of the operation
    they will be printed to sys.stderr.
    Args:
        operation: a long-running operation you want to wait on.
        verbose_name: (optional) a more verbose name of the operation,
            used only during error and warning reporting.
        timeout: how long (in seconds) to wait for operation to finish.
            If None, wait indefinitely.
    Returns:
        Whatever the operation.result() returns.
    Raises:
        This method will raise the exception received from `operation.exception()`
        or RuntimeError if there is no exception set, but there is an `error_code`
        set for the `operation`.
        In case of an operation taking longer than `timeout` seconds to complete,
        a `concurrent.futures.TimeoutError` will be raised.
    """

    result = operation.result(timeout=timeout)

    if operation.error_code:
        logger.error(
            f"Error during {verbose_name} {operation.name}: {operation.error_message}"
        )
        logger.error(f"Operation ID: {operation.name}")
        raise operation.exception() or RuntimeError(operation.error_message)

    if operation.warnings:
        logger.warning(f"Warnings during {verbose_name} {operation.name}:")
        for warning in operation.warnings:
            logger.warning(f" - {warning.code}: {warning.message}")

    return result


def wait_for_operation(compute, project, zone, operation):
    print("Waiting for operation to finish...")
    while True:
        result = (
            compute.zoneOperations()
            .get(project=project, zone=zone, operation=operation)
            .execute()
        )

        if result["status"] == "DONE":
            print("done.")
            if "error" in result:
                raise Exception(result["error"])
            return result

        time.sleep(1)


def wait_for_operation_global(compute, project, operation):
    print("Waiting for operation to finish...")
    while True:
        result = (
            compute.globalOperations()
            .get(project=project, operation=operation)
            .execute()
        )

        if result["status"] == "DONE":
            print("done.")
            if "error" in result:
                raise Exception(result["error"])
            return result
