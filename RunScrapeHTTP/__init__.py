import logging
import pyodbc
from bs4 import BeautifulSoup
import requests
import azure.functions as func
from azure.durable_functions import DurableOrchestrationClient
import azure.durable_functions as df
import os
import typing
import json
import time


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = "RunScrapeHTTP"
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )
