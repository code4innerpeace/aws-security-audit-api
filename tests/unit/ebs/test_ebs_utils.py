import pytest
import boto3
import datetime
import botocore.session
from botocore.exceptions import ClientError
from botocore.stub import Stubber
from ebs import ebs_utils

pytest.describe_volumes_response = {
	'Volumes': [{
		'Attachments': [{
			'AttachTime': datetime.datetime(2019, 6, 18, 20, 4, 3),
			'Device': '/dev/xvda',
			'InstanceId': 'i-012ceef000c123456',
			'State': 'attached',
			'VolumeId': 'vol-123456e6f62ccf1bd',
			'DeleteOnTermination': True
		}],
		'AvailabilityZone': 'us-east-1a',
		'CreateTime': datetime.datetime(2019, 6, 18, 20, 4, 3),
		'Encrypted': False,
		'Size': 8,
		'SnapshotId': 'snap-01ccbc2bc3ae4e5e6',
		'State': 'in-use',
		'VolumeId': 'vol-123456e6f62ccf1bd',
		'Iops': 100,
		'VolumeType': 'gp2'
	}],
	'ResponseMetadata': {
		'RequestId': '5e7ef75f-123d-1234-a123-0a123a123d12',
		'HTTPStatusCode': 200,
		'HTTPHeaders': {
			'content-type': 'text/xml;charset=UTF-8',
			'content-length': '1783',
			'date': 'Mon, 29 Jul 2019 14:32:54 GMT',
			'server': 'AmazonEC2'
		},
		'RetryAttempts': 0
	}
}


@pytest.fixture('module')
def ec2_describe_volumes_response():
	response = pytest.describe_volumes_response
	yield response


@pytest.fixture('module')
def ebs_volume_details():
	response = pytest.describe_volumes_response
	yield response['Volumes'][0]


def test_get_ebs_volume_id_from_event_success():
    event = {
        'pathParameters': {
            'ebsVolumeId': 'sg-01234567890abcde'
        }
    }
    assert 'sg-01234567890abcde' == ebs_utils.get_ebs_volume_id_from_event(event)


def test_get_ebs_volume_id_from_event_exception():
    with pytest.raises(KeyError):
        event = {}
        ebs_utils.get_ebs_volume_id_from_event(event)


def test_get_ebs_volume_details_success(ec2_describe_volumes_response):
    response = ec2_describe_volumes_response
    ec2_client = botocore.session.get_session().create_client('ec2')
    with Stubber(ec2_client) as stubber:
        expected_parameters = {'VolumeIds': ['vol-123456e6f62ccf1bd']}
        stubber.add_response('describe_volumes', response, expected_parameters)
        service_response = ebs_utils.get_ebs_volume_details(ec2_client, 'vol-123456e6f62ccf1bd')

    assert service_response == response['Volumes'][0]


def test_get_ebs_volume_details_client_error():
    ec2_client = botocore.session.get_session().create_client('ec2')
    stubber = Stubber(ec2_client)
    stubber.add_client_error('describe_volumes')
    with pytest.raises(ClientError) as e:
        service_response = ec2_client.describe_volumes(VolumeIds=['vol-1234'])


def test_ebs_volume_id_success(ebs_volume_details):
    assert ebs_volume_details['VolumeId'] == ebs_utils.get_ebs_volume_id(ebs_volume_details)


def test_get_ebs_volume_encryption_status_success(ebs_volume_details):
    assert ebs_volume_details['Encrypted'] == ebs_utils.get_ebs_volume_encryption_status(ebs_volume_details)


def test_get_ec2_client_success():
    # TODO: Not sure how to compare two ec2 client instances.
    # client = boto3.client('ec2')
    # assert ebs_utils.get_ec2_client()._endpoint is client._endpoint
    assert False
    

#TODO: This test passes when provided with correct ebs volume id.
# But this is not the right way. Need to use patch or monkey patch
# to mock the response.
def test_create_client_response_success():
    event = {
        'pathParameters': {
            'ebsVolumeId': 'vol-123456e6f62ccf1bd'
        }
    }
    client_response = {}
    client_response['statusCode'] = 200
    assert client_response['statusCode'] == ebs_utils.create_client_response(event)['statusCode']


def test_create_client_response_keyerror():
    event = {}
    client_response = {}
    client_response['statusCode'] = 500
    assert client_response['statusCode'] == ebs_utils.create_client_response(event)['statusCode']


def test_create_client_response_clienterror():
    event = {}
    ec2_client = botocore.session.get_session().create_client('ec2')
    stubber = Stubber(ec2_client)
    stubber.add_client_error('describe_volumes')
    stubber.activate()
    client_response = {}
    client_response['statusCode'] = 500
    assert client_response['statusCode'] == ebs_utils.create_client_response(event)['statusCode']
    stubber.deactivate()

