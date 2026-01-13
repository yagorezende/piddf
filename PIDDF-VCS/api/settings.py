import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Keycloak setup
OIDC_OP_JWKS_ENDPOINT = os.environ.get('OIDC_OP_JWKS_ENDPOINT')
OIDC_RP_SIGN_ALGO = os.environ.get('OIDC_RP_SIGN_ALGO')
OIDC_RP_CLIENT_ID = os.environ.get('OIDC_RP_CLIENT_ID')
OIDC_RP_CLIENT_SECRET = os.environ.get('OIDC_RP_CLIENT_SECRET')
OIDC_OP_AUTHORIZATION_ENDPOINT = os.environ.get('OIDC_OP_AUTHORIZATION_ENDPOINT')
OIDC_OP_LOGOUT_ENDPOINT = os.environ.get('OIDC_OP_LOGOUT_ENDPOINT')
OIDC_OP_ENDSESSION_ENDPOINT = os.environ.get('OIDC_OP_ENDSESSION_ENDPOINT')
OIDC_OP_LOGOUT_URL_METHOD = os.environ.get('OIDC_OP_LOGOUT_URL_METHOD')
OIDC_OP_TOKEN_ENDPOINT = os.environ.get('OIDC_OP_TOKEN_ENDPOINT')
OIDC_OP_USER_ENDPOINT = os.environ.get('OIDC_OP_USER_ENDPOINT')
OIDC_CALLBACK_PUBLIC_URI = "http://localhost:8080"

LOGIN_REDIRECT_URL = OIDC_CALLBACK_PUBLIC_URI
LOGOUT_REDIRECT_URL = OIDC_CALLBACK_PUBLIC_URI

KEYCLOAK_ADMIN_USERNAME = os.environ.get('KEYCLOAK_USERNAME')
KEYCLOAK_ADMIN_PASSWORD = os.environ.get('KEYCLOAK_USER_PASSWORD')

KEYCLOAK_CONFIG = {
    'KEYCLOAK_SERVER_URL': os.environ.get('KEYCLOAK_SERVER_URL'),
    'KEYCLOAK_REALM': os.environ.get('OIDC_RP_REALM_ID'),
    'KEYCLOAK_CLIENT_ID': os.environ.get('OIDC_RP_CLIENT_ID'),
    'KEYCLOAK_CLIENT_SECRET_KEY': os.environ.get('OIDC_RP_CLIENT_SECRET')
}

ISSUER_DID = os.environ.get('ISSUER_DID')
KEYCLOAK_ISSUER = os.getenv("KEYCLOAK_ISSUER", "http://localhost:7080/auth/realms/labgen")

ORB_URL = os.environ.get('ORB_URL', 'http://localhost:9000')

OPEN_BAO_ADDRESS = os.environ.get('OPEN_BAO_ADDRESS', 'http://localhost:8200')
OPEN_BAO_ROOT_TOKEN = os.environ.get('OPEN_BAO_ROOT_TOKEN', 'root-key')
OPEN_BAO_POLICY_NAME = os.environ.get('OPEN_BAO_POLICY_NAME', '"piddf-per-user-policy"')
OPEN_BAO_POLICY_PATH = os.environ.get('OPEN_BAO_POLICY_PATH', BASE_DIR / 'data/openbao/piddf-per-user-policy.hcl')
OPEN_BAO_OIDC_ISSUER = os.environ.get('OPEN_BAO_OIDC_ISSUER', KEYCLOAK_ISSUER)
OPEN_BAO_POLICY=None

if OPEN_BAO_POLICY_PATH and os.path.exists(OPEN_BAO_POLICY_PATH):
    with open(OPEN_BAO_POLICY_PATH, 'r') as policy_file:
        OPEN_BAO_POLICY = policy_file.read()