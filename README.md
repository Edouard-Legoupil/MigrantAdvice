# BEACUL: Migrant Advice LLM Testing Framework

## 1. Objective

This project introduces **BEACUL**, a Python-based framework for testing Large Language Models (LLMs). BEACUL focuses on evaluating LLM-generated advice for migrants across six key dimensions:
*   **B** – Bias & Fairness
*   **E** – Explainability
*   **A** – Accuracy & Relevance
*   **C** – Cultural Sensitivity
*   **U** – Usability
*   **L** – Legal & Ethical

The BEACUL framework aims to help developers and researchers evaluate and improve LLMs intended for this critical application.

## 2. Current Status & Limitations (Alpha)

*   **Initial Framework:** This is an early-stage framework. Core components are in place, including a `run_tests.py` script for orchestration.
*   **Mock LLM:** Currently, testing is performed against a `MockLLMAdviser` which returns predefined responses. Integration with real LLMs is a future step.
*   **Basic Evaluation:** Evaluation logic is primarily keyword-based.
*   **Limited Test Cases:** A small, illustrative set of migrant profiles and test cases are provided.

## 3. Directory Structure

Here's an overview of the main directories and their purpose (project root):

*   `core_types/`: Contains Python dataclasses for core data structures (`MigrantProfile`, `TestCase`, `TestResult`).
*   `profiles/`: Stores synthetic migrant profiles as JSON files. Includes `profile_generator.py` to help create these.
*   `test_cases/`: Stores test cases categorized by evaluation criteria (e.g., `A_accuracy_relevance/`, `B_bias_fairness/`). Test cases are in JSON format.
*   `llm_wrappers/`: Contains the `llm_interface.py` module, which defines the `LLMAdviser` abstract base class and the `MockLLMAdviser` implementation.
*   `evaluators/`: Contains `evaluator.py`, which includes logic for scoring LLM responses based on test case criteria.
*   `results/`: Directory where result reports (e.g., JSON output from `run_tests.py`) are saved.
*   `run_tests.py`: The main script for orchestrating test execution.
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

## 5. How to Use

The primary way to run tests using the BEACUL framework is via the `run_tests.py` script located in the project root directory.

### 5.1. Running Tests

Navigate to the project root directory in your terminal and execute the script using Python:

```bash
python run_tests.py [OPTIONS]
```

### 5.2. Command-Line Options

The behavior of `run_tests.py` can be customized with the following command-line arguments:

*   `--test_cases_dir DIRECTORY`: Path to the directory containing test case category subdirectories.
    *   Default: `./test_cases`
*   `--profiles_dir DIRECTORY`: Path to the directory containing migrant profile JSON files.
    *   Default: `./profiles`
*   `--results_dir DIRECTORY`: Directory where result reports (e.g., JSON output) will be saved.
    *   Default: `./results`
*   `--categories CATEGORY [CATEGORY ...]`: Run only tests from the specified categories (e.g., `A_accuracy_relevance` `C_cultural_sensitivity`). If not provided, tests from all categories will be run.
    *   Example: `python run_tests.py --categories A_accuracy_relevance D_legal_ethical`
*   `--llm_type TYPE`: Specifies which LLM adviser to use.
    *   Default: `mock`
    *   Currently available: `mock`, `azure_openai` (requires environment variables for configuration - see below).
*   `--output_filename FILENAME`: Filename for the JSON report saved in the `results_dir`.
    *   Default: `test_results.json`
*   `-v`, `--verbose`: Enable verbose logging, which sets the logging level to DEBUG. Useful for troubleshooting.

### 5.3. Example Executions

*   **Run all tests with default settings:**
    ```bash
    python run_tests.py
    ```
*   **Run tests for specific categories and save results to a custom file:**
    ```bash
    python run_tests.py --categories A_accuracy_relevance C_cultural_sensitivity --output_filename custom_results.json
    ```
*   **Run tests with verbose output:**
    ```bash
    python run_tests.py -v
    ```

### 5.4. Interpreting Output

*   **Console Output:** The script will print live progress, including which tests are being run and their pass/fail status. A summary report will be displayed at the end, showing total tests run, pass/fail counts, a list of failed tests, and a category-wise breakdown.
*   **JSON Report:** A JSON file (default: `results/test_results.json`) will be generated containing a list of all `TestResult` objects in dictionary format. This file provides detailed information for each test run.

*(The previous sub-section detailing manual script execution can be removed or archived as `run_tests.py` is now the standard method.)*

### 5.5. Using with Azure OpenAI Service

To use your own Azure OpenAI Service models, you can specify `--llm_type azure_openai`. This requires the following environment variables to be set:

*   `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI resource endpoint (e.g., `https://your-resource-name.openai.azure.com/`).
*   `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key.
*   `AZURE_OPENAI_DEPLOYMENT_NAME`: The name of your specific model deployment on Azure (e.g., `gpt-35-turbo`, `gpt-4-deployment`).
*   `AZURE_OPENAI_API_VERSION`: The API version your Azure OpenAI resource uses (e.g., `2023-07-01-preview`).

**Example command:**
```bash
export AZURE_OPENAI_ENDPOINT="your_endpoint_here"
export AZURE_OPENAI_API_KEY="your_api_key_here"
export AZURE_OPENAI_DEPLOYMENT_NAME="your_deployment_name_here"
export AZURE_OPENAI_API_VERSION="your_api_version_here"
python run_tests.py --llm_type azure_openai --categories A_accuracy_relevance
```
**Note:** Ensure the `openai` Python library is installed in your environment (`pip install openai`).

## 6. Future Development

*   **Expand Real LLM Integration:** Further integration with various LLM APIs (e.g., direct OpenAI API, other cloud provider LLMs, locally hosted models via Ollama). Azure OpenAI Service integration is the first step.
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
