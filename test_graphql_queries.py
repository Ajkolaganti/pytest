import os
import pytest
import requests
import re

def get_query_files():
    """Helper function to get all .graphql files from the queries directory."""
    query_dir = 'graphql_queries'
    if not os.path.exists(query_dir):
        return []
    return [f for f in os.listdir(query_dir) if f.endswith('.graphql')]

# def is_work_environment():
#     """Check if we're in the work environment by trying to access the API."""
#     try:
#         response = requests.get(os.getenv('API_URL'), verify=False)
#         return response.status_code != 403
#     except:
#         return False

# # Skip all tests if not in work environment
# pytestmark = pytest.mark.skipif(
#     not is_work_environment(),
#     reason="Tests can only be run from work environment due to IP restrictions"
# )

def is_valid_graphql_query(query):
    """Validate if the string is a proper GraphQL query."""
    # Remove comments and whitespace
    query = re.sub(r'#.*$', '', query, flags=re.MULTILINE).strip()
    
    # Basic GraphQL query structure validation
    if not query.startswith(('query', 'mutation', '{')):
        return False
    
    # Check for balanced braces
    brace_count = 0
    for char in query:
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
        if brace_count < 0:
            return False
    
    return brace_count == 0

@pytest.mark.parametrize('query_file', get_query_files())
def test_graphql_query(graphql_client, load_query, query_file):
    """Test each GraphQL query file."""
    # Load the query from file
    query = load_query(query_file)
    
    # Validate query structure
    assert is_valid_graphql_query(query), f"Invalid GraphQL query structure in {query_file}"
    
    try:
        # Execute the query
        response = graphql_client.execute_query(query)
        
        # Assert response structure
        assert isinstance(response, dict), f"Response for {query_file} is not a dictionary"
        assert 'data' in response or 'errors' in response, \
            f"Response for {query_file} must contain either 'data' or 'errors'"
        
        # If there are GraphQL errors, fail the test with error details
        if 'errors' in response:
            error_messages = [error.get('message', str(error)) for error in response['errors']]
            pytest.fail(f"GraphQL query in {query_file} failed with errors: {', '.join(error_messages)}")
        
        # Validate data structure
        assert 'data' in response, f"Response for {query_file} must contain 'data'"
        assert isinstance(response['data'], dict), \
            f"'data' in response for {query_file} must be a dictionary"
        
        # Validate that data is not empty
        assert response['data'], f"Response data for {query_file} should not be empty"
        
        # Validate that at least one field exists in the response
        assert len(response['data']) > 0, f"Response for {query_file} should have at least one field"
            
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Query {query_file} failed with error: {str(e)}")

def test_invalid_query(graphql_client):
    """Test handling of invalid query."""
    invalid_query = "{ invalid { field } }"
    
    response = graphql_client.execute_query(invalid_query)
    assert 'errors' in response, "Invalid query should return errors"
    assert isinstance(response['errors'], list), "Errors should be a list"
    assert len(response['errors']) > 0, "Should have at least one error message"
    assert 'message' in response['errors'][0], "Error should have a message" 