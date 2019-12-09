import os
import sys
import logging
import calendar
from datetime import datetime

sys.path.append("/opt")

import boto3  # noqa
import requests  # noqa

# from aws_xray_sdk.core import patch_all  # noqa

# patch_all()

logger = logging.getLogger(__name__)
logger.setLevel(os.environ['LOGGING'])


dynamodb = boto3.resource('dynamodb')
dynamodb_table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])


def check_postcode(postcode):
    r = requests.get(str.format(
        'https://api.getAddress.io/find/{}?expand=true&api-key={}',
        postcode,
        os.environ['GETADDRESS_APIKEY']
    ))

    logger.debug(str.format('r.status_code {}', r.status_code))

    if r.status_code == 200:
        logger.debug(str.format('r.url {}', r.url))
        logger.debug(str.format('r.json {}', r.json()))

        # TODO Need to check that the addresses[n]['district'] is
        # a value we want
        # validDistricts = ["Waltham Forest"]
        # if addresses[0]['district'] in validDistricts:

        return r.json()

    else:
        # TODO Need to deal with this in a nicer way
        logger.error(str.format(
            'Error with getaddress API: {}', r.status_code))
        return None


def store_session(slots, session={}):

    # if session is empty it's new.
    if 'reference' not in session:
        # Already exists so we update
        session['reference'] = '324234234'
        session['timestamp'] = datetime.now().isoformat()

    for k, v in list(slots.items()):
        session[k] = v

    # Store the session info to DynamoDB
    response = dynamodb_table.put_item(
        Item=session,
    )

    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        logger.debug('Entry updated')
    else:
        logger.debug('Error')

    logger.debug(str.format('response {}', response['ResponseMetadata']))

    return session


def create_buttons(buttons):

    buttons_list = []
    for b in buttons:
        buttons_list.append({
            "text": b,
            "value": b.lower()
        })

    return buttons_list


def lambda_handler(event, context):
    """
    Lambda handler / entry point
    """

    logger.debug(str.format('event {}', event))

    if event['currentIntent']['name'] == 'QOne':
        # Check if the user is danger
        if event['currentIntent']['slots']['immediateDanger'].lower() == 'yes':
            dialogAction = {
                "type": "Close",
                "fulfillmentState": "Fulfilled",
                "message": {
                    "contentType": "PlainText",
                    "content": "If someone is at risk of danger or harm, this sounds like an emergency.  Please dial 999.!"  # noqa
                }
            }
        else:
            buttons = ['Yes', 'No']
            dialogAction = {
                "type": "ElicitSlot",
                "message": {
                    "contentType": "PlainText",
                    "content": "Did the incident happen in the last six months?"  # noqa
                },
                "intentName": "QTwo",
                "slots": {
                    "sixMonths": "null"
                },
                "slotToElicit": "sixMonths",
                "responseCard": {
                    "version": 1,
                    "contentType": "application/vnd.amazonaws.card.generic",
                    "genericAttachments": [
                        {
                            "buttons": create_buttons(buttons)
                        }
                    ]
                }
            }

    elif event['currentIntent']['name'] == 'QTwo':
        if event['currentIntent']['slots']['sixMonths'].lower() == 'no':
            dialogAction = {
                "type": "Close",
                "fulfillmentState": "Fulfilled",
                "message": {
                    "contentType": "PlainText",
                    "content": "Unfortunately we are unable to process issues older than six months."  # noqa
                }
            }
        else:
            buttons = ["Street based", "Property based"]
            dialogAction = {
                "type": "ElicitSlot",
                "message":  {
                    "contentType": "PlainText",
                    "content": "Okay, lets process your report.  What type of incident occurred?"  # noqa
                },
                "intentName": "QThree",
                "slots": {
                    "incidentType": "null"
                },
                "slotToElicit": "incidentType",
                "responseCard": {
                    "version": 1,
                    "contentType": "application/vnd.amazonaws.card.generic",
                    "genericAttachments": [
                        {
                            "buttons": create_buttons(buttons)
                        }
                    ]
                }
            }

    elif event['currentIntent']['name'] == 'QThree':
        if event['currentIntent']['slots']['incidentType'].lower() == 'street based':  # noqa
            buttons = [
                'Street Drinking', 'Aggressive Begging',
                'Congregation and loitering', 'Drugs']
        else:
            buttons = ['Drugs', 'Nusiance neighbours']

        dialogAction = {
            "type": "ElicitSlot",
            "message":  {
                "contentType": "PlainText",
                "content": "And in a bit more detail?"
            },
            "intentName": "QFour",
            "slots": {
                "incidentTypeDetail": "null"
            },
            "slotToElicit": "incidentTypeDetail",
            "responseCard": {
                "version": 1,
                "contentType": "application/vnd.amazonaws.card.generic",
                "genericAttachments": [
                    {
                        "buttons": create_buttons(buttons)
                    }
                ]
            }
        }

    elif event['currentIntent']['name'] == 'QFour':

        buttons = []
        for i in range(10, 15):
            buttons.append(calendar.month_name[i])

        dialogAction = {
            "type": "ElicitSlot",
            "message":  {
                "contentType": "PlainText",
                "content": "Which month did this happen in?"
            },
            "intentName": "QFive",
            "slots": {
                "incidentTypeMonth": "null",
                "incidentTypeDate": "null"
            },
            "slotToElicit": "incidentTypeMonth",
            "responseCard": {
                "version": 1,
                "contentType": "application/vnd.amazonaws.card.generic",
                "genericAttachments": [
                    {
                        "buttons": create_buttons(buttons)
                    }
                ]
            }
        }

    # elif event['currentIntent']['name'] == 'QFive':

    # elif event['currentIntent']['name'] == 'QSix':

    #     addressData = check_postcode(
    #         event['currentIntent']['slots']['reportedLocation'])
    #     if addressData is not None:

    #         logger.debug(str.format(
    #             'addressData count {}', len(addressData['addresses'])))

    #         message = str.format(
    #             "Addresses found: {} for: {}",
    #             len(addressData['addresses']),
    #             event['currentIntent']['slots']['reportedLocation'])
    #     else:
    #         message = str.format(
    #             "Problem getting postcode data for: {}",
    #             event['currentIntent']['slots']['reportedLocation'])

    #     dialogAction = {
    #         "type": "ElicitSlot",
    #         "message": {
    #             "contentType": "PlainText",
    #             "content": "Please can you provide your address?"
    #         },
    #         "intentName": "ASBResidentLocation",
    #         "slots": {
    #             "residentLocation": "null"
    #         },
    #         "slotToElicit": "residentLocation"
    #     }

    else:
        # End it
        dialogAction = {
            "type": "Close",
            "fulfillmentState": "Fulfilled",
            "message": {
                "contentType": "PlainText",
                "content": "Thank you"
            }
        }

    resultMap = {
        "sessionAttributes": store_session(event['currentIntent']['slots'], event['sessionAttributes'])  # noqa
        ,
        "dialogAction": dialogAction
    }

    logger.debug(str.format('resultMap {}', resultMap))

    return resultMap
