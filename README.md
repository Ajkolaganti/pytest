# GraphQL API Testing Project

This project contains automated tests for the GraphQL API using Pytest. It includes authentication with bearer token and runs parameterized tests against multiple GraphQL queries.

## Important Note About IP Restrictions

The API endpoint is protected by IP restrictions and can only be accessed from work environment IPs. The tests will automatically skip if run from a non-work environment.

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and fill in your credentials:
   ```bash
   cp .env.example .env
   ```

## Environment Variables

- `BEARER_TOKEN`: Your API bearer token
- `API_URL`: GraphQL API endpoint

## Project Structure

```
├── graphql_queries/     # Directory containing .graphql query files
├── conftest.py         # Pytest fixtures and configuration
├── test_graphql_queries.py  # Test implementation
├── requirements.txt    # Project dependencies
├── .env.example       # Example environment variables
├── azure-pipelines.yml # CI/CD configuration
└── README.md          # This file
```

## Running Tests

To run tests:
```bash
pytest
```

Note: Tests will be skipped if run outside the work environment due to IP restrictions.

To generate HTML report:
```bash
pytest --html=report.html --self-contained-html
```

## CI/CD

The project includes Azure Pipelines configuration that:
- Runs on every commit to main branch
- Installs dependencies
- Sets up environment variables from Azure DevOps library
- Runs tests and generates HTML report
- Publishes test results and report as artifacts

Note: Ensure your CI/CD pipeline runs in an environment with allowed IP addresses.

## Adding New Queries

1. Create a new `.graphql` file in the `graphql_queries` directory
2. The file will automatically be included in the parameterized tests
3. Tests validate that responses contain either `data` or `errors` fields with correct types

## Troubleshooting

If you get a 403 Forbidden error:
1. Ensure you're running the tests from a work environment
2. Check that your bearer token is valid and not expired
3. If needed, connect to your work VPN before running tests 