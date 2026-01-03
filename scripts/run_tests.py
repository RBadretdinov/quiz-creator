#!/usr/bin/env python3
"""
Comprehensive Test Runner for Quiz Application

This script runs all tests in the application and provides detailed reporting.
"""

import os
import sys
import subprocess
import time
import json
from pathlib import Path
from typing import Dict, List, Any
import argparse

class TestRunner:
    """Comprehensive test runner for the quiz application."""
    
    def __init__(self, verbose: bool = False, coverage: bool = False):
        """Initialize test runner."""
        self.verbose = verbose
        self.coverage = coverage
        self.results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'skipped_tests': 0,
            'test_suites': [],
            'start_time': None,
            'end_time': None,
            'duration': 0
        }
        
        # Test suites to run
        self.test_suites = [
            'tests/test_models.py',
            'tests/test_quiz_engine.py',
            'tests/test_quiz_session.py',
            'tests/test_data_persistence.py',
            'tests/test_enhanced_tag_system.py',
            'tests/test_performance_optimization_phase_5_3.py',
            'tests/test_error_handling_validation_phase_5_2.py',
            'tests/test_import_export_phase_4_2.py',
            'tests/test_enhanced_console_phase_4_3.py',
            'tests/test_ocr_phase_4_1.py'
        ]
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all test suites and return results."""
        print("🧪 Starting Comprehensive Test Suite")
        print("=" * 60)
        
        self.results['start_time'] = time.time()
        
        for test_suite in self.test_suites:
            if os.path.exists(test_suite):
                print(f"\n📋 Running {test_suite}...")
                suite_results = self.run_test_suite(test_suite)
                self.results['test_suites'].append(suite_results)
            else:
                print(f"⚠️  Test suite not found: {test_suite}")
        
        self.results['end_time'] = time.time()
        self.results['duration'] = self.results['end_time'] - self.results['start_time']
        
        # Calculate totals
        for suite in self.results['test_suites']:
            self.results['total_tests'] += suite['total_tests']
            self.results['passed_tests'] += suite['passed_tests']
            self.results['failed_tests'] += suite['failed_tests']
            self.results['skipped_tests'] += suite['skipped_tests']
        
        return self.results
    
    def run_test_suite(self, test_suite: str) -> Dict[str, Any]:
        """Run a single test suite."""
        suite_results = {
            'name': test_suite,
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'skipped_tests': 0,
            'duration': 0,
            'start_time': None,
            'end_time': None,
            'output': '',
            'errors': []
        }
        
        start_time = time.time()
        suite_results['start_time'] = start_time
        
        try:
            # Build command
            cmd = [sys.executable, test_suite]
            if self.verbose:
                cmd.append('-v')
            
            # Run test suite
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=os.getcwd()
            )
            
            suite_results['end_time'] = time.time()
            suite_results['duration'] = suite_results['end_time'] - start_time
            suite_results['output'] = result.stdout + result.stderr
            
            # Parse output for test results
            self.parse_test_output(suite_results, result.stdout)
            
            if result.returncode == 0:
                print(f"✅ {test_suite} - PASSED")
            else:
                print(f"❌ {test_suite} - FAILED")
                suite_results['errors'].append(f"Exit code: {result.returncode}")
        
        except Exception as e:
            suite_results['end_time'] = time.time()
            suite_results['duration'] = suite_results['end_time'] - start_time
            suite_results['errors'].append(str(e))
            print(f"❌ {test_suite} - ERROR: {e}")
        
        return suite_results
    
    def parse_test_output(self, suite_results: Dict, output: str) -> None:
        """Parse test output to extract test counts."""
        lines = output.split('\n')
        
        for line in lines:
            if 'test' in line.lower() and ('ok' in line.lower() or 'fail' in line.lower()):
                if 'ok' in line.lower():
                    suite_results['passed_tests'] += 1
                elif 'fail' in line.lower():
                    suite_results['failed_tests'] += 1
            
            # Count test methods
            if line.strip().startswith('test_'):
                suite_results['total_tests'] += 1
    
    def run_coverage_analysis(self) -> Dict[str, Any]:
        """Run coverage analysis if enabled."""
        if not self.coverage:
            return {}
        
        print("\n📊 Running Coverage Analysis...")
        
        try:
            # Run coverage
            cmd = [
                sys.executable, '-m', 'pytest', '--cov=src', 
                '--cov-report=html', '--cov-report=json',
                'tests/'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            coverage_results = {
                'coverage_output': result.stdout,
                'coverage_errors': result.stderr,
                'exit_code': result.returncode
            }
            
            # Try to read coverage report
            if os.path.exists('coverage.json'):
                with open('coverage.json', 'r') as f:
                    coverage_data = json.load(f)
                    coverage_results['coverage_data'] = coverage_data
            
            return coverage_results
        
        except Exception as e:
            return {'error': str(e)}
    
    def generate_report(self) -> str:
        """Generate comprehensive test report."""
        report = []
        report.append("🧪 Quiz Application - Test Report")
        report.append("=" * 60)
        report.append("")
        
        # Summary
        report.append("📊 Test Summary")
        report.append("-" * 20)
        report.append(f"Total Tests: {self.results['total_tests']}")
        report.append(f"Passed: {self.results['passed_tests']}")
        report.append(f"Failed: {self.results['failed_tests']}")
        report.append(f"Skipped: {self.results['skipped_tests']}")
        report.append(f"Success Rate: {(self.results['passed_tests'] / max(self.results['total_tests'], 1)) * 100:.1f}%")
        report.append(f"Duration: {self.results['duration']:.2f} seconds")
        report.append("")
        
        # Test Suites
        report.append("📋 Test Suites")
        report.append("-" * 20)
        for suite in self.results['test_suites']:
            status = "✅ PASSED" if suite['failed_tests'] == 0 else "❌ FAILED"
            report.append(f"{suite['name']}: {status}")
            report.append(f"  Tests: {suite['total_tests']}, Passed: {suite['passed_tests']}, Failed: {suite['failed_tests']}")
            report.append(f"  Duration: {suite['duration']:.2f}s")
            if suite['errors']:
                report.append(f"  Errors: {', '.join(suite['errors'])}")
            report.append("")
        
        # Coverage (if enabled)
        if self.coverage:
            report.append("📊 Coverage Analysis")
            report.append("-" * 20)
            report.append("Coverage report generated in htmlcov/")
            report.append("")
        
        # Recommendations
        report.append("💡 Recommendations")
        report.append("-" * 20)
        if self.results['failed_tests'] > 0:
            report.append("• Fix failing tests before deployment")
            report.append("• Review test output for specific failures")
        if self.results['total_tests'] < 100:
            report.append("• Consider adding more test cases")
        if self.results['duration'] > 300:
            report.append("• Consider optimizing slow tests")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def save_report(self, filename: str = "test_report.txt") -> None:
        """Save test report to file."""
        report = self.generate_report()
        
        with open(filename, 'w') as f:
            f.write(report)
        
        print(f"📄 Test report saved to {filename}")
    
    def print_summary(self) -> None:
        """Print test summary."""
        print("\n" + "=" * 60)
        print("🧪 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.results['total_tests']}")
        print(f"Passed: {self.results['passed_tests']}")
        print(f"Failed: {self.results['failed_tests']}")
        print(f"Skipped: {self.results['skipped_tests']}")
        print(f"Success Rate: {(self.results['passed_tests'] / max(self.results['total_tests'], 1)) * 100:.1f}%")
        print(f"Duration: {self.results['duration']:.2f} seconds")
        
        if self.results['failed_tests'] > 0:
            print("\n❌ Some tests failed. Check the output above for details.")
        else:
            print("\n✅ All tests passed!")
        
        print("=" * 60)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Run comprehensive test suite')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--coverage', '-c', action='store_true', help='Run coverage analysis')
    parser.add_argument('--report', '-r', action='store_true', help='Generate test report')
    parser.add_argument('--output', '-o', default='test_report.txt', help='Output file for report')
    
    args = parser.parse_args()
    
    # Create test runner
    runner = TestRunner(verbose=args.verbose, coverage=args.coverage)
    
    # Run tests
    results = runner.run_all_tests()
    
    # Run coverage if requested
    if args.coverage:
        coverage_results = runner.run_coverage_analysis()
        results['coverage'] = coverage_results
    
    # Generate report if requested
    if args.report:
        runner.save_report(args.output)
    
    # Print summary
    runner.print_summary()
    
    # Exit with appropriate code
    if results['failed_tests'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
