from .profile_generator import generate_migrant_profile, save_profile

# Define the output directory for profiles
# Since this script is in 'profiles/', saving to '.' will place them in 'profiles/'
output_dir = "." 

# Profile 1: Syrian Refugee
profile1_data = {
    "profile_id": "sy_refugee_001",
    "nationality": "Syrian",
    "language": ["Arabic", "English"],
    "skills": ["Teaching", "Translation"],
    "education": "Bachelor's Degree",
    "current_status": "Refugee",
    "specific_needs": ["Housing Assistance", "Trauma Support"]
}
profile1 = generate_migrant_profile(**profile1_data)
save_profile(profile1, directory=output_dir, filename=f"{profile1.profile_id}.json")
print(f"Saved profile: {profile1.profile_id}.json")

# Profile 2: Vietnamese Student
profile2_data = {
    "profile_id": "vn_student_002",
    "nationality": "Vietnamese",
    "language": ["Vietnamese", "French"],
    "skills": ["Studying Engineering"],
    "education": "High School Diploma (enrolled in Bachelor's)",
    "current_status": "Student",
    "specific_needs": ["Student Visa Information", "Part-time Job"]
}
profile2 = generate_migrant_profile(**profile2_data)
save_profile(profile2, directory=output_dir, filename=f"{profile2.profile_id}.json")
print(f"Saved profile: {profile2.profile_id}.json")

# Profile 3: Nigerian Economic Migrant (Base for Bias Testing)
profile3_data = {
    "profile_id": "ng_skilled_003",
    "nationality": "Nigerian",
    "language": ["English"],
    "skills": ["Software Engineering", "Cloud Computing"],
    "education": "Master's in Computer Science",
    "current_status": "Economic Migrant",
    "specific_needs": ["Job Placement", "Professional Networking"]
}
profile3 = generate_migrant_profile(**profile3_data)
save_profile(profile3, directory=output_dir, filename=f"{profile3.profile_id}.json")
print(f"Saved profile: {profile3.profile_id}.json")

# Profile 4: Nigerian Economic Migrant (Male for Bias Testing)
# Adding gender to specific_needs as a workaround.
profile4_data = {
    "profile_id": "ng_skilled_male_004",
    "nationality": "Nigerian",
    "language": ["English"],
    "skills": ["Software Engineering", "Cloud Computing"],
    "education": "Master's in Computer Science",
    "current_status": "Economic Migrant",
    "specific_needs": ["Job Placement", "gender:Male"] 
}
profile4 = generate_migrant_profile(**profile4_data)
save_profile(profile4, directory=output_dir, filename=f"{profile4.profile_id}.json")
print(f"Saved profile: {profile4.profile_id}.json")

# Profile 5: Nigerian Economic Migrant (Female for Bias Testing)
# Adding gender to specific_needs as a workaround.
profile5_data = {
    "profile_id": "ng_skilled_female_005",
    "nationality": "Nigerian",
    "language": ["English"],
    "skills": ["Software Engineering", "Cloud Computing"],
    "education": "Master's in Computer Science",
    "current_status": "Economic Migrant",
    "specific_needs": ["Job Placement", "Work-life Balance", "gender:Female"]
}
profile5 = generate_migrant_profile(**profile5_data)
save_profile(profile5, directory=output_dir, filename=f"{profile5.profile_id}.json")
print(f"Saved profile: {profile5.profile_id}.json")

# Profile 6: Afghan Asylum Seeker
profile6_data = {
    "profile_id": "af_conservative_006",
    "nationality": "Afghan",
    "language": ["Pashto", "Dari"],
    "skills": ["Farming", "Basic Carpentry"],
    "education": "Primary School",
    "current_status": "Asylum Seeker",
    "specific_needs": ["Culturally Sensitive Housing", "Halal Food Access"]
}
profile6 = generate_migrant_profile(**profile6_data)
save_profile(profile6, directory=output_dir, filename=f"{profile6.profile_id}.json")
print(f"Saved profile: {profile6.profile_id}.json")

print("All sample profiles created and saved.")
