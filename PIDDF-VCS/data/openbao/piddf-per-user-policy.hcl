path "transit/keys/{{identity.entity.aliases.$jwt_accessor_id.metadata.sub}}-did-key" {
  capabilities = ["create", "read", "update", "patch", "delete", "list", "scan"]
}

path "transit/keys/{{identity.entity.aliases.$jwt_accessor_id.metadata.sub}}-recovery-key" {
  capabilities = ["create", "read", "update", "patch", "delete", "list", "scan"]
}

path "transit/keys/{{identity.entity.aliases.$jwt_accessor_id.metadata.sub}}-update-key" {
  capabilities = ["create", "read", "update", "patch", "delete", "list", "scan"]
}

path "transit/sign/{{identity.entity.aliases.$jwt_accessor_id.metadata.sub}}-did-key" {
  capabilities = ["update"]
}

path "transit/sign/{{identity.entity.aliases.$jwt_accessor_id.metadata.sub}}-recovery-key" {
  capabilities = ["update"]
}

path "transit/sign/{{identity.entity.aliases.$jwt_accessor_id.metadata.sub}}-update-key" {
  capabilities = ["update"]
}

path "transit/keys" {
  capabilities = ["list"]
}