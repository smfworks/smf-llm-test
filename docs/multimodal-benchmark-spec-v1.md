# Multimodal Benchmark Specification v1.0

**Author:** Aiona Edge, Chief AI Research Scientist, SMF Works  
**Date:** June 6, 2026  
**Status:** Design Draft — Pending Review

---

## Executive Summary

The SMF Works Multimodal Benchmark extends our proven 15-test text-only harness to evaluate models across **five input modalities**: text, image, video, audio, and physical action. The goal is identical to the original series: test models the way users actually use them, with single-attempt, no-retry discipline.

**Key difference:** Evaluation must handle non-text outputs — coordinate arrays, action trajectories, temporal predictions, and physical reasoning chains.

---

## Target Models

| Model | Provider | Access | Modality Focus | Why Test |
|-------|----------|--------|---------------|----------|
| **GPT-4o** | OpenAI API | API | Text + Image + Audio | The standard for general multimodal |
| **Gemini 1.5 Pro** | Google API / OpenRouter | API | Text + Image + Video (long) | 1M token context, video understanding |
| **Claude 3.5 Sonnet** | Anthropic API / OpenRouter | API | Text + Image | Document analysis, chart reading |
| **Qwen2-VL** | Ollama / HuggingFace | Local | Text + Image | Open-weights vision alternative |
| **MiniMax M3** | OpenRouter | API | Text + Image + Audio | Extend existing text benchmark |
| **NVIDIA Cosmos 3** | HuggingFace / Self-host | Local/API | Text + Image + Video + Audio + Action | Physical AI world model — unique category |

---

## Test Architecture

### Three Test Tiers

| Tier | Focus | Tests | Output Types |
|------|-------|-------|-------------|
| **A. Perceptual** | "What do you see/hear?" | 6 | Text descriptions, transcriptions |
| **B. Reasoning** | "What does it mean?" | 5 | Text analysis, causal chains |
| **C. Physical/Action** | "What will happen / what should I do?" | 4 | Coordinates, trajectories, predictions |

**Total: 15 tests** — same count as text benchmark for comparability.

---

## Tier A: Perceptual Tests (6)

### A1. Image Description — Complex Scene
**Input:** High-resolution photograph of a cluttered workspace (10+ objects, 3+ people, text on screen, depth layers)  
**Prompt:** "Describe everything visible in this image. Include: all objects, people's actions, text readable on screens, spatial relationships (left/right, foreground/background), lighting conditions."
**Evaluation:**
- Object recall (0.3): Did it name ≥8 of 10 key objects?
- Action accuracy (0.2): Did it correctly describe what people are doing?
- Text extraction (0.2): Did it transcribe screen text correctly?
- Spatial precision (0.2): Are left/right, near/far relationships correct?
- Hallucination check (0.1): Did it invent objects not present?

**Asset:** `assets/images/workspace-complex-01.jpg` (synthetic or stock, annotated with ground truth)

### A2. Image Description — Abstract/Artistic
**Input:** Abstract digital art or surrealist painting  
**Prompt:** "Describe the mood, color palette, composition, and any symbolic elements. What emotion does this evoke?"
**Evaluation:**
- Color accuracy (0.3): Did it identify dominant colors correctly?
- Composition awareness (0.3): Did it note focal points, balance, negative space?
- Emotional interpretation (0.4): Is the mood description plausible and non-generic?

**Asset:** `assets/images/abstract-emotion-01.png` (generated, with intended mood documented)

### A3. Video Summary — Narrative Clip
**Input:** 60-second narrative video (e.g., cooking tutorial, DIY demonstration)  
**Prompt:** "Summarize what happens in this video in 3-4 sentences. Include the sequence of key actions and the final outcome."
**Evaluation:**
- Action sequence (0.4): Are actions in correct temporal order?
- Key event coverage (0.4): Did it mention ≥4 of 5 key events?
- Conciseness (0.2): Is summary within target length?

**Asset:** `assets/videos/cooking-tutorial-01.mp4` (60s, 5 annotated key events)

### A4. Video Summary — Dynamic Scene
**Input:** 30-second video of a busy street intersection or sports play  
**Prompt:** "Describe the motion and interactions in this scene. What is the most significant event?"
**Evaluation:**
- Motion description (0.3): Does it capture movement directions and speeds?
- Interaction identification (0.4): Did it identify the key interaction/collision/decision?
- Significance judgment (0.3): Is the "most significant event" choice defensible?

**Asset:** `assets/videos/street-intersection-01.mp4` (30s, annotated with key moment timestamp)

### A5. Audio Transcription — Clean Speech
**Input:** 30-second audio clip of clear spoken English (podcast excerpt or audiobook)  
**Prompt:** "Transcribe this audio word-for-word."
**Evaluation:**
- Word accuracy (0.7): % of words correct vs. ground truth transcript
- Punctuation (0.2): Did it add appropriate punctuation?
- Speaker labeling (0.1): If multiple speakers, did it identify them?

**Asset:** `assets/audio/clean-speech-01.mp3` (30s, ground truth transcript provided)

### A6. Audio Understanding — Noisy/Complex
**Input:** 20-second audio clip with background music + multiple speakers + ambient noise  
**Prompt:** "What is being discussed? Who are the speakers? What emotion do you detect?"
**Evaluation:**
- Topic extraction (0.4): Did it identify the subject matter?
- Speaker count (0.2): Did it correctly identify 2+ speakers?
- Emotion detection (0.3): Is the emotional tone description accurate?
- Noise resilience (0.1): Did it correctly ignore or note background music?

**Asset:** `assets/audio/noisy-conversation-01.mp3` (20s, annotated with topic, speakers, emotion)

---

## Tier B: Reasoning Tests (5)

### B1. Visual Reasoning — Chart/Data Interpretation
**Input:** Complex chart or infographic (line chart with 3+ series, or infographic with 8+ data points)  
**Prompt:** "What trend does this chart show? What is the most significant data point? What prediction would you make?"
**Evaluation:**
- Trend accuracy (0.4): Did it correctly identify the overall trend?
- Data point precision (0.3): Did it identify the correct most-significant point?
- Prediction plausibility (0.3): Is the prediction grounded in the data?

**Asset:** `assets/images/chart-complex-01.png` (generated chart with ground truth trends)

### B2. Visual Reasoning — Spatial/Geometric
**Input:** Image showing geometric puzzle or architectural floor plan  
**Prompt:** "How many triangles are in this figure?" or "What is the shortest path from A to B?"
**Evaluation:**
- Answer correctness (0.5): Exact count or correct path?
- Reasoning transparency (0.5): Did it show its work?

**Asset:** `assets/images/geometric-puzzle-01.png` (triangle counting puzzle, answer: 13)

### B3. Cross-Modal — Audio + Context
**Input:** Audio clip + accompanying text description (partial or misleading)  
**Prompt:** "The text claims X. Does the audio support or contradict this? What evidence do you hear?"
**Evaluation:**
- Contradiction detection (0.5): Did it correctly identify support/contradiction?
- Evidence citation (0.5): Did it cite specific audio moments?

**Asset:** `assets/audio/text-mismatch-01.mp3` + `assets/text/mismatch-context-01.txt` (audio contradicts text)

### B4. Cross-Modal — Video + Question
**Input:** Video clip + specific question requiring temporal reasoning  
**Prompt:** "At what timestamp does the person pick up the blue object? What happens immediately after?"
**Evaluation:**
- Timestamp accuracy (0.4): Within ±2 seconds of ground truth?
- Temporal consequence (0.4): Did it correctly describe the next event?
- Precision (0.2): Did it specify "blue object" vs. generic "object"?

**Asset:** `assets/videos/temporal-question-01.mp4` (annotated with timestamp and next event)

### B5. Cross-Modal — Image + Audio Synthesis
**Input:** Image of a scene + audio clip of ambient sound from that scene  
**Prompt:** "What is happening in this scene based on the image and sound together?"
**Evaluation:**
- Cross-modal fusion (0.4): Does it integrate both modalities coherently?
- Audio-specific insight (0.3): Did it use sound cues not visible in image?
- Image-specific insight (0.3): Did it use visual cues not audible in audio?

**Asset:** `assets/images/scene-with-sound-01.jpg` + `assets/audio/scene-sound-01.mp3`

---

## Tier C: Physical / Action Tests (4)

### C1. Physical Reasoning — Causality Prediction
**Input:** Image or short video of a physical setup (e.g., stacked blocks, pendulum, ball on ramp)  
**Prompt:** "What will happen if the red block is removed? Describe the sequence of events."
**Evaluation:**
- Causal chain (0.4): Did it predict the correct sequence?
- Physics accuracy (0.4): Is the prediction physically plausible?
- Specificity (0.2): Did it reference the red block specifically?

**Asset:** `assets/images/physics-setup-01.jpg` (stacked blocks, remove middle → top falls)

### C2. Action Prediction — Robot Trajectory
**Input:** Image of a robot arm near objects + text goal  
**Prompt:** "The robot needs to pick up the red flower and place it in the blue vase. What trajectory should the gripper follow? Provide coordinates [x, y] for each key point."
**Evaluation:**
- Coordinate format (0.2): Did it output valid [x, y] arrays?
- Start/end accuracy (0.3): Do coordinates begin near gripper and end near target?
- Obstacle avoidance (0.3): Does trajectory avoid obvious obstacles?
- Path efficiency (0.2): Is the path reasonably direct?

**Asset:** `assets/images/robot-scene-01.jpg` (annotated with gripper pos, flower pos, vase pos, obstacles)

### C3. Action Prediction — Autonomous Driving
**Input:** Dashcam-style video frame (intersection, traffic, pedestrians)  
**Prompt:** "You are driving. What action should you take? Explain your reasoning based on visible cues."
**Evaluation:**
- Action correctness (0.4): Is the action (brake/turn/accelerate/stop) appropriate?
- Cue identification (0.4): Did it identify ≥3 relevant visual cues?
- Reasoning chain (0.2): Is the logic sound?

**Asset:** `assets/images/driving-scene-01.jpg` (complex intersection, annotated with correct action)

### C4. Physical AI — Video Prediction
**Input:** 3-second video clip ending mid-action (ball rolling, person beginning to fall)  
**Prompt:** "What happens in the next 3 seconds? Describe the physical outcome."
**Evaluation:**
- Outcome accuracy (0.5): Did it predict the correct physical outcome?
- Temporal precision (0.3): Did it estimate timing reasonably?
- Physics plausibility (0.2): Is the prediction physically consistent?

**Asset:** `assets/videos/partial-action-01.mp4` (3s, ground truth continuation documented)

---

## Asset Requirements

### Image Assets (8)
- `workspace-complex-01.jpg` — cluttered workspace (synthetic or Creative Commons)
- `abstract-emotion-01.png` — abstract art (generate with image_generate)
- `chart-complex-01.png` — data chart (generate programmatically)
- `geometric-puzzle-01.png` — triangle puzzle (generate programmatically)
- `physics-setup-01.jpg` — stacked blocks (generate or stock)
- `robot-scene-01.jpg` — robot arm scene (generate or stock)
- `driving-scene-01.jpg` — dashcam frame (generate or stock)
- `scene-with-sound-01.jpg` — scene for audio pairing

### Video Assets (5)
- `cooking-tutorial-01.mp4` — 60s, 5 key events
- `street-intersection-01.mp4` — 30s, key moment
- `temporal-question-01.mp4` — for timestamp accuracy test
- `partial-action-01.mp4` — 3s, physics prediction
- `robot-video-01.mp4` — optional, for robot action test

### Audio Assets (4)
- `clean-speech-01.mp3` — 30s, ground truth transcript
- `noisy-conversation-01.mp3` — 20s, annotated
- `text-mismatch-01.mp3` — contradicts accompanying text
- `scene-sound-01.mp3` — ambient sound for cross-modal test

### Text Assets (2)
- `mismatch-context-01.txt` — contradicts audio
- Ground truth annotation files for all assets

**Total asset footprint:** ~50-100MB estimated

---

## Evaluation Framework

### Text-Output Tests (A1-A6, B1-B5)
Same automated rubric scoring as existing harness. Human review for edge cases.

### Coordinate/Array Output Tests (C2)
Custom evaluator:
```python
def evaluate_trajectory(predicted: List[Tuple[float, float]], 
                         ground_truth: List[Tuple[float, float]]) -> Dict:
    """
    Scores robot trajectory predictions.
    - Format validity: are points [x, y] tuples?
    - Endpoint accuracy: Euclidean distance from start/end targets
    - Obstacle clearance: minimum distance from known obstacles
    - Path smoothness: no erratic jumps
    """
```

### Physics Prediction Tests (C1, C3, C4)
Human-evaluated with binary correctness + reasoning quality rubric:
- Correct outcome (0.5)
- Correct reasoning (0.3)
- Specificity (0.2)

### Cross-Modal Tests (B3, B4, B5)
Require asset pairing in test definition:
```python
class MultimodalTestDefinition(TestDefinition):
    primary_asset: str  # image/video/audio path
    secondary_asset: Optional[str] = None  # paired asset
    asset_type: str  # "image" | "video" | "audio" | "pair"
```

---

## Infrastructure Requirements

### Provider Interface Changes

```python
class MultimodalRequest(LLMRequest):
    """Extends LLMRequest with asset attachment"""
    image_path: Optional[str] = None
    video_path: Optional[str] = None
    audio_path: Optional[str] = None
    # Base64 encoding handled by provider
```

### Provider-Specific Upload

| Provider | Image Upload | Video Upload | Audio Upload |
|----------|-------------|-------------|-------------|
| OpenAI (GPT-4o) | Base64 in message | Not supported (use frames) | Base64 in message |
| Google (Gemini) | File upload or base64 | File upload (up to 1 hour) | File upload |
| Anthropic (Claude) | Base64 in message | Not supported | Not supported |
| Ollama (Qwen2-VL) | Base64 in request | Not supported | Not supported |
| OpenRouter | Varies by underlying model | Varies | Varies |
| Cosmos 3 (HuggingFace) | Pipeline input | Pipeline input | Pipeline input |

**Decision:** Use base64 encoding for images across all providers. Video only for Gemini. Audio where supported.

### Cost Estimation

| Model | Image Input | Video Input | Audio Input | Expected Cost/Test |
|-------|-------------|-------------|-------------|-------------------|
| GPT-4o | ~$0.005/image | N/A | ~$0.006/min | $0.15-0.30 |
| Gemini 1.5 Pro | ~$0.003/image | ~$0.05/min | ~$0.002/min | $0.10-0.50 |
| Claude 3.5 | ~$0.003/image | N/A | N/A | $0.08-0.15 |
| Cosmos 3 | Local = compute cost | Local = compute cost | Local = compute cost | $0.05-0.20 (GPU) |

**Estimated total cost for 6 models × 15 tests:** $15-30 (mostly API costs for GPT-4o/Gemini)

---

## Execution Plan

### Phase 1: Asset Generation (Day 1)
1. Generate synthetic images (chart, geometric puzzle, abstract art)
2. Source or generate video clips
3. Record/generate audio samples
4. Create ground truth annotations
5. Validate asset quality

### Phase 2: Harness Extension (Day 2)
1. Add MultimodalRequest class
2. Implement base64 encoding for image upload
3. Add provider-specific upload logic
4. Create custom evaluators for coordinate/physics tests
5. Add asset path resolution

### Phase 3: Pilot Testing (Day 3)
1. Run 3 tests against GPT-4o to validate pipeline
2. Debug asset upload issues
3. Calibrate scoring thresholds
4. Document failure modes

### Phase 4: Full Benchmark (Days 4-6)
1. Run all 15 tests against all 6 models
2. Single attempt, no retries
3. Collect timing data
4. Generate reports

### Phase 5: Analysis & Publication (Day 7)
1. Compare results across models
2. Identify modality-specific strengths
3. Write "Beyond the Leaderboard: Multimodal Week" post
4. Publish with hero image

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Video upload failures (Gemini) | Medium | High | Fallback to frame extraction |
| Audio not supported (Claude) | High | Medium | Skip audio tests for Claude, note in report |
| Cosmos 3 setup complexity | High | High | Start setup early, use HuggingFace inference API |
| Asset quality issues | Medium | Medium | Generate synthetic assets for control |
| Cost overrun | Low | Medium | Start with cheaper models, test pipeline first |
| Evaluation subjectivity | Medium | Medium | Human review sample, automated scoring primary |

---

## Open Questions

1. **Cosmos 3 access:** Do we self-host on local GPU, use HuggingFace inference API, or NVIDIA NGC?
2. **Video for non-Gemini models:** Extract frames (e.g., 3 keyframes) or skip video tests for models without native video support?
3. **Audio for GPT-4o:** Use whisper-style transcription or native audio understanding?
4. **Scoring calibration:** Should physics prediction tests be scored by human or automated heuristic?
5. **Asset licensing:** Use synthetic/generated assets exclusively to avoid copyright issues?

---

## Recommendation

Proceed with Phase 1 (asset generation) immediately. The spec is ready for implementation. Cosmos 3 setup should begin in parallel — it's the highest-risk component due to self-hosting complexity.

**Decision needed from Michael:**
1. Approve asset generation (synthetic preferred?)
2. Cosmos 3 hosting preference (local GPU vs. HuggingFace API)
3. Budget ceiling for API costs (~$30 estimated)

---

*Aiona Edge, Chief AI Research Scientist, SMF Works*  
*June 6, 2026*