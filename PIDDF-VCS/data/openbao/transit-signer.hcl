# transit-signer.hcl
path "transit/keys/ec-p256-key" {
    # Allows reading public key and key configuration metadata
    capabilities = ["read"]
}

path "transit/sign/ec-p256-key" {
    # Allows cryptographic signing (Key Issuance/Usage)
    capabilities = ["update"]
}

path "transit/verify/ec-p256-key" {
    # Allows signature verification
    capabilities = ["update"]
}

path "transit/keys/ec-p256-key/soft-delete" {
    # Allows soft deletion of the key
    capabilities = ["update"]
}

path "transit/keys/ec-p256-key/soft-delete-restore" {
    # Allows restoration of a softly deleted key (Key Recovery)
    capabilities = ["update"]
}