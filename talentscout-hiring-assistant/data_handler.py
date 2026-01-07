import json
import os
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional

DATA_FILE = "candidate_data.json"

def init_storage():
    """Initialize the data storage file if it doesn't exist."""
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as f:
            json.dump([], f)

def save_candidate_data(candidate_info: Dict):
    """Save candidate data to the local JSON file."""
    init_storage()
    
    # Add timestamp
    candidate_info['timestamp'] = datetime.now().isoformat()
    
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        data = []
    
    # Check if candidate already exists (by email) and update
    email = candidate_info.get('email')
    if email:
        updated = False
        for i, entry in enumerate(data):
            if entry.get('email') == email:
                data[i] = candidate_info
                updated = True
                break
        if not updated:
            data.append(candidate_info)
    else:
        data.append(candidate_info)
        
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def calculate_score(candidate: Dict) -> int:
    """
    Calculate candidate score based on:
    - Completeness of profile (40%)
    - Question responses quality (40%) - Placeholder or based on length/keywords
    - Interaction time (20%) - Placeholder or based on logic
    """
    score = 0
    
    # 1. Profile Completeness (40 points)
    fields = ['full_name', 'email', 'phone', 'experience', 'position', 'location', 'tech_stack']
    filled_fields = sum(1 for field in fields if candidate.get(field))
    completeness_score = (filled_fields / len(fields)) * 40
    score += completeness_score
    
    # 2. Response Quality (40 points)
    # This is a heuristic since we don't have a real grader yet. 
    # We'll use the average length of answers as a proxy for "effort".
    answers = candidate.get('technical_answers', {})
    if answers:
        avg_len = sum(len(a) for a in answers.values()) / len(answers)
        # Cap at 40 points for reasonable length (e.g., 200 chars avg)
        quality_score = min(40, (avg_len / 5)) 
    else:
        quality_score = 0
    score += quality_score
    
    # 3. Time (20 points) - Simpler placeholder: Random/Fixed for now as we don't track start/end strictly in dict yet
    # Assigning a default 20 for completing it.
    score += 20
    
    return int(score)

def get_leaderboard() -> List[Dict]:
    """Get the top 10 candidates for the leaderboard."""
    init_storage()
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
    except Exception:
        return []
    
    leaderboard_data = []
    for c in data:
        leaderboard_data.append({
            'name': c.get('full_name', 'Anonymous'),
            'score': calculate_score(c),
            'role': c.get('position', 'N/A')
        })
    
    # Sort by score desc
    leaderboard_data.sort(key=lambda x: x['score'], reverse=True)
    return leaderboard_data[:10]
