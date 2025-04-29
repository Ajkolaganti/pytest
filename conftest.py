import os
import pytest
import requests
from dotenv import load_dotenv

load_dotenv()

class GraphQLClient:
    def __init__(self):
        self.api_url = os.getenv('API_URL')
        self.bearer_token = os.getenv('BEARER_TOKEN')
        
        if not self.bearer_token:
            raise ValueError("Missing BEARER_TOKEN in environment variables")
            
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.bearer_token}',
            'Content-Type': 'application/json',
        })

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