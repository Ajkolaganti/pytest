from setuptools import setup, find_packages

setup(
    name="graphql-api-tests",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pytest>=8.0.0",
        "pytest-html>=4.1.1",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        "jsonschema>=4.0.0",
        "msal>=1.20.0"
    ],
    python_requires=">=3.11",
    
    # Metadata
    author="Your Name",
    author_email="your.email@example.com",
    description="Automated tests for GraphQL API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    
    # Package data
    package_data={
        "": ["schemas/*.json", "assets/*.css"]
    },
    
    # Entry points
    entry_points={
        "pytest11": [
            "graphql-api-tests = graphql_api_tests.plugin",
        ],
    },
    
    # Classifiers
    classifiers=[
        "Framework :: Pytest",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Testing",
        "Private :: Do Not Upload"
    ]
) 