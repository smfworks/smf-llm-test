"""
SMF Works Real-World AI Model Testing Suite
15 standardized tests with evaluation criteria
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Callable

@dataclass
class TestDefinition:
    id: str
    name: str
    category: str
    timeout_seconds: int
    prompt: str
    evaluation_type: str  # 'exact_match', 'contains', 'code_compile', 'json_valid', 'rubric', 'human_review'
    expected_patterns: Optional[List[str]] = None
    rubric: Optional[Dict[str, Any]] = None
    requires_tool: bool = False
    requires_context: bool = False
    context_document: Optional[str] = None

TESTS = {
    "basic_reasoning": TestDefinition(
        id="basic_reasoning",
        name="Basic Reasoning",
        category="cognitive",
        timeout_seconds=30,
        prompt="""Solve this step by step, showing your work: A bakery has 48 cupcakes. They sell 3/4 of them in the morning. In the afternoon, they bake 24 more. How many cupcakes do they have at the end of the day? Explain your reasoning in 2-3 sentences.""",
        evaluation_type="rubric",
        rubric={
            "correct_answer": {"weight": 0.4, "expected": "36", "description": "Final answer must be 36"},
            "shows_work": {"weight": 0.3, "description": "Shows intermediate steps (48 * 3/4 = 36, 48-36=12, 12+24=36)"},
            "concise_explanation": {"weight": 0.3, "description": "Explanation in 2-3 sentences"}
        }
    ),

    "code_generation": TestDefinition(
        id="code_generation",
        name="Code Generation",
        category="coding",
        timeout_seconds=60,
        prompt="""Write a Python function called `calculate_fibonacci` that returns the nth Fibonacci number.
Requirements:
- Use type hints
- Include a docstring explaining parameters and return value
- Handle edge cases (n <= 0)
- Use an efficient algorithm (not naive recursion)
- Return the result, don't print it""",
        evaluation_type="code_compile",
        expected_patterns=["def calculate_fibonacci", "Type hints", "docstring", "n <= 0", "O(n)"]
    ),

    "debugging": TestDefinition(
        id="debugging",
        name="Debugging",
        category="coding",
        timeout_seconds=60,
        prompt="""This Python code has a bug. Find it, fix it, and explain why it was wrong:

```python
def process_data(items):
    result = []
    for item in items:
        if item > 0:
            result.append(item * 2)
    return result

data = [1, -2, 3, -4, 5]
print(process_data(data))  # Expected: [2, 6, 10]
```

Wait, actually the output IS [2, 6, 10]. The bug is more subtle. Look at what happens if we call `process_data` twice on the same list.""",
        evaluation_type="rubric",
        rubric={
            "identifies_mutability_bug": {"weight": 0.5, "description": "Recognizes that if `result` were initialized outside or if items were modified, but the real bug is: what if items contains non-integers? Or what if we need to handle the case where the function modifies items? Actually, re-reading: the function is fine. The 'subtle bug' hint is a test of whether they'll hallucinate a bug or correctly say 'this code is actually correct for the stated behavior'."},
            "correct_assessment": {"weight": 0.5, "description": "Either correctly identifies no bug OR correctly finds a real edge case (type safety, empty list handling, etc.)"}
        }
    ),

    "algorithm_explanation": TestDefinition(
        id="algorithm_explanation",
        name="Algorithm Explanation",
        category="cognitive",
        timeout_seconds=30,
        prompt="""Explain how a binary search algorithm works in exactly 3 sentences. Then state its time and space complexity.""",
        evaluation_type="rubric",
        rubric={
            "three_sentences": {"weight": 0.3, "description": "Exactly 3 sentences for explanation"},
            "correct_logic": {"weight": 0.4, "description": "Correctly describes sorted array, middle element comparison, halving search space"},
            "complexity": {"weight": 0.3, "description": "States O(log n) time, O(1) space (iterative) or O(log n) stack (recursive)"}
        }
    ),

    "complex_reasoning": TestDefinition(
        id="complex_reasoning",
        name="Complex Multi-Step Reasoning",
        category="cognitive",
        timeout_seconds=300,
        prompt="""Five friends (Alice, Bob, Carol, Dave, Eve) are sitting in a row. Solve this logic puzzle:

1. Alice is not at either end
2. Bob sits next to exactly one person who wears glasses
3. Carol sits in the middle (position 3)
4. Dave is to the left of someone who is to the left of Eve
5. The person in position 2 wears glasses

Question: Who sits in position 4? Explain your reasoning step by step.""",
        evaluation_type="rubric",
        rubric={
            "correct_answer": {"weight": 0.5, "expected": "Dave", "description": "Position 4 is Dave"},
            "logical_steps": {"weight": 0.5, "description": "Shows valid deduction chain: Carol=3, Alice∈{2,4}, Dave left of someone left of Eve means Dave∈{1,2}, if Dave=2 then Alice=4, but then Bob and Eve at 1,5..."}
        }
    ),

    "content_generation": TestDefinition(
        id="content_generation",
        name="Content Generation",
        category="creative",
        timeout_seconds=90,
        prompt="""Write exactly 200 words explaining why API rate limiting is important for SaaS businesses. Target audience: technical product managers. Tone: professional but conversational. Do not use the words 'scalable', 'robust', or 'leverage'.""",
        evaluation_type="rubric",
        rubric={
            "word_count": {"weight": 0.2, "description": "180-220 words"},
            "banned_words": {"weight": 0.2, "description": "Does not use 'scalable', 'robust', or 'leverage'"},
            "audience_match": {"weight": 0.3, "description": "Appropriate depth for technical PMs (not too basic, not engineer-deep)"},
            "tone": {"weight": 0.3, "description": "Professional but conversational"}
        }
    ),

    "edge_case_handling": TestDefinition(
        id="edge_case_handling",
        name="Edge Case Handling",
        category="reliability",
        timeout_seconds=60,
        prompt="""I want you to plan a trip for me. I leave tomorrow, I want to go somewhere warm, I have a budget of $500, and I hate flying.

(Note: intentionally missing key information like departure city, duration, and specific preferences. The correct response should ask clarifying questions rather than hallucinating assumptions.)""",
        evaluation_type="rubric",
        rubric={
            "asks_clarifying_questions": {"weight": 0.6, "description": "Asks about departure location, trip duration, at minimum"},
            "no_hallucinated_assumptions": {"weight": 0.4, "description": "Does not invent departure city, dates, or specific destinations"}
        }
    ),

    "long_context_rag": TestDefinition(
        id="long_context_rag",
        name="Long-Context / Document RAG",
        category="reliability",
        timeout_seconds=120,
        requires_context=True,
        context_document="""ARTIFICIAL INTELLIGENCE IN MODERN ENTERPRISES: A COMPREHENSIVE ANALYSIS

[This is a 10,000-word technical document. Key facts embedded at specific positions:]

[BEGINNING - Paragraph 1-5]
The adoption of artificial intelligence in enterprise settings has accelerated dramatically since 2023. According to the McKinsey Global Survey conducted in March 2025, 72% of organizations have deployed at least one AI system in production, up from 55% in 2024. The primary drivers cited were operational efficiency (68% of respondents), cost reduction (52%), and competitive pressure (47%). However, the survey also revealed significant challenges: 41% of organizations reported difficulties with data quality, 38% struggled with integration into existing workflows, and 33% cited talent shortages as a major barrier.

The financial implications are substantial. Gartner estimates that global enterprise AI spending reached $184 billion in 2024, with projections indicating $298 billion by 2027. The average ROI timeline for AI implementations has shortened from 24 months in 2022 to 14 months in 2024, suggesting that organizations are becoming more sophisticated in their deployment strategies.

[MIDDLE - Paragraph 50-55]
A critical but often overlooked aspect of AI deployment is the 'technical debt' accumulated through rapid implementation. Dr. Sarah Chen of MIT's Computer Science and Artificial Intelligence Laboratory (CSAIL) published research in October 2024 demonstrating that 63% of production AI systems contain at least one significant architectural flaw that will require refactoring within 18 months. The most common issues include: monolithic model architectures that resist updating (34% of flawed systems), insufficient monitoring and observability pipelines (28%), and hardcoded business logic that couples models to specific use cases (22%).

Chen's research introduced the 'AI Technical Debt Index' (AI-TDI), which quantifies these risks on a scale of 0-100. Organizations with scores above 60 are considered high-risk. The average AI-TDI for Fortune 500 companies in 2024 was 47, indicating moderate but manageable technical debt. However, organizations that rushed implementations during the 2023-2024 hype cycle showed average scores of 71, placing them in the high-risk category.

The recommended remediation approach, according to Chen, involves three phases: (1) audit and inventory all production AI systems, (2) establish clear model versioning and lineage tracking, and (3) implement continuous monitoring for data drift, model degradation, and concept drift. Organizations that followed this three-phase approach reduced their AI-TDI by an average of 23 points over 12 months.

[END - Paragraph 95-100]
Looking forward, the next frontier in enterprise AI is not larger models but more intelligent integration. The 2025 AI Infrastructure Report from Stanford HAI emphasizes that 'model performance plateaus are driving investment toward orchestration layers, retrieval systems, and multi-agent architectures.' The report identifies three emerging paradigms that will define the 2026-2028 landscape:

First, 'composable AI' — systems built from interchangeable, domain-specific models coordinated through a meta-layer. This approach reduces single-model dependency and enables more granular updates.

Second, 'continuous learning pipelines' that update models incrementally without full retraining. This addresses the 'frozen model' problem where production systems become outdated within months of deployment.

Third, 'cognitive architecture standards' that define how multiple AI systems should coordinate, share context, and maintain state across interactions. The IEEE P3123 working group, established in late 2024, is developing these standards with expected publication in Q3 2026.

The report concludes with a stark warning: 'Organizations that continue to treat AI as a point solution rather than an infrastructure layer will face compounding integration costs that exceed their initial AI investments by 2028.' This aligns with the broader consensus that AI maturity is measured not by model capability but by operational sophistication.

Key statistics from this document:
- 72% of organizations have deployed AI in production (McKinsey 2025)
- $184 billion enterprise AI spending in 2024 (Gartner)
- 63% of production AI systems have architectural flaws (Chen/CSAIL, Oct 2024)
- Average Fortune 500 AI-TDI: 47 (Chen/CSAIL)
- High-risk organizations (rushed implementations): AI-TDI of 71
- IEEE P3123 expected publication: Q3 2026""",
        prompt="""Based on the document provided, answer these three questions:
1. What percentage of organizations have deployed AI in production according to McKinsey?
2. What is the 'AI Technical Debt Index' and who created it?
3. What are the three emerging paradigms identified by the Stanford HAI report for 2026-2028?""",
        evaluation_type="rubric",
        rubric={
            "mckinsey_stat": {"weight": 0.33, "expected": "72%", "description": "Correctly identifies 72%"},
            "ai_tdi": {"weight": 0.33, "expected": "Sarah Chen, MIT CSAIL", "description": "Names Chen and MIT CSAIL"},
            "three_paradigms": {"weight": 0.34, "description": "Lists composable AI, continuous learning pipelines, cognitive architecture standards"}
        }
    ),

    "structured_output": TestDefinition(
        id="structured_output",
        name="Structured Output / JSON Mode",
        category="reliability",
        timeout_seconds=60,
        prompt="""Return a JSON object with this exact schema (no markdown fences, no extra text):

{
  "analysis": {
    "topic": string (exactly "API Design"),
    "confidence": number (between 0.0 and 1.0),
    "tags": array of 3 strings (must include "rest" and "json")
  },
  "recommendations": [
    {
      "priority": number (1-3),
      "action": string (max 50 chars),
      "estimated_hours": number (integer)
    }
  ] (exactly 2 items)
}

Fill in reasonable values. Do not wrap in ```json or ```.""",
        evaluation_type="json_valid",
        expected_patterns=["\"topic\": \"API Design\"", "\"tags\":", "\"rest\"", "\"json\"", "\"recommendations\":"]
    ),

    "tool_use": TestDefinition(
        id="tool_use",
        name="Tool Use / Function Calling",
        category="agentic",
        timeout_seconds=90,
        requires_tool=True,
        prompt="""You have access to these functions:
1. `get_weather(city: str)` - returns weather for a city
2. `convert_currency(amount: float, from_currency: str, to_currency: str)` - converts currency
3. `search_flights(origin: str, destination: str, date: str)` - searches flights

Task: "I need to fly from Boston to London on July 15th. What's the weather in London? And if the flight costs $850, how much is that in Euros?"

Call the functions in the correct order with correct parameters.""",
        evaluation_type="rubric",
        rubric={
            "correct_tools": {"weight": 0.4, "description": "Calls all 3 functions: search_flights, get_weather, convert_currency"},
            "correct_params": {"weight": 0.4, "description": "Boston, London, July 15th; London; 850, USD, EUR"},
            "correct_order": {"weight": 0.2, "description": "Flights → Weather → Currency (or any logical order, not missing dependencies)"}
        }
    ),

    "instruction_following": TestDefinition(
        id="instruction_following",
        name="Instruction Following Precision",
        category="reliability",
        timeout_seconds=60,
        prompt="""Write a paragraph about cloud computing with these exact constraints:
- Exactly 5 sentences
- Do not use the letter 'e' more than 15 times
- Include the word "serverless" exactly once
- End with the word "future"
- Do not use the word "scalable"
- Format in ALL CAPS""",
        evaluation_type="rubric",
        rubric={
            "five_sentences": {"weight": 0.2, "description": "Exactly 5 sentences"},
            "e_count": {"weight": 0.2, "description": "Letter 'e' appears at most 15 times"},
            "serverless_once": {"weight": 0.2, "description": "'serverless' appears exactly once"},
            "ends_with_future": {"weight": 0.2, "description": "Last word is 'future'"},
            "all_caps": {"weight": 0.2, "description": "Entire output is uppercase"}
        }
    ),

    "adversarial": TestDefinition(
        id="adversarial",
        name="Adversarial / Trick Question",
        category="reliability",
        timeout_seconds=30,
        prompt="""If it takes 5 machines 5 minutes to make 5 widgets, how long would it take 100 machines to make 100 widgets?

Hint: Many people incorrectly answer 100 minutes. Think carefully.""",
        evaluation_type="rubric",
        rubric={
            "correct_answer": {"weight": 0.5, "expected": "5 minutes", "description": "Answers 5 minutes (not 100)"},
            "correct_reasoning": {"weight": 0.5, "description": "Explains that each machine makes 1 widget in 5 minutes, so 100 machines make 100 widgets in 5 minutes"}
        }
    ),

    "code_execution_reasoning": TestDefinition(
        id="code_execution_reasoning",
        name="Code Execution Reasoning",
        category="coding",
        timeout_seconds=60,
        prompt="""What does this Python code print? Explain why:

```python
def mystery():
    x = [1, 2, 3]
    y = x
    z = x[:]
    y.append(4)
    z.append(5)
    print(x)
    print(y)
    print(z)

mystery()
```""",
        evaluation_type="rubric",
        rubric={
            "x_output": {"weight": 0.25, "expected": "[1, 2, 3, 4]", "description": "x prints [1, 2, 3, 4]"},
            "y_output": {"weight": 0.25, "expected": "[1, 2, 3, 4]", "description": "y prints [1, 2, 3, 4]"},
            "z_output": {"weight": 0.25, "expected": "[1, 2, 3, 5]", "description": "z prints [1, 2, 3, 5]"},
            "reference_explanation": {"weight": 0.25, "description": "Explains y is a reference to x, z is a copy (slice)"}
        }
    ),

    "summarization": TestDefinition(
        id="summarization",
        name="Summarization Fidelity",
        category="cognitive",
        timeout_seconds=90,
        prompt="""Summarize this article in exactly 100 words. Preserve all key facts. Do not add information not in the text.

ARTICLE:
Quantum computing startup IonQ announced Tuesday that its latest quantum processor, Forte Enterprise, has achieved a 99.9% two-qubit gate fidelity, a critical threshold for error-corrected quantum computing. The 36-qubit system demonstrated this performance at room temperature using trapped-ion technology, defying conventional wisdom that extreme cryogenic cooling is necessary. CEO Peter Chapman noted that this breakthrough could accelerate commercial quantum advantage timelines by 2-3 years. The company also revealed partnerships with three Fortune 500 companies in finance, logistics, and pharmaceuticals to develop quantum-ready algorithms. However, independent physicists cautioned that gate fidelity is just one metric and that full error correction requires millions of physical qubits, not dozens. The stock rose 12% on the news but remains 67% below its 2021 IPO price.""",
        evaluation_type="rubric",
        rubric={
            "word_count": {"weight": 0.2, "description": "90-110 words"},
            "key_facts": {"weight": 0.6, "description": "Mentions: IonQ, Forte Enterprise, 99.9% fidelity, 36 qubits, room temperature, trapped-ion, Peter Chapman, 2-3 year acceleration, 3 Fortune 500 partnerships, independent physicist caution, millions of qubits needed, stock +12%, 67% below IPO"},
            "no_hallucination": {"weight": 0.2, "description": "Does not add facts not in text"}
        }
    ),

    "recent_knowledge": TestDefinition(
        id="recent_knowledge",
        name="Recent Knowledge / World Events",
        category="knowledge",
        timeout_seconds=30,
        prompt="""What happened at the June 2025 G7 summit in Kananaskis, Canada? What were the main outcomes?""",
        evaluation_type="rubric",
        rubric={
            "acknowledges_uncertainty": {"weight": 0.5, "description": "If model has knowledge cutoff before June 2025, should state this clearly rather than hallucinate"},
            "no_hallucination": {"weight": 0.5, "description": "Does not invent specific outcomes, leaders, or agreements"}
        }
    )
}

ENVIRONMENT_CONFIGS = {
    "cold_start": {
        "description": "First request after idle period",
        "setup": "sleep_30_seconds",
        "runs": 1
    },
    "warm": {
        "description": "Subsequent requests",
        "setup": "run_priming_prompt",
        "runs": 3
    },
    "sustained_load": {
        "description": "5 rapid-fire requests",
        "setup": "rapid_fire_5",
        "runs": 5,
        "delay_between_ms": 100
    },
    "error_recovery": {
        "description": "Bad prompt followed by valid prompt",
        "setup": "error_then_valid",
        "runs": 2
    }
}
