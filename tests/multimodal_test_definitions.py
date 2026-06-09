"""
Multimodal Test Definitions for SMF Works Benchmark Harness
15 tests across image, video, audio, and cross-modal reasoning
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum

class Modality(Enum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    TEXT = "text"
    PAIR = "pair"  # Two modalities together

@dataclass
class MultimodalTestDefinition:
    """Test definition with asset support for multimodal inputs"""
    id: str
    name: str
    category: str  # perceptual, reasoning, physical
    modality: Modality
    primary_asset: str  # Path to image/video/audio asset
    secondary_asset: Optional[str] = None  # For pair tests
    prompt: str = ""
    evaluation_criteria: List[Dict[str, Any]] = field(default_factory=list)
    expected_output_type: str = "text"  # text, coordinates, trajectory
    ground_truth_path: Optional[str] = None
    timeout: int = 120

# ==================== TIER A: PERCEPTUAL (6 tests) ====================

A1_IMAGE_DESCRIPTION_COMPLEX = MultimodalTestDefinition(
    id="A1",
    name="Image Description — Complex Scene",
    category="perceptual",
    modality=Modality.IMAGE,
    primary_asset="assets/images/workspace-complex-01.jpg",
    prompt="Describe everything visible in this image. Include: all objects, people's actions, text readable on screens, spatial relationships (left/right, foreground/background), lighting conditions.",
    evaluation_criteria=[
        {"name": "object_recall", "weight": 0.3, "target": "≥8 of 10 key objects named"},
        {"name": "action_accuracy", "weight": 0.2, "target": "People's actions correctly described"},
        {"name": "text_extraction", "weight": 0.2, "target": "Screen text transcribed correctly"},
        {"name": "spatial_precision", "weight": 0.2, "target": "Left/right, near/far relationships correct"},
        {"name": "hallucination_check", "weight": 0.1, "target": "No invented objects"}
    ],
    ground_truth_path="assets/ground-truth/workspace-complex-01.json",
    timeout=120
)

A2_IMAGE_DESCRIPTION_ABSTRACT = MultimodalTestDefinition(
    id="A2",
    name="Image Description — Abstract/Artistic",
    category="perceptual",
    modality=Modality.IMAGE,
    primary_asset="assets/images/abstract-emotion-01.png",
    prompt="Describe the mood, color palette, composition, and any symbolic elements. What emotion does this evoke?",
    evaluation_criteria=[
        {"name": "color_accuracy", "weight": 0.3, "target": "≥3 of 4 dominant colors identified"},
        {"name": "composition_awareness", "weight": 0.3, "target": "Focal points, balance, negative space noted"},
        {"name": "emotional_interpretation", "weight": 0.4, "target": "Mood description plausible and non-generic"}
    ],
    ground_truth_path="assets/ground-truth/abstract-emotion-01.json",
    timeout=120
)

A3_VIDEO_SUMMARY_NARRATIVE = MultimodalTestDefinition(
    id="A3",
    name="Video Summary — Narrative Clip",
    category="perceptual",
    modality=Modality.VIDEO,
    primary_asset="assets/videos/cooking-tutorial-01.mp4",
    prompt="Summarize what happens in this video in 3-4 sentences. Include the sequence of key actions and the final outcome.",
    evaluation_criteria=[
        {"name": "action_sequence", "weight": 0.4, "target": "Actions in correct temporal order"},
        {"name": "key_event_coverage", "weight": 0.4, "target": "≥4 of 5 key events mentioned"},
        {"name": "conciseness", "weight": 0.2, "target": "Summary within target length"}
    ],
    timeout=180
)

A4_VIDEO_SUMMARY_DYNAMIC = MultimodalTestDefinition(
    id="A4",
    name="Video Summary — Dynamic Scene",
    category="perceptual",
    modality=Modality.VIDEO,
    primary_asset="assets/videos/street-intersection-01.mp4",
    prompt="Describe the motion and interactions in this scene. What is the most significant event?",
    evaluation_criteria=[
        {"name": "motion_description", "weight": 0.3, "target": "Movement directions and speeds captured"},
        {"name": "interaction_identification", "weight": 0.4, "target": "Key interaction/collision/decision identified"},
        {"name": "significance_judgment", "weight": 0.3, "target": "'Most significant event' choice defensible"}
    ],
    timeout=180
)

A5_AUDIO_TRANSCRIPTION_CLEAN = MultimodalTestDefinition(
    id="A5",
    name="Audio Transcription — Clean Speech",
    category="perceptual",
    modality=Modality.AUDIO,
    primary_asset="assets/audio/clean-speech-01.mp3",
    prompt="Transcribe this audio word-for-word.",
    evaluation_criteria=[
        {"name": "word_accuracy", "weight": 0.7, "target": "% of words correct vs. ground truth"},
        {"name": "punctuation", "weight": 0.2, "target": "Appropriate punctuation added"},
        {"name": "speaker_labeling", "weight": 0.1, "target": "Multiple speakers identified if present"}
    ],
    ground_truth_path="assets/ground-truth/clean-speech-01.txt",
    timeout=120
)

A6_AUDIO_UNDERSTANDING_NOISY = MultimodalTestDefinition(
    id="A6",
    name="Audio Understanding — Noisy/Complex",
    category="perceptual",
    modality=Modality.AUDIO,
    primary_asset="assets/audio/noisy-conversation-01.mp3",
    prompt="What is being discussed? Who are the speakers? What emotion do you detect?",
    evaluation_criteria=[
        {"name": "topic_extraction", "weight": 0.4, "target": "Subject matter identified"},
        {"name": "speaker_count", "weight": 0.2, "target": "2+ speakers correctly identified"},
        {"name": "emotion_detection", "weight": 0.3, "target": "Emotional tone description accurate"},
        {"name": "noise_resilience", "weight": 0.1, "target": "Background music correctly noted/ignored"}
    ],
    ground_truth_path="assets/ground-truth/noisy-conversation-01.json",
    timeout=120
)

# ==================== TIER B: REASONING (5 tests) ====================

B1_CHART_INTERPRETATION = MultimodalTestDefinition(
    id="B1",
    name="Visual Reasoning — Chart/Data Interpretation",
    category="reasoning",
    modality=Modality.IMAGE,
    primary_asset="assets/images/chart-complex-01.png",
    prompt="What trend does this chart show? What is the most significant data point? What prediction would you make?",
    evaluation_criteria=[
        {"name": "trend_accuracy", "weight": 0.4, "target": "Overall trend correctly identified"},
        {"name": "data_point_precision", "weight": 0.3, "target": "Correct most-significant point identified"},
        {"name": "prediction_plausibility", "weight": 0.3, "target": "Prediction grounded in data"}
    ],
    ground_truth_path="assets/ground-truth/chart-complex-01.json",
    timeout=120
)

B2_GEOMETRIC_PUZZLE = MultimodalTestDefinition(
    id="B2",
    name="Visual Reasoning — Spatial/Geometric",
    category="reasoning",
    modality=Modality.IMAGE,
    primary_asset="assets/images/geometric-puzzle-01.png",
    prompt="How many triangles are in this figure?",
    evaluation_criteria=[
        {"name": "answer_correctness", "weight": 0.5, "target": "Exact count (13)"},
        {"name": "reasoning_transparency", "weight": 0.5, "target": "Shows work — counts by size or systematic enumeration"}
    ],
    ground_truth_path="assets/ground-truth/geometric-puzzle-01.json",
    timeout=120
)

B3_AUDIO_TEXT_MISMATCH = MultimodalTestDefinition(
    id="B3",
    name="Cross-Modal — Audio + Context",
    category="reasoning",
    modality=Modality.PAIR,
    primary_asset="assets/audio/text-mismatch-01.mp3",
    secondary_asset="assets/text/mismatch-context-01.txt",
    prompt="The text claims X. Does the audio support or contradict this? What evidence do you hear?",
    evaluation_criteria=[
        {"name": "contradiction_detection", "weight": 0.5, "target": "Correctly identifies support/contradiction"},
        {"name": "evidence_citation", "weight": 0.5, "target": "Cites specific audio moments"}
    ],
    ground_truth_path="assets/ground-truth/text-mismatch-01.json",
    timeout=120
)

B4_VIDEO_TEMPORAL_QUESTION = MultimodalTestDefinition(
    id="B4",
    name="Cross-Modal — Video + Question",
    category="reasoning",
    modality=Modality.VIDEO,
    primary_asset="assets/videos/temporal-question-01.mp4",
    prompt="At what timestamp does the person pick up the blue object? What happens immediately after?",
    evaluation_criteria=[
        {"name": "timestamp_accuracy", "weight": 0.4, "target": "Within ±2 seconds of ground truth"},
        {"name": "temporal_consequence", "weight": 0.4, "target": "Next event correctly described"},
        {"name": "precision", "weight": 0.2, "target": "Specifies 'blue object' vs. generic 'object'"}
    ],
    ground_truth_path="assets/ground-truth/temporal-question-01.json",
    timeout=180
)

B5_IMAGE_AUDIO_SYNTHESIS = MultimodalTestDefinition(
    id="B5",
    name="Cross-Modal — Image + Audio Synthesis",
    category="reasoning",
    modality=Modality.PAIR,
    primary_asset="assets/images/scene-with-sound-01.png",
    secondary_asset="assets/audio/scene-sound-01.mp3",
    prompt="What is happening in this scene based on the image and sound together?",
    evaluation_criteria=[
        {"name": "cross_modal_fusion", "weight": 0.4, "target": "Integrates both modalities coherently"},
        {"name": "audio_specific_insight", "weight": 0.3, "target": "Uses sound cues not visible in image"},
        {"name": "image_specific_insight", "weight": 0.3, "target": "Uses visual cues not audible in audio"}
    ],
    ground_truth_path="assets/ground-truth/scene-with-sound-01.json",
    timeout=120
)

# ==================== TIER C: PHYSICAL / ACTION (4 tests) ====================

C1_PHYSICS_CAUSALITY = MultimodalTestDefinition(
    id="C1",
    name="Physical Reasoning — Causality Prediction",
    category="physical",
    modality=Modality.IMAGE,
    primary_asset="assets/images/physics-setup-01.png",
    prompt="What will happen if the red block is removed? Describe the sequence of events.",
    evaluation_criteria=[
        {"name": "causal_chain", "weight": 0.4, "target": "Correct sequence predicted"},
        {"name": "physics_accuracy", "weight": 0.4, "target": "Prediction physically plausible"},
        {"name": "specificity", "weight": 0.2, "target": "References red block specifically"}
    ],
    ground_truth_path="assets/ground-truth/physics-setup-01.json",
    timeout=120
)

C2_ROBOT_TRAJECTORY = MultimodalTestDefinition(
    id="C2",
    name="Action Prediction — Robot Trajectory",
    category="physical",
    modality=Modality.IMAGE,
    primary_asset="assets/images/robot-scene-01.png",
    prompt="The robot needs to pick up the red flower and place it in the blue vase. What trajectory should the gripper follow? Provide coordinates [x, y] for each key point.",
    expected_output_type="coordinates",
    evaluation_criteria=[
        {"name": "format_validity", "weight": 0.2, "target": "Outputs valid [x, y] coordinate arrays"},
        {"name": "start_end_accuracy", "weight": 0.3, "target": "Starts near gripper, ends near vase"},
        {"name": "obstacle_avoidance", "weight": 0.3, "target": "Trajectory clears wooden block obstacle"},
        {"name": "path_efficiency", "weight": 0.2, "target": "Reasonable waypoint count (5-10), not erratic"}
    ],
    ground_truth_path="assets/ground-truth/robot-scene-01.json",
    timeout=120
)

C3_AUTONOMOUS_DRIVING = MultimodalTestDefinition(
    id="C3",
    name="Action Prediction — Autonomous Driving",
    category="physical",
    modality=Modality.IMAGE,
    primary_asset="assets/images/driving-scene-01.png",
    prompt="You are driving. What action should you take? Explain your reasoning based on visible cues.",
    evaluation_criteria=[
        {"name": "action_correctness", "weight": 0.4, "target": "Decelerate/stop — not proceed or accelerate"},
        {"name": "cue_identification", "weight": 0.4, "target": "≥3 of 6 critical cues mentioned"},
        {"name": "reasoning_chain", "weight": 0.2, "target": "Logic connects cues to action coherently"}
    ],
    ground_truth_path="assets/ground-truth/driving-scene-01.json",
    timeout=120
)

C4_VIDEO_PREDICTION = MultimodalTestDefinition(
    id="C4",
    name="Physical AI — Video Prediction",
    category="physical",
    modality=Modality.VIDEO,
    primary_asset="assets/videos/partial-action-01.mp4",
    prompt="What happens in the next 3 seconds? Describe the physical outcome.",
    evaluation_criteria=[
        {"name": "outcome_accuracy", "weight": 0.5, "target": "Correct physical outcome predicted"},
        {"name": "temporal_precision", "weight": 0.3, "target": "Timing estimated reasonably"},
        {"name": "physics_plausibility", "weight": 0.2, "target": "Prediction physically consistent"}
    ],
    ground_truth_path="assets/ground-truth/partial-action-01.json",
    timeout=180
)

# ==================== TEST SUITE ====================

MULTIMODAL_TEST_SUITE = [
    A1_IMAGE_DESCRIPTION_COMPLEX,
    A2_IMAGE_DESCRIPTION_ABSTRACT,
    A3_VIDEO_SUMMARY_NARRATIVE,
    A4_VIDEO_SUMMARY_DYNAMIC,
    A5_AUDIO_TRANSCRIPTION_CLEAN,
    A6_AUDIO_UNDERSTANDING_NOISY,
    B1_CHART_INTERPRETATION,
    B2_GEOMETRIC_PUZZLE,
    B3_AUDIO_TEXT_MISMATCH,
    B4_VIDEO_TEMPORAL_QUESTION,
    B5_IMAGE_AUDIO_SYNTHESIS,
    C1_PHYSICS_CAUSALITY,
    C2_ROBOT_TRAJECTORY,
    C3_AUTONOMOUS_DRIVING,
    C4_VIDEO_PREDICTION,
]

# Map for easy lookup
MULTIMODAL_TESTS_BY_ID = {test.id: test for test in MULTIMODAL_TEST_SUITE}
