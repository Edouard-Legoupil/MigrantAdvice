import json
from typing import List, Dict, Optional
from ..core_types.data_classes import MigrantProfile # Relative import
import uuid # To generate unique profile IDs

def generate_migrant_profile(
    profile_id: Optional[str] = None,
    nationality: str = "Unknown",
    language: List[str] = ["English"],
    skills: List[str] = ["Unskilled"],
    education: str = "Unknown",
    current_status: str = "Migrant",
    specific_needs: List[str] = [],
    **kwargs # To allow for future expansion of MigrantProfile fields
) -> MigrantProfile:
    if profile_id is None:
        profile_id = f"profile_{uuid.uuid4().hex[:8]}"
    
    # Collect any additional fields passed via kwargs that are valid for MigrantProfile
    profile_data = {
        "profile_id": profile_id,
        "nationality": nationality,
        "language": language,
        "skills": skills,
        "education": education,
        "current_status": current_status,
        "specific_needs": specific_needs,
    }
    profile_data.update(kwargs) # Add any extra fields

    # Filter kwargs to only include those that are actual fields in MigrantProfile
    # This requires inspecting MigrantProfile.__annotations__ or being careful
    # For now, let's assume MigrantProfile constructor handles extra kwargs gracefully or we only pass valid ones.
    # A more robust solution would be to dynamically check fields.
    
    return MigrantProfile(**profile_data)

def save_profile(profile: MigrantProfile, directory: str, filename: Optional[str] = None):
    if filename is None:
        filename = f"{profile.profile_id}.json"
    filepath = f"{directory}/{filename}" # Use os.path.join for robustness in a real scenario
    
    # Ensure directory exists (os.makedirs(directory, exist_ok=True)) - Worker should handle this.
    # For simplicity in instruction, assuming worker can ensure directory.
    
    profile_dict = {
        "profile_id": profile.profile_id,
        "nationality": profile.nationality,
        "language": profile.language,
        "skills": profile.skills,
        "education": profile.education,
        "current_status": profile.current_status,
        "specific_needs": profile.specific_needs,
    }
    # Handle any other fields that might have been added to MigrantProfile

    with open(filepath, 'w') as f:
        json.dump(profile_dict, f, indent=4)
    print(f"Profile saved to {filepath}") # Optional: for confirmation

def load_profile(filepath: str) -> MigrantProfile:
    with open(filepath, 'r') as f:
        data = json.load(f)
    return MigrantProfile(**data)

if __name__ == "__main__":
    # Example Usage
    # Create a sample profile
    sample_profile_data = {
        "profile_id": "sample001",
        "nationality": "Syrian",
        "language": ["Arabic", "English"],
        "skills": ["Software Development", "Project Management"],
        "education": "Master's Degree",
        "current_status": "Refugee",
        "specific_needs": ["Housing", "Language Course"]
    }
    profile1 = generate_migrant_profile(**sample_profile_data)
    print(f"Generated Profile 1: {profile1}")

    # Create another profile with minimal info, relying on defaults and auto ID
    profile2 = generate_migrant_profile(
        nationality="Eritrean",
        language=["Tigrinya"],
        current_status="Asylum Seeker"
    )
    print(f"Generated Profile 2: {profile2}")

    # Define the directory to save profiles (relative to where the script is run from)
    # The worker should ensure this path is correct within its execution environment.
    # If profiles/ is in the root of the project, and this script is in profiles/,
    # then saving to "." or "generated_profiles_output" within profiles/ might be appropriate.
    # For this subtask, let's assume the worker will create a subdirectory if needed,
    # or save it directly in the `profiles` directory.
    
    # The worker needs to ensure 'migrant_llm_test_framework/profiles/generated_examples/' exists
    # or adapt the save path. For the subtask, let's simplify and ask it to save
    # in the `profiles` directory itself.
    output_dir = "." # Save in the current directory (which is migrant_llm_test_framework/profiles/)
    
    # Save the profiles
    # The worker will need to create the 'migrant_llm_test_framework/profiles/' directory first if running this script standalone.
    # However, the directory structure is already created from Step 1.
    save_profile(profile1, directory=output_dir) 
    save_profile(profile2, directory=output_dir, filename="asylum_seeker_profile.json")

    # Load a profile
    try:
        loaded_profile = load_profile(f"{output_dir}/sample001.json")
        print(f"Loaded Profile: {loaded_profile}")
    except FileNotFoundError:
        print("File sample001.json not found for loading example. Ensure it was saved.")
    
    print("Profile generation example finished.")
