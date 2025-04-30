import os
import pytest
import requests

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

@pytest.mark.parametrize('query_file', get_query_files())
def test_graphql_query(graphql_client, load_query, query_file):
    """Test each GraphQL query file."""
    # Load the query from file
    query = load_query(query_file)
    
    try:
        # Execute the query
        response = graphql_client.execute_query(query)
        
        # Assert response structure
        assert isinstance(response, dict), f"Response for {query_file} is not a dictionary"
        assert 'data' in response or 'errors' in response, \
            f"Response for {query_file} must contain either 'data' or 'errors'"
        
        # If there are GraphQL errors, the test should still pass
        # as long as they are well-formed errors
        if 'errors' in response:
            assert isinstance(response['errors'], list), \
                f"'errors' in response for {query_file} must be a list"
            for error in response['errors']:
                assert 'message' in error, \
                    f"Error in response for {query_file} must have a message"
        
        # If there is data, validate its structure
        if 'data' in response:
            assert isinstance(response['data'], dict), \
                f"'data' in response for {query_file} must be a dictionary"
            
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Query {query_file} failed with error: {str(e)}")

def test_invalid_query(graphql_client):
    """Test handling of invalid query."""
    invalid_query = "{ invalid { field } }"
    
    response = graphql_client.execute_query(invalid_query)
    assert 'errors' in response, "Invalid query should return errors"
    assert isinstance(response['errors'], list), "Errors should be a list" 