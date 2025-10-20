import jwt
import json

token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyIiwiaXNzIjoiQVBJaVFnQUxLb0hwRVkzIiwibmJmIjoxNzYwNzc3NTcwLCJleHAiOjE3NjA3OTkxNzB9.NWl_SyJ1VFXMDrKBHvnS2zYepytB8wTQKtfX5tct2_U'

# Decode without verification to see payload
decoded = jwt.decode(token, options={'verify_signature': False})
print('📋 Decoded token payload:')
print(json.dumps(decoded, indent=2))
