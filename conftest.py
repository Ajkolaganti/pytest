import os
import pytest
import msal
import requests
from dotenv import load_dotenv

load_dotenv()

class GraphQLClient:
    def __init__(self):
        self.api_url = os.getenv('API_URL')
        self.access_token = self._get_access_token()
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
        })

    def _get_access_token(self):
        client_id = os.getenv('CLIENT_ID')
        client_secret = os.getenv('CLIENT_SECRET')
        tenant_id = os.getenv('TENANT_ID')
        scope = os.getenv('SCOPE')

        if not all([client_id, client_secret, tenant_id, scope]):
            raise ValueError("Missing required environment variables for authentication")

        authority = f'https://login.microsoftonline.com/{tenant_id}'
        app = msal.ConfidentialClientApplication(
            client_id=client_id,
            client_credential=client_secret,
            authority=authority
        )

        result = app.acquire_token_for_client(scopes=[scope])
        
        if 'access_token' not in result:
            raise Exception(f"Failed to acquire token: {result.get('error_description', 'Unknown error')}")
            
        return result['access_token']

    def execute_query(self, query, variables=None):
        payload = {
            'query': query,
            'variables': variables or {}
        }
        
        response = self.session.post(self.api_url, json=payload)
        response.raise_for_status()
        return response.json()

@pytest.fixture(scope="session")
def graphql_client():
    """Fixture that provides a GraphQL client instance."""
    try:
        client = GraphQLClient()
        return client
    except Exception as e:
        pytest.fail(f"Failed to initialize GraphQL client: {str(e)}")

@pytest.fixture
def load_query():
    """Fixture to load GraphQL queries from files."""
    def _load_query(filename):
        query_path = os.path.join('graphql_queries', filename)
        with open(query_path, 'r') as f:
            return f.read().strip()
    return _load_query 