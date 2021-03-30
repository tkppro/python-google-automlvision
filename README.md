# python-google-automlvision

#Requirements:
`python 3.8.*`

#How to run?
``
poetry install
``

``
uvicorn main:app --reload --host 0.0.0.0
``


#Build
``
docker build . -t automl-vision
``

``
gcloud builds submit --tag gcr.io/sproject-3697d/automl-vision
``