import argparse
import os
import requests
import json
import base64
from pathlib import Path
from typing import Any
from dotenv import load_dotenv
from datetime import datetime, timezone
from jwcrypto import jwk, jws
from jwcrypto.common import json_encode, json_decode

from openbao.interface import OpenBaoInterface
from util.helpers import generate_issue_keys, create_credential_payload, sign_credential_jwt, resolve_did, \
    verify_jwt_with_issuer_did, add_proof_to_credential, create_did_payload

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent

KEY_PVT = {
    "crv":"P-256",
    "d":"SOME_KEY",
    "kid":"issuer-key-1",
    "kty":"EC",
    "x":"SOME_KEY",
    "y":"SOME_KEY"
}

KEY_PUB = {
    "crv":"P-256",
    "kid":"issuer-key-1",
    "kty":"EC",
    "x":"SOME_KEY",
    "y":"SOME_KEY"
}

KMS_URL = os.getenv("KMS_URL", "http://localhost:8074")

KEYCLOAK_ISSUER = os.getenv("KEYCLOAK_ISSUER", "http://localhost:7080/auth/realms/labgen")
ACCESS_TOKEN = "SOME_KEY.SOME_KEY.SOME_KEY"
COUNTER_ACCESS_TOKEN = "SOME_KEY.SOME_KEY.SOME_KEY"
ISSUER_DID = "did:orb:uAAA:<add_issuer_did_here>"

class VCDIDTesterCLI:
    def __init__(self):
        pass

    def handle(self, command, *args, **kwargs) -> Any | None:
        if command == 'create_did':
            return self.create_did(*args, **kwargs)
        if command == 'issue_vc':
            return self.issue_vc(*args, **kwargs)
        if command == 'verify_vc':
            return self.verify_vc(*args, **kwargs)
        if command == 'create_vcs':
            return self.create_vcs(*args, **kwargs)
        return None

    def create_did(self, orb_url: str, openbao: OpenBaoInterface, bao_headers: dict, user_token: str) -> str | None:
        """
        Create a DID using the Trustbloc orb API.
        Args:
            orb_url: The base URL of the orb node (e.g., http://orb1.local)
        Returns:
            The created DID string or None on failure.
        """
        orb_api_url = f"{orb_url}/sidetree/v1/operations"

        # # Create private, public key pair
        # did_private_key_jwk, did_public_key_jwk = generate_issue_keys()
        # # Create the recovery and update keys (using the same key pair for simplicity)
        # recovery_private_key_jwk, recovery_public_key_jwk = generate_issue_keys()
        # update_private_key_jwk, update_public_key_jwk = generate_issue_keys()

        user_jwt = OpenBaoInterface.get_jwt_token(user_token)

        did_public_key_jwk = openbao.get_jwk_key("did-key", user_jwt, bao_headers)
        recovery_public_key_jwk = openbao.get_jwk_key("recovery-key", user_jwt, bao_headers)
        update_public_key_jwk = openbao.get_jwk_key("update-key", user_jwt, bao_headers)

        print("Generated DID Key Pair (JWK):")
        # print(json.dumps(json_decode(did_private_key_jwk), indent=2))
        print(json.dumps(did_public_key_jwk, indent=2))
        print("Generated Recovery Key Pair (JWK):")
        # print(json.dumps(json_decode(recovery_private_key_jwk), indent=2))
        print(json.dumps(recovery_public_key_jwk, indent=2))
        print("Generated Update Key Pair (JWK):")
        # print(json.dumps(json_decode(update_private_key_jwk), indent=2))
        print(json.dumps(update_public_key_jwk, indent=2))

        did = create_did_payload(did_public_key_jwk, recovery_public_key_jwk, update_public_key_jwk, "http://orb1.local")

        print("Generated DID (JWK):")
        print(json.dumps(did, indent=2))

        created_did = requests.post(orb_api_url, headers={
            "Accept": "application/ld+json",
            "Content-Type": "application/ld+json"
        }, json=did)

        if created_did.status_code >= 400:
            raise Exception(f"Failed to create DID: {created_did.status_code} - {created_did.text}")

        return created_did.json().get("didDocument").get("id")


    def issue_vc(self, profile_id: str, profile_version: str, issuer_did: str, subject_did: str, subject_name: str, degree_type: str = "BachelorDegree", degree_name: str = "BSc Computer Science") -> Any | None:
        """
        Issue a Verifiable Credential using the Trustbloc VCS API.
        """
        pass

    def verify_vc(self, profile_id: str, profile_version: str, vc: dict) -> Any | None:
        """
        Verify a Verifiable Credential using the Trustbloc VCS API.
        """
        pass

    def create_vcs(self, profile_id: str, profile_version: str, credential: dict, options: dict = None, name: str = None, description: str = None, template_id: str = None, claims: dict = None) -> Any | None:
        pass

    def test(self, parameters):

        openbao = OpenBaoInterface(
            "http://localhost:8200",
            "3fTaTH2dfpawAZdCi6E3ab",
            f"{KEYCLOAK_ISSUER}/protocol/openid-connect/token",
            "piddf",
            "HBpOpbw86JRGhaj5eImDLmYNwSq6u76y"
        )

        bao_token = openbao.setup_per_user_auth(
            f"{KEYCLOAK_ISSUER}/protocol/openid-connect/certs",
            KEYCLOAK_ISSUER,
            ACCESS_TOKEN,
            None,
            True
        )

        bao_headers = openbao.get_bao_headers(bao_token)

        jwt = OpenBaoInterface.get_jwt_token(ACCESS_TOKEN)

        did_key = openbao.create_key_for_user("did-key", jwt, bao_headers)
        recovery_key = openbao.create_key_for_user("recovery-key", jwt, bao_headers)
        update_key = openbao.create_key_for_user("update-key", jwt, bao_headers)


        # issuer_private_key_jwk, issuer_public_key_jwk = did_key.export_private(), did_key.export_public()
        # issuer_private_key_jwk, issuer_public_key_jwk = generate_issue_keys()


        did = ISSUER_DID
        print(f"Created DID: {did}")
        # print(f"Issuer Private Key (JWK): {issuer_private_key_jwk}")
        # print(f"Issuer Public Key (JWK): {issuer_public_key_jwk}")

        # create a sample VC
        holder_did = cli.create_did(orb_url=parameters.orb_url, openbao=openbao, bao_headers=bao_headers, user_token=ACCESS_TOKEN)
        subject_attributes = {
            "degree": {
                "type": "BachelorDegree",
                "name": "BSc Computer Science"
            },
            "GPA": "3.8",
            "name": "Alice"
        }
        credential_payload = create_credential_payload(issuer_did=did, holder_did=holder_did, subject_data=subject_attributes, issuer_oidc=KEYCLOAK_ISSUER)
        print("Sample Verifiable Credential Payload:")
        print(json.dumps(credential_payload, indent=2))

        signing_key_name = jwt.get("sub") + "-did-key"
        # Sign the VC
        credential_jwt = openbao.sign_payload(signing_key_name, credential_payload, bao_headers)

        signed_vc_jwt = add_proof_to_credential(credential_payload, credential_jwt)
        print("\n--- Signed Verifiable Credential (JWT) ---")
        print(json.dumps(signed_vc_jwt, indent=2))

        # Resolve the issuer's DID to show it's registered on Orb (after being anchored)
        resolved_did_document = resolve_did(parameters.orb_url, holder_did)
        print("\n--- Resolved DID Document ---")
        print(json.dumps(resolved_did_document, indent=2) if resolved_did_document else "Failed to resolve DID")

        print("\n--- Verifiable Credential ---")
        print("Verifiable Credential (JWT) created and signed successfully.")
        print("This credential can now be given to a holder")
        print("and later verified by a verifier using the issuer's DID Document.")

        # Verify the signed VC using the issuer's DID Document
        is_valid = verify_jwt_with_issuer_did(parameters.orb_url, signed_vc_jwt)
        print(f"\n--- Verification Result ---\nCredential is valid: {is_valid}")
        return signed_vc_jwt

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Trustbloc VCDID CLI')
    parser.add_argument('--version', action='version', version='Trustbloc VCDID CLI 0.1')
    subparsers = parser.add_subparsers(dest='command')

    parser_did = subparsers.add_parser('test')
    parser_did.add_argument('--orb-url', default='http://localhost:48326', help='ORB base URL')
    parser_did.add_argument('--public-key-type', default='Ed25519', help='Public key type')
    parser_did.add_argument('--open-bao-address', default='http://localhost:8076', help='OpenBAO API address')
    parser_did.add_argument('--open-bao-token', default='', help='OpenBAO API token')
    parser_did.add_argument('--oidc-token-url', default='http://localhost:8075/token', help='OIDC token URL')
    parser_did.add_argument('--oidc-client-id', default='client', help='OIDC client ID')
    parser_did.add_argument('--oidc-client-secret', default='secret', help='OIDC client secret')
    parser_did.add_argument('--oidc-user-token', default='', help='OIDC user token')

    parser_create_did = subparsers.add_parser('create_did')
    parser_create_did.add_argument('--orb-url', default='http://localhost:48326', help='ORB base URL')

    args = parser.parse_args()
    cli = VCDIDTesterCLI()

    if args.command == 'test':
        cli.test(args)
    elif args.command == 'create_did':
        # did = cli.create_did(orb_url=args.orb_url, None, {}, "")
        # print(f"Created DID: {did}")
        print("create_did command is not fully implemented yet.")


