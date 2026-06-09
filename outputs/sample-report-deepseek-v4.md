# Benchmark Results: ollama-deepseek-v4

**Date:** 2026-06-02T09:58:18.533282

**Environment:** warm

## Summary

| Metric | Value |
|--------|-------|
| Overall Score | 0.72/1.00 |
| Tests Passed | 6/15 |
| Errors | 0 |
| Avg Accuracy Score | 0.59 |
| Avg Time to First Token | 1751ms |
| Avg Total Time | 35020ms |
| Reliability | 100.00% |
| Total Runtime | 525.3s |

## Detailed Results

### ✅ Basic Reasoning

- **Status:** success
- **Score:** 0.70
- **Time:** 34758ms (TTF: 17923ms)
- **Tokens:** 233 (13.8/s)
- **Evaluation:** Rubric score: 0.70 (1/3 criteria passed)
- **Preview:** Step-by-step solution:  1. Start with 48 cupcakes. 2. Sell 3/4 of them in the morning:    - 3/4 × 48 = 36 cupcakes sold.    - Remaining after morning: 48 - 36 = 12 cupcakes. 3. In the afternoon, bake ...

### ✅ Code Generation

- **Status:** success
- **Score:** 0.70
- **Time:** 17030ms (TTF: 436ms)
- **Tokens:** 773 (46.6/s)
- **Evaluation:** Compiles: True, Patterns: 2/5
- **Preview:** ```python def calculate_fibonacci(n: int) -> int:     """     Calculate the nth Fibonacci number.      The Fibonacci sequence is defined as:         F(1) = 1, F(2) = 1, and F(n) = F(n-1) + F(n-2) for ...

### ❌ Debugging

- **Status:** success
- **Score:** 0.50
- **Time:** 89606ms (TTF: 448ms)
- **Tokens:** 4000 (44.9/s)
- **Evaluation:** Rubric score: 0.50 (0/2 criteria passed)

### ❌ Algorithm Explanation

- **Status:** success
- **Score:** 0.35
- **Time:** 4727ms (TTF: 391ms)
- **Tokens:** 312 (71.9/s)
- **Evaluation:** Rubric score: 0.35 (0/3 criteria passed)
- **Preview:** Binary search operates on a sorted array by repeatedly comparing the target value to the middle element of the current search interval, discarding the half that cannot contain the target based on the ...

### ❌ Complex Multi-Step Reasoning

- **Status:** success
- **Score:** 0.25
- **Time:** 75278ms (TTF: 497ms)
- **Tokens:** 4000 (53.5/s)
- **Evaluation:** Rubric score: 0.25 (0/2 criteria passed)

### ❌ Content Generation

- **Status:** success
- **Score:** 0.50
- **Time:** 112314ms (TTF: 395ms)
- **Tokens:** 4000 (35.7/s)
- **Evaluation:** Rubric score: 0.50 (0/4 criteria passed)

### ❌ Edge Case Handling

- **Status:** success
- **Score:** 0.50
- **Time:** 6689ms (TTF: 412ms)
- **Tokens:** 393 (62.6/s)
- **Evaluation:** Rubric score: 0.50 (0/2 criteria passed)
- **Preview:** I'd love to help you plan a quick warm-weather getaway! Before I can give you a solid plan, I need to fill in a few blanks so I don't make wild guesses. Here’s what I’m missing:  - **Where are you lea...

### ❌ Long-Context / Document RAG

- **Status:** success
- **Score:** 0.50
- **Time:** 16605ms (TTF: 468ms)
- **Tokens:** 483 (29.9/s)
- **Evaluation:** Rubric score: 0.50 (1/3 criteria passed)
- **Preview:** 1. According to the McKinsey Global Survey conducted in March 2025, **72%** of organizations have deployed at least one AI system in production.  2. The **AI Technical Debt Index (AI-TDI)** is a metri...

### ✅ Structured Output / JSON Mode

- **Status:** success
- **Score:** 1.00
- **Time:** 5429ms (TTF: 451ms)
- **Tokens:** 320 (64.3/s)
- **Evaluation:** Valid JSON: yes, Structure: 1.0, Patterns: 5/5
- **Preview:** {   "analysis": {     "topic": "API Design",     "confidence": 0.95,     "tags": ["rest", "json", "api"]   },   "recommendations": [     {       "priority": 1,       "action": "Implement consistent er...

### ❌ Tool Use / Function Calling

- **Status:** success
- **Score:** 0.50
- **Time:** 12206ms (TTF: 2649ms)
- **Tokens:** 534 (55.9/s)
- **Evaluation:** Rubric score: 0.50 (0/3 criteria passed)
- **Preview:** search_flights("Boston", "London", "July 15th") get_weather("London") convert_currency(850, "USD", "EUR")...

### ✅ Instruction Following Precision

- **Status:** success
- **Score:** 0.70
- **Time:** 82910ms (TTF: 380ms)
- **Tokens:** 3926 (47.6/s)
- **Evaluation:** Rubric score: 0.70 (2/5 criteria passed)
- **Preview:** CLOUD COMPUTING GRANTS INSTANT IT CAPACITY. VIRTUAL HOSTS RUN ON COMMON INFRA. SERVERLESS COMPUTING RUNS YOUR APP WITHOUT YOUR OWN HARD. DATA HOLDING WORKS ADAPTABLY IN CLOUD. CLOUD COMPUTING IS OUR D...

### ✅ Adversarial / Trick Question

- **Status:** success
- **Score:** 0.75
- **Time:** 14993ms (TTF: 453ms)
- **Tokens:** 549 (37.8/s)
- **Evaluation:** Rubric score: 0.75 (1/2 criteria passed)
- **Preview:** It takes **5 minutes**.  Here's the step-by-step reasoning:  1. **Find the rate of one machine:**      If 5 machines make 5 widgets in 5 minutes, then in those 5 minutes, each machine makes 1 widget. ...

### ✅ Code Execution Reasoning

- **Status:** success
- **Score:** 0.88
- **Time:** 16803ms (TTF: 422ms)
- **Tokens:** 670 (40.9/s)
- **Evaluation:** Rubric score: 0.88 (3/4 criteria passed)
- **Preview:** The code prints: ``` [1, 2, 3, 4] [1, 2, 3, 4] [1, 2, 3, 5] ```  **Explanation:** - `x = [1, 2, 3]` creates a list object and assigns it to `x`. - `y = x` makes `y` point to the **same** list object i...

### ❌ Summarization Fidelity

- **Status:** success
- **Score:** 0.50
- **Time:** 32967ms (TTF: 413ms)
- **Tokens:** 1611 (49.5/s)
- **Evaluation:** Rubric score: 0.50 (0/3 criteria passed)
- **Preview:** IonQ announced Tuesday that its latest quantum processor, Forte Enterprise, has achieved 99.9% two-qubit gate fidelity, a critical threshold for error-corrected quantum computing. The 36-qubit system ...

### ❌ Recent Knowledge / World Events

- **Status:** success
- **Score:** 0.50
- **Time:** 2989ms (TTF: 520ms)
- **Tokens:** 163 (66.0/s)
- **Evaluation:** Rubric score: 0.50 (0/2 criteria passed)
- **Preview:** I'm sorry, but I can't provide information about events that haven't occurred yet. My knowledge only goes up to May 2025, so I don't have details on the June 2025 G7 summit. Is there anything else I c...

