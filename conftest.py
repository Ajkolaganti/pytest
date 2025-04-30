import os
import json
import pytest
import requests
from datetime import datetime
from dotenv import load_dotenv
import sys

load_dotenv()

def check_api_health():
    """Check if the API is healthy and if its schema has changed."""
    api_url = os.getenv('API_URL')
    bearer_token = os.getenv('BEARER_TOKEN')
    
    if not api_url or not bearer_token:
        print("API Health Check Failed: Missing API_URL or BEARER_TOKEN in environment variables")
        return False
        
    try:
        # Use POST with a simple introspection query
        headers = {
            'Content-Type': 'application/json',
            'Authorization': bearer_token
        }
        
        # Simple introspection query
        payload = {
            'query': '{ __typename }'
        }
        
        print(f"Checking API health at: {api_url}")
        response = requests.post(api_url, json=payload, headers=headers, verify=False)
        
        # Print response details for debugging
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text[:200]}...")  # Print first 200 chars
        
        if response.status_code not in (200, 400):  # Both are valid for GraphQL
            print(f"API Health Check Failed: Status code {response.status_code}")
            return False
            
        return True
    except Exception as e:
        print(f"API Health Check Failed: {str(e)}")
        return False

# Run API health check before tests
def pytest_configure(config):
    """Configure test session."""
    if not check_api_health():
        pytest.exit("API health check failed. Skipping tests.")
    
    # Initialize metadata if it doesn't exist
    if not hasattr(config, '_metadata'):
        config._metadata = {}
    
    # Add environment info
    config._metadata['GraphQL API URL'] = os.getenv('API_URL')
    config._metadata['Python Version'] = sys.version
    config._metadata['Timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

@pytest.hookimpl(optionalhook=True)
def pytest_html_report_title(report):
    """Set the title for the HTML report."""
    report.title = "GraphQL API Test Report"

@pytest.hookimpl(optionalhook=True)
def pytest_html_results_table_header(cells):
    """Add custom column headers to the HTML report."""
    cells.insert(2, "<th>Response Time</th>")
    cells.insert(3, "<th>Query</th>")
    cells.insert(4, "<th>Schema</th>")

@pytest.hookimpl(optionalhook=True)
def pytest_html_results_table_row(report, cells):
    """Add custom row data to the HTML report."""
    if hasattr(report, "response_time"):
        cells.insert(2, f"<td>{report.response_time:.2f}s</td>")
    else:
        cells.insert(2, "<td>N/A</td>")
    
    if hasattr(report, "graphql_query"):
        cells.insert(3, f"<td><pre>{report.graphql_query}</pre></td>")
    else:
        cells.insert(3, "<td>N/A</td>")
    
    if hasattr(report, "schema_validation"):
        cells.insert(4, f"<td>{report.schema_validation}</td>")
    else:
        cells.insert(4, "<td>N/A</td>")

def pytest_html_assets_path(config):
    return os.path.join(os.path.dirname(__file__), 'assets')

def pytest_html_report_data(report):
    # Add custom CSS
    report.style_sheets.append("custom.css")
    
    # Add custom JavaScript for collapsible sections
    report.scripts.append("""
        function toggleDetails(element) {
            var content = element.nextElementSibling;
            if (content.style.display === "none" || content.style.display === "") {
                content.style.display = "block";
                element.textContent = element.textContent.replace("▶", "▼");
            } else {
                content.style.display = "none";
                element.textContent = element.textContent.replace("▼", "▶");
            }
        }
        
        // Add collapsible functionality to all sections after page load
        window.addEventListener('load', function() {
            var sections = document.querySelectorAll('.collapsible');
            sections.forEach(function(section) {
                section.style.cursor = 'pointer';
                section.addEventListener('click', function() {
                    toggleDetails(this);
                });
                // Initially hide the content
                var content = section.nextElementSibling;
                if (content) {
                    content.style.display = 'none';
                }
            });
        });
    """)

# Store request/response data for reporting
class GraphQLRequestData:
    def __init__(self):
        self.clear()
    
    def clear(self):
        self.request_headers = None
        self.request_payload = None
        self.response_status = None
        self.response_body = None
        self.graphql_errors = None

request_data = GraphQLRequestData()

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
        # Clear previous request data
        request_data.clear()
        
        # Format the payload exactly like the curl example
        payload = {
            'query': query if query.startswith('query ') else f"query {query}"
        }
        if variables:
            payload['variables'] = variables
        
        # Store request data for reporting
        headers_for_report = dict(self.session.headers)
        headers_for_report['Authorization'] = '<token-hidden>'
        request_data.request_headers = headers_for_report
        request_data.request_payload = payload
        
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
            
            # Store response data for reporting
            request_data.response_status = response.status_code
            
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
                request_data.response_body = response_json
                print(json.dumps(response_json, indent=2))
                
                # Handle GraphQL errors
                if 'errors' in response_json:
                    request_data.graphql_errors = response_json['errors']
                    print("\nGraphQL Errors:")
                    for error in response_json['errors']:
                        print(f"- {error.get('message', str(error))}")
                        if 'locations' in error:
                            print(f"  Location: {error['locations']}")
                        if 'path' in error:
                            print(f"  Path: {error['path']}")
                
                # If we got a JSON response with GraphQL errors, that's valid
                if response.status_code == 400 and 'errors' in response_json:
                    return response_json
                    
                # For other status codes, raise the HTTP error
                response.raise_for_status()
                return response_json
                
            except json.JSONDecodeError:
                print("Raw response (not JSON):")
                print(response.text)
                request_data.response_body = response.text
                response.raise_for_status()
            
        except requests.exceptions.RequestException as e:
            print(f"\nRequest Error: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_json = e.response.json()
                    print("Error details:")
                    print(json.dumps(error_json, indent=2))
                    request_data.response_body = error_json
                except:
                    print(f"Raw error response: {e.response.text}")
                    request_data.response_body = e.response.text
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

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    
    # Add extra information to HTML report for test cases
    if report.when == "call":
        # Add request/response data if available
        if hasattr(request_data, 'request_payload'):
            report.extra = []
            
            # Add request details
            if request_data.request_headers:
                report.extra.append({
                    'name': 'Request Headers',
                    'content': json.dumps(request_data.request_headers, indent=2),
                    'format': 'json'
                })
            
            if request_data.request_payload:
                report.extra.append({
                    'name': 'Request Payload',
                    'content': json.dumps(request_data.request_payload, indent=2),
                    'format': 'json'
                })
            
            # Add response details
            if request_data.response_status:
                report.extra.append({
                    'name': 'Response Status',
                    'content': str(request_data.response_status)
                })
            
            if request_data.response_body:
                report.extra.append({
                    'name': 'Response Body',
                    'content': json.dumps(request_data.response_body, indent=2) if isinstance(request_data.response_body, (dict, list)) else str(request_data.response_body),
                    'format': 'json' if isinstance(request_data.response_body, (dict, list)) else 'text'
                })
            
            if request_data.graphql_errors:
                report.extra.append({
                    'name': 'GraphQL Errors',
                    'content': json.dumps(request_data.graphql_errors, indent=2),
                    'format': 'json'
                }) 