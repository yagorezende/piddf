import json
import requests

from credentials.model import IdentityModel
from openbao.interface import OpenBaoInterface
from util.helpers import create_credential_payload, create_did_payload, add_proof_to_credential, \
    verify_jwt_with_issuer_did


class VCDIDInterface:
    def __init__(self, issuer_oidc: str, issuer_did: str, openbao: OpenBaoInterface, orb_url, issuer_anchor_origin: str = "http://orb1.local"):
        self.issuer_oidc = issuer_oidc
        self.issuer_did = issuer_did
        self.openbao = openbao
        self.orb_url = orb_url
        self.issuer_anchor_origin = issuer_anchor_origin

    def create_did(self, bao_headers: dict, user_jwt: dict) -> str | None:
        """
        Create a DID using the Trustbloc orb API.
        """
        orb_api_url = f"{self.orb_url}/sidetree/v1/operations"

        # Try to create the key if it doesn't already exist
        self.openbao.create_key_for_user("did-key", user_jwt, bao_headers)
        self.openbao.create_key_for_user("recovery-key", user_jwt, bao_headers)
        self.openbao.create_key_for_user("update-key", user_jwt, bao_headers)

        # recovering the user public keys
        did_public_key_jwk = self.openbao.get_jwk_key("did-key", user_jwt, bao_headers)
        recovery_public_key_jwk = self.openbao.get_jwk_key("recovery-key", user_jwt, bao_headers)
        update_public_key_jwk = self.openbao.get_jwk_key("update-key", user_jwt, bao_headers)

        did = create_did_payload(
            did_public_key_jwk,
            recovery_public_key_jwk,
            update_public_key_jwk,
            anchor_origin=self.issuer_anchor_origin
        )

        created_did = requests.post(orb_api_url, headers={
            "Accept": "application/ld+json",
            "Content-Type": "application/ld+json"
        }, json=did)

        if created_did.status_code >= 400:
            raise Exception(f"Failed to create DID: {created_did.status_code} - {created_did.text}")

        return created_did.json().get("didDocument").get("id")

    def issue_vc(self, identity: IdentityModel, alternative_issuer_did: str = None):

        bao_token = self.openbao.get_bao_token_for_user(identity.access_token)
        bao_headers = self.openbao.get_bao_headers(bao_token)
        jwt = OpenBaoInterface.get_jwt_token(identity.access_token)

        # Create or recover new key
        holder_did = self.create_did(bao_headers=bao_headers, user_jwt=jwt)

        issuer_did = alternative_issuer_did if alternative_issuer_did else self.issuer_did

        signing_key_name = jwt.get("sub") + "-did-key"
        credential_payload = identity.to_credential_payload(issuer_did, holder_did, self.issuer_oidc)
        # Sign the VC
        credential_jwt = self.openbao.sign_payload(
            signing_key_name,
            credential_payload,
            bao_headers
        )

        return add_proof_to_credential(credential_payload, credential_jwt)

    def validate_vc(self, signed_vc_jwt: dict) -> IdentityModel | None:
        if verify_jwt_with_issuer_did(self.orb_url, signed_vc_jwt):
            return IdentityModel().from_json(signed_vc_jwt.get("credentialSubject"))
        return None