from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class MigrantProfile:
    profile_id: str
    nationality: str
    language: List[str]
    skills: List[str]
    education: str
    current_status: str  # e.g., asylum_seeker, refugee, economic_migrant, student
    specific_needs: List[str] = field(default_factory=list)

@dataclass
class TestCase:
    test_id: str
    category: str  # A, B, C, D, E, F
    migrant_profile_id: str # Link to a MigrantProfile
    query: str
    expected_keywords: List[str] = field(default_factory=list)
    negative_keywords: List[str] = field(default_factory=list)
    evaluation_rubric: Optional[str] = None

@dataclass
class TestResult:
    test_case_id: str
    llm_response: str
    scores: Dict[str, float]
    pass_fail: bool
    raw_scores: Dict[str, float] = field(default_factory=dict)
    evaluation_notes: Optional[str] = None
