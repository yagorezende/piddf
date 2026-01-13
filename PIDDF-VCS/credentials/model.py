from util.helpers import create_credential_payload


class IdentityModel:
    def __init__(self):
        self.keycloak_user_id = None
        self.full_name = None
        self.social_name = None
        self.birth_country = None
        self.birthday = None # type str ; format 'YYYY-MM-DD'
        self.email = None
        self.access_token = None
        self.openbao_token = None
        self.did = None
        self.height = None
        self.gender = None
        self.image_blob = None

    def to_vc_json(self) -> dict:
        """
        Convert the identity model to a verifiable credential JSON payload.
        model: Person from https://w3c-ccg.github.io/citizenship-vocab/contexts/citizenship-v2.jsonld
        :return: dict representing the verifiable credential
        """
        return {
            "additionalName": self.social_name,
            "email": self.email,
            "birthCountry": self.birth_country,
            "birthDate": self.birthday,
            "familyName": self.full_name.split()[-1] if self.full_name else None,
            "gender": self.gender,
            "givenName": self.full_name.split()[0] if self.full_name else None,
            "height": self.height,
            "image": self.image_blob,
        }

    def from_json(self, vc: dict) -> "IdentityModel":
        """
        Populate the identity model from a verifiable credential JSON payload.
        :param vc: dict representing the verifiable credential
        :return: IdentityModel instance
        """
        self.social_name = vc.get("additionalName")
        self.email = vc.get("email")
        self.birth_country = vc.get("birthCountry")
        self.birthday = vc.get("birthDate")
        self.full_name = f"{vc.get('givenName', '')} {vc.get('familyName', '')}"
        self.gender = vc.get("gender")
        self.height = vc.get("height")
        self.image_blob = vc.get("image")
        return self

    def to_credential_payload(self, issuer_did: str, holder_did: str, issuer_oidc) -> dict:
        """
        Create a verifiable credential payload using the identity model.
        :return: dict representing the verifiable credential payload
        """
        credential_subject = self.to_vc_json()
        credential_payload = create_credential_payload(
            issuer_did=issuer_did,
            holder_did=holder_did,
            subject_data=credential_subject,
            issuer_oidc=issuer_oidc,
            credential_type="Profile",
        )

        return credential_payload