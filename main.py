import uvicorn
from fastapi import FastAPI, File, APIRouter, HTTPException, Body
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from python_automl_vision.services.services import (
    detect_labels_uri,
    detect_labels_file,
    predict,
    batch_predict,
    get_batch_status,
    get_sample_online_predict,
)

app = FastAPI(
    middleware=[
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        )
    ]
)

api = APIRouter()

#
# @api.post("/detect-uri")
# async def detect_image_url(uri: str):
#     results = detect_labels_uri(uri)
#     return results
#
#
# @api.post("/detect-file")
# async def detect_image_file(file: bytes = File(...)):
#     results = detect_labels_file(file)
#     return results


@api.post("/predict")
async def predict_image_file(
    file: bytes = File(None),
    is_uploaded: bool = Body(True),
    blob: str = Body(None),
    predict_type: str = Body("ONLINE_PREDICTION"),
):
    if not file and is_uploaded:
        raise HTTPException(status_code=400, detail="File must not be empty!")
    results = predict(file, is_uploaded, blob, predict_type)
    return results


@api.post("/batch-predict")
async def batch_predict_image():
    results = batch_predict()
    return results


@api.get("/batch/status")
async def batch_status():
    results = get_batch_status()
    return results


@api.get("/predict/sample")
async def sample_online_predict():
    results = get_sample_online_predict()
    return results


if __name__ == "__main__":
    app.include_router(api, prefix="/api")
    uvicorn.run(app, host="0.0.0.0", port=8003)
