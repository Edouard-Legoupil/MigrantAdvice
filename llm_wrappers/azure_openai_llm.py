import openai # Ensure openai library is available in the environment
import os
import logging
from typing import Optional, List, Dict, Any

# Assuming these paths are correct after restructuring
from core_types.data_classes import MigrantProfile
from llm_wrappers.llm_interface import LLMAdviser

class AzureOpenAILLMAdviser(LLMAdviser):
    """
    LLM Adviser implementation for Azure OpenAI Service.
    Uses environment variables for configuration by default.
    Required environment variables:
    - AZURE_OPENAI_ENDPOINT: The endpoint URL for your Azure OpenAI resource.
    - AZURE_OPENAI_API_KEY: The API key for your Azure OpenAI resource.
    - AZURE_OPENAI_DEPLOYMENT_NAME: The deployment name (model name) on Azure.
    - AZURE_OPENAI_API_VERSION: The API version (e.g., "2023-07-01-preview").
    """
    def __init__(self,
                 azure_endpoint: Optional[str] = None,
                 api_key: Optional[str] = None,
                 deployment_name: Optional[str] = None,
                 api_version: Optional[str] = None):

        self.azure_endpoint = azure_endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY")
        self.deployment_name = deployment_name or os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        self.api_version = api_version or os.getenv("AZURE_OPENAI_API_VERSION")

        self.initialized = False
        if not all([self.azure_endpoint, self.api_key, self.deployment_name, self.api_version]):
            logging.error(
                "AzureOpenAILLMAdviser not configured. "
                "Please set AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, "
                "AZURE_OPENAI_DEPLOYMENT_NAME, and AZURE_OPENAI_API_VERSION "
                "environment variables or pass them to the constructor."
            )
        else:
            self.initialized = True
            logging.info(f"AzureOpenAILLMAdviser initialized for endpoint: {self.azure_endpoint}, deployment: {self.deployment_name}")


    def get_advice(self, profile: MigrantProfile, query: str, test_id: Optional[str] = None) -> str:
        if not self.initialized:
            return "Error: AzureOpenAILLMAdviser is not configured. Please check environment variables."

        # Configure OpenAI library for Azure for this call
        # Note: This sets module-level configurations. If other OpenAI wrappers are used
        # (e.g., for direct OpenAI API), this could conflict.
        # A more robust solution for multiple OpenAI services (Azure vs Direct) might involve
        # using the newer OpenAI client instances (OpenAI() vs AzureOpenAI()) if library version allows.
        # For now, this is a common way for older library versions or single Azure focus.

        # Store original values to restore them later if they were set
        original_api_type = openai.api_type
        original_azure_endpoint = getattr(openai, 'azure_endpoint', None) # older versions used openai.api_base
        original_api_version = openai.api_version
        original_api_key = openai.api_key

        try:
            openai.api_type = "azure"
            # Some older versions of the library might expect api_base instead of azure_endpoint
            # Checking for Azure-specific attribute first
            if hasattr(openai, 'azure_endpoint'):
                openai.azure_endpoint = self.azure_endpoint
            else: # Fallback for very old library versions
                openai.api_base = self.azure_endpoint
            openai.api_version = self.api_version
            openai.api_key = self.api_key

            messages = [
                {"role": "system", "content": "You are a helpful assistant providing advice to migrants. Be concise and clear."},
                # Consider adding some profile context here if beneficial
                # E.g., {"role": "system", "content": f"User profile: Nationality: {profile.nationality}, Status: {profile.current_status}"},
                {"role": "user", "content": query}
            ]

            logging.debug(f"Azure OpenAI Request: engine={self.deployment_name}, messages={messages}")

            # Actual API call (worker will not execute this successfully without credentials)
            response = openai.ChatCompletion.create(
                engine=self.deployment_name, # For Azure, 'engine' is the deployment name
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )

            advice = response.choices[0].message.content.strip()
            logging.debug(f"Azure OpenAI Response: {advice}")
            return advice

        except openai.APIError as e:
            logging.error(f"Azure OpenAI API Error: {e}")
            return f"Error: Azure OpenAI API error - {e}"
        except openai.AuthenticationError as e:
            logging.error(f"Azure OpenAI Authentication Error: {e}")
            return f"Error: Azure OpenAI authentication failed. Check API key and endpoint. - {e}"
        except openai.RateLimitError as e:
            logging.error(f"Azure OpenAI Rate Limit Error: {e}")
            return f"Error: Azure OpenAI rate limit exceeded. - {e}"
        except Exception as e:
            logging.error(f"An unexpected error occurred with Azure OpenAI: {e}")
            return f"Error: Unexpected error with Azure OpenAI - {e}"
        finally:
            # Restore original OpenAI settings
            openai.api_type = original_api_type
            if hasattr(openai, 'azure_endpoint'):
                openai.azure_endpoint = original_azure_endpoint
            else:
                openai.api_base = original_azure_endpoint # Match fallback
            openai.api_version = original_api_version
            openai.api_key = original_api_key

if __name__ == "__main__":
    # This basic test will check for environment variables.
    # The worker will not have these set, so it's expected to log an error.
    print("Attempting to initialize AzureOpenAILLMAdviser...")
    adviser = AzureOpenAILLMAdviser()
    if not adviser.initialized:
        print("Adviser initialization failed (as expected without env vars).")
    else:
        print("Adviser initialized (unexpected, check if dummy env vars are set for testing).")
        # Example of how it might be called (won't work without real config)
        # dummy_profile = MigrantProfile(profile_id="test", nationality="Testland", language=["English"], skills=[], education="None", current_status="Test")
        # advice = adviser.get_advice(dummy_profile, "Hello?")
        # print(f"Dummy advice call: {advice}")
    print("AzureOpenAILLMAdviser __main__ check complete.")
