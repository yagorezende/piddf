import base64
import copy
import hashlib
import json
from typing import Tuple

import requests
from datetime import timezone, datetime

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from jwcrypto import jwk, jws
from jwcrypto.common import json_encode, json_decode

from openbao.interface import OpenBaoInterface


def sign_json_with_pem_key(data: dict, pem_key: str, pem_password: bytes) -> str:
    """
    Signs a JSON object using a PEM formatted private key and returns a JWS compact serialization.
    :param data: dict - The JSON object to sign.
    :param pem_key: str - The PEM formatted private key.
    :param pem_password: bytes - The password for the PEM key if it is encrypted, otherwise None.
    :return: str - The JWS compact serialization of the signed JSON object.
    """
    private_key = load_pem_private_key(pem_key.encode(), password=pem_password)

    # ==== CREATE DIGEST HEADER ====
    body_bytes = json_encode(data).encode()
    digest = base64.b64encode(hashlib.sha256(body_bytes).digest()).decode("utf-8")
    digest_header = f"SHA-256={digest}"

    # ==== DATE HEADER ====
    date_header = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")

    # ==== CREATE SIGNING STRING ====
    method = "post"
    path = "/v1/keystores/d3bdbgougjds73fat630/keys"
    host = "localhost:8074"

    signing_string = f"(request-target): {method} {path}\nhost: {host}\ndate: {date_header}\ndigest: {digest_header}"

    # ==== SIGN WITH PRIVATE KEY (ECDSA P-256) ====
    signature = private_key.sign(
        signing_string.encode("utf-8"),
        ec.ECDSA(hashes.SHA256())
    )

    # Base64 encode the signature
    signature_b64 = base64.b64encode(signature).decode("utf-8")

    # ==== BUILD SIGNATURE HEADER ====
    signature_header = (
        f'keyId="{data['keyID']}"\n",'
        f'algorithm="ecdsa-sha256",'
        f'headers="(request-target) host date digest",'
        f'signature="{signature_b64}"'
    )

    # Return the compact serialization of the JWS
    return signature_header

def base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")

def sha256_multihash(data: bytes) -> str:
    # multihash prefix for SHA2-256 is 0x12 0x20
    prefix = bytes([0x12, 0x20])
    digest = hashlib.sha256(data).digest()
    return base64url_encode(prefix + digest)

def canonicalize_jwk(jwk: dict) -> bytes:
    """
    JCS canonicalization: sort keys, no whitespace.
    """
    return json_encode(jwk).encode("utf-8")

def generate_issue_keys():
    """
    Generates an Elliptic Curve key pair for issuing Verifiable Credentials.
    :return: Tuple containing the private and public keys in a JWK format.
    """
    key = jwk.JWK.generate(kty='EC', crv='P-256', kid='issuer-key-1')
    return key.export_private(), key.export_public()

def create_kms_did_keystore(kms_url: str, did: str) -> str | None:
    """
    Creates a keystore in the KMS for the given DID.
    :param kms_url: str - The base URL of the KMS.
    :param did: str - The DID for which to create the keystore.
    :return: str | None - The keystore ID if created successfully, None otherwise.
    """
    try:
        response = requests.post(f"{kms_url}/keystores", json={"controller": did})
        response.raise_for_status()
        keystore_info = response.json()
        return keystore_info.get("keystoreID")
    except requests.RequestException as e:
        print(f"Error creating keystore in KMS: {e}")
        return None

def save_jwk_on_kms(kms_url: str, private_jwk: dict, keystore_id: str) -> str | None:
    """
    Saves the provided private JWK key to the KMS and returns the key ID.
    :param kms_url: str - The base URL of the KMS.
    :param private_jwk: dict - The private JWK key in JSON format.
    :param keystore_id: str - The ID of the keystore where the key will be saved.
    :return: str | None - The key ID if saved successfully, None otherwise.
    """
    try:
        response = requests.post(f"{kms_url}/keys/{keystore_id}", json=private_jwk)
        response.raise_for_status()
        key_info = response.json()
        return key_info.get("kid")
    except requests.RequestException as e:
        print(f"Error saving JWK to KMS: {e}")
        return None

def create_did_payload(public_key_jwk: dict, recovery_jwk: dict, update_jwk: dict, anchor_origin: str, ) -> dict:
    """
    Creates a DID payload for Trustbloc orb API based on the provided public key JWK.
    :param public_key_jwk: dict - The public key in JWK format.
    :param recovery_jwk: dict - The recovery key in JWK format.
    :param update_jwk: dict - The update key in JWK format.
    :param anchor_origin: str - The anchor origin for the DID.
    :return: dict - The DID payload to be sent to the orb API.
    """

    delta = {
        "patches": [
            {
                "action": "add-public-keys",
                "publicKeys": [
                    {
                        "id": "issuer-key-1",
                        "type": "JsonWebKey2020",
                        "publicKeyJwk": {
                            "kty": public_key_jwk["kty"],
                            "crv": public_key_jwk["crv"],
                            "x": public_key_jwk["x"],
                            "y": public_key_jwk["y"]
                        },
                        "purposes": [
                            "authentication"
                        ]
                    }
                ]
            }
        ],
        "updateCommitment": sha256_multihash(canonicalize_jwk(update_jwk))
    }

    payload = {"type": "create", "delta": delta}

    # create the suffixData using the public key
    suffix_data = {
        "anchorOrigin": anchor_origin,
        "deltaHash": sha256_multihash(canonicalize_jwk(delta)),
        "recoveryCommitment": sha256_multihash(canonicalize_jwk(recovery_jwk))
    }

    payload["suffixData"] = suffix_data
    return payload

def create_credential_payload(issuer_did: str, holder_did: str, subject_data: dict, credential_type="Profile", issuer_oidc: str = "http://localhost:7080/auth",):
    """
    Creates a Verifiable Credential payload based on W3C standards.
    :param issuer_did: str - The DID of the issuer.
    :param holder_did: str - The DID of the credential holder.
    :param subject_data: dict - The subject data to include in the credential.
    :param credential_type: str - The type of the credential (default: Profile).
    :param issuer_oidc: str - The OIDC URL of the issuer (default: http://localhost:7080/auth).
    :return: dict - The Verifiable Credential payload in the W3C standard.
    """

    now = datetime.now(timezone.utc).isoformat(timespec="seconds") + "Z"

    credential = {
        "@context": [
            "https://www.w3.org/ns/credentials/v2",
            "https://w3id.org/citizenship/v2"
        ],
        "id": f"urn:uuid:{base64.urlsafe_b64encode(now.encode()).decode()}",
        "type": ["VerifiableCredential", credential_type],
        "issuer": issuer_did,
        "issuer_well_known": f"{issuer_oidc}/.well-known/openid-configuration",
        "issuanceDate": now,
        "credentialSubject": {
            "did": holder_did,
            **subject_data # Merge additional subject data
        }
        # "proof": {}  # Proof will be added after signing
    }
    return credential

def sign_credential_jwt(credential_payload: dict, private_jwk: dict) -> str:
    """
    Signs a Verifiable Credential payload using the provided private JWK key and returns a JWT.
    :param credential_payload: dict - The Verifiable Credential payload to sign.
    :param private_jwk: dict - The private JWK key in JSON format.
    :return: str - The signed JWT representing the Verifiable Credential.
    """
    # Create a JSON Web Signature (JWS) object
    jws_obj = jws.JWS(json_encode(credential_payload))
    jwk_obj = jwk.JWK(**private_jwk)

    # Set the protected header
    protected_header = {
        "alg": "ES256", # Algorithm used with the Elliptic Curve key
        "kid": private_jwk["kid"] if "kid" in private_jwk else None, # Key ID if available
        "verificationMethod": f"{credential_payload['issuer']}#issuer-key-1" # Example verification method
    }

    # Sign the JWT (JSON Web Token)
    jws_obj.add_signature(jwk_obj, protected=json_encode(protected_header))
    signed_vc_jwt = jws_obj.serialize()
    return signed_vc_jwt

def add_proof_to_credential(credential: dict, signature: dict) -> dict:
    """
    Adds a proof to the Verifiable Credential by signing it with the provided private JWK key.
    :param credential: dict - The Verifiable Credential payload to sign.
    :param signature: dict - The signature to add as proof.
    :return: dict - The Verifiable Credential with the added proof.
    """

    proof = {
        "type": "'JsonWebKey2020'",
        "created": datetime.now(timezone.utc).isoformat(timespec="seconds") + "Z",
        "proofPurpose": "assertionMethod",
        "verificationMethod": f"{credential['credentialSubject']['did']}#issuer-key-1", # Example verification method
        "jws": signature
    }

    # Add the proof to the credential
    credential_with_proof = credential.copy()
    credential_with_proof["proof"] = proof
    return credential_with_proof

def resolve_did(orb_url: str, did: str) -> dict | None:
    """
    Resolves a DID using the Trustbloc orb API.
    Args:
        orb_url: The base URL of the orb node (e.g., http://orb1.local)
        did: The DID to resolve
    Returns:
        The resolved DID Document as a dictionary or None on failure.
    """
    resolve_url = f"{orb_url}/sidetree/v1/identifiers/{did}"
    try:
        response = requests.get(resolve_url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error resolving DID: {e}")
        return None


def verify_jwt_with_issuer_did(orb_url: str, vc_jwt: dict) -> bool:
    """
    Verifies a JWT Verifiable Credential using the issuer's DID Document.
    Args:
        orb_url: The base URL of the orb node (e.g., http://orb1.local)
        vc_jwt: The JWT Verifiable Credential to verify
    Returns:
        True if the JWT is valid and verified, False otherwise.
    """
    try:
        # Decode the JWS without verification to extract the header and payload
        # Extract the issuer DID from the payload
        payload = copy.deepcopy(vc_jwt)
        proof = payload.get("proof")
        # Decode the signature (Vault returns base64 under the hood but wrapped as "vault:v1:<b64>")
        sig_b64 = proof.get("jws").get("signature").split(":")[-1]
        sig_bytes = base64.b64decode(sig_b64)

        del payload["proof"]

        payload_bytes = json_encode(payload).encode("utf-8")
        b64_payload = base64.b64encode(payload_bytes).decode("utf-8")


        holder_did = vc_jwt.get("credentialSubject").get("did")
        if not holder_did:
            print("Issuer DID not found in the credential payload.")
            return False

        # Resolve the issuer's DID Document
        did_doc = resolve_did(orb_url, holder_did)
        if not did_doc:
            print("Failed to resolve issuer DID.")
            return False

        # Extract the public key from the DID Document
        public_keys = did_doc.get("didDocument", {}).get("verificationMethod", [])
        if not public_keys:
            print("No public keys found in the DID Document.")
            return False

        public_key_info = None
        for public_key in public_keys:
            if public_key.get("id") == proof.get("verificationMethod"):
                public_key_info = public_key
                break

        if not public_key_info:
            print("Verification method not found in the DID Document.")
            return False

        # Create a JWK object from the public key JWK
        jwk_key = jwk.JWK.from_json(json_encode(public_key_info.get("publicKeyJwk")))
        pubkey_pem = jwk_key.export_to_pem()
        public_key = serialization.load_pem_public_key(pubkey_pem)

        try:
            public_key.verify(sig_bytes, payload_bytes, ec.ECDSA(hashes.SHA256()))
            print("✅ Signature is valid!")
            return True
        except InvalidSignature:
            print("❌ Signature is INVALID!")
            return False

    except Exception as e:
        print(f"Error verifying JWT: {e}")
        return False

if __name__ == "__main__":
    # Example usage
    pem_key = """
        -----BEGIN EC PRIVATE KEY-----
        MHcCAQEEIPeVpJXwpTQSRYnz5NKlggsdDyKRGlUvYloRSazKxJw2oAoGCCqGSM49
        AwEHoUQDQgAECxtVp156uXThqN0zHFpgiN+RvFT31pcO3OMXLwX8sSqUTERMApUd
        80lBKaNngqo09MSnWcvHRFypEenmgMd5oQ==
        -----END EC PRIVATE KEY-----
    """
    data = {
        "crv":"P-256",
        "keyType":"EC",
        "type": "JsonWebKey2020",
        "keyID": "issuer-key-1"
    }

    signed_jws = sign_json_with_pem_key(data, pem_key, None)
    print("Signed JWS:", signed_jws)