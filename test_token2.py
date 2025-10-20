"""Test LiveKit token generation with different approaches"""
import os
from livekit import api

# Load credentials
livekit_api_key = "APIiQgALKoHpEY3"
livekit_api_secret = "fwjTeWepQPijebcRRP6X97PF0zWBHRjlryR3EPH2CHcA"
room_name = "test-room-456"

print(f"Room: {room_name}\n")

# Approach 1: Chained with_grants
print("=== Approach 1: Chained ===")
try:
    token1 = api.AccessToken(livekit_api_key, livekit_api_secret)
    token1 = token1.with_identity("user")
    token1 = token1.with_name("User")
    video_grants = api.VideoGrants(room_join=True, room=room_name)
    token1 = token1.with_grants(video_grants)
    jwt1 = token1.to_jwt()
    print(f"✅ JWT: {jwt1[:150]}...")
    
    # Decode to check
    import base64
    import json
    payload = jwt1.split('.')[1]
    # Add padding
    payload += '=' * (4 - len(payload) % 4)
    decoded = json.loads(base64.urlsafe_b64decode(payload))
    print(f"📋 Decoded payload: {json.dumps(decoded, indent=2)}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
