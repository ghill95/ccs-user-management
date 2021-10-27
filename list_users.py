import argparse
import boto3
import logging
import json

logging.basicConfig(level=logging.INFO)


def parse_arguments():
    description = "Arguments to list IAM users"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--json-filename",
        help="The name of the JSON file containing the list of AWS accounts to check",
        dest="json_filename",
        required=True
    )
    parser.add_argument(
        "--iam-users",
        help="A comma separated list of users to check for in IAM",
        dest="iam_users",
        required=True
    )
    return parser.parse_args()


def get_args(args=parse_arguments()):
    json_filename = args.json_filename
    iam_users = args.iam_users
    return json_filename, iam_users


def convert_iam_users_to_list(iam_users):
    list_of_iam_users = iam_users.split(",")
    return list_of_iam_users


def get_list_of_aws_accounts(json_filename):
    with open(json_filename) as aws_accounts_json_filename:
        aws_accounts = json.load(aws_accounts_json_filename)
        return aws_accounts['aws_account_names']


def get_list_of_iam_users_in_aws_account(aws_account):
    session = boto3.session.Session(profile_name=aws_account)
    iam_client = session.client('iam')
    iam_client_list_users_response = iam_client.list_users()
    iam_users = iam_client_list_users_response['Users']
    return iam_users


def check_if_user_has_iam_account(aws_account, iam_user, iam_users):
    iam_user_item = (item for item in iam_users)
    iam_user_is_present = list(filter(lambda person: person['UserName'] == iam_user, iam_user_item))
    if iam_user_is_present:
        logging.info(f"User {iam_user_is_present[0]['UserName']} has an IAM account in the {aws_account} account")
    else:
        logging.debug(f"User {iam_user} DOES NOT exist in the {aws_account} account")


def list_users():
    json_filename, iam_users = get_args()
    list_of_iam_users = convert_iam_users_to_list(iam_users=iam_users)
    list_of_aws_accounts = get_list_of_aws_accounts(json_filename=json_filename)
    for aws_account in list_of_aws_accounts:
        print(" ")
        logging.info(f"Checking for IAM users in the {aws_account} account")
        iam_users = get_list_of_iam_users_in_aws_account(aws_account=aws_account)
        if iam_users:
            for iam_user in list_of_iam_users:
                check_if_user_has_iam_account(aws_account=aws_account, iam_user=iam_user, iam_users=iam_users)
        else:
            logging.info(f"No IAM users found in the {aws_account} account")


list_users()
