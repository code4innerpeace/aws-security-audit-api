import json
import ebs_utils

def lambda_handler(event, context):

    client_response = ebs_utils.create_client_response(event)
    # print("Client Response : {}".format(client_response))
    return {
        "statusCode": client_response['statusCode'],
        "body": json.dumps(client_response),
    }
