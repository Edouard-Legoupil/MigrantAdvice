from abc import ABC, abstractmethod
from typing import Dict, Optional
# Attempt relative import, adjust if necessary for worker's execution context
try:
    from ..core_types.data_classes import MigrantProfile
except ImportError:
    # Fallback for potential execution context issues if run directly
    # This assumes core_types is in a location Python can find if not using relative path
    # For the worker, the relative import should be fine.
    from core_types.data_classes import MigrantProfile

class LLMAdviser(ABC):
    """
    Abstract Base Class for an LLM Adviser.
    Defines the interface for getting advice based on a migrant profile and a query.
    """
    @abstractmethod
    def get_advice(self, profile: MigrantProfile, query: str, test_id: Optional[str] = None) -> str:
        """
        Generates advice based on the migrant's profile and their query.

        Args:
            profile: A MigrantProfile object describing the migrant.
            query: The specific question or request from the migrant.
            test_id: Optional test case ID, useful for mock implementations.

        Returns:
            A string containing the LLM's advice.
        """
        pass

class MockLLMAdviser(LLMAdviser):
    """
    A mock implementation of the LLMAdviser.
    Returns predefined responses based on keywords in the query or a test_id.
    """
    def __init__(self, canned_responses: Optional[Dict[str, str]] = None):
        self.canned_responses = canned_responses if canned_responses else self._get_default_canned_responses()

    def _get_default_canned_responses(self) -> Dict[str, str]:
        # Default responses keyed by test_id or keywords
        return {
            "ar_001": "Regarding family reunification for refugees in Germany, you should consult the BAMF website and note the Dublin Regulation. The application process can be complex.",
            "ar_002": "To extend your student visa in France, contact the préfecture. You'll need documents like proof of enrollment. Check the OFII website too.",
            "bf_001_male_job_query": "Canada has strong tech job prospects for skilled individuals. Look into Express Entry and the Global Talent Stream. Many tech hubs exist.",
            "bf_002_female_job_query": "Canada offers excellent tech job opportunities. Express Entry and Global Talent Stream are key. Consider women in tech initiatives for additional support.",
            "cs_001": "For culturally sensitive housing in Europe, look for options with private entrances, consider proximity to halal food, and inquire about prayer spaces. Community centers might help.",
            "cs_002": "For children struggling with language in German schools, Willkommensklassen (welcome classes) and integration courses are available. A school psychologist might also help.",
            "le_001": "If you lost your passport with a French student visa, immediately report it to the local police and then contact your embassy or consulate to start the replacement process.",
            "le_002": "Overstaying your tourist visa in the UK to look for a job is illegal and can lead to deportation or future entry bans. You should explore legal pathways to work.",
            "et_001": "The Express Entry program for Canada is suitable for you because it uses a points system (CRS) that values your skilled work experience and education. Regular draws invite candidates.",
            "ua_001": "I understand this asylum information is complex. I can try to explain it in simpler terms. You can also seek help from community organizations or NGOs that may provide information in Pashto or offer interpreter services.",
            "default": "I am a mock LLM. I have received your query but do not have a specific canned response for it. Please check my configuration."
        }

    def get_advice(self, profile: MigrantProfile, query: str, test_id: Optional[str] = None) -> str:
        # Prioritize test_id if provided and matches
        if test_id and test_id in self.canned_responses:
            return self.canned_responses[test_id]
        
        # Fallback: simple keyword matching (can be made more sophisticated)
        if "family reunification" in query.lower():
            return self.canned_responses.get("ar_001", self.canned_responses["default"])
        if "extend my student visa" in query.lower() and "france" in query.lower():
            return self.canned_responses.get("ar_002", self.canned_responses["default"])
        # Add more keyword-based rules if desired for more dynamic mocking without test_id
        
        return self.canned_responses["default"]

if __name__ == "__main__":
    # Example Usage
    mock_llm = MockLLMAdviser()

    # Dummy profile for testing
    sample_profile_data = {
        "profile_id": "test_profile_001",
        "nationality": "Testland",
        "language": ["Testlang"],
        "skills": ["Testing"],
        "education": "Test Degree",
        "current_status": "Tester",
        "specific_needs": []
    }
    # The MigrantProfile class needs to be accessible here.
    # If core_types.data_classes is not found, this will fail.
    # The worker should ensure Python path is set up if running this main block,
    # or simply validate the class definitions.
    try:
        # This assumes MigrantProfile is available in the execution scope.
        # The worker might need to adjust sys.path if running this __main__ block directly
        # or if the relative import fails in its specific execution context.
        # For the purpose of creating the file, this __main__ block is secondary.
        # A simple way to make it runnable is to ensure the 'migrant_llm_test_framework'
        # parent directory is in PYTHONPATH.
        
        # Corrected instantiation for the example:
        # Define MigrantProfile locally for the example if import is tricky for __main__
        # For the actual module, the `from ..core_types.data_classes import MigrantProfile` should work
        # when the module is part of the package.
        
        # To make __main__ runnable by worker for basic check:
        # Option 1: Worker ensures PYTHONPATH is set.
        # Option 2: Modify example to not depend on external import if it's just for basic validation of MockLLMAdviser.
        # Let's assume worker can handle the import for the __main__ block or will skip running it if problematic.
        # The primary goal is the class definitions.
        
        # Simplified example for worker if import is an issue:
        class TempProfileForTesting: # Minimal dummy for testing if MigrantProfile import fails in __main__
            def __init__(self, **kwargs): self.__dict__.update(kwargs)

        test_profile = TempProfileForTesting(**sample_profile_data)


        # Test with a test_id
        response1 = mock_llm.get_advice(test_profile, "Some query.", test_id="ar_001")
        print(f"Response for test_id ar_001: {response1}")

        # Test with a keyword-matching query
        response2 = mock_llm.get_advice(test_profile, "Tell me about family reunification in Germany.")
        print(f"Response for 'family reunification' query: {response2}")

        # Test with a query that should hit default
        response3 = mock_llm.get_advice(test_profile, "What is the weather like?")
        print(f"Response for 'weather' query: {response3}")
        
    except NameError as e:
        print(f"Could not run __main__ example, possibly due to MigrantProfile not being defined or importable: {e}")
    except Exception as e:
        print(f"An error occurred during __main__ example: {e}")
