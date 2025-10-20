"""Test the new token generation with method chaining"""
from livekit import api
import jwt
import json
import os

# Get credentials
livekit_api_key = os.getenv("LIVEKIT_API_KEY", "APIiQgALKoHpEY3")
livekit_api_secret = os.getenv("LIVEKIT_API_SECRET", "fwjTeWepQPijebcRRP6X97PF0zWBHRjlryR3EPH2CHcA")
room_name = "test-room-with-grants"

# Create VideoGrants
grants = api.VideoGrants(
    room_join=True,
    room=room_name,
    can_publish=True,
    can_subscribe=True,
    can_publish_data=True
)

# Create token using fluent API with method chaining
token = (api.AccessToken(livekit_api_key, livekit_api_secret)
        .with_identity("user")
        .with_name("User")
        .with_grants(grants))

access_token = token.to_jwt()

print(f"✅ JWT: {access_token}\n")

# Decode to verify
decoded = jwt.decode(access_token, options={'verify_signature': False})
print("📋 Decoded payload:")
print(json.dumps(decoded, indent=2))

# Check if video grants are present
if 'video' in decoded:
    print("\n✅ SUCCESS: 'video' claim is present in token!")
    print(f"   Room: {decoded['video'].get('room')}")
    print(f"   Room Join: {decoded['video'].get('roomJoin')}")
else:
    print("\n❌ ERROR: 'video' claim is MISSING from token!")
