import os

management_client_id = os.environ['AUTH0_MACHINE_CLIENT_ID']
management_client_secret = os.environ['AUTH0_MACHINE_CLIENT_SECRET']
auth_audience = os.environ['AUTH0_API_AUDIENCE']
auth_domain = os.environ['AUTH0_DOMAIN']
machine_account_email = "duber+ManagementApi@mercator.tech"
machine_account_sub_id = os.environ["AUTH0_MACHINE_CLIENT_ID"] + "@clients"