"""fanout.py reads from kinesis analytic output and fans out to SNS and DynamoDB."""
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import pprint
import base64
import json
import os
from datetime import datetime

import boto3

ddb = boto3.resource("dynamodb")
sns = boto3.client("sns")


def handler(event, context):
    payload = event["records"][0]["data"]
    data_dump = base64.b64decode(payload).decode("utf-8")
    data = json.loads(data_dump)
    pprint.pprint(data)

    table = ddb.Table(os.environ["TABLE_NAME"])

    item = data
    item['lastHourSum'] = int(item['lastHourSum'])
    item['lastHourTotal'] = int(item['lastHourTotal'])
    item['lastThreeSum'] = int(item['lastThreeSum'])
    item['lastFiveMinutes'] = int(item['lastFiveMinutes'])
    item['createdAt'] = str(datetime.now())
    item['inspectedAt'] = str(datetime.now())
    item['transactionId'] = item['createdAt']

    # Best effort, Kinesis Analytics Output is "at least once" delivery, meaning this lambda function can be invoked multiple times with the same item
    # We can ensure idempotency with a condition expression
    table.put_item(
        Item=item,
        ConditionExpression="attribute_not_exists(inspectedAt)"
    )
    sns.publish(
        TopicArn=os.environ["TOPIC_ARN"],
        Message=json.dumps(item)
    )

    return {"statusCode": 200, "body": json.dumps(item)}
