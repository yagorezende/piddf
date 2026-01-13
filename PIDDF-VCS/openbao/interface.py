import requests
import base64
import json
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePublicKey
from jwcrypto.common import json_encode
from jwcrypto.jwk import JWK
from jwcrypto.jwt import JWT

ACCESS_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJmQW5uY1BMTUstNWN0Zl9td0x0c1hDWGlvQjVjUTZQSzlVVU5uWTdrLXk0In0.eyJleHAiOjE3NjA3ODU3NjksImlhdCI6MTc2MDY5OTM2OSwianRpIjoiNzk2YmY1NTktM2JhNC00MDQzLWEyNjAtZGI3ZDgyZGE3YmFmIiwiaXNzIjoiaHR0cDovL2xvY2FsaG9zdDo3MDgwL2F1dGgvcmVhbG1zL2xhYmdlbiIsImF1ZCI6ImFjY291bnQiLCJzdWIiOiJkODc2NTZmOS05MzhmLTQyZDgtYTkyMC02NTFjYzY2OTRiNGYiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJwaWRkZiIsInNpZCI6ImJjMjM4NjgwLTUwZjQtNGNlZC05NzllLTQ2ZTUyOTcyYTU2YSIsImFjciI6IjEiLCJhbGxvd2VkLW9yaWdpbnMiOlsiKiJdLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsib2ZmbGluZV9hY2Nlc3MiLCJ1bWFfYXV0aG9yaXphdGlvbiIsImRlZmF1bHQtcm9sZXMtbGFiZ2VuIl19LCJyZXNvdXJjZV9hY2Nlc3MiOnsiYWNjb3VudCI6eyJyb2xlcyI6WyJtYW5hZ2UtYWNjb3VudCIsIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwidmlldy1wcm9maWxlIl19fSwic2NvcGUiOiJlbWFpbCBwcm9maWxlIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsIm5hbWUiOiJZYWdvIFJlemVuZGUiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJ5YWdvcmV6ZW5kZSIsImdpdmVuX25hbWUiOiJZYWdvIiwiZmFtaWx5X25hbWUiOiJSZXplbmRlIiwiZW1haWwiOiJ5YWdvcmV6ZW5kZUBpZC51ZmYuYnIifQ.owgcRGTmrh8nwHV6pVHbmsBVL4_QrNLZc3ZJiVM1GJ5KbCAsPxIyQlYUUQTyvHku0_gE3ANqsySFGJ2H287mhS2A8FdvCT7UnlJF1QeG5oyHlvQ-AvyrYDAZMIBnJuW5l-8zB48t2u-cRNyh1VFeii5tqQCL0OF4HGWYNspfxAbAb0q9eGz3nVSn94kHAP-5w5XoOUlq2lKQ0U0dnISG8KLMGd8PZJla_riUI1VlLt6ZY541HUqJhyZ9lLoUs9YiD7A3GgT3xTgxTmDrLbPzup07ZYUIt5anbEBgwyVCRS8cL9Pp0JzWFulQY34thAopUsv9elsibeLaYS8fKyM7xw"
COUNTER_ACCESS_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJmQW5uY1BMTUstNWN0Zl9td0x0c1hDWGlvQjVjUTZQSzlVVU5uWTdrLXk0In0.eyJleHAiOjE3NjAzOTM0MDMsImlhdCI6MTc2MDM5MzEwMywianRpIjoiYTc3MTAzNzYtNWNiYy00NDNjLThiM2QtZjc5MWVlZjRhMGYwIiwiaXNzIjoiaHR0cDovL2xvY2FsaG9zdDo3MDgwL2F1dGgvcmVhbG1zL2xhYmdlbiIsImF1ZCI6ImFjY291bnQiLCJzdWIiOiJjNWI0MTQwNy0yNzFiLTRmZjMtYTU2Ny1jNmQxNWQyY2I1ODEiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJwaWRkZiIsInNpZCI6IjQ1Y2Y0Mjk2LWU4MWItNDkwMi1hYjYxLWQzZjI0ZjcwOTdkNSIsImFjciI6IjEiLCJhbGxvd2VkLW9yaWdpbnMiOlsiKiJdLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsib2ZmbGluZV9hY2Nlc3MiLCJ1bWFfYXV0aG9yaXphdGlvbiIsImRlZmF1bHQtcm9sZXMtbGFiZ2VuIl19LCJyZXNvdXJjZV9hY2Nlc3MiOnsiYWNjb3VudCI6eyJyb2xlcyI6WyJtYW5hZ2UtYWNjb3VudCIsIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwidmlldy1wcm9maWxlIl19fSwic2NvcGUiOiJlbWFpbCBwcm9maWxlIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsIm5hbWUiOiJZYWdvIFJlemVuZGUiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJ5YWdvcmV6ZW5kZTIiLCJnaXZlbl9uYW1lIjoiWWFnbyIsImZhbWlseV9uYW1lIjoiUmV6ZW5kZSIsImVtYWlsIjoieWFnb3JlemVuZGVAbWlkaWFjb20udWZmLmJyIn0.kOCXuT-ehyjP2RP8bKsiQWoV3Jlw2BzYRLwO3JjptjNUs810ug-iMNsvskl4ykg7jR1OhPKqqE2QYUdbHy9vYX_zFWSzhSqWu9XznxE48t4wwQxpGNRPkScOQIJTPzTQ6a28_PEdBpYvTaPjQUaBuquqJ3B-JisjDUdX_Yh3yHkei9sVv1I7k3U3hRllb9WxJZ3z9Vv1DI9ovgFdGVVd1SG1kynePqai_iyuYNRcdJ3QVk9LTBm-zZFugK0A_LK8ZwfNYEfIqaxLWqPRVkvCHoKUnmqWx3wpJLgYgiMyyhq8G1OvCGSDGzOTRwKm5q9dTid2ktXLUwB2ARNklEAfpg"
ACCEPT_KEY_TYPES = {"did-key", "recovery-key", "update-key"}


class OpenBaoInterface:
    def __init__(self, open_bao_address: str, open_bao_token: str, oidc_token_url: str, oidc_client_id: str, oidc_client_secret: str):
        self.open_bao_address = open_bao_address
        self.open_bao_token = open_bao_token
        self.oidc_token_url = oidc_token_url
        self.oidc_client_id = oidc_client_id
        self.oidc_client_secret = oidc_client_secret
        self.headers = {"X-Vault-Token": open_bao_token}

    @staticmethod
    def get_bao_headers(bao_token: str) -> dict:
        return {"X-Vault-Token": bao_token}

    @staticmethod
    def get_jwt_token(access_token: str) -> dict:
        """
        Extracts and returns the payload of a JWT access token.
        :param access_token: str - The JWT access token.
        :return: the payload of the JWT token as a dictionary.
        """

        # Decode the JWT token to extract the 'sub' claim
        headers = access_token.split(".")[0] + "=="
        payload = access_token.split(".")[1] + "=="
        content = json.loads(base64.urlsafe_b64decode(payload).decode())
        content["access_token"] = access_token
        content["headers"] = json.loads(base64.urlsafe_b64decode(headers).decode())
        return content

    def get_jwk_key(self, key_type: str, jwt: dict, bao_headers: dict) -> JWK:

        if key_type not in ACCEPT_KEY_TYPES:
            raise ValueError(f"Invalid key_type '{key_type}'. Must be one of {ACCEPT_KEY_TYPES}.")

        self.enable_transit_engine()

        user_sub = jwt["sub"]
        key_name = f"{user_sub}-{key_type}"

        # === Fetch public key ===
        resp = requests.get(
            f"{self.open_bao_address}/v1/transit/keys/{key_name}",
            headers=bao_headers
        )
        if resp.status_code != 200:
            raise Exception(f"Error fetching key: {resp.text}")

        pubkey_pem = resp.json()["data"]["keys"]["1"]["public_key"]
        print("📜 Public Key PEM:\n", pubkey_pem)

        jwk = serialization.load_pem_public_key(pubkey_pem.encode())
        jwk = JWK.from_pyca(jwk)

        return jwk

    def get_jwt_open_bao_accessor_id(self):
        data = self.auth_list()

        accessor_id = data.get("jwt/", {}).get("accessor", None)
        # print("JWT Accessor ID:", accessor_id)

        if not accessor_id:
            raise Exception("JWT auth method not enabled or accessor ID not found.")

        return accessor_id

    def enable_jwt_auth(self, jwks_url: str, issuer: str, policy_hcl: str, transit_policy_name: str = "piddf-per-user-policy"):
        # Enable jwt auth method
        resp = requests.post(
            f"{self.open_bao_address}/v1/sys/auth/jwt",
            headers=self.headers,
            json={"type": "jwt"}
        )
        print("Enable jwt:", resp.status_code, resp.text)

        jwt_accessor_id = self.get_jwt_open_bao_accessor_id()

        resp = requests.post(
            f"{self.open_bao_address}/v1/auth/jwt/config",
            headers=self.headers,
            json={
                "jwks_url": jwks_url,
                "issuer": issuer,
                "accessor": jwt_accessor_id,
                # "bound_issuer": issuer,
                # "oidc_client_id": self.oidc_client_id,
                # "oidc_client_secret": self.oidc_client_secret,
                # "oidc_discovery_url": issuer,
            }
        )
        print("Config jwt:", resp.status_code, resp.text)

        jwt_accessor_id = self.get_jwt_open_bao_accessor_id()
        print("JWT Accessor ID:", jwt_accessor_id)
        # adjust the policy to include the accessor ID
        policy_hcl = policy_hcl.replace("$jwt_accessor_id", jwt_accessor_id)

        resp = requests.put(
            f"{self.open_bao_address}/v1/sys/policy/{transit_policy_name}",
            headers=self.headers,
            json={
                "policy": policy_hcl
            }
        )
        print("Policy write:", resp.status_code, resp.text)

        role_data = {
            "role_type": "jwt",
            "bound_audiences": "account",
            "user_claim": "sub",
            "claim_mappings": {"sub": "sub"},
            "policies": transit_policy_name,
            "ttl": "365d"
        }

        resp = requests.post(
            f"{self.open_bao_address}/v1/auth/jwt/role/default-roles-labgen",
            headers=self.headers,
            json=role_data
        )
        print("Role create:", resp.status_code, resp.text)

    def get_bao_token_for_user(self, access_token: str) -> str:
        resp = requests.post(
            f"{self.open_bao_address}/v1/auth/jwt/login",
            json={"role": "default-roles-labgen", "jwt": access_token}
        )
        bao_token = resp.json()["auth"]["client_token"]
        print("OpenBao token:", bao_token)
        return bao_token

    def setup_per_user_auth(self, jwks_url: str, issuer: str, access_token: str, policy_hcl: str | None, skip_creation: bool = False) -> str:
        if not skip_creation:
            self.enable_jwt_auth(jwks_url, issuer, policy_hcl, "piddf-per-user-policy")
        return self.get_bao_token_for_user(access_token)

    def setup_client_auth(self, jwks_url: str, issuer: str, policy_hcl: str | None, skip_creation: bool = False) -> str:
        if not skip_creation:
            self.enable_jwt_auth(jwks_url, issuer, policy_hcl)

        resp = requests.post(
            self.oidc_token_url,
            data={
                "grant_type": "client_credentials",
                "client_id": self.oidc_client_id,
                "client_secret": self.oidc_client_secret
            }
        )
        kc_token = resp.json()["access_token"]
        print("KC Token:", kc_token[:40], "...")

        resp = requests.post(
            f"{self.open_bao_address}/v1/auth/jwt/login",
            json={"role": "default-roles-labgen", "jwt": kc_token}
        )
        bao_token = resp.json()["auth"]["client_token"]
        print("OpenBao token:", bao_token)
        return bao_token

    def enable_transit_engine(self):
        resp = requests.post(
            f"{self.open_bao_address}/v1/sys/mounts/transit",
            headers=self.headers,
            json={"type": "transit"}
        )
        if resp.status_code not in (200, 204):
            print("✅ Transit engine may already be enabled. No action needed.")

    def test_create_key(self, key_name: str, bao_headers: dict):
        self.enable_transit_engine()
        # === 1. Check if key exists ===
        resp = requests.get(
            f"{self.open_bao_address}/v1/transit/keys/{key_name}",
            headers=bao_headers
        )
        if resp.status_code == 200:
            print(f"Key '{key_name}' already exists. Deleting it first...")
        else:
            print(f"Key '{key_name}' does not exist. Proceeding to create it...")

            # === 2. Create EC P-256 key ===
            resp = requests.post(
                f"{self.open_bao_address}/v1/transit/keys/{key_name}",
                headers=bao_headers,
                json={"type": "ecdsa-p256"}
            )

            if resp.status_code >= 400:
                raise Exception(f"Error creating key: {resp.text}")

            print(f"Key '{key_name}' created successfully.")


    def list_keys(self, bao_headers: dict):
        self.enable_transit_engine()
        # === List keys ===
        resp = requests.get(
            f"{self.open_bao_address}/v1/transit/keys?list=true",
            headers=bao_headers
        )
        if resp.status_code != 200:
            return []

        keys = resp.json().get("data", {}).get("keys", [])
        print("Available keys:", keys)
        return keys

    def create_key_for_user(self, key_type: str, user_jwt: dict, bao_headers: dict):
        """
        Creates a key in OpenBao for a specific user based on their JWT 'sub' claim.
        The key is named using the 'sub' claim to ensure uniqueness per user.
        :param key_type: str - The type of key to create possible values: did-key, recovery-key, or update-key.
        :param user_jwt: dict - The JWT token decoded to a dictionary.
        :param bao_headers: dict - Headers including the OpenBao token for authentication.
        :return: the name of the created key.
        """

        if key_type not in ACCEPT_KEY_TYPES:
            raise ValueError(f"Invalid key_type '{key_type}'. Must be one of {ACCEPT_KEY_TYPES}.")

        self.enable_transit_engine()
        user_sub = user_jwt["sub"]
        key_name = f"{user_sub}-{key_type}"
        # key_name = f"{user_sub}"

        # === 1. Check if key exists ===
        resp = requests.get(
            f"{self.open_bao_address}/v1/transit/keys/{key_name}",
            headers=bao_headers
        )
        if resp.status_code == 200:
            print(f"Key '{key_name}' already exists. returning existing key.")
            return key_name
        else:
            print(f"Key '{key_name}' does not exist. Proceeding to create it...")

            # === 2. Create EC P-256 key ===
            resp = requests.post(
                f"{self.open_bao_address}/v1/transit/keys/{key_name}",
                headers=bao_headers,
                json={"type": "ecdsa-p256"}
            )

            if resp.status_code >= 400:
                raise Exception(f"Error creating key: {resp.text}")

            print(f"Key '{key_name}' created successfully.")
        return key_name

    def verify_signature(self, key_name: str, payload: dict, signature: str, bao_headers: dict) -> bool:
        self.enable_transit_engine()
        # === 1. Fetch public key ===
        resp = requests.get(
            f"{self.open_bao_address}/v1/transit/keys/{key_name}",
            headers=bao_headers
        )
        if resp.status_code != 200:
            raise Exception(f"Error fetching key: {resp.text}")

        pubkey_pem = resp.json()["data"]["keys"]["1"]["public_key"]
        print("📜 Public Key PEM:\n", pubkey_pem)

        # Decode the signature (Vault returns base64 under the hood but wrapped as "vault:v1:<b64>")
        sig_b64 = signature.split(":")[-1]
        sig_bytes = base64.b64decode(sig_b64)

        # Load public key
        public_key = serialization.load_pem_public_key(pubkey_pem.encode())

        # Hash the original payload (Vault signs SHA256 digest of input bytes)
        payload_bytes = json.dumps(payload).encode()

        try:
            public_key.verify(sig_bytes, payload_bytes, ec.ECDSA(hashes.SHA256()))
            print("✅ Signature is valid!")
            return True
        except InvalidSignature:
            print("❌ Signature is INVALID!")
            return False

    def sign_payload(self, key_name: str, payload: dict, bao_headers: dict) -> dict:
        self.enable_transit_engine()
        # === 1. Sign data ===
        payload_bytes = json_encode(payload).encode("utf-8")
        b64_payload = base64.b64encode(payload_bytes).decode("utf-8")

        resp = requests.post(
            f"{self.open_bao_address}/v1/transit/sign/{key_name}",
            headers=bao_headers,
            json={"input": b64_payload}
        )
        if resp.status_code != 200:
            raise Exception(f"Error signing payload: {resp.text}")

        signature = resp.json()["data"]["signature"]
        print("🔑 Signature:", signature)
        return resp.json()["data"]

    def test_sign_verify_payload(self, key_name: str, payload: dict, bao_headers: dict):
        self.enable_transit_engine()
        # === 1. Sign data ===
        b64_payload = base64.b64encode(json.dumps(payload).encode()).decode()

        resp = requests.post(
            f"{self.open_bao_address}/v1/transit/sign/{key_name}",
            headers=bao_headers,
            json={"input": b64_payload}
        )
        signature = resp.json()["data"]["signature"]
        print("🔑 Signature:", signature)

        # === 5. Fetch public key ===
        resp = requests.get(
            f"{self.open_bao_address}/v1/transit/keys/{key_name}",
            headers=bao_headers
        )
        pubkey_pem = resp.json()["data"]["keys"]["1"]["public_key"]
        print("📜 Public Key PEM:\n", pubkey_pem)

        # === 6. Verify signature ===
        # Decode the signature (Vault returns base64 under the hood but wrapped as "vault:v1:<b64>")
        sig_b64 = signature.split(":")[-1]
        sig_bytes = base64.b64decode(sig_b64)

        # Load public key
        public_key = serialization.load_pem_public_key(pubkey_pem.encode())

        # Hash the original payload (Vault signs SHA256 digest of input bytes)
        payload_bytes = json.dumps(payload).encode()

        try:
            public_key.verify(sig_bytes, payload_bytes, ec.ECDSA(hashes.SHA256()))
            print("✅ Signature is valid!")
        except InvalidSignature:
            print("❌ Signature is INVALID!")

    def test(self, key_name: str):
        # 1. Enable the transit engine (safe to ignore errors if already enabled)
        print("🔑 Enabling transit engine...")
        resp = requests.post(
            f"{self.open_bao_address}/v1/sys/mounts/transit",
            headers=self.headers,
            json={"type": "transit"}
        )
        if resp.status_code not in (200, 204):
            print("Transit engine may already be enabled:", resp.text)

        # 2. Create an EC P-256 key
        print("🔑 Creating EC P-256 key...")
        resp = requests.post(
            f"{self.open_bao_address}/v1/transit/keys/{key_name}",
            headers=self.headers,
            json={"type": "ecdsa-p256"}
        )
        print("Key creation response:", resp.status_code, resp.text)

        # 3. Sign a JSON object
        payload = {"sub": "alice", "role": "admin"}
        payload_bytes = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        b64_payload = base64.b64encode(payload_bytes).decode("utf-8")

        print("🖊️ Signing payload:", payload)
        resp = requests.post(
            f"{self.open_bao_address}/v1/transit/sign/{key_name}",
            headers=self.headers,
            json={"input": b64_payload}
        )
        if resp.status_code != 200:
            raise Exception(f"Error signing: {resp.text}")
        signature = resp.json()["data"]["signature"]
        print("✅ Signature:", signature)

        # 4. Fetch the public key
        print("🔎 Fetching public key...")
        resp = requests.get(
            f"{self.open_bao_address}/v1/transit/keys/{key_name}",
            headers=self.headers
        )
        if resp.status_code != 200:
            raise Exception(f"Error fetching key: {resp.text}")
        pubkey_info = resp.json()["data"]["keys"]

        print("✅ Public keys:")
        print(json.dumps(pubkey_info, indent=2))

    def delete_key(self, key_name: str, bao_headers: dict):
        self.enable_transit_engine()
        # === Delete key ===
        resp = requests.delete(
            f"{self.open_bao_address}/v1/transit/keys/{key_name}",
            headers=bao_headers
        )
        if resp.status_code != 204:
            raise Exception(f"Error deleting key: {resp.text}")

        print(f"Key '{key_name}' deleted successfully.")

    def auth_list(self):
        # get root token info
        resp = requests.get(
            f"{self.open_bao_address}/v1/sys/auth",
            headers=self.headers
        )
        if resp.status_code != 200:
            raise Exception(f"Error listing auth methods: {resp.text}")

        auths = resp.json()
        # print("Auth methods:", json.dumps(auths, indent=2))
        return auths


if __name__ == "__main__":

    policy_hcl = open("../../data/openbao/piddf-per-user-policy.hcl").read()
    print("Policy HCL:\n", policy_hcl)

    openbao = OpenBaoInterface(
        "http://localhost:8200",
        "3fTaTH2dfpawAZdCi6E3ab",
        "http://localhost:7080/auth/realms/labgen/protocol/openid-connect/token",
        "piddf",
        "HBpOpbw86JRGhaj5eImDLmYNwSq6u76y"
    )
    # bao_token = openbao.setup_client_auth(
    #     "http://keycloak:7080/auth/realms/labgen/protocol/openid-connect/certs",
    #     "http://keycloak:7080/auth/realms/labgen",
    #     policy_hcl
    # )

    # change the token to a JWT encoded token for testing per-user auth
    jwt = OpenBaoInterface.get_jwt_token(ACCESS_TOKEN)

    bao_token = openbao.setup_per_user_auth(
        "http://keycloak:7080/auth/realms/labgen/protocol/openid-connect/certs",
        "http://keycloak:7080/auth/realms/labgen",
        ACCESS_TOKEN,
        policy_hcl
    )

    bao_headers = openbao.get_bao_headers(bao_token)

    # # list auth methods
    # openbao.auth_list()
    #
    # openbao.list_keys(bao_headers)
    #
    # did_key_name = openbao.create_key_for_user("did-key", jwt, bao_headers)
    # openbao.create_key_for_user("update-key", jwt, bao_headers)
    # openbao.create_key_for_user("recovery-key", jwt, bao_headers)
    #
    # public_key = openbao.get_jwk_key("did-key", jwt, bao_headers)
    #
    # # openbao.test_sign_verify_payload("piddf_key", {"sub": "alice", "role": "admin"}, bao_headers)
    #
    # openbao.list_keys(bao_headers)
    # openbao.delete_key('d87656f9-938f-42d8-a920-651cc6694b4f', bao_headers)
    # openbao.list_keys(bao_headers)
    print("Done") #auth_token_c8c48ea1
