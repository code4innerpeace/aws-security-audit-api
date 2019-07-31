import boto3
from botocore.exceptions import ClientError


def get_security_group_id_from_event(event: dict) -> str:
    """
        This method fetches security group id
        from event dictionary.
        This method throws KeyError if
        event['pathParameters']['securityGroupId'] not found.

    :param event:
    :return: security group id
    :exception: throws KeyError exception if key not found
    """
    return event['pathParameters']['securityGroupId']


def get_ec2_client():
    """
        This method returns ec2 client.
    :return: ec2 client object
    """
    return boto3.client('ec2')


def get_security_group_details(ec2_client, security_group_id: str) -> dict:
    """
        This method return security group details.
    :param security_group_id:
    :return: security group details
    :exception: throws ClientError exception
    """
    response = ec2_client\
        .describe_security_groups(GroupIds=[security_group_id])
    return response['SecurityGroups'][0]


def get_security_group_name(security_group_details: dict) -> str:
    """
        This method returns security group name.
    :param security_group_details:
    :return: security group name
    """
    return security_group_details['GroupName']


def get_security_group_description(security_group_details: dict) -> str:
    """
        This method returns security group description.
    :param security_group_details:
    :return: security group description
    """
    return security_group_details['Description']


def get_security_group_id(security_group_details: dict) -> str:
    """
        This method returns security group id.
    :param security_group_details:
    :return: security group id.
    """
    return security_group_details['GroupId']


def get_security_group_vpc_id(security_group_details: dict) -> str:
    """
        This method returns security group vpc id.
    :param security_group_details:
    :return: security group vpc id
    """
    return security_group_details['VpcId']


def is_security_group_rule_open_to_entire_world(security_group_rule: dict) -> bool:
    """
        This method returns true if one of IpRanges
        key value is 0.0.0.0/0
    :param security_group_rule:
    :return:
    """
    return '0.0.0.0/0' in [i['CidrIp']
                           for i in security_group_rule['IpRanges']]


def get_ingress_security_group_rules_ports_open_to_entire_world(security_group_details: dict) -> list:
    """
        This method returns ingress security group rules,
        which allow traffic from 0.0.0.0/0
    :param security_group_details:
    :return: ingress security group rules ports open to the world.
    """
    ingress_security_group_rules_ports_open_to_entire_world = []
    ingress_rules = security_group_details['IpPermissions']

    for ingress_rule in ingress_rules:
        if is_security_group_rule_open_to_entire_world(ingress_rule):

            rule_details = {}

            if ingress_rule['IpProtocol'] == -1:
                rule_details['FromPort'] = 'ALL'
                rule_details['ToPort'] = 'ALL'
            else:
                rule_details['FromPort'] = ingress_rule['FromPort']
                rule_details['ToPort'] = ingress_rule['ToPort']

            ingress_security_group_rules_ports_open_to_entire_world\
                .append(rule_details)

    return ingress_security_group_rules_ports_open_to_entire_world


def create_client_response(event: dict) -> dict:
    """
        This method returns security group info
        for the client.
    :param event:
    :return: security group info dictionary
    """
    # TODO:
    #   This method should catch KeyError or any other exception. If KeyError
    #   then it should create client error message with details.
    #   else it should generate success message.
    client_response = {}
    security_group_info = {}
    try:
        security_group_id = get_security_group_id_from_event(event)
        ec2_client = get_ec2_client()
        security_group_details = get_security_group_details(
            ec2_client, security_group_id)
        security_group_info['name'] = get_security_group_name(
            security_group_details)
        security_group_info['description'] = get_security_group_description(
            security_group_details)
        security_group_info['vpc_id'] = get_security_group_vpc_id(
            security_group_details)
        security_group_info['security_group_id'] = get_security_group_id(
            security_group_details)
        security_group_info['ingress_security_group_rules_ports_open_to_entire_world'] \
            = get_ingress_security_group_rules_ports_open_to_entire_world(
            security_group_details)

        client_response['statusCode'] = 200
        client_response['message'] = "Successfully fetched security group info"
        client_response['security_group_info'] = security_group_info
    except KeyError:
        client_response['statusCode'] = 500
        client_response['message'] = """Key 'pathParameters'
        or 'securityGroupId' doesn't exist."""
    except ClientError:
        client_response['statusCode'] = 500
        client_response['message'] = "botocore.exceptions.ClientError received"

    finally:
        return client_response


if __name__ == "__main__":
    pass
