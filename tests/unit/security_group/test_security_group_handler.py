import json
import pytest
from mock import patch
from security_group import app
from security_group import sg_utils

# sg-1234567b96583a62c
# vpc-01234567890abcde

@pytest.fixture(scope='module')
def api_event():
    event = {
        'resource': '/security_group/{securityGroupId}',
        'path': '/security_group/sg-01234567890abcde',
        'httpMethod': 'GET',
        'headers': None,
        'multiValueHeaders': None,
        'queryStringParameters': None,
        'multiValueQueryStringParameters': None,
        'pathParameters': {
            'securityGroupId': 'sg-01234567890abcde'
        },
        'stageVariables': None,
        'requestContext': {
            'resourceId': 'tvkm54',
            'resourcePath': '/security_group/{securityGroupId}',
            'operationName': 'getSecurityGroupById',
            'httpMethod': 'GET',
            'extendedRequestId': 'dPDmhGPKIAMFiTg=',
            'path': '/security_group/{securityGroupId}',
            'accountId': '01234567890',
            'stage': 'test-invoke-stage',
            'domainPrefix': 'testPrefix',
            'requestId': 'ec2dd955-ac9e-11e9-a9c9-91ff5e1b6bf3',
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
                'caller': 'AROAJZSOL3QTVYEM7AFNU:vijay@vijaytech.com',
                'sourceIp': 'test-invoke-source-ip',
                'accessKey': 'ASNAQ6GFULM5GKGPH4O5',
                'cognitoAuthenticationProvider': None,
                'user': 'AROAJZSOL3QTVYEM7AFNU:vijay@vijaytech.com'
            },
            'domainName': 'testPrefix.testDomainName',
            'apiId': '9ssxsuk38l'
        },
        'body': None,
        'isBase64Encoded': False
    }

    yield event


@patch('sg_utils.create_client_response')
def test_lambda_handler(sgUtilsMockObject, api_event):

    client_response =  {
                'statusCode': 200,
                'message': 'Successfully fetched security group info',
                'security_group_info': {
                    'name': 'Test Security Group',
                    'description': 'Test Security Group.',
                    'vpc_id': 'vpc-01234567890abcde',
                    'security_group_id': 'sg-01234567890abcde'
                }
             }

    sgUtilsMockObject.return_value = client_response
    client_response = app.lambda_handler(api_event,{})
    assert 200 == client_response['statusCode']
