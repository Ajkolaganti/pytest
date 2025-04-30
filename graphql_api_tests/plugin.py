import pytest
import json
import time
import os
from datetime import datetime
from pathlib import Path

def pytest_configure(config):
    """Add custom markers and initialize test metrics."""
    config.addinivalue_line("markers", "api: mark test as an API test")
    config.addinivalue_line("markers", "schema: mark test as a schema validation test")
    
    # Initialize metrics storage
    config._graphql_metrics = {
        'start_time': time.time(),
        'response_times': [],
        'total_queries': 0,
        'failed_queries': 0,
        'schema_violations': 0,
        'error_types': {},
        'error_details': []
    }
    
    # Create directories for error artifacts
    artifacts_dir = Path(os.getenv('TEST_REPORT_DIR', 'test-reports'))
    config._error_artifacts_dir = artifacts_dir / 'error_artifacts'
    config._error_artifacts_dir.mkdir(parents=True, exist_ok=True)

def pytest_runtest_setup(item):
    """Setup test metrics collection."""
    item._start_time = time.time()
    item._error_details = []

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Enhanced error reporting with detailed logs and screenshots."""
    outcome = yield
    report = outcome.get_result()
    
    if not hasattr(item.config, '_graphql_metrics'):
        return
    
    metrics = item.config._graphql_metrics
    
    if call.when == 'call':
        # Calculate response time
        response_time = time.time() - item._start_time
        metrics['response_times'].append(response_time)
        report.response_time = response_time
        
        # Track query execution and collect detailed error info
        if 'api' in item.keywords:
            metrics['total_queries'] += 1
            if call.excinfo:
                metrics['failed_queries'] += 1
                error_type = type(call.excinfo.value).__name__
                metrics['error_types'][error_type] = metrics['error_types'].get(error_type, 0) + 1
                
                # Collect detailed error information
                error_detail = {
                    'test_name': item.name,
                    'error_type': error_type,
                    'error_message': str(call.excinfo.value),
                    'traceback': str(call.excinfo.traceback),
                    'timestamp': datetime.now().isoformat()
                }
                
                # Add request/response details if available
                if hasattr(item, '_request_data'):
                    error_detail['request'] = item._request_data
                if hasattr(item, '_response_data'):
                    error_detail['response'] = item._response_data
                
                metrics['error_details'].append(error_detail)
                
                # Save detailed error log
                error_log_path = item.config._error_artifacts_dir / f"error_{item.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(error_log_path, 'w') as f:
                    json.dump(error_detail, f, indent=2)
                
                # Capture screenshot if webdriver is available
                try:
                    if hasattr(item, 'funcargs') and 'driver' in item.funcargs:
                        driver = item.funcargs['driver']
                        screenshot_path = item.config._error_artifacts_dir / f"screenshot_{item.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                        driver.save_screenshot(str(screenshot_path))
                        error_detail['screenshot'] = str(screenshot_path)
                except Exception as e:
                    print(f"Failed to capture screenshot: {str(e)}")
                
                # Add error details to the report
                if not hasattr(report, 'sections'):
                    report.sections = []
                
                report.sections.append((
                    "Error Details",
                    f"Error Type: {error_type}\n"
                    f"Error Message: {str(call.excinfo.value)}\n"
                    f"Traceback:\n{call.excinfo.traceback}\n"
                    f"Error artifacts saved to: {item.config._error_artifacts_dir}"
                ))
        
        # Track schema violations
        if 'schema' in item.keywords and call.excinfo:
            metrics['schema_violations'] += 1

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Add custom summary to terminal output."""
    if not hasattr(config, '_graphql_metrics'):
        return
    
    metrics = config._graphql_metrics
    
    # Calculate execution time
    total_time = time.time() - metrics['start_time']
    avg_response = sum(metrics['response_times']) / len(metrics['response_times']) if metrics['response_times'] else 0
    
    # Print summary
    terminalreporter.write_sep("=", "GraphQL API Test Summary")
    terminalreporter.write_line(f"Total Execution Time: {total_time:.2f}s")
    terminalreporter.write_line(f"Average Response Time: {avg_response:.2f}s")
    terminalreporter.write_line(f"Total Queries: {metrics['total_queries']}")
    terminalreporter.write_line(f"Failed Queries: {metrics['failed_queries']}")
    terminalreporter.write_line(f"Schema Violations: {metrics['schema_violations']}")
    
    if metrics['error_types']:
        terminalreporter.write_line("\nError Types:")
        for error_type, count in metrics['error_types'].items():
            terminalreporter.write_line(f"  {error_type}: {count}")

def pytest_html_report_title(report):
    """Customize the HTML report title."""
    report.title = "GraphQL API Test Report"

def pytest_html_results_table_header(cells):
    """Add custom columns to the HTML report."""
    cells.insert(2, "<th>Response Time</th>")
    cells.insert(3, "<th>Query</th>")
    cells.insert(4, "<th>Schema</th>")

def pytest_html_results_table_row(report, cells):
    """Enhanced HTML report with error details."""
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
    
    # Add error details if available
    if hasattr(report, 'sections'):
        for name, content in report.sections:
            cells.append(f"<td class='error-details'><pre>{content}</pre></td>")

def pytest_html_results_summary(prefix, summary, postfix):
    """Enhanced summary with error details."""
    if hasattr(pytest.config, '_graphql_metrics'):
        metrics = pytest.config._graphql_metrics
        
        # Create metrics summary
        summary.extend([
            "<div class='metrics-summary'>",
            "<h2>Test Metrics</h2>",
            "<table>",
            f"<tr><td>Total Execution Time:</td><td>{time.time() - metrics['start_time']:.2f}s</td></tr>",
            f"<tr><td>Average Response Time:</td><td>{sum(metrics['response_times']) / len(metrics['response_times']) if metrics['response_times'] else 0:.2f}s</td></tr>",
            f"<tr><td>Total Queries:</td><td>{metrics['total_queries']}</td></tr>",
            f"<tr><td>Failed Queries:</td><td>{metrics['failed_queries']}</td></tr>",
            f"<tr><td>Schema Violations:</td><td>{metrics['schema_violations']}</td></tr>",
            "</table>",
            "</div>"
        ])
        
        # Add error breakdown
        if metrics['error_types']:
            summary.extend([
                "<div class='error-breakdown'>",
                "<h2>Error Breakdown</h2>",
                "<table>",
                *[f"<tr><td>{error_type}:</td><td>{count}</td></tr>" 
                  for error_type, count in metrics['error_types'].items()],
                "</table>",
                "</div>"
            ])
            
        # Add detailed error section
        if metrics['error_details']:
            summary.extend([
                "<div class='detailed-errors'>",
                "<h2>Detailed Error Reports</h2>",
                "<div class='error-list'>",
                *[f"""
                    <div class='error-item'>
                        <h3>{error['test_name']}</h3>
                        <p class='error-type'>{error['error_type']}</p>
                        <p class='error-message'>{error['error_message']}</p>
                        <pre class='error-traceback'>{error['traceback']}</pre>
                        {'<img src="' + error['screenshot'] + '" class="error-screenshot">' if 'screenshot' in error else ''}
                    </div>
                """ for error in metrics['error_details']],
                "</div>",
                "</div>"
            ]) 