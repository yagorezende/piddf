class KeycloakACError(Exception):
    def __init__(self):
        self.message = "Keycloak middleware error."
        self.error_code = 500


class MissingTokenError(KeycloakACError):
    def __init__(self):
        self.message = "Missing token. Please send a token in the Authorization header."
        self.error_code = 401


class InvalidTokenError(KeycloakACError):
    def __init__(self):
        self.message = "Invalid token. Please send a valid token in the Authorization header."
        self.error_code = 401


class UnauthorizedError(KeycloakACError):
    def __init__(self):
        self.message = "Unauthorized. You do not have permission to perform this action."
        self.error_code = 403


class MissingScopeError(KeycloakACError):
    def __init__(self):
        self.message = "Missing scope. Please send a scope in the request header."
        self.error_code = 400
