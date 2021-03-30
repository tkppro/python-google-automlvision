import csv
import io
import os

from google.cloud import vision
from google.protobuf.json_format import MessageToDict

from ..config import *

gsutil = "gs://{}/{}"
public_image_url = "https://storage.googleapis.com/{}/{}"


def detect_labels_uri(uri):
    """Detects labels in the file located in Google Cloud Storage or on the
    Web."""

    client = vision.ImageAnnotatorClient()
    image = vision.Image()
    image.source.image_uri = uri

    response = client.label_detection(image=image)
    labels = response.label_annotations
    result = []

    for label in labels:
        result.append(label.description)

    if response.error.message:
        raise Exception(
            "{}\nFor more info on error messages, check: "
            "https://cloud.google.com/apis/design/errors".format(response.error.message)
        )
    return result


def detect_labels_file(content):
    """Detects labels in the file."""

    # import io

    client = vision.ImageAnnotatorClient()

    # with io.open(path, "rb") as image_file:
    #     content = image_file.read()

    image = vision.Image(content=content)

    response = client.label_detection(image=image)
    labels = response.label_annotations
    results = []

    for label in labels:
        results.append(
            dict(
                description=label.description,
                score=label.score,
                topicality=label.topicality,
            )
        )

    if response.error.message:
        raise Exception(
            "{}\nFor more info on error messages, check: "
            "https://cloud.google.com/apis/design/errors".format(response.error.message)
        )
    return results


def predict(content, is_uploaded=True, blob="", predict_type="ONLINE_PREDICTION"):
    if predict_type == "BATCH_PREDICTION":
        return batch_predict()

    file_download = ""
    # Get the full path of the model.
    model_full_id = automl.AutoMlClient.model_path(PROJECT_ID, "us-central1", MODEL_ID)
    if not is_uploaded:
        file_download = download_file(blob)
        with io.open(file_download, "rb") as image_file:
            content = image_file.read()
    # Read the file.
    image = automl.Image(image_bytes=content)
    payload = automl.ExamplePayload(image=image)

    # params is additional domain-specific parameters.
    # score_threshold is used to filter the result
    # https://cloud.google.com/automl/docs/reference/rpc/google.cloud.automl.v1#predictrequest
    params = {"score_threshold": "0.8"}

    request = automl.PredictRequest(name=model_full_id, payload=payload, params=params)
    response = prediction_client.predict(request=request)
    results = {}
    for result in response.payload:
        results = dict(name=result.display_name, score=result.classification.score)

    # remove file
    if os.path.exists(file_download) and file_download != "":
        os.remove(file_download)
    return results


def generate_batch_test_file():
    bucket = storage_client.get_bucket(BUCKET_NAME)
    blobs = bucket.list_blobs(prefix=TEST_DIR, delimiter="/")
    result = [
        gsutil.format(BUCKET_NAME, blob.name) for blob in blobs if blob.name != TEST_DIR
    ]
    with open("./batch_prediction.csv", mode="w") as csv_file:
        csv_writer = csv.writer(
            csv_file,
            delimiter="\n",
            quotechar="|",
            quoting=csv.QUOTE_MINIMAL,
            lineterminator="\n",
        )
        # for item in result:
        csv_writer.writerow(result)

    upload_blob = bucket.blob(TEST_DIR)
    upload_blob.upload_from_filename("./batch_prediction.csv")


def batch_predict():
    model_full_id = automl.AutoMlClient.model_path(PROJECT_ID, "us-central1", MODEL_ID)
    input_uri = gsutil.format(BUCKET_NAME, "tests/batch_prediction.csv")
    gcs_source = automl.GcsSource(input_uris=[input_uri])

    input_config = automl.BatchPredictInputConfig(gcs_source=gcs_source)
    gcs_destination = automl.GcsDestination(
        output_uri_prefix=gsutil.format(BUCKET_NAME, BATCH_RESULTS_DIR)
    )
    output_config = automl.BatchPredictOutputConfig(gcs_destination=gcs_destination)

    response = prediction_client.batch_predict(
        name=model_full_id, input_config=input_config, output_config=output_config
    )

    print("Waiting for operation to complete...")
    print(
        # f"Batch Prediction results saved to Cloud Storage bucket. {response.result()}"
    )
    return "BATCH PREDICTION is running"


def get_batch_status():
    operation_full_id = (
        "projects/864689882485/locations/us-central1/operations/ICN1108187049397059584"
    )

    r = prediction_client.transport.operations_client.get_operation(
        name=operation_full_id
    )

    response = MessageToDict(r)
    return response


def get_sample_online_predict():
    bucket = storage_client.get_bucket(BUCKET_NAME)
    blobs = bucket.list_blobs(prefix=TEST_DIR, delimiter="/")
    result = [
        dict(url=public_image_url.format(BUCKET_NAME, blob.name), blob_name=blob.name)
        for blob in blobs
        if blob.name != TEST_DIR and not blob.name.endswith(".csv")
    ]

    return result


def download_file(blob_name):
    bucket = storage_client.get_bucket(BUCKET_NAME)
    blob = bucket.blob(blob_name)
    file_download = f"./download/{blob.name.split('/')[1]}"
    blob.download_to_filename(file_download)
    return file_download
