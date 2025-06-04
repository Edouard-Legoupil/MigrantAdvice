import json
import os
import pathlib
import logging
import argparse # Added
import dataclasses # Added for asdict
from typing import List, Optional, Dict, Any

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Assuming the script is run from the project root 'migrant_llm_test_framework/'
try:
    from core_types.data_classes import TestCase, TestResult, MigrantProfile
    from llm_wrappers.llm_interface import LLMAdviser, MockLLMAdviser
    from evaluators.evaluator import run_evaluation
except ImportError as e:
    logging.error(f"Failed to import necessary modules. Ensure PYTHONPATH is set correctly or script is run from project root. Error: {e}")
    # Critical error, re-raise to stop execution if core modules are missing
    raise

def parse_arguments() -> argparse.Namespace:
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(description="Run LLM Migrant Advice Tests.")
    parser.add_argument(
        "--test_cases_dir", type=str, default="./test_cases",
        help="Directory containing test case category subdirectories."
    )
    parser.add_argument(
        "--profiles_dir", type=str, default="./profiles",
        help="Directory containing migrant profile JSON files."
    )
    parser.add_argument(
        "--results_dir", type=str, default="./results",
        help="Directory to save result reports."
    )
    parser.add_argument(
        "--categories", type=str, nargs='*', default=None,
        help="Optional list of categories to run (e.g., A_accuracy_relevance B_bias_fairness). Runs all if not specified."
    )
    parser.add_argument(
        "--llm_type", type=str, default="mock", choices=["mock"], # Add more choices as they are implemented
        help="Specify which LLM to use (currently only 'mock' is available)."
    )
    parser.add_argument(
        "--output_filename", type=str, default="test_results.json",
        help="Filename for the JSON report (saved in results_dir)."
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="Enable verbose logging (DEBUG level)."
    )
    args = parser.parse_args()
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    logging.debug(f"Parsed arguments: {args}")
    return args

def generate_summary_report(test_results: List[TestResult], results_dir: pathlib.Path, output_filename: str):
    """Generates a console summary and saves results to a JSON file."""
    if not test_results:
        logging.info("No test results to report.")
        return

    passed_count = sum(1 for r in test_results if r.pass_fail)
    failed_count = len(test_results) - passed_count

    # Console Summary
    print("\n--- Test Execution Summary ---")
    print(f"Total Tests Run: {len(test_results)}")
    print(f"Tests Passed: {passed_count}")
    print(f"Tests Failed: {failed_count}")

    if failed_count > 0:
        print("\nFailed Tests:")
        for r in test_results:
            if not r.pass_fail:
                # Attempt to get category from test_case object if available in TestResult, or from raw_scores
                # For now, we'll rely on the test_id naming convention for a simple category grouping for now.
                category_key = "Unknown"
                if r.test_case_id and '_' in r.test_case_id:
                    category_key = r.test_case_id.split('_')[0]

                print(f"  - Test ID: {r.test_case_id}, Score: {r.scores.get('overall_assessment_score', 'N/A')}, Category: {category_key}")

    # Category breakdown
    category_summary: Dict[str, Dict[str, int]] = {}
    for r in test_results:
        category_key = "unknown_category"
        if r.test_case_id and '_' in r.test_case_id:
            category_key = r.test_case_id.split('_')[0] # Heuristic: ar_001 -> ar

        if category_key not in category_summary:
            category_summary[category_key] = {"passed": 0, "failed": 0, "total": 0}

        category_summary[category_key]["total"] += 1
        if r.pass_fail:
            category_summary[category_key]["passed"] += 1
        else:
            category_summary[category_key]["failed"] += 1

    if category_summary:
        print("\nCategory Breakdown:")
        for cat, counts in category_summary.items():
            print(f"  - Category '{cat}': {counts['passed']}/{counts['total']} passed.")


    # JSON File Output
    results_dir.mkdir(parents=True, exist_ok=True) # Ensure results_dir exists
    output_path = results_dir / output_filename

    # Convert TestResult objects to dictionaries for JSON serialization
    results_as_dicts = [dataclasses.asdict(r) for r in test_results]

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results_as_dicts, f, indent=4)
        logging.info(f"Full test results saved to: {output_path}")
    except Exception as e:
        logging.error(f"Failed to save JSON report to {output_path}: {e}")


# --- Functions from previous step (discover_test_files, load_test_case_from_file, etc.) ---
# --- Assume they are already present in the worker's version of the file ---
# --- Only showing changes and new functions here for brevity ---

def discover_test_files(test_cases_dir: pathlib.Path, specific_categories: Optional[List[str]] = None) -> List[pathlib.Path]:
    """Scans test_cases_dir for .json test case files."."""
    found_files = []
    if not test_cases_dir.is_dir():
        logging.error(f"Test cases directory not found: {test_cases_dir}")
        return found_files

    categories_to_scan_dirs = []
    if specific_categories:
        for cat_name in specific_categories:
            cat_dir = test_cases_dir / cat_name
            if cat_dir.is_dir():
                categories_to_scan_dirs.append(cat_dir)
            else:
                logging.warning(f"Specified category directory not found: {cat_dir}")
        if not categories_to_scan_dirs:
            logging.warning(f"None of the specified categories were found: {specific_categories}")
    else:
        categories_to_scan_dirs = [d for d in test_cases_dir.iterdir() if d.is_dir()]

    for category_dir in categories_to_scan_dirs:
        for filepath in category_dir.glob("*.json"):
            found_files.append(filepath)

    logging.info(f"Discovered {len(found_files)} test files from specified criteria.")
    return found_files

def load_test_case_from_file(filepath: pathlib.Path) -> Optional[TestCase]:
    """Loads a TestCase object from a JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        required_fields = ["test_id", "category", "migrant_profile_id", "query"]
        if not all(field in data for field in required_fields):
            logging.warning(f"Skipping invalid test case file (missing required fields): {filepath}")
            return None
        return TestCase(**data)
    except json.JSONDecodeError:
        logging.warning(f"Skipping invalid JSON file: {filepath}")
        return None
    except Exception as e:
        logging.error(f"Error loading test case from {filepath}: {e}")
        return None

def load_migrant_profile(profile_id: str, profiles_dir: pathlib.Path) -> Optional[MigrantProfile]:
    """Loads a MigrantProfile object from a JSON file using profile_id."""
    profile_filepath = profiles_dir / f"{profile_id}.json"
    try:
        if not profile_filepath.exists():
            logging.warning(f"Profile file not found: {profile_filepath}")
            return None
        with open(profile_filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if not data.get("profile_id"):
            logging.warning(f"Skipping invalid profile file (missing profile_id): {profile_filepath}")
            return None
        return MigrantProfile(**data)
    except json.JSONDecodeError:
        logging.warning(f"Skipping invalid JSON in profile file: {profile_filepath}")
        return None
    except Exception as e:
        logging.error(f"Error loading profile {profile_id} from {profile_filepath}: {e}")
        return None

def initialize_llm_adviser(llm_type: str = "mock") -> Optional[LLMAdviser]:
    """Initializes and returns an LLM adviser instance."""
    if llm_type.lower() == "mock":
        logging.info("Initializing MockLLMAdviser.")
        if 'MockLLMAdviser' not in globals():
            logging.error("MockLLMAdviser not available due to import issues.")
            return None
        return MockLLMAdviser()
    else:
        logging.error(f"Unsupported LLM type: {llm_type}")
        return None

def run_single_test(test_case: TestCase, profile: MigrantProfile, llm_adviser: LLMAdviser) -> Optional[TestResult]:
    """Runs a single test case and returns the TestResult."""
    try:
        logging.info(f"Running test: {test_case.test_id} (Category: {test_case.category}) for profile: {profile.profile_id}")
        llm_response = llm_adviser.get_advice(profile, test_case.query, test_id=test_case.test_id)
        if 'run_evaluation' not in globals():
            logging.error("run_evaluation function not available due to import issues.")
            return None
        test_result = run_evaluation(test_case, llm_response)
        logging.info(f"Test {test_case.test_id} completed. Pass/Fail: {'PASS' if test_result.pass_fail else 'FAIL'}")
        return test_result
    except Exception as e:
        logging.error(f"Exception during test {test_case.test_id}: {e}")
        return None

def main():
    args = parse_arguments() # Get CLI args

    # Resolve paths from project root (assuming script is in project root)
    project_root = pathlib.Path(__file__).parent.resolve()
    test_cases_dir = project_root / args.test_cases_dir
    profiles_dir = project_root / args.profiles_dir
    results_dir = project_root / args.results_dir

    logging.info(f"Using Test Cases from: {test_cases_dir}")
    logging.info(f"Using Profiles from: {profiles_dir}")
    logging.info(f"Saving Results to: {results_dir}")
    if args.categories:
        logging.info(f"Running for categories: {', '.join(args.categories)}")

    llm_adviser = initialize_llm_adviser(llm_type=args.llm_type)
    if not llm_adviser:
        logging.critical("Could not initialize LLM Adviser. Exiting.")
        return

    test_files = discover_test_files(test_cases_dir, args.categories)
    if not test_files:
        logging.warning("No test files found matching criteria. Exiting.")
        return

    all_test_results: List[TestResult] = []
    for test_filepath in test_files:
        logging.debug(f"Processing test file: {test_filepath}")
        test_case = load_test_case_from_file(test_filepath)
        if not test_case:
            continue

        # Filter by category if specified (double check, discover_test_files should also handle this)
        if args.categories and test_case.category not in args.categories:
            logging.debug(f"Skipping test case {test_case.test_id} as its category '{test_case.category}' is not in specified categories.")
            continue

        profile = load_migrant_profile(test_case.migrant_profile_id, profiles_dir)
        if not profile:
            logging.warning(f"Could not load profile {test_case.migrant_profile_id} for test {test_case.test_id}. Skipping test.")
            continue

        if 'run_evaluation' not in globals() or 'MockLLMAdviser' not in globals() or not llm_adviser:
             logging.critical("Essential functions or LLM adviser not loaded. Cannot proceed.")
             return

        test_result = run_single_test(test_case, profile, llm_adviser)
        if test_result:
            all_test_results.append(test_result)

    logging.info(f"Finished running {len(all_test_results)} applicable tests.")

    generate_summary_report(all_test_results, results_dir, args.output_filename)

if __name__ == "__main__":
    if 'TestCase' not in globals() or 'MockLLMAdviser' not in globals() or 'run_evaluation' not in globals():
        logging.warning("One or more core components not defined. Check imports/PYTHONPATH.")
    main()
