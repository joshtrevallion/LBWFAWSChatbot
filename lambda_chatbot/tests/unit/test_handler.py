import json
import pytest
from lambda_chatbot import app


@pytest.fixture()
def intent_QOne_noDanger():
    """ Generates API GW Event"""

    return {
        "messageVersion": "1.0",
        "invocationSource": "FulfillmentCodeHook",
        "userId": "tsheq4tgk74stuo0m9ih4e32ulmgj2ro",
        "sessionAttributes": {
        },
        "requestAttributes": "None",
        "bot": {
            "name": "LBWFBot",
            "alias": "$LATEST",
            "version": "$LATEST"
        },
        "outputDialogMode": "Text",
        "currentIntent": {
            "name": "ASBReport",
            "slots": {
                "ImmediateDanger": "Yes"
            },
            "slotDetails": {
                "ImmediateDanger": {
                    "resolutions": [
                        {
                            "value": "Yes"
                        }
                    ],
                    "originalValue": "yes"
                }
            },
            "confirmationStatus": "None",
            "sourceLexNLUIntentInterpretation": "None"
        },
        "inputTranscript": "no"
    }


def test_lambda_handler(intent_QOne_noDanger, mocker):

    ret = app.lambda_handler(intent_QOne_noDanger, "")
    data = json.loads(ret["body"])

    assert ret["statusCode"] == 200
    assert "message" in ret["body"]
    assert data["message"] == "hello world"
