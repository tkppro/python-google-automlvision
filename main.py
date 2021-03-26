import uvicorn
from fastapi import FastAPI, File, UploadFile

from python_automl_vision.services.services import (
    detect_labels_uri,
    detect_labels_file,
    predict,
)

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/detect-uri")
async def detect_image_url(uri: str):
    results = detect_labels_uri(uri)
    return results


@app.post("/detect-file")
async def detect_image_file(file: bytes = File(...)):
    results = detect_labels_file(file)
    return results


@app.post("/predict")
async def predict_image_file(file: bytes = File(...)):
    results = predict(file)
    return results


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)
