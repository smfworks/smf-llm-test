# Benchmark Results: openrouter-gemma-4-26b

**Date:** 2026-06-05T23:11:23.675548

**Environment:** warm

## Summary

| Metric | Value |
|--------|-------|
| Overall Score | 0.82/1.00 |
| Tests Passed | 7/15 |
| Errors | 0 |
| Avg Accuracy Score | 0.65 |
| Avg Time to First Token | 784ms |
| Avg Total Time | 7947ms |
| Reliability | 100.00% |
| Total Runtime | 119.2s |

## Detailed Results

### ✅ Basic Reasoning

- **Status:** success
- **Score:** 0.70
- **Time:** 5272ms (TTF: 600ms)
- **Tokens:** 232 (49.7/s)
- **Evaluation:** Rubric score: 0.70 (1/3 criteria passed)
- **Preview:** To solve this problem, we will break it down into three steps: calculating the cupcakes sold, finding the remaining amount, and adding the new batch.  **Step 1: Find how many cupcakes were sold in the...

### ✅ Code Generation

- **Status:** success
- **Score:** 0.90
- **Time:** 4367ms (TTF: 268ms)
- **Tokens:** 585 (142.7/s)
- **Evaluation:** Compiles: True, Patterns: 4/5
- **Preview:** Here is the implementation using an iterative approach, which is highly efficient with $O(n)$ time complexity and $O(1)$ space complexity.  ```python def calculate_fibonacci(n: int) -> int:     """   ...

### ❌ Debugging

- **Status:** success
- **Score:** 0.50
- **Time:** 20124ms (TTF: 1015ms)
- **Tokens:** 581 (30.4/s)
- **Evaluation:** Rubric score: 0.50 (0/2 criteria passed)
- **Preview:** Actually, looking closely at the code provided, there is **no bug** regarding calling the function twice on the same list.   In Python, when you pass a list to a function, you are passing a reference ...

### ❌ Algorithm Explanation

- **Status:** success
- **Score:** 0.50
- **Time:** 1374ms (TTF: 304ms)
- **Tokens:** 101 (94.5/s)
- **Evaluation:** Rubric score: 0.50 (0/3 criteria passed)
- **Preview:** Binary search works by repeatedly dividing a sorted array in half to locate a specific target value. The algorithm compares the target to the middle element, determining if the value lies in the left ...

### ✅ Complex Multi-Step Reasoning

- **Status:** success
- **Score:** 0.75
- **Time:** 48114ms (TTF: 264ms)
- **Tokens:** 1972 (41.2/s)
- **Evaluation:** Rubric score: 0.75 (1/2 criteria passed)
- **Preview:** To solve this puzzle, we will determine the positions of the five friends (1, 2, 3, 4, 5) step by step based on the clues provided.  ### Step 1: Determine Carol's position *   **Clue 3** states: "Caro...

### ❌ Content Generation

- **Status:** success
- **Score:** 0.50
- **Time:** 4431ms (TTF: 370ms)
- **Tokens:** 342 (84.2/s)
- **Evaluation:** Rubric score: 0.50 (0/4 criteria passed)
- **Preview:** For technical product managers, API rate limiting is not just a defensive tactic; it is a fundamental requirement for maintaining service reliability and predictable unit economics. When you build a S...

### ❌ Edge Case Handling

- **Status:** success
- **Score:** 0.50
- **Time:** 6186ms (TTF: 333ms)
- **Tokens:** 259 (44.3/s)
- **Evaluation:** Rubric score: 0.50 (0/2 criteria passed)
- **Preview:** I would love to help you plan this, but since you are leaving tomorrow and have some very specific constraints, I need a bit more information to ensure the plan is actually realistic and enjoyable for...

### ❌ Long-Context / Document RAG

- **Status:** success
- **Score:** 0.50
- **Time:** 4679ms (TTF: 295ms)
- **Tokens:** 242 (55.2/s)
- **Evaluation:** Rubric score: 0.50 (1/3 criteria passed)
- **Preview:** Based on the document provided, here are the answers to your questions:  1. **Percentage of organizations with AI in production:** According to the McKinsey Global Survey conducted in March 2025, **72...

### ✅ Structured Output / JSON Mode

- **Status:** success
- **Score:** 1.00
- **Time:** 2655ms (TTF: 1296ms)
- **Tokens:** 101 (74.3/s)
- **Evaluation:** Valid JSON: yes, Structure: 1.0, Patterns: 5/5
- **Preview:** {   "analysis": {     "topic": "API Design",     "confidence": 0.95,     "tags": [       "rest",       "json",       "documentation"     ]   },   "recommendations": [     {       "priority": 1,       ...

### ❌ Tool Use / Function Calling

- **Status:** success
- **Score:** 0.50
- **Time:** 2393ms (TTF: 1498ms)
- **Tokens:** 43 (48.1/s)
- **Evaluation:** Rubric score: 0.50 (0/3 criteria passed)
- **Preview:** `search_flights(origin='Boston', destination='London', date='July 15th')` `get_weather(city='London')` `convert_currency(amount=850.0, from_currency='USD', to_currency='EUR')`...

### ✅ Instruction Following Precision

- **Status:** success
- **Score:** 0.70
- **Time:** 3700ms (TTF: 3162ms)
- **Tokens:** 25 (46.5/s)
- **Evaluation:** Rubric score: 0.70 (2/5 criteria passed)
- **Preview:** CLOUD DATA WORKS FAST. IT USES SERVERLESS TOOLS. BIG COMPUTING GROWS. DATA FLOWS NOW. IT IS OUR FUTURE....

### ✅ Adversarial / Trick Question

- **Status:** success
- **Score:** 0.75
- **Time:** 3113ms (TTF: 602ms)
- **Tokens:** 127 (50.6/s)
- **Evaluation:** Rubric score: 0.75 (1/2 criteria passed)
- **Preview:** It would take **5 minutes**.  **Here is the breakdown:**  1.  **Analyze the rate of a single machine:** If 5 machines make 5 widgets in 5 minutes, it means each individual machine takes 5 minutes to m...

### ✅ Code Execution Reasoning

- **Status:** success
- **Score:** 0.88
- **Time:** 5864ms (TTF: 549ms)
- **Tokens:** 380 (71.5/s)
- **Evaluation:** Rubric score: 0.88 (3/4 criteria passed)
- **Preview:** ### Output  ```text [1, 2, 3, 4] [1, 2, 3, 4] [1, 2, 3, 5] ```  ---  ### Explanation  The key to understanding this code is understanding how Python handles **references** versus **copies** of mutable...

### ❌ Summarization Fidelity

- **Status:** success
- **Score:** 0.50
- **Time:** 5155ms (TTF: 640ms)
- **Tokens:** 177 (39.2/s)
- **Evaluation:** Rubric score: 0.50 (0/3 criteria passed)
- **Preview:** Quantum startup IonQ announced its Forte Enterprise processor achieved 99.9% two-qubit gate fidelity, a milestone for error-corrected quantum computing. The 36-qubit system utilizes trapped-ion techno...

### ❌ Recent Knowledge / World Events

- **Status:** success
- **Score:** 0.50
- **Time:** 1777ms (TTF: 567ms)
- **Tokens:** 51 (42.1/s)
- **Evaluation:** Rubric score: 0.50 (0/2 criteria passed)
- **Preview:** I do not have information regarding events that occur after January 2025. As my knowledge cutoff is January 2025, I cannot provide details on the outcomes or proceedings of a summit scheduled for June...

