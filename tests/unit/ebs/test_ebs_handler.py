import json
import pytest
from mock import patch
from ebs import app
from ebs import ebs_utils


# sg-1234567b96583a62c
# vpc-01234567890abcde

@pytest.fixture(scope='module')
def api_event():
    event = {
            'resource': '/ebs/{ebsVolumeId}',
            'path': '/ebs/vol-123456e6f62ccf1bd',
            'httpMethod': 'GET',
            'headers': None,
            'multiValueHeaders': None,
            'queryStringParameters': None,
            'multiValueQueryStringParameters': None,
            'pathParameters': {
                'ebsVolumeId': 'vol-123456e6f62ccf1bd'
            },
            'stageVariables': None,
            'requestContext': {
                'resourceId': 'tvkm54',
                'resourcePath': '/ebs/{ebsVolumeId}',
                'operationName': 'getEBSVolumeById',
                'httpMethod': 'GET',
                'extendedRequestId': 'dPDmhGPKIAMFiTg=',
                'path': '/ebs/{ebsVolumeId}',
                'accountId': '01234567890',
                'stage': 'test-invoke-stage',
                'domainPrefix': 'testPrefix',
                'requestId': 'ec2dd955-ac9e-12e9-a9c9-91ff5e1b6bf3',
                'identity': {
                    'cognitoIdentityPoolId': None,
                    'cognitoIdentityId': None,
                    'apiKey': 'test-invoke-api-key',
                    'principalOrgId': None,
                    'cognitoAuthenticationType': None,
                    'userArn': 'arn:aws:sts::01234567890:assumed-role/VijayTest/vijay@vijaytech.com',
                    'apiKeyId': 'test-invoke-api-key-id',
                    'userAgent': 'aws-internal/3 aws-sdk-java/1.11.563',
                    'accountId': '01234567890',
                    'caller': 'AROBJKSOK3QTVYEM7AFNU:vijay@vijaytech.com',
                    'sourceIp': 'test-invoke-source-ip',
                    'accessKey': 'ASIAQ6IGULM5GKGPH4O5',
                    'cognitoAuthenticationProvider': None,
                    'user': 'AROAJZTOK3QTVYEM7AFNU:vijay@vijaytech.com'
                },
                'domainName': 'testPrefix.testDomainName',
                'apiId': '9ssxsuk38l'
            },
            'body': None,
            'isBase64Encoded': False
        }
    yield event


@patch('ebs_utils.create_client_response')
def test_lambda_handler(ebsUtilsMockObject, api_event):
    client_response = {
        'statusCode': 200,
        'message': 'Successfully fetched ebs volume info',
        'ebs_volume_info': {
            'volumeId': 'vpc-01234567890abcde',
            'encryptionStatus': 'false'
        }
    }

    ebsUtilsMockObject.return_value = client_response
    client_response = app.lambda_handler(api_event, {})
    assert 200 == client_response['statusCode']
