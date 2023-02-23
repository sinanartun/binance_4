import requests


def get():
    # retrieve the IAM role name
    url = "http://169.254.169.254/latest/meta-data/iam/security-credentials/"
    role_name = requests.get(url).text.strip()

    # retrieve temporary security token
    token_url = "http://169.254.169.254/latest/api/token"
    headers = {"X-aws-ec2-metadata-token-ttl-seconds": "21600"}
    token = requests.put(token_url, headers=headers).text.strip()

    # retrieve security credentials
    security_credentials_url = f"http://169.254.169.254/latest/meta-data/iam/security-credentials/{role_name}"
    headers = {"X-aws-ec2-metadata-token": token}
    response = requests.get(security_credentials_url, headers=headers)

    # parse the security credentials
    security_credentials = response.json()
    print(security_credentials)
    return security_credentials

    # print the security credentials


if __name__ == '__main__':
    get()
