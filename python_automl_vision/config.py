import json

import google.auth
from starlette.config import Config
from google.cloud import storage
from google.oauth2 import service_account
from google.cloud import automl

config = Config(".env")

PROJECT_ID = config("PROJECT_ID")
MODEL_ID = config("MODEL_ID")
BUCKET_NAME = config("BUCKET_NAME")
TEST_DIR = config("TEST_DIR")
BATCH_RESULTS_DIR = config("BATCH_RESULTS_DIR")

AUTOML_ENV = config("AUTOML_ENV")
if AUTOML_ENV != "local":
    credentials, project = google.auth.default()
    storage_client = storage.Client(credentials=credentials)
    prediction_client = automl.PredictionServiceClient(credentials=credentials)

else:
    service_account_info = json.load(open(config("SERVICE_ACCOUNT_DIR")))
    credentials = service_account.Credentials.from_service_account_info(
        service_account_info
    )
    storage_client = storage.Client(credentials=credentials)
    prediction_client = automl.PredictionServiceClient(credentials=credentials)
