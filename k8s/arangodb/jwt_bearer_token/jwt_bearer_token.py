#!/usr/bin/env python3
import base64
import os
import logging
import jwt
from kubernetes import client, config
from kubernetes.client.rest import ApiException


# Some values like a k8s token and a namespace can be accessed through special files, though it's always nice to have
# an option to overwrite the values through envs
def get_env_or_file(env, path):
    if env in os.environ:
        value = os.environ.get(env)
    else:
        with open(path, 'r', encoding='utf-8') as f:
            value = f.readline().strip()
    return value


# Helps to avoid nasty surprises with boolean envs.
def convert_to_bool(value):
    if value in ['True', 'true', True]:
        return True
    else:
        return False


# Since the script is intended to be used in k8s, everything is configured through envs.
def load_config():
    # We need to ensure some of the envs are always present.
    mandatory_envs = [
        'KUBERNETES_SERVICE_HOST',
        'KUBERNETES_SERVICE_PORT_HTTPS',
        'JWT_SECRET_NAME',
        'JWT_BEARER_TOKEN_SECRET_NAME'
    ]
    for env in mandatory_envs:
        if env not in os.environ:
            raise EnvironmentError(f"Failure: mandatory env {env} is not set.")

    # Temporary variables.
    k8s_port = os.environ.get('KUBERNETES_SERVICE_PORT_HTTPS')
    k8s_host = os.environ.get('KUBERNETES_SERVICE_HOST')

    # Here we'll store the config.
    script_config = {
        'k8s_url': f'https://{k8s_host}:{k8s_port}',
        'verify_ssl': convert_to_bool(os.environ.get('VERIFY_SSL', False)),
        'k8s_token': get_env_or_file('TOKEN', '/var/run/secrets/kubernetes.io/serviceaccount/token'),
        'k8s_namespace': get_env_or_file('NAMESPACE', '/var/run/secrets/kubernetes.io/serviceaccount/namespace'),
        'k8s_replace_secret': convert_to_bool(os.environ.get('REPLACE_SECRET', False)),
        'jwt_bearer_token_secret_name': os.environ.get('JWT_BEARER_TOKEN_SECRET_NAME'),
        'jwt_secret_name': os.environ.get('JWT_SECRET_NAME')
    }
    return script_config


# We'll use custom logging
def configure_logging():
    logger = logging.getLogger(__name__)
    c_handler = logging.StreamHandler()
    c_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    c_handler.setFormatter(c_format)
    logger.addHandler(c_handler)
    logger.setLevel(logging.INFO)
    return logger


# Useful when we read values from k8s secrets.
def decode_base64(data):
    return base64.b64decode(data).decode('utf-8')


# Useful for encoding data into k8s secrets.
def encode_base64(data):
    return base64.b64encode(data.encode('utf-8')).decode('utf-8')


# Helps to create a bearer token based on jwt secret.
def create_jwt_bearer_token(jwt_secret):
    payload = {
        "allowed_paths": [
            "/_admin/statistics",
            "/_admin/statistics-description",
            "/_admin/metrics"
        ],
        "iss": "arangodb",
        "server_id": "exporter"
    }
    encoded_jwt = jwt.encode(payload, jwt_secret, algorithm='HS256').decode('utf-8')
    return encoded_jwt


def main():
    logger = configure_logging()

    logger.info('Loading script configuration')
    script_config = load_config()

    logger.info('Constructing an API instance')
    k8s_config = client.Configuration()
    k8s_config.host = script_config['k8s_url']
    k8s_config.api_key = {"authorization": "Bearer " + script_config['k8s_token']}
    k8s_config.verify_ssl = script_config['verify_ssl']

    # If the verify ssl flag is enabled, we should load the CA cert from the standard location.
    if k8s_config.verify_ssl:
        k8s_config.ssl_ca_cert = "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"

    api_instance = client.ApiClient(k8s_config)
    v1 = client.CoreV1Api(api_instance)

    try:
        logger.info(f"Retrieving jwt secret {script_config['jwt_secret_name']} (ns: {script_config['k8s_namespace']})")
        api_response = v1.read_namespaced_secret(script_config['jwt_secret_name'], script_config['k8s_namespace'])

        logger.info("Creating bearer token")
        jwt_secret = decode_base64(api_response.data['token'])
        jwt_bearer_token = create_jwt_bearer_token(jwt_secret)

        logger.info(f"Constructing the secret {script_config['jwt_bearer_token_secret_name']}")
        body = client.V1Secret()
        body.api_version = 'v1'
        body.kind = 'Secret'
        body.metadata = {'name': script_config['jwt_bearer_token_secret_name']}
        body.data = {'token': encode_base64(jwt_bearer_token)}

        logger.info(f"Checking if the secret {script_config['jwt_bearer_token_secret_name']} already exists")
        api_response = v1.list_namespaced_secret(script_config['k8s_namespace'], watch=False)
        existing_secrets = [item.metadata.name for item in api_response.items]

        # Three options:
        # 1. The secret exists, we need to replace it (REPLACE_SECRET=True);
        # 2. The secret exists, we have to retain it (REPLACE_SECRET=False);
        # 3. The secret does not exist, we need to create it.
        if script_config['jwt_bearer_token_secret_name'] in existing_secrets:
            logger.info("There is a pre-existing secret")
            if script_config['k8s_replace_secret']:
                logger.info("The script has been configured to replace pre-existing secrets via REPLACE_SECRET env")
                logger.info(f"Replacing the secret {script_config['jwt_bearer_token_secret_name']}")
                api_response = v1.replace_namespaced_secret(script_config['jwt_bearer_token_secret_name'],
                                                            script_config['k8s_namespace'], body)
            else:
                logger.info("The script has been configured to retain pre-existing secrets via REPLACE_SECRET env")
                logger.info("Skipping the secret creation")
        else:
            logger.info(f"Creating the secret {script_config['jwt_bearer_token_secret_name']}")
            api_response = v1.create_namespaced_secret(script_config['k8s_namespace'], body)

    except ApiException as e:
        logger.error("Exception when calling CoreV1Api->read_namespaced_secret: %s\n" % e)
        return 1


if __name__ == '__main__':
    main()
