# Beyond the Leaderboard — Real-World AI Model Benchmark

A reproducible benchmark harness for testing LLMs the way users actually use them: single-attempt, no-retry, under realistic conditions. No cherry-picked prompts. No hidden retries. Just 15 standardized tests that reveal how models perform when there's no one standing behind them with a screwdriver.

**Maintained by:** [SMF Works](https://smfworks.com) — Aiona Edge, Chief AI Research Scientist

---

## Table of Contents

- [Quick Start](#quick-start)
- [What Makes This Different](#what-makes-this-different)
- [The 15 Tests](#the-15-tests)
- [Scoring Methodology](#scoring-methodology)
- [Supported Providers](#supported-providers)
- [Configuration](#configuration)
- [Usage](#usage)
- [Adding Custom Tests](#adding-custom-tests)
- [Multimodal Extension](#multimodal-extension)
- [Sample Reports](#sample-reports)
- [Contributing](#contributing)
- [License](#license)

---

## Quick Start

```bash
# Clone
git clone https://github.com/smfworks/smf-ai-benchmark.git
cd smf-ai-benchmark

# Install dependencies
pip install -r requirements.txt

# Set your API key(s)
cp .env.example .env
# Edit .env with your OpenRouter, OpenAI, or Anthropic key

# Run against any configured model
python harness.py ollama-kimik2.6

# Or run a specific test
python harness.py ollama-deepseek-v4 --tests code_generation adversarial

# Generate report
# Results saved to outputs/<model>_<timestamp>.json and .md
```

---

## What Makes This Different

Most benchmarks measure what models *can* do. We measure what models *do* when no one is watching.

| Standard Benchmarks | This Harness |
|---|---|
| Cherry-picked prompts with known answers | Adversarial, ambiguous, and real-world prompts |
| Multiple retries, temperature tuning | Single attempt, fixed temperature (0.7) |
| Academic datasets | Tests derived from actual production failures |
| Pass/fail on exact match | Rubric-based scoring with partial credit |
| Speed ignored or averaged | Time-to-first-token and total latency measured per-test |
| One-shot evaluation | Environment-aware (cold start, warm, sustained load) |

**Our philosophy:** The leaderboard is a map, not the territory. Models that score 95% on MMLU can fail at "write exactly 200 words without using the word 'scalable.'" This harness finds those gaps.

### The Single-Attempt Rule

Every test gets **one shot**. No retry logic. No "let me ask that again." If the model hallucinates, contradicts itself, or misses a constraint, it gets scored on what it actually produced. This mirrors how users interact with AI in production: they don't have a grad student standing by to re-prompt.

---

## The 15 Tests

Each test is designed to expose a specific failure mode common in production deployments.

### Category: Cognitive (4 tests)

| # | Test | What It Measures | Timeout |
|---|------|-----------------|---------|
| 1 | **Basic Reasoning** | Arithmetic + explanation quality | 30s |
| 2 | **Algorithm Explanation** | Concise technical communication | 30s |
| 3 | **Complex Multi-Step Reasoning** | Logic puzzle with 5 constraints | 300s |
| 4 | **Summarization Fidelity** | Distills 500 words to 100 without adding facts | 90s |

### Category: Coding (3 tests)

| # | Test | What It Measures | Timeout |
|---|------|-----------------|---------|
| 5 | **Code Generation** | Type hints, docstrings, edge cases, efficiency | 60s |
| 6 | **Debugging** | Identifies real vs. hallucinated bugs | 60s |
| 7 | **Code Execution Reasoning** | Predicts Python mutable reference behavior | 60s |

### Category: Reliability (5 tests)

| # | Test | What It Measures | Timeout |
|---|------|-----------------|---------|
| 8 | **Edge Case Handling** | Asks clarifying questions vs. hallucinating assumptions | 60s |
| 9 | **Long-Context / Document RAG** | Retrieves facts from 10,000-word doc at specific positions | 120s |
| 10 | **Structured Output / JSON Mode** | Returns exact schema without markdown fences | 60s |
| 11 | **Instruction Following Precision** | Follows 6 simultaneous constraints (word count, banned letters, formatting) | 60s |
| 12 | **Adversarial / Trick Question** | Resists common cognitive traps (e.g., widget problem) | 30s |

### Category: Creative (1 test)

| # | Test | What It Measures | Timeout |
|---|------|-----------------|---------|
| 13 | **Content Generation** | Writes to spec: word count, banned words, audience, tone | 90s |

### Category: Agentic (1 test)

| # | Test | What It Measures | Timeout |
|---|------|-----------------|---------|
| 14 | **Tool Use / Function Calling** | Calls correct functions with correct params in correct order | 90s |

### Category: Knowledge (1 test)

| # | Test | What It Measures | Timeout |
|---|------|-----------------|---------|
| 15 | **Recent Knowledge** | Accurately states knowledge cutoff without hallucinating | 30s |

### Test Design Principles

1. **Ambiguity is intentional.** The debugging test includes code that *actually works* — the real bug is whether the model will hallucinate one or correctly assess the code.
2. **Constraints stack.** The instruction-following test requires exactly 5 sentences, ≤15 uses of the letter 'e', the word "serverless" exactly once, ending with "future", no "scalable", and ALL CAPS. Most models fail 2-3 constraints.
3. **Context placement matters.** The RAG document buries key facts at beginning, middle, and end to test uniform attention, not just recency bias.
4. **Adversarial framing.** The adversarial test explicitly warns that "many people answer incorrectly" — testing whether the model can override its own training data's most common (wrong) answer.

---

## Scoring Methodology

### Three Scoring Engines

**1. Evaluator** — Per-test accuracy scoring

| Evaluation Type | How It Works |
|----------------|--------------|
| `exact_match` | Expected string must appear in response |
| `contains` | Response must contain ≥70% of expected patterns |
| `code_compile` | Code extracts from markdown, compiles, + pattern matching |
| `json_valid` | Extracts JSON, validates schema, checks required fields |
| `rubric` | Weighted criteria scoring (see below) |
| `human_review` | Reserved for subjective evaluation |

**2. PerformanceScorer** — Speed and reliability

| Metric | Weight | Calculation |
|--------|--------|-------------|
| **Accuracy** | 50% | Average of all test scores |
| **Timing** | 25% | Time-to-first-token + total time vs. timeout |
| **Reliability** | 25% | Error rate (timeouts, exceptions, API failures) |

**3. Overall Score** — Weighted composite

```
Overall = (Accuracy × 0.5) + (Timing × 0.25) + (Reliability × 0.25)
```

Scored 0.00–1.00. No model has scored above 0.85 on our suite.

### Rubric Scoring Detail

Rubric tests use weighted criteria. Example from **Instruction Following**:

| Criterion | Weight | How Scored |
|-----------|--------|------------|
| Exactly 5 sentences | 20% | Sentence count == 5 |
| Letter 'e' ≤ 15 times | 20% | Character frequency count |
| "serverless" exactly once | 20% | Word frequency count |
| Ends with "future" | 20% | Last word == "future" |
| ALL CAPS | 20% | `response.upper() == response` |

Partial credit is given where applicable.

---

## Supported Providers

Configure any model from these providers in `config.json`:

| Provider | Local/Cloud | Auth Required | Notes |
|----------|-------------|---------------|-------|
| **Ollama** | Local | None | Self-hosted models via `http://localhost:11434` |
| **OpenRouter** | Cloud | API Key | Access 100+ models through unified API |
| **OpenAI** | Cloud | API Key | GPT-4o, GPT-4o-mini, etc. |
| **Anthropic** | Cloud | API Key | Claude Opus, Sonnet, etc. |

### Adding a New Model

Edit `config.json`:

```json
{
  "models": {
    "my-custom-model": {
      "provider": "openrouter",
      "model": "vendor/model-name",
      "base_url": "https://openrouter.ai/api/v1",
      "timeout": 120
    }
  }
}
```

Then run:
```bash
python harness.py my-custom-model
```

---

## Configuration

### Environment Variables

Create `.env` from `.env.example`:

| Variable | Required For | Description |
|----------|-------------|-------------|
| `OPENROUTER_API_KEY` | OpenRouter models | Your OpenRouter API key |
| `OPENAI_API_KEY` | OpenAI models | Your OpenAI API key |
| `ANTHROPIC_API_KEY` | Anthropic models | Your Anthropic API key |

### Config File (`config.json`)

```json
{
  "models": { ... },
  "test_suite": {
    "tests": ["basic_reasoning", "code_generation", ...],
    "environments": ["cold_start", "warm", "sustained_load", "error_recovery"]
  },
  "metrics": {
    "time_to_first_token": true,
    "total_generation_time": true,
    "tokens_per_second": true,
    "accuracy_score": true,
    "timeout_rate": true,
    "error_recovery": true
  },
  "output": {
    "format": "markdown",
    "include_raw_responses": false,
    "include_charts": false
  }
}
```

---

## Usage

### Basic Run

```bash
# Run full suite against a configured model
python harness.py ollama-kimik2.6

# Run in specific environment
python harness.py ollama-deepseek-v4 --env cold_start

# Run specific tests
python harness.py openrouter-gpt-4o --tests instruction_following adversarial code_generation

# Custom output directory
python harness.py ollama-qwen3.5 --output ./my-results

# Custom config
python harness.py my-model --config ./my-config.json
```

### Output

Results are saved to `outputs/` as:
- **JSON** — Full structured data for programmatic analysis
- **Markdown** — Human-readable report with per-test breakdown

```
outputs/
├── ollama-kimik2.6_20240609_143022.json   # Raw data
├── ollama-kimik2.6_20240609_143022.md     # Human report
└── ...
```

### Sample Report Structure

```markdown
# Benchmark Results: ollama-kimik2.6

**Date:** 2024-06-09T14:30:22
**Environment:** warm

## Summary

| Metric | Value |
|--------|-------|
| Overall Score | 0.72/1.00 |
| Tests Passed | 9/15 |
| Errors | 1 |
| Avg Accuracy Score | 0.68 |
| Avg Time to First Token | 2200ms |
| Reliability | 93% |

## Detailed Results

### ✅ Basic Reasoning
- **Status:** success
- **Score:** 1.00
- **Time:** 3200ms (TTF: 2100ms)
- **Tokens:** 142 (44.4/s)
- **Evaluation:** Rubric score: 1.00 (3/3 criteria passed)

### ❌ Instruction Following Precision
- **Status:** success
- **Score:** 0.40
- **Time:** 5800ms (TTF: 2200ms)
- **Evaluation:** Rubric score: 0.40 (2/5 criteria passed)
- **Preview:** CLOUD COMPUTING OFFERS A WAY TO RUN CODE WITHOUT MANAGING...
```

---

## Adding Custom Tests

Create a new test in `tests/test_definitions.py`:

```python
"my_custom_test": TestDefinition(
    id="my_custom_test",
    name="My Custom Test",
    category="reliability",
    timeout_seconds=60,
    prompt="""Your prompt here with specific constraints.""",
    evaluation_type="rubric",  # or exact_match, contains, code_compile, json_valid
    rubric={
        "criterion_1": {"weight": 0.5, "description": "What to check"},
        "criterion_2": {"weight": 0.5, "expected": "exact string", "description": "Must contain this"}
    }
)
```

Add to `config.json` test_suite.tests list, then run:

```bash
python harness.py your-model --tests my_custom_test
```

---

## Multimodal Extension

The repository includes a **design draft** for extending this harness to multimodal models (vision, audio, video):

- **Document:** `docs/multimodal-benchmark-spec-v1.md`
- **Status:** Design draft — pending implementation
- **Target models:** GPT-4o, Gemini 1.5 Pro, Claude 3.5 Sonnet, Qwen2-VL
- **Test tiers:** Perceptual (6), Reasoning (5), Physical/Action (4)

Contributors interested in multimodal evaluation are welcome to open issues or PRs.

---

## Sample Reports

See `outputs/` for example benchmark reports from real runs:

| Report | Model | Overall Score |
|--------|-------|---------------|
| `sample-report-deepseek-v4.md` | DeepSeek-V4-Pro | 0.72 |
| `sample-report-kimi-k2.6.md` | Kimi K2.6 | 0.66 |
| `sample-report-gemma-4-26b.md` | Gemma 4 26B | 0.58 |

These are unedited single-attempt runs with no retries.

---

## Contributing

We welcome contributions that improve test coverage, add providers, or refine scoring.

**Before contributing:**
- Read the test design principles above
- All tests must be reproducible with a single prompt
- No external dependencies beyond the provider SDK
- Rubric criteria must be objectively scorable

**Areas we'd love help with:**
- Additional adversarial tests
- Better code evaluation (AST parsing vs. string matching)
- Automated cost tracking per model
- Visualization layer for comparing runs
- Multimodal test implementation

---

## License

MIT License — See [LICENSE](LICENSE)

**Citation:**

```bibtex
@misc{smf-benchmark-2024,
  title={Beyond the Leaderboard: Real-World AI Model Benchmark},
  author={Edge, Aiona and SMF Works},
  year={2024},
  howpublished={\url{https://github.com/smfworks/smf-ai-benchmark}}
}
```

---

## About SMF Works

[SMF Works](https://smfworks.com) is an AI services company focused on multi-agent systems, AI-powered automation, and the skills that make them useful. This benchmark is part of our commitment to transparent, reproducible AI evaluation.

**Questions?** Open an issue or reach out to Aiona Edge at aionaedge@agentmail.to.

---

*"The leaderboard is a map, not the territory."*
