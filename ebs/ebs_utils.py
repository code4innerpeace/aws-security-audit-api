import boto3
from botocore.exceptions import ClientError


def get_ebs_volume_id_from_event(event: dict) -> str:
    """
        This method fetches ebs volume id
        from event dictionary.
        This method throws KeyError if
        event['pathParameters']['ebsVolumeId'] not found.

    :param event:
    :return: ebs volume id
    :exception: throws KeyError exception if key not found
    """
    return event['pathParameters']['ebsVolumeId']


def get_ec2_client():
    """
        This method returns ec2 client.
    :return: ec2 client object
    """
    return boto3.client('ec2')


def get_ebs_volume_details(ec2_client, ebs_volume_id: str) -> dict:
    """
        This method returns ebs volume details.
    :param ec2_client:
    :param ebs_volume_id:
    :return: ebs volume details.
    """
    response = ec2_client.describe_volumes(VolumeIds=[ebs_volume_id])
    return response['Volumes'][0]


def get_ebs_volume_id(ebs_volume_details: dict) -> str:
    """
        This method returns ebs volume id
    :param ebs_volume_details:
    :return: ebs volume id
    """
    return ebs_volume_details['VolumeId']


def get_ebs_volume_encryption_status(ebs_volume_details: dict) -> bool:
    """
        This method return if ebs volume is encrypted or not.
    :param ebs_volume_details:
    :return: True or False
    """
    return ebs_volume_details['Encrypted']


def create_client_response(event: dict) -> dict:
    """
        This method creates ebs volume info
        for the client.
    :param event:
    :return: ebs volume info.
    """
    client_response = {}
    ebs_volume_info = {}
    try:
        ebs_volume_id = get_ebs_volume_id_from_event(event)
        ec2_client = get_ec2_client()
        ebs_volume_details = get_ebs_volume_details(ec2_client, ebs_volume_id)
        ebs_volume_info['volumeId'] = get_ebs_volume_id(ebs_volume_details)
        ebs_volume_info['encryptionStatus'] = \
            get_ebs_volume_encryption_status(ebs_volume_details)
        client_response['statusCode'] = 200
        client_response['message'] = "Successfully fetched ebs volume info"
        client_response['ebs_volume_info'] = ebs_volume_info
    except KeyError:
        client_response['statusCode'] = 500
        client_response['message'] = """Key 'pathParameters'
        or 'ebsVolumeId' doesn't exist."""
    except ClientError:
        client_response['statusCode'] = 500
        client_response['message'] = "botocore.exceptions.ClientError received"

    finally:
        return client_response
