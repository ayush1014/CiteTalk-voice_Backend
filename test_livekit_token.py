"""Test LiveKit token generation"""
import os
from livekit import api

# Load credentials
livekit_api_key = os.getenv("LIVEKIT_API_KEY", "APIiQgALKoHpEY3")
livekit_api_secret = os.getenv("LIVEKIT_API_SECRET", "fwjTeWepQPijebcRRP6X97PF0zWBHRjlryR3EPH2CHcA")
room_name = "test-room-123"

print(f"API Key: {livekit_api_key}")
print(f"Room: {room_name}")
print()

# Try different approaches
print("=== Approach 1: Direct property assignment ===")
try:
    token1 = api.AccessToken(livekit_api_key, livekit_api_secret)
    token1.identity = "user"
    token1.name = "User"
    token1.video_grants = api.VideoGrants(
        room_join=True,
        room=room_name
    )
    jwt1 = token1.to_jwt()
    print(f"✅ Success! Token: {jwt1[:100]}...")
except Exception as e:
    print(f"❌ Error: {e}")

print()
print("=== Approach 2: Using add_grant method (if exists) ===")
try:
    token2 = api.AccessToken(livekit_api_key, livekit_api_secret)
    token2.identity = "user"
    token2.name = "User"
    grants = api.VideoGrants(room_join=True, room=room_name)
    token2.add_grant(grants)  # This might not exist
    jwt2 = token2.to_jwt()
    print(f"✅ Success! Token: {jwt2[:100]}...")
except Exception as e:
    print(f"❌ Error: {e}")

print()
print("=== Approach 3: Check AccessToken attributes ===")
token3 = api.AccessToken(livekit_api_key, livekit_api_secret)
print(f"Available attributes: {[attr for attr in dir(token3) if not attr.startswith('_')]}")
