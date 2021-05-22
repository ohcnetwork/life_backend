import json
import logging
import os
from signal import SIGINT, SIGTERM, signal

import boto3
import django
from django.conf import settings

LOGGER = logging.getLogger("Life SQS Worker")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

django.setup()

from life.app.models import LifeData
from django.db.models import F

client_args = {
    "region_name": settings.SQS_AWS_REGION,
    "aws_access_key_id": settings.SQS_AWS_ACCESS_KEY_ID,
    "aws_secret_access_key": settings.SQS_AWS_SECRET_ACCESS_KEY,
}

# Create SQS client
sqs_client = boto3.client("sqs", **client_args)
queue_URL = sqs_client.get_queue_url(QueueName=settings.SQS_QUEUE_NAME,)["QueueUrl"]
LOGGER.info(f"Starting SQS Poller for {queue_URL}")
CHOICES = {"0": "upvotes", "1": "downvotes", "2": "verifiedAndAvailable", "3": "verifiedAndUnavailable"}


def handle(external_id, status):
    try:
        if status not in CHOICES:
            return
        feedback = {status: F(status) + 1}
        LifeData.objects.filter(external_id=external_id).update(**feedback)
    except Exception as e:
        return
    return True


class SignalHandler:
    def __init__(self):
        self.received_signal = False
        signal(SIGINT, self._signal_handler)
        signal(SIGTERM, self._signal_handler)

    def _signal_handler(self, signal, frame):
        LOGGER.info(
            f"handling signal {signal}, exiting gracefully. Please Wait until all pending messages are processed"
        )
        self.received_signal = True


def recieve_sqs_message(sqs):
    return sqs.receive_message(
        QueueUrl=queue_URL,
        MessageAttributeNames=["All"],
        MaxNumberOfMessages=10,
        VisibilityTimeout=39600,  # 11 Hours
        # WaitTimeSeconds=0,
    )


def sqs_check_new_log_messages():

    # Receive message from SQS queue
    response = recieve_sqs_message(sqs_client)

    while len(response.get("Messages", [])) != 0:

        if "Messages" in response:

            messages = response["Messages"]
            for message in messages:
                receipt_handle = message["ReceiptHandle"]
                run = False
                try:
                    external_id = message["MessageAttributes"]["ExternalID"]["StringValue"]
                    feedback = message["MessageAttributes"]["Feedback"]["StringValue"]
                    handle(external_id, feedback)
                    LOGGER.info(f"Processed {feedback} for {external_id}")
                except Exception as e:
                    LOGGER.error(
                        f"Exception when handling message with external_id {external_id} for event {feedback}"
                    )
                    run = True

                if run:
                    sqs_client.delete_message(QueueUrl=queue_URL, ReceiptHandle=receipt_handle)

        response = recieve_sqs_message(sqs_client)


signal_handler = SignalHandler()
LOGGER.info("Starting to Listen for new log file SQS Events")
while not signal_handler.received_signal:
    sqs_check_new_log_messages()
LOGGER.info("Stopped Listening for new log file SQS Events")
