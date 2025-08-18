#!/bin/bash
set -euo pipefail

ALLURE_RESULTS_BASE="${ALLURE_RESULTS_BASE:-/app/allure/allure-results}"
ALLURE_REPORT_BASE="${ALLURE_REPORT_BASE:-/app/allure/allure-report}"
TESTS_PATH="${TESTS_PATH:-tests}"
POETRY_BIN="${POETRY_BIN:-poetry}"
PYTEST_ARGS="${PYTEST_ARGS:- -v}"

mkdir -p "$ALLURE_RESULTS_BASE" "$ALLURE_REPORT_BASE"

failed=0

# -------------------------------
# Function: run tests for a specific DNS server
# -------------------------------
run_for_dns() {
    local dns="$1"
    
    # Sanitize DNS for filesystem paths (replace risky characters)
    local dns_safe="${dns//[:/]/_}"

    echo "=== Using DNS: $dns ==="
    echo "nameserver $dns" > /etc/resolv.conf
    echo "Current resolver:"
    cat /etc/resolv.conf

    local run_dir="${ALLURE_RESULTS_BASE}/${dns_safe}"
    local report_dir="${ALLURE_REPORT_BASE}/${dns_safe}"

    # Clean previous runs
    rm -rf "$run_dir" "$report_dir"
    mkdir -p "$run_dir"

    # Run tests but don't abort the whole script if pytest fails
    set +e
    $POETRY_BIN run python -m pytest $PYTEST_ARGS "$TESTS_PATH" --alluredir="$run_dir"
    local pytest_exit=$?
    set -e

    echo "Generating Allure report for DNS $dns -> $report_dir"
    allure generate "$run_dir" -o "$report_dir" --clean || true
    
    if [ $pytest_exit -ne 0 ]; then
        echo "Pytest failed for DNS $dns with exit code $pytest_exit"
        failed=1
    fi
}

# -------------------------------
# Main execution
# -------------------------------
if [ -n "${DNS_SERVERS:-}" ]; then
    echo "Running tests for DNS servers: $DNS_SERVERS"
    for dns in $DNS_SERVERS; do
        run_for_dns "$dns"
    done

else
    echo "No DNS_SERVERS specified. Running tests with default system DNS."

    run_dir="${ALLURE_RESULTS_BASE}/default"
    report_dir="${ALLURE_REPORT_BASE}/default"

    # Clean previous runs
    rm -rf "$run_dir" "$report_dir"
    mkdir -p "$run_dir"

    set +e
    $POETRY_BIN run python -m pytest $PYTEST_ARGS "$TESTS_PATH" --alluredir="$run_dir"
    pytest_exit=$?
    set -e

    echo "Generating Allure report for default DNS -> $report_dir"
    allure generate --single-file "$run_dir" -o "$report_dir" --clean || true
    
    if [ $pytest_exit -ne 0 ]; then
        failed=1
    fi
fi

echo "Allure reports are available under: $ALLURE_REPORT_BASE"
ls -1 "$ALLURE_REPORT_BASE" || true

# Exit with non-zero if any run failed (reports are still generated)
exit $failed