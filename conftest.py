import os
import json
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
        # Disable SSL verification for testing
        self.session.verify = False
        # Suppress SSL warnings
        requests.packages.urllib3.disable_warnings()

    def execute_query(self, query, variables=None):
        payload = {
            'query': query,
            'variables': variables or {}
        }
        
        # Log the request details
        print("\n=== GraphQL Request ===")
        print(f"URL: {self.api_url}")
        print("Headers:")
        for key, value in self.session.headers.items():
            # Hide the actual token value
            if key == 'Authorization':
                print(f"{key}: Bearer <token-hidden>")
            else:
                print(f"{key}: {value}")
        print("\nQuery:")
        print(json.dumps(payload, indent=2))
        
        try:
            response = self.session.post(self.api_url, json=payload)
            
            # Log the response details
            print("\n=== GraphQL Response ===")
            print(f"Status Code: {response.status_code}")
            print("Response Headers:")
            for key, value in response.headers.items():
                print(f"{key}: {value}")
            print("\nResponse Body:")
            try:
                print(json.dumps(response.json(), indent=2))
            except:
                print(response.text)
                
            # Handle 403 Forbidden specifically
            if response.status_code == 403:
                print("\nAccess Forbidden - Possible causes:")
                print("1. IP address not whitelisted")
                print("2. Invalid or expired bearer token")
                print("3. Insufficient permissions")
                
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"\nError: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response text: {e.response.text}")
            raise

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