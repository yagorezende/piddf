from flask import request
from flask_restx import Namespace, Resource

from credentials.interface import VCDIDInterface
from credentials.model import IdentityModel
from keycloak_interface.keycloakInterface import KeycloakInterface
from keycloak_interface.utils.functions import extract_header_token
from api import settings
from openbao.interface import OpenBaoInterface

api: Namespace = Namespace('VCS', description='PIDDF Verifiable Credentials Service Endpoints')

keycloak_interface = KeycloakInterface(
    server_url=settings.KEYCLOAK_CONFIG.get('KEYCLOAK_SERVER_URL'),
    realm_name=settings.KEYCLOAK_CONFIG.get('KEYCLOAK_REALM'),
    client_id=settings.KEYCLOAK_CONFIG.get('KEYCLOAK_CLIENT_ID'),
    client_secret_key=settings.KEYCLOAK_CONFIG.get('KEYCLOAK_CLIENT_SECRET_KEY')
)

openbao = OpenBaoInterface(
    settings.OPEN_BAO_ADDRESS,
    settings.OPEN_BAO_ROOT_TOKEN,
    f"{settings.KEYCLOAK_ISSUER}/protocol/openid-connect/token",
    settings.KEYCLOAK_CONFIG.get('KEYCLOAK_CLIENT_ID'),
    settings.KEYCLOAK_CONFIG.get('KEYCLOAK_CLIENT_SECRET_KEY')
)

openbao.enable_transit_engine()

vc_interface = VCDIDInterface(
    issuer_did=settings.ISSUER_DID,
    issuer_oidc=settings.KEYCLOAK_ISSUER,
    orb_url=settings.ORB_URL,
    openbao=openbao
)

openbao.enable_jwt_auth(
    f"{settings.OPEN_BAO_OIDC_ISSUER}/protocol/openid-connect/certs",
    settings.OPEN_BAO_OIDC_ISSUER,
    settings.OPEN_BAO_POLICY
)

@api.route("/status")
class VCSStatusView(Resource):
    @api.doc('vcs_status')
    def get(self):
        """
        Get the status of the Verifiable Credentials Service
        """
        return {'status': 'VCS is operational'}, 200


@api.route("/credentials")
class VCSCredentialsView(Resource):
    @api.doc('issue_credential')
    def post(self):
        """
        Issue a new verifiable credential
        """

        token = extract_header_token(request)
        if not keycloak_interface.validate_request_token(token):
            return {'error': 'Invalid or missing token'}, 401
        try:
            payload = request.get_json()
            identity = IdentityModel().from_json(payload)
            identity.access_token = token

            if payload.get('issuer'):
                return vc_interface.issue_vc(identity, payload.get("issuer")), 201
            return vc_interface.issue_vc(identity), 201

        except Exception as e:
            return {'error': str(e)}, 400


@api.route("/verify")
class VCSVerifyView(Resource):
    @api.doc('verify_credential')
    def post(self):
        """
        Verify a verifiable credential
        """
        token = extract_header_token(request)
        if not keycloak_interface.validate_request_token(token):
            return {'error': 'Invalid or missing token'}, 401

        try:
            payload = request.get_json()
            identity = vc_interface.validate_vc(payload)
            if not identity:
                return {'error': 'Credential verification failed'}, 400
            return identity.to_vc_json(), 200
        except Exception as e:
            return {'error': str(e)}, 400
