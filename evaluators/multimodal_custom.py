"""
Custom Evaluators for Multimodal Benchmark
Handles non-text outputs: coordinates, trajectories, physics predictions
"""

import re
import json
import math
from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class CoordinatePoint:
    x: float
    y: float

@dataclass
class TrajectoryResult:
    points: List[CoordinatePoint]
    valid_format: bool
    start_point: Optional[CoordinatePoint] = None
    end_point: Optional[CoordinatePoint] = None


def parse_coordinate_string(text: str) -> TrajectoryResult:
    """
    Extract [x, y] coordinate arrays from model output text.
    Handles formats like:
    - [100, 200], [300, 400]
    - [(100, 200), (300, 400)]
    - x=100, y=200
    """
    points = []
    valid_format = False
    
    # Try to find [x, y] or (x, y) patterns
    patterns = [
        r'\[(\d+(?:\.\d+)?),\s*(\d+(?:\.\d+)?)\]',  # [100, 200]
        r'\((\d+(?:\.\d+)?),\s*(\d+(?:\.\d+)?)\)',  # (100, 200)
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        if matches:
            valid_format = True
            for match in matches:
                try:
                    x = float(match[0])
                    y = float(match[1])
                    points.append(CoordinatePoint(x, y))
                except ValueError:
                    continue
            break
    
    # Also try JSON array format
    if not valid_format:
        try:
            # Look for JSON-like array in the text
            json_match = re.search(r'\[\s*\[.*?\]\s*\]', text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                if isinstance(data, list) and len(data) > 0:
                    valid_format = True
                    for item in data:
                        if isinstance(item, (list, tuple)) and len(item) >= 2:
                            points.append(CoordinatePoint(float(item[0]), float(item[1])))
        except (json.JSONDecodeError, ValueError):
            pass
    
    start_point = points[0] if points else None
    end_point = points[-1] if points else None
    
    return TrajectoryResult(
        points=points,
        valid_format=valid_format,
        start_point=start_point,
        end_point=end_point
    )


def euclidean_distance(p1: CoordinatePoint, p2: CoordinatePoint) -> float:
    """Calculate Euclidean distance between two points."""
    return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)


def evaluate_robot_trajectory(
    predicted_text: str,
    ground_truth: Dict[str, Any]
) -> Dict[str, float]:
    """
    Evaluate robot trajectory prediction.
    Returns dict with scores for format, endpoints, obstacle avoidance, efficiency.
    """
    result = parse_coordinate_string(predicted_text)
    scores = {}
    
    # Format validity (0.2)
    scores["format_validity"] = 1.0 if result.valid_format else 0.0
    
    if not result.valid_format or not result.points:
        scores["start_end_accuracy"] = 0.0
        scores["obstacle_avoidance"] = 0.0
        scores["path_efficiency"] = 0.0
        return scores
    
    # Start/end accuracy (0.3)
    gt_gripper = CoordinatePoint(*ground_truth["coordinates_approximate"]["gripper_start"])
    gt_vase = CoordinatePoint(*ground_truth["coordinates_approximate"]["vase_location"])
    
    start_dist = euclidean_distance(result.start_point, gt_gripper) if result.start_point else float('inf')
    end_dist = euclidean_distance(result.end_point, gt_vase) if result.end_point else float('inf')
    
    # Normalize distances (assuming 800x600 workspace)
    max_dist = math.sqrt(800**2 + 600**2)
    start_score = max(0, 1 - (start_dist / max_dist))
    end_score = max(0, 1 - (end_dist / max_dist))
    scores["start_end_accuracy"] = (start_score + end_score) / 2
    
    # Obstacle avoidance (0.3)
    obstacle = ground_truth["coordinates_approximate"]["obstacle_location"]
    obstacle_dims = ground_truth["coordinates_approximate"]["obstacle_dimensions"]
    
    min_distance_to_obstacle = float('inf')
    for point in result.points:
        # Simple box distance calculation
        dx = max(obstacle[0] - obstacle_dims[0]/2 - point.x, 
                point.x - (obstacle[0] + obstacle_dims[0]/2), 0)
        dy = max(obstacle[1] - obstacle_dims[1]/2 - point.y,
                point.y - (obstacle[1] + obstacle_dims[1]/2), 0)
        dist = math.sqrt(dx**2 + dy**2)
        min_distance_to_obstacle = min(min_distance_to_obstacle, dist)
    
    # Score: full credit if stays 50+ pixels away, partial if within 50
    scores["obstacle_avoidance"] = min(1.0, min_distance_to_obstacle / 50.0)
    
    # Path efficiency (0.2)
    if len(result.points) >= 3:
        # Calculate total path length
        total_length = sum(
            euclidean_distance(result.points[i], result.points[i+1])
            for i in range(len(result.points) - 1)
        )
        # Direct distance from start to end
        direct_dist = euclidean_distance(result.start_point, result.end_point) if result.start_point and result.end_point else 1
        
        # Efficiency ratio: direct / total (closer to 1 = more efficient)
        efficiency = direct_dist / total_length if total_length > 0 else 0
        scores["path_efficiency"] = efficiency
    else:
        scores["path_efficiency"] = 0.0
    
    return scores


def evaluate_physics_prediction(
    predicted_text: str,
    ground_truth: Dict[str, Any]
) -> Dict[str, float]:
    """
    Evaluate physics/causality prediction.
    Uses keyword matching + semantic reasoning detection.
    """
    text_lower = predicted_text.lower()
    scores = {}
    
    # Causal chain (0.4) — check for key sequence elements
    expected_sequence = ground_truth.get("causal_chain", [])
    sequence_score = 0.0
    
    if expected_sequence:
        matched_steps = 0
        for step in expected_sequence:
            # Extract key action words from each step
            action_words = step.lower().split()
            # Check if any significant words appear in prediction
            significant_words = [w for w in action_words if len(w) > 4]
            if any(word in text_lower for word in significant_words):
                matched_steps += 1
        
        sequence_score = matched_steps / len(expected_sequence)
    
    scores["causal_chain"] = sequence_score
    
    # Physics accuracy (0.4) — check for physically plausible outcomes
    correct_keywords = ["stable", "remain", "no effect", "doesn't fall", "stays upright"]
    wrong_keywords = ["everything falls", "all blocks fall", "tower collapses", "green falls", "blue falls"]
    
    correct_mentions = sum(1 for kw in correct_keywords if kw in text_lower)
    wrong_mentions = sum(1 for kw in wrong_keywords if kw in text_lower)
    
    if wrong_mentions > 0:
        scores["physics_accuracy"] = 0.0  # Any wrong prediction = full penalty
    elif correct_mentions > 0:
        scores["physics_accuracy"] = min(1.0, correct_mentions / 2.0)
    else:
        # No clear keywords — check for nuanced understanding
        scores["physics_accuracy"] = 0.3  # Partial credit for coherent but vague
    
    # Specificity (0.2) — references red block specifically
    red_mentions = text_lower.count("red")
    block_mentions = text_lower.count("block")
    
    if red_mentions >= 1 and block_mentions >= 1:
        scores["specificity"] = 1.0
    elif block_mentions >= 1:
        scores["specificity"] = 0.5
    else:
        scores["specificity"] = 0.0
    
    return scores


def evaluate_driving_action(
    predicted_text: str,
    ground_truth: Dict[str, Any]
) -> Dict[str, float]:
    """
    Evaluate autonomous driving action prediction.
    """
    text_lower = predicted_text.lower()
    scores = {}
    
    # Action correctness (0.4)
    correct_actions = ["decelerate", "slow down", "brake", "stop", "prepare to stop"]
    wrong_actions = ["accelerate", "speed up", "proceed", "go", "continue", "turn right"]
    
    correct_mentions = sum(1 for action in correct_actions if action in text_lower)
    wrong_mentions = sum(1 for action in wrong_actions if action in text_lower)
    
    if wrong_mentions > 0:
        scores["action_correctness"] = 0.0
    elif correct_mentions > 0:
        scores["action_correctness"] = 1.0
    else:
        # Check for cautious language
        cautious = ["caution", "careful", "yield", "wait"]
        if any(word in text_lower for word in cautious):
            scores["action_correctness"] = 0.7
        else:
            scores["action_correctness"] = 0.3
    
    # Cue identification (0.4)
    critical_cues = ground_truth.get("critical_cues", [])
    mentioned_cues = 0
    
    for cue in critical_cues:
        cue_keywords = cue.lower().split()[:3]  # First 3 words as keywords
        if any(kw in text_lower for kw in cue_keywords):
            mentioned_cues += 1
    
    scores["cue_identification"] = min(1.0, mentioned_cues / 3.0)  # Full credit for ≥3 cues
    
    # Reasoning chain (0.2)
    has_because = "because" in text_lower or "since" in text_lower or "due to" in text_lower
    has_so = "so" in text_lower or "therefore" in text_lower or "thus" in text_lower
    
    if has_because and has_so:
        scores["reasoning_chain"] = 1.0
    elif has_because or has_so:
        scores["reasoning_chain"] = 0.6
    else:
        scores["reasoning_chain"] = 0.2
    
    return scores


def evaluate_video_prediction(
    predicted_text: str,
    ground_truth: Dict[str, Any]
) -> Dict[str, float]:
    """
    Evaluate physical outcome prediction from partial video.
    """
    text_lower = predicted_text.lower()
    scores = {}
    
    # Outcome accuracy (0.5)
    correct_outcomes = ground_truth.get("correct_outcomes", [])
    if correct_outcomes:
        matched = sum(1 for outcome in correct_outcomes if outcome.lower() in text_lower)
        scores["outcome_accuracy"] = min(1.0, matched / 1.0)
    else:
        # Check for physical plausibility keywords
        physical = ["falls", "rolls", "bounces", "stops", "lands", "hits"]
        if any(word in text_lower for word in physical):
            scores["outcome_accuracy"] = 0.5
        else:
            scores["outcome_accuracy"] = 0.2
    
    # Temporal precision (0.3)
    time_mentions = re.findall(r'(\d+(?:\.\d+)?)\s*(second|sec|s)', text_lower)
    if time_mentions:
        predicted_time = float(time_mentions[0][0])
        gt_time = ground_truth.get("expected_time_seconds", 3.0)
        time_error = abs(predicted_time - gt_time)
        scores["temporal_precision"] = max(0, 1 - (time_error / gt_time))
    else:
        scores["temporal_precision"] = 0.0
    
    # Physics plausibility (0.2)
    plausible = ["gravity", "momentum", "friction", "energy", "velocity", "acceleration"]
    mentioned = sum(1 for word in plausible if word in text_lower)
    scores["physics_plausibility"] = min(1.0, mentioned / 2.0)
    
    return scores


# Master evaluator dispatch
CUSTOM_EVALUATORS = {
    "C2": evaluate_robot_trajectory,      # Robot Trajectory
    "C1": evaluate_physics_prediction,    # Physics Causality
    "C3": evaluate_driving_action,         # Autonomous Driving
    "C4": evaluate_video_prediction,        # Video Prediction
}

def get_custom_evaluator(test_id: str):
    """Get the custom evaluator for a given test ID."""
    return CUSTOM_EVALUATORS.get(test_id)

def has_custom_evaluator(test_id: str) -> bool:
    """Check if a test has a custom evaluator."""
    return test_id in CUSTOM_EVALUATORS
