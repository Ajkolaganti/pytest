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
            
        # Add Bearer prefix if not present
        if not self.bearer_token.startswith('Bearer '):
            self.bearer_token = f'Bearer {self.bearer_token}'
            
        self.session = requests.Session()
        
        # Set cookies that appear to be required
        self.session.cookies.set(
            'ARRAffinity',
            '7d577d29f8e00b2374ddb413016b2f6617c84445e3b963399a9d336135481e13',
            domain='azurewebsites.net'
        )
        self.session.cookies.set(
            'ARRAffinitySameSite',
            '7d577d29f8e00b2374ddb413016b2f6617c84445e3b963399a9d336135481e13',
            domain='azurewebsites.net'
        )
        
        # Update headers to match the curl example exactly
        self.session.headers.update({
            'Authorization': self.bearer_token,
            'Content-Type': 'application/json',
        })
        
        # Disable SSL verification for testing
        self.session.verify = False
        # Suppress SSL warnings
        requests.packages.urllib3.disable_warnings()

    def execute_query(self, query, variables=None):
        # Format the payload exactly like the curl example
        payload = {
            'query': query if query.startswith('query ') else f"query {query}"
        }
        if variables:
            payload['variables'] = variables
        
        # Log the request details
        print("\n=== GraphQL Request ===")
        print(f"URL: {self.api_url}")
        print("Headers:")
        for key, value in self.session.headers.items():
            # Hide the actual token value
            if key == 'Authorization':
                print(f"{key}: <token-hidden>")
            else:
                print(f"{key}: {value}")
        print("\nCookies:")
        for cookie in self.session.cookies:
            print(f"{cookie.name}: {cookie.value}")
        print("\nRequest Payload:")
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
            
            # Try to parse and format JSON response
            try:
                response_json = response.json()
                print(json.dumps(response_json, indent=2))
                
                # Handle GraphQL errors
                if 'errors' in response_json:
                    print("\nGraphQL Errors:")
                    for error in response_json['errors']:
                        print(f"- {error.get('message', str(error))}")
                        if 'locations' in error:
                            print(f"  Location: {error['locations']}")
                        if 'path' in error:
                            print(f"  Path: {error['path']}")
                
            except json.JSONDecodeError:
                print("Raw response (not JSON):")
                print(response.text)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"\nRequest Error: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_json = e.response.json()
                    print("Error details:")
                    print(json.dumps(error_json, indent=2))
                except:
                    print(f"Raw error response: {e.response.text}")
            raise

    def execute_query_file(self, query_file):
        """Execute a GraphQL query from a file."""
        with open(query_file, 'r') as f:
            query = f.read().strip()
        return self.execute_query(query)

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