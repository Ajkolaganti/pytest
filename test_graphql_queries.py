import os
import pytest

def get_query_files():
    """Helper function to get all .graphql files from the queries directory."""
    query_dir = 'graphql_queries'
    if not os.path.exists(query_dir):
        return []
    return [f for f in os.listdir(query_dir) if f.endswith('.graphql')]

@pytest.mark.parametrize('query_file', get_query_files())
def test_graphql_query(graphql_client, load_query, query_file):
    """Test each GraphQL query file."""
    # Load the query from file
    query = load_query(query_file)
    
    # Execute the query
    try:
        response = graphql_client.execute_query(query)
        
        # Assert response structure
        assert isinstance(response, dict), f"Response for {query_file} is not a dictionary"
        assert 'data' in response or 'errors' in response, \
            f"Response for {query_file} must contain either 'data' or 'errors'"
        
        # Validate data if present
        if 'data' in response:
            assert isinstance(response['data'], dict), \
                f"'data' in response for {query_file} must be a dictionary"
            
        # Validate errors if present
        if 'errors' in response:
            assert isinstance(response['errors'], list), \
                f"'errors' in response for {query_file} must be a list"
            
    except Exception as e:
        pytest.fail(f"Query {query_file} failed with error: {str(e)}")

def test_invalid_query(graphql_client):
    """Test handling of invalid query."""
    invalid_query = "{ invalid { field } }"
    
    response = graphql_client.execute_query(invalid_query)
    assert 'errors' in response, "Invalid query should return errors"
    assert isinstance(response['errors'], list), "Errors should be a list" 