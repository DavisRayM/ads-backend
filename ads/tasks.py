from flask import current_app
import tensorflow as tf

from celery import shared_task
from ads.db import Prediction


@shared_task
def process_prediction(prediction_id: int):
    """
    Asynchronous task to run prediction model on a Prediction
    """
    prediction = Prediction.get(prediction_id)
    model = tf.saved_model.load(current_app.config["MODEL_DIRECTORY"])
    import ipdb

    ipdb.set_trace()
