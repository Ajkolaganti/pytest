# GraphQL API Testing Project

This project contains automated tests for the GraphQL API using Pytest. It includes authentication with Microsoft Entra ID (Azure AD) and runs parameterized tests against multiple GraphQL queries.

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

- `CLIENT_ID`: Azure AD client ID
- `CLIENT_SECRET`: Azure AD client secret
- `TENANT_ID`: Azure AD tenant ID
- `SCOPE`: API scope for authentication
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

To run tests locally:
```bash
pytest
```

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

## Adding New Queries

1. Create a new `.graphql` file in the `graphql_queries` directory
2. The file will automatically be included in the parameterized tests
3. Tests validate that responses contain either `data` or `errors` fields with correct types 