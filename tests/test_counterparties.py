import pytest
from graphql_client import GraphQLClient

def test_get_counterparties(graphql_client):
    """Test retrieving counterparties list"""
    # Execute the query
    response = graphql_client.execute_query_file('graphql_queries/get_counterparties.graphql')
    
    # Verify the response structure
    assert 'data' in response
    assert 'counterparties' in response['data']
    
    counterparties = response['data']['counterparties']
    
    # Verify the response contains all expected fields
    assert 'totalCount' in counterparties
    assert 'edges' in counterparties
    assert 'nodes' in counterparties
    assert 'pageInfo' in counterparties
    
    # Verify pageInfo structure
    page_info = counterparties['pageInfo']
    assert all(key in page_info for key in ['endCursor', 'hasNextPage', 'hasPreviousPage', 'startCursor'])
    
    # If there are any counterparties, verify their structure
    if counterparties['totalCount'] > 0:
        # Check first node in edges
        first_edge = counterparties['edges'][0]
        assert 'cursor' in first_edge
        assert 'node' in first_edge
        
        # Check first node in nodes
        first_node = counterparties['nodes'][0]
        
        # Verify all expected fields are present in the node
        expected_fields = {
            'aba', 'accountName', 'address1', 'address2', 'bankName',
            'city', 'contactName', 'counterpartyEmailAddress', 'counterpartyId',
            'counterpartyName', 'createdBy', 'createdDt', 'dda',
            'departmentName', 'state', 'updatedBy', 'updatedDt', 'zip'
        }
        
        assert all(field in first_node for field in expected_fields) 