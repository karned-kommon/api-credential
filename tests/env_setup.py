import os

# Set environment variables required by the application
os.environ['API_NAME'] = 'test-api'
os.environ['API_TAG_NAME'] = 'test-tag'
os.environ['URL_API_GATEWAY'] = 'http://test-gateway'
os.environ['KEYCLOAK_HOST'] = 'http://test-keycloak'
os.environ['KEYCLOAK_REALM'] = 'test-realm'
os.environ['KEYCLOAK_CLIENT_ID'] = 'test-client-id'
os.environ['KEYCLOAK_CLIENT_SECRET'] = 'test-client-secret'
os.environ['REDIS_HOST'] = 'test-redis'
os.environ['REDIS_PORT'] = '6379'
os.environ['REDIS_DB'] = '0'
os.environ['REDIS_PASSWORD'] = 'test-password'
os.environ['VAULT_HOST'] = 'test-vault'
os.environ['VAULT_PORT'] = '8200'
os.environ['VAULT_TOKEN'] = 'test-token'
os.environ['VAULT_SECRET_PATH'] = 'test-path'