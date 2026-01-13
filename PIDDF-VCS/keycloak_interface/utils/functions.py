from flask import Request

from keycloak_interface.errors import MissingTokenError
from keycloak_interface.utils.handlers import KeyCloakRootConnection


def extract_header_token(request: Request) -> str:
    """
    Validate the request token against Keycloak.
    :param request: flask request object containing the Authorization header
    :return: token string (raises MissingTokenError if no token is provided)
    """
    token = request.headers.get('Authorization')
    if not token or not token.startswith('Bearer '):
        raise MissingTokenError()
    return token.split(' ')[1]


def get_keycloak_user(username):
    return KeyCloakRootConnection().get_keycloak_user_id(username)


def get_keycloak_user_by_email(email):
    return KeyCloakRootConnection().get_keycloak_user_by_email(email)


def get_keycloak_user_roles(user_id):
    roles = [role['name'] for role in KeyCloakRootConnection().get_user_role(user_id)]
    return roles


def get_keycloak_organisation_roles():
    return KeyCloakRootConnection().get_realm_roles()


def create_keycloak_organisation_role(name) -> str | None:
    return KeyCloakRootConnection().create_realm_role(name)


def get_keycloak_organization_groups():
    return KeyCloakRootConnection().get_realm_groups()


def create_keycloak_organisation_group(name) -> str | None:
    return KeyCloakRootConnection().create_group(name)


def get_or_create_keycloak_user(username, email, name, password, role):
    keycloak_user_id = get_keycloak_user(username)
    keycloak_root_connection = KeyCloakRootConnection()
    created = False
    if keycloak_user_id is None:
        created = True
        keycloak_user_id = keycloak_root_connection.create_keycloak_user(
            {"username": username, "email": email, "name": name})
        keycloak_root_connection.set_user_password(keycloak_user_id, password, False)
    # role_obj = keycloak_root_connection.get_realm_role(role)
    # keycloak_root_connection.set_user_role(keycloak_user_id, role_obj)
    keycloak_user = keycloak_root_connection.get_user(keycloak_user_id)
    return keycloak_user, created
