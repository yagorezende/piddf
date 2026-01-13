#!/bin/bash
# This script automates the creation of issuer and subject DIDs and issues an Identity Card VC using the Trustbloc CLI.
# Usage: ./automate_identity_card_vc.sh <name> <birthDate> <documentNumber>

set -e

PROFILE_ID="labgen_issuer"
PROFILE_VERSION="v1.0"
ORB_URL="http://orb1.local"

NAME="$1"
BIRTH_DATE="$2"
DOCUMENT_NUMBER="$3"

if [ -z "$NAME" ] || [ -z "$BIRTH_DATE" ] || [ -z "$DOCUMENT_NUMBER" ]; then
  echo "Usage: $0 <name> <birthDate> <documentNumber>"
  exit 1
fi

cd "$(dirname "$0")"

# Create issuer DID
echo "Creating issuer DID..."
ISSUER_DID=$(python3 cli.py create_did --orb-url "$ORB_URL" | grep 'DID created:' | awk '{print $3}')
if [ -z "$ISSUER_DID" ]; then
  echo "Failed to create issuer DID."
  exit 1
fi

# Create subject DID
echo "Creating subject DID..."
SUBJECT_DID=$(python3 cli.py create_did --orb-url "$ORB_URL" | grep 'DID created:' | awk '{print $3}')
if [ -z "$SUBJECT_DID" ]; then
  echo "Failed to create subject DID."
  exit 1
fi

echo "Issuer DID: $ISSUER_DID"
echo "Subject DID: $SUBJECT_DID"

echo "Issuing Identity Card VC..."
python3 cli.py issue_identity_card_vc \
  --profile-id "$PROFILE_ID" \
  --profile-version "$PROFILE_VERSION" \
  --issuer-did "$ISSUER_DID" \
  --subject-did "$SUBJECT_DID" \
  --name "$NAME" \
  --birth-date "$BIRTH_DATE" \
  --document-number "$DOCUMENT_NUMBER"

