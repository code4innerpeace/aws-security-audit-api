import pytest
import boto3
import botocore.session
from mock import patch
from botocore.exceptions import ClientError
from botocore.stub import Stubber
from security_group import sg_utils

pytest.describe_security_groups_response = {
        'SecurityGroups': [{
            'Description': 'Test Security Group.',
            'GroupName': 'Test Security Group',
            'IpPermissions': [{
                'FromPort': 22,
                'IpProtocol': 'tcp',
                'IpRanges': [{
                    'CidrIp': '1.2.3.4/32'
                }, {
                    'CidrIp': '5.6.7.8/32'
                }, {
                    'CidrIp': '9.10.11.12/32'
                }],
                'Ipv6Ranges': [],
                'PrefixListIds': [],
                'ToPort': 22,
                'UserIdGroupPairs': []
            }, {
                'FromPort': 4444,
                'IpProtocol': 'tcp',
                'IpRanges': [{
                    'CidrIp': '192.168.0.0/24',
                    'Description': 'Lambda Shell'
                }],
                'Ipv6Ranges': [],
                'PrefixListIds': [],
                'ToPort': 4444,
                'UserIdGroupPairs': []
            }],
            'OwnerId': '012345678910',
            'GroupId': 'sg-01234567890abcde',
            'IpPermissionsEgress': [{
                'IpProtocol': '-1',
                'IpRanges': [{
                    'CidrIp': '0.0.0.0/0'
                }],
                'Ipv6Ranges': [],
                'PrefixListIds': [],
                'UserIdGroupPairs': []
            }],
            'VpcId': 'vpc-01234567890abcde'
        }],
        'ResponseMetadata': {
            'RequestId': '593d805a-64ef-447c-beed-927748ef4307',
            'HTTPStatusCode': 200,
            'HTTPHeaders': {
                'content-type': 'text/xml;charset=UTF-8',
                'content-length': '3618',
                'vary': 'accept-encoding',
                'date': 'Wed, 24 Jul 2019 22:49:09 GMT',
                'server': 'AmazonEC2'
            },
            'RetryAttempts': 0
        }
    }


@pytest.fixture(scope='module')
def ec2_describe_security_groups_response():
    response = pytest.describe_security_groups_response
    yield response


@pytest.fixture(scope='module')
def security_group_details():
    response = pytest.describe_security_groups_response['SecurityGroups'][0]
    yield response


@pytest.fixture(scope='module')
def security_group_details_rules_open_to_world():
    response = pytest.describe_security_groups_response['SecurityGroups'][0]
    response['IpPermissions'][0]['IpRanges'].append({
                'CidrIp': '0.0.0.0/0'
            })
    yield response


def test_get_security_group_id_from_event_success():
    event = {
                'pathParameters': {
                    'securityGroupId': 'sg-01234567890abcde'
                }
            }
    assert 'sg-01234567890abcde' == sg_utils.get_security_group_id_from_event(event)


def test_get_security_group_id_from_event_exception():
    with pytest.raises(KeyError):
        event = {}
        sg_utils.get_security_group_id_from_event(event)


def test_get_ec2_client_success():
    # TODO: Not sure how to compare two ec2 client instances.
    # client = boto3.client('ec2')
    # assert sg_utils.get_ec2_client()._endpoint is client._endpoint
    assert False


def test_get_security_group_details_success(ec2_describe_security_groups_response):
    response = ec2_describe_security_groups_response
    ec2_client = botocore.session.get_session().create_client('ec2')
    with Stubber(ec2_client) as stubber:
        expected_parameters = {'GroupIds': ['sg-abc1234']}
        stubber.add_response('describe_security_groups', response, expected_parameters)
        service_response = sg_utils.get_security_group_details(ec2_client, 'sg-abc1234')

    assert service_response == response['SecurityGroups'][0]


def test_get_security_group_details_client_error():
    ec2_client = botocore.session.get_session().create_client('ec2')
    stubber = Stubber(ec2_client)
    stubber.add_client_error('describe_security_groups')
    with pytest.raises(ClientError) as e:
        service_response = ec2_client.describe_security_groups(GroupIds=['sg-abc1234'])


def test_get_security_group_name_success(security_group_details):
    response = security_group_details
    assert sg_utils.get_security_group_name(response) == response['GroupName']


def test_get_security_group_description_success(security_group_details):
    response = security_group_details
    assert sg_utils.get_security_group_description(response) == response['Description']


def test_get_security_group_id_success(security_group_details):
    response = security_group_details
    assert sg_utils.get_security_group_id(response) == response['GroupId']


def test_get_security_group_vpc_id_success(security_group_details):
    response = security_group_details
    assert sg_utils.get_security_group_vpc_id(response) == response['VpcId']

def test_is_security_group_rule_open_to_entire_world_true():
    security_group_rule = {
                            'FromPort': 22,
                            'IpProtocol': 'tcp',
                            'IpRanges': [{
                                'CidrIp': '1.2.3.4/32'
                            }, {
                                'CidrIp': '5.6.7.8/32'
                            }, {
                                'CidrIp': '10.11.12.13/32'
                            }, {
                                'CidrIp': '0.0.0.0/0'
                            }],
                            'Ipv6Ranges': [],
                            'PrefixListIds': [],
                            'ToPort': 22,
                            'UserIdGroupPairs': []
                        }
    assert True == sg_utils.is_security_group_rule_open_to_entire_world(security_group_rule)


def test_is_security_group_rule_open_to_entire_world_false():
    security_group_rule = {
        'FromPort': 22,
        'IpProtocol': 'tcp',
        'IpRanges': [{
            'CidrIp': '1.2.3.4/32'
        }, {
            'CidrIp': '5.6.7.8/32'
        }, {
            'CidrIp': '10.11.12.13/32'
        }],
        'Ipv6Ranges': [],
        'PrefixListIds': [],
        'ToPort': 22,
        'UserIdGroupPairs': []
    }
    assert False == sg_utils.is_security_group_rule_open_to_entire_world(security_group_rule)


def test_get_ingress_security_group_rules_ports_open_to_entire_world(security_group_details):
    assert [] == sg_utils.get_ingress_security_group_rules_ports_open_to_entire_world(security_group_details)


def test_get_ingress_security_group_rules_ports_open_to_entire_world_with_rules_open_to_world(security_group_details_rules_open_to_world):
    ingress_security_group_rules_ports_open_to_entire_world = []
    rule_details = {}
    rule_details['FromPort'] = 22
    rule_details['ToPort'] = 22
    ingress_security_group_rules_ports_open_to_entire_world.append(rule_details)
    assert ingress_security_group_rules_ports_open_to_entire_world == sg_utils.get_ingress_security_group_rules_ports_open_to_entire_world(security_group_details_rules_open_to_world)

# TODO: This test is failing, need to check why its failing.
# def test_create_client_response_success_monkey_patch(monkeypatch):
#     response = {
#         'statusCode': 200,
#         'message': 'Successfully fetched security group info',
#         'security_group_info': {
#             'name': 'Test Security Group',
#             'description': 'Test Security Group.',
#             'vpc_id': 'vpc-01234567890abcde',
#             'security_group_id': 'sg-01234567890abcde'
#         }
#     }
#     monkeypatch.setattr('sg_utils.create_client_response',response)
#     event = {
#         'pathParameters': {
#             'securityGroupId': 'sg-01234567890abcde'
#         }
#     }
#     client_response = {}
#     client_response['statusCode'] = 200
#     assert client_response['statusCode'] == sg_utils.create_client_response(event)['statusCode']


# TODO: This test is failing, need to check why its failing.
# @patch('sg_utils.create_client_response')
# def test_create_client_response_success_patch(sgUtilsCreateClientResponseMockObject):
#     event = {
#         'pathParameters': {
#             'securityGroupId': 'sg-01234567890abcde'
#         }
#     }
#     client_response = {}
#     response = {
#         'statusCode': 200,
#         'message': 'Successfully fetched security group info',
#         'security_group_info': {
#             'name': 'Test Security Group',
#             'description': 'Test Security Group.',
#             'vpc_id': 'vpc-01234567890abcde',
#             'security_group_id': 'sg-01234567890abcde'
#         }
#     }
#
#     client_response['statusCode'] = 200
#     sgUtilsCreateClientResponseMockObject.return_value = response
#     assert client_response['statusCode'] == sg_utils.create_client_response(event)['statusCode']


#TODO: This test passes when provided with correct security group id.
def test_create_client_response_success():
    event = {
        'pathParameters': {
            'securityGroupId': 'sg-01234567890abcde'
        }
    }
    client_response = {}
    client_response['statusCode'] = 200
    assert client_response['statusCode'] == sg_utils.create_client_response(event)['statusCode']


def test_create_client_response_keyerror():
    event = {}
    client_response = {}
    client_response['statusCode'] = 500
    assert client_response['statusCode'] == sg_utils.create_client_response(event)['statusCode']


def test_create_client_response_clienterror():
    event = {}
    ec2_client = botocore.session.get_session().create_client('ec2')
    stubber = Stubber(ec2_client)
    stubber.add_client_error('describe_security_groups')
    stubber.activate()
    client_response = {}
    client_response['statusCode'] = 500
    assert client_response['statusCode'] == sg_utils.create_client_response(event)['statusCode']
    stubber.deactivate()



