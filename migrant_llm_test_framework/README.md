# Migrant LLM Testing Framework

## 1. Objective

This project provides a Python-based framework for testing Large Language Models (LLMs) on their ability to provide accurate, fair, culturally sensitive, legally compliant, and useful advice to migrants. It aims to help developers and researchers evaluate and improve LLMs intended for this critical application.

## 2. Current Status & Limitations (Alpha)

*   **Initial Framework:** This is an early-stage framework. Core components are in place, but it's not yet feature-complete.
*   **Mock LLM:** Currently, testing is performed against a `MockLLMAdviser` which returns predefined responses based on test case IDs or keywords. Integration with real LLMs is a future step.
*   **Basic Evaluation:** Evaluation logic is primarily keyword-based. More nuanced semantic understanding and context-aware evaluation are planned.
*   **Limited Test Cases:** A small, illustrative set of migrant profiles and test cases are provided. These need significant expansion for comprehensive testing.
*   **No Orchestration Script Yet:** A master script (`run_tests.py`) to automate the execution of all tests and generate a consolidated report is planned but not yet implemented. Manual execution or custom scripting is required to run tests using the existing components.

## 3. Directory Structure

Here's an overview of the main directories and their purpose:

*   `migrant_llm_test_framework/`
    *   `core_types/`: Contains Python dataclasses for core data structures (`MigrantProfile`, `TestCase`, `TestResult`).
    *   `profiles/`: Stores synthetic migrant profiles as JSON files. Includes `profile_generator.py` to help create these.
    *   `test_cases/`: Stores test cases categorized by evaluation criteria (e.g., `A_accuracy_relevance/`, `B_bias_fairness/`). Test cases are in JSON format.
    *   `llm_wrappers/`: Contains the `llm_interface.py` module, which defines the `LLMAdviser` abstract base class and the `MockLLMAdviser` implementation.
    *   `evaluators/`: Contains `evaluator.py`, which includes logic for scoring LLM responses based on test case criteria.
    *   `results/`: (Planned) Intended for storing test results.
    *   `README.md`: This file.

## 4. Key Components

### 4.1. Core Data Classes (`core_types/data_classes.py`)

*   **`MigrantProfile`**: Represents a synthetic migrant with attributes like:
    *   `profile_id` (str): Unique identifier for the profile.
    *   `nationality` (str)
    *   `language` (List[str])
    *   `skills` (List[str])
    *   `education` (str)
    *   `current_status` (str): E.g., "Refugee", "Student", "Economic Migrant".
    *   `specific_needs` (List[str]): E.g., "Housing Assistance", "Visa Information".
*   **`TestCase`**: Defines a specific scenario to test the LLM:
    *   `test_id` (str): Unique identifier for the test case.
    *   `category` (str): The evaluation category (e.g., "A_accuracy_relevance").
    *   `migrant_profile_id` (str): ID of the `MigrantProfile` to use for this test.
    *   `query` (str): The question or prompt to pose to the LLM.
    *   `expected_keywords` (List[str]): Keywords expected in a good response.
    *   `negative_keywords` (List[str]): Keywords that should NOT be in the response.
    *   `evaluation_rubric` (Optional[str]): Qualitative criteria or notes for evaluation.
*   **`TestResult`**: Stores the outcome of a single test case evaluation:
    *   `test_case_id` (str)
    *   `llm_response` (str): The actual response from the LLM.
    *   `scores` (Dict[str, float]): Aggregated scores (e.g., `{"overall_assessment_score": 0.75}`).
    *   `pass_fail` (bool): Overall pass/fail status based on current logic.
    *   `raw_scores` (Dict[str, float]): Detailed scores from the specific evaluation functions (e.g., `{"keyword_presence_score": 0.8}`).
    *   `evaluation_notes` (Optional[str]): Any qualitative notes from the evaluator.

### 4.2. Migrant Profiles (`profiles/`)

*   Synthetic migrant profiles are stored as individual JSON files (e.g., `sy_refugee_001.json`) in the `profiles/` directory.
*   You can create new profiles by:
    1.  Manually creating a new JSON file following the `MigrantProfile` structure.
    2.  Using the `profile_generator.py` script's functions (`generate_migrant_profile`, `save_profile`) as a helper.
        ```python
        # Example using profile_generator.py (run from within profiles/ or adjust paths)
        from profile_generator import generate_migrant_profile, save_profile

        new_profile = generate_migrant_profile(
            profile_id="example_profile_007",
            nationality="Testlandian",
            language=["Testlang", "English"],
            skills=["Basket Weaving"],
            education="Primary School",
            current_status="Economic Migrant",
            specific_needs=["Job opportunities"]
        )
        save_profile(new_profile, directory=".", filename="example_profile_007.json")
        ```

### 4.3. Test Cases (`test_cases/`)

*   Test cases are stored as JSON files within subdirectories named after their category (e.g., `test_cases/A_accuracy_relevance/ar_003.json`).
*   Each JSON file directly maps to the `TestCase` data class structure.
*   To add a new test case:
    1.  Identify the appropriate category (A-F).
    2.  Ensure the `migrant_profile_id` you want to use corresponds to an existing profile JSON file in `profiles/`.
    3.  Create a new JSON file (e.g., `ar_003.json`) in the category directory with the defined `TestCase` fields.

### 4.4. LLM Interaction (`llm_wrappers/llm_interface.py`)

*   **`LLMAdviser` (Abstract Base Class)**: Defines the interface that any LLM wrapper should implement. Its core method is `get_advice(profile: MigrantProfile, query: str, test_id: Optional[str]) -> str`.
*   **`MockLLMAdviser`**: A simple implementation that uses a dictionary of pre-defined "canned" responses.
    *   It attempts to match a `test_id` first.
    *   If no `test_id` match, it falls back to simple keyword matching in the `query`.
    *   This is useful for testing the framework's mechanics without actual LLM calls. The canned responses are hardcoded in `MockLLMAdviser._get_default_canned_responses()`.

### 4.5. Evaluation Logic (`evaluators/evaluator.py`)

*   This module is responsible for assessing the LLM's response for a given `TestCase`.
*   **Helper Functions:**
    *   `evaluate_keyword_presence()`: Scores based on the proportion of `expected_keywords` found.
    *   `evaluate_keyword_absence()`: Scores 1.0 if no `negative_keywords` are found, 0.0 otherwise.
*   **Category-Specific Evaluators:** Functions like `evaluate_accuracy_relevance()`, `evaluate_cultural_sensitivity()`, etc., are defined. These currently use the keyword helper functions.
*   **`run_evaluation(test_case: TestCase, llm_response: str) -> TestResult`**:
    1.  Takes a `TestCase` and the `llm_response`.
    2.  Selects the appropriate category-specific evaluation function.
    3.  Calculates `raw_scores` based on that function.
    4.  Determines an overall `pass_fail` status (currently, all raw scores must meet certain thresholds).
    5.  Aggregates raw scores into a summary `scores` dictionary.
    6.  Returns a `TestResult` object.

## 5. How to Use (Current Workflow - Manual)

As the main orchestration script (`run_tests.py`) is not yet implemented, using the framework involves the following manual steps:

1.  **Define/Ensure Profiles:** Create or verify the `MigrantProfile` JSON files you need in `profiles/`.
2.  **Define Test Cases:** Create the `TestCase` JSON files in the appropriate `test_cases/` subdirectories, linking to your profiles.
3.  **Write a Custom Script:** You'll need to write a Python script to:
    *   Load `MigrantProfile` objects (e.g., using `json.load` and creating `MigrantProfile` instances, or using `load_profile` from `profile_generator.py`).
    *   Load `TestCase` objects (e.g., using `json.load` and creating `TestCase` instances).
    *   Instantiate an LLM adviser (e.g., `MockLLMAdviser`).
    *   For each test case:
        *   Get the LLM's response using `llm_adviser.get_advice(profile, test_case.query, test_id=test_case.test_id)`.
        *   Evaluate the response using `run_evaluation(test_case, llm_response)` from `evaluator.py`.
        *   Collect and review the `TestResult` objects.

    ```python
    # --- Example snippet for a custom script ---
    # (Assumes this script is in the root 'migrant_llm_test_framework' directory or paths adjusted)
    import json
    from core_types.data_classes import MigrantProfile, TestCase
    from llm_wrappers.llm_interface import MockLLMAdviser
    from evaluators.evaluator import run_evaluation
    from profiles.profile_generator import load_profile # Helper

    # 1. Load a profile
    # Make sure 'profiles/sy_refugee_001.json' exists
    try:
        profile = load_profile("profiles/sy_refugee_001.json")
    except FileNotFoundError:
        print("Error: Sample profile 'profiles/sy_refugee_001.json' not found.")
        # exit() # Avoid exit() in non-interactive context if possible
    except json.JSONDecodeError:
        print("Error: Could not decode 'profiles/sy_refugee_001.json'. Ensure it's valid JSON.")
        # exit()

    # 2. Load a test case
    # Make sure 'test_cases/A_accuracy_relevance/ar_001.json' exists
    try:
        with open("test_cases/A_accuracy_relevance/ar_001.json", 'r') as f:
            tc_data = json.load(f)
        test_case = TestCase(**tc_data)
    except FileNotFoundError:
        print("Error: Sample test case 'test_cases/A_accuracy_relevance/ar_001.json' not found.")
        # exit()
    except json.JSONDecodeError:
        print("Error: Could not decode 'test_cases/A_accuracy_relevance/ar_001.json'. Ensure it's valid JSON.")
        # exit()

    # 3. Instantiate LLM Adviser
    llm = MockLLMAdviser()

    # 4. Get advice and evaluate
    # Ensure profile and test_case were loaded successfully before proceeding
    if 'profile' in locals() and 'test_case' in locals() and profile.profile_id == test_case.migrant_profile_id:
        response = llm.get_advice(profile, test_case.query, test_id=test_case.test_id)
        result = run_evaluation(test_case, response)

        print(f"--- Test Result for {result.test_case_id} ---")
        print(f"Query: {test_case.query}")
        print(f"LLM Response: {result.llm_response}")
        print(f"Pass/Fail: {'PASS' if result.pass_fail else 'FAIL'}")
        print(f"Aggregated Score: {result.scores.get('overall_assessment_score', 'N/A')}")
        print(f"Raw Scores: {result.raw_scores}")
        print(f"Evaluation Notes: {result.evaluation_notes}")
    elif not ('profile' in locals() and 'test_case' in locals()):
        print("Skipping advice and evaluation due to earlier errors loading profile or test case.")
    else:
        print(f"Profile ID mismatch: {profile.profile_id} vs {test_case.migrant_profile_id}")
    # --- End Example ---
    ```

## 6. Future Development

*   **`run_tests.py` Orchestration Script:** A top-level script to automatically discover and run all test cases, collect results, and generate a comprehensive report.
*   **Real LLM Integration:** Implement wrappers for actual LLM APIs (e.g., OpenAI GPT, Anthropic Claude, open-source models).
*   **Advanced Evaluation Metrics:**
    *   Semantic similarity scoring.
    *   Fact-checking against a knowledge base.
    *   More nuanced bias detection (e.g., comparing responses for varied demographics on similar queries).
    *   Rubric-based evaluation support.
*   **Expanded Test Suites:** Creation of a much larger and more diverse set of migrant profiles and test cases.
*   **Human-in-the-Loop Evaluation:** Interface for incorporating human judgment for complex or subjective evaluations.
*   **Reporting:** More sophisticated reporting of test results (e.g., HTML reports, dashboards).

## 7. Contributing

(Placeholder for contribution guidelines - e.g., how to suggest new test cases, improve evaluation logic, or add LLM wrappers).
