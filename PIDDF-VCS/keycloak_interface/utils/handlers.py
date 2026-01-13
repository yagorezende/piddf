from typing import List

from keycloak import KeycloakAdmin
from keycloak import KeycloakOpenIDConnection

from api import settings


class KeycloakHandler:
    def __init__(self, environ):
        self.environ = environ
        self.connection = None
        self.keycloak_admin = None

    def connect(self, user, password):
        if self.environ is None:
            raise Exception("Environment variables not found")
        self.connection = KeycloakOpenIDConnection(
            server_url=self.environ.KEYCLOAK_CONFIG.get("KEYCLOAK_SERVER_URL") + "/realms",
            username=user,
            password=password,
            realm_name=self.environ.KEYCLOAK_CONFIG.get("KEYCLOAK_REALM"),
            client_id="admin-cli",
            user_realm_name="master",
        )
        self.keycloak_admin = KeycloakAdmin(connection=self.connection)
        return self

    def get_realm_roles(self):
        roles = self.keycloak_admin.get_realm_roles()
        to_dict = {}
        for role in roles:
            if role['description'] == '${default-roles}':
                to_dict[role['name']] = role
        return to_dict

    def create_realm_role(self, name) -> str | None:
        """
        Create a role in Keycloak.
        :param name: the name of the role to create (must be unique)
        :return: keycloak role id or None if the role already exists
        """
        try:
            return self.keycloak_admin.create_realm_role({"name": name, "description": "${default_role}"})
        except Exception as e:
            raise Exception(f"Error creating role: {str(e)}")

    def get_realm_groups(self) -> List:
        return self.keycloak_admin.get_groups()

    def create_group(self, group_name) -> str | None:
        """
        Create a group in Keycloak.
        :param group_name: the name of the group to create (must be unique)
        :return: keycloak group id or None if the group already exists
        """
        try:
            return self.keycloak_admin.create_group({"name": group_name})
        except Exception as e:
            raise Exception(f"Error creating group: {str(e)}")

    def get_group(self, group_name) -> dict | None:
        """
        Get a group by name in Keycloak.
        :param group_name: the name of the group to retrieve
        :return: keycloak group id or None if the group does not exist
        """
        try:
            groups = self.keycloak_admin.get_groups(query={"search": group_name, "max": 1, "exact": True})
            return groups[0] if len(groups) == 1 else None
        except Exception as e:
            raise Exception(f"Error retrieving group: {str(e)}")

    def set_user_group(self, user_id, group_id):
        """
        Assign a user to a group in Keycloak.
        :param user_id: the ID of the user to assign
        :param group_id: the ID of the group to assign the user to
        """
        try:
            self.keycloak_admin.group_user_add(user_id, group_id)
        except Exception as e:
            raise Exception(f"Error assigning user to group: {str(e)}")

    def get_realm_role(self, role_name):
        return self.keycloak_admin.get_realm_role(role_name)

    def get_user(self, user_id):
        return self.keycloak_admin.get_user(user_id)

    def get_user_role(self, user_id):
        return self.keycloak_admin.get_realm_roles_of_user(user_id)

    def set_user_role(self, user_id, role):
        self.keycloak_admin.assign_realm_roles(user_id, role)

    def get_keycloak_user_by_email(self, email):
        try:
            users = self.keycloak_admin.get_users(query={"email": email, "max": 1, "exact": True})
            return users[0] if len(users) == 1 else None
        except Exception as e:
            return None

    def get_keycloak_user_list(self, query=None):
        """
        Get a list of users from Keycloak.
        :param query: optional query parameters to filter users
        :return: list of users
        """
        try:
            return self.keycloak_admin.get_users(query=query)
        except Exception as e:
            raise Exception(f"Error retrieving user list: {str(e)}")

    def get_keycloak_user_list_count(self, query=None) -> int:
        """
        Get the count of users in Keycloak.
        :return: count of users
        """
        try:
            return self.keycloak_admin.users_count(query)
        except Exception as e:
            raise Exception(f"Error retrieving user count: {str(e)}")


    def get_keycloak_user(self, username):
        try:
            return self.keycloak_admin.get_user(self.keycloak_admin.get_user_id(username))
        except Exception as e:
            return None

    def get_keycloak_user_id(self, username):
        return self.keycloak_admin.get_user_id(username)

    def set_user_attributes(self, user_id, attributes):
        """
        Set user attributes in Keycloak.
        :param user_id: the ID of the user to update
        :param attributes: a dictionary of attributes to set
        """
        try:
            self.keycloak_admin.update_user(user_id, {"attributes": attributes})
        except Exception as e:
            raise Exception(f"Error setting user attributes: {str(e)}")

    def create_keycloak_user(self, data):
        try:
            return self.keycloak_admin.create_user({
                "email": data['email'],
                "username": data['username'],
                "enabled": True,
                "firstName": data['name'].split(' ')[0],
                "lastName": ' '.join(x for x in data['name'].split(' ')[1::]),
                "emailVerified": True,
                "attributes": {
                    "locale": ["en"],
                    "userPublicKey": ["N/A"],
                    "userWalletAddress": ["N/A"],
                    "userLocationLat": ["0.0"],
                    "userLocationLong": ["0.0"],
                }
            })
        except Exception as e:
            return self.keycloak_admin.get_user_id(data['email'])

    def set_user_password(self, user_id, password, temporary=True):
        return self.keycloak_admin.set_user_password(user_id, password, temporary)


class KeyCloakRootConnection(KeycloakHandler):
    def __init__(self):
        super().__init__(settings)
        super().connect(settings.KEYCLOAK_ADMIN_USERNAME, settings.KEYCLOAK_ADMIN_PASSWORD)
