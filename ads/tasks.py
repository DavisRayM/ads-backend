import os
from flask import current_app

from celery import shared_task
from ads.db import Prediction

import tensorflow as tf
from keras.models import load_model
import numpy as np


def preprocess_image(file_path):
    img = tf.io.read_file(file_path)
    img = tf.image.decode_jpeg(img, channels=3)
    img = tf.image.resize(img, [256, 256])  # Resize the image to 256x256
    img = img / 255.0  # Normalize the image
    return img


def predict_image(image_path):
    model = load_model(current_app.config["MODEL_DIRECTORY"])
    img = preprocess_image(image_path)
    img = np.expand_dims(img, axis=0)
    prediction = model.predict(img)
    predicted_class = np.argmax(prediction, axis=1)
    if predicted_class == 0:
        return "gliona"
    elif predicted_class == 1:
        return "meningioma"
    elif predicted_class == 2:
        return "notumor"
    elif predicted_class == 3:
        return "pituitary"
    else:
        return "error"


@shared_task
def process_prediction(prediction_id: int):
    """
    Asynchronous task to run prediction model on a Prediction
    """
    prediction_request = Prediction.get(prediction_id)
    if prediction_request:
        prediction_request.status = "In Progress"
        prediction_request._save()
        result = predict_image(prediction_request.file_path)
        prediction_request.result = result
        prediction_request.status = "Complete"
        os.remove(prediction_request.file_path)
        prediction_request.file_path = ""
        prediction_request._save()
