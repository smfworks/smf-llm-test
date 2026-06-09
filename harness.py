#!/usr/bin/env python3
"""
SMF Works Real-World AI Model Benchmark Harness
Runs the 15-test suite against configured LLM providers
"""

import json
import time
import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add package paths
sys.path.insert(0, str(Path(__file__).parent))

from tests.test_definitions import TESTS, ENVIRONMENT_CONFIGS
from providers.base import LLMRequest
from evaluators.scoring import Evaluator, PerformanceScorer

# Provider imports (lazy to avoid missing deps)
PROVIDER_MAP = {}

def load_provider(name: str, config: Dict[str, Any]):
    """Dynamically load a provider by name"""
    global PROVIDER_MAP
    if not PROVIDER_MAP:
        try:
            from providers.ollama import OllamaProvider
            PROVIDER_MAP["ollama"] = OllamaProvider
        except ImportError as e:
            print(f"Warning: Ollama provider not available: {e}")
        try:
            from providers.openai import OpenAIProvider
            PROVIDER_MAP["openai"] = OpenAIProvider
        except ImportError as e:
            print(f"Warning: OpenAI provider not available: {e}")
        try:
            from providers.anthropic import AnthropicProvider
            PROVIDER_MAP["anthropic"] = AnthropicProvider
        except ImportError as e:
            print(f"Warning: Anthropic provider not available: {e}")
        try:
            from providers.openrouter import OpenRouterProvider
            PROVIDER_MAP["openrouter"] = OpenRouterProvider
        except ImportError as e:
            print(f"Warning: OpenRouter provider not available: {e}")
    
    provider_class = PROVIDER_MAP.get(config["provider"])
    if not provider_class:
        raise ValueError(f"Provider '{config['provider']}' not available. Install dependencies.")
    
    return provider_class(config)


class BenchmarkHarness:
    def __init__(self, config_path: str = "config.json"):
        with open(config_path) as f:
            self.config = json.load(f)
        self.evaluator = Evaluator()
        self.scorer = PerformanceScorer()
    
    def run_test(self, test_id: str, model_id: str, environment: str = "warm") -> Dict[str, Any]:
        """Run a single test against a model"""
        test = TESTS.get(test_id)
        if not test:
            raise ValueError(f"Unknown test: {test_id}")
        
        model_config = self.config["models"].get(model_id)
        if not model_config:
            raise ValueError(f"Unknown model: {model_id}")
        
        provider = load_provider(model_id, model_config)
        
        # Build request
        request = LLMRequest(
            prompt=test.prompt,
            max_tokens=4000,
            temperature=0.7,
            context_document=test.context_document
        )
        
        # For JSON mode tests
        if test.evaluation_type == "json_valid":
            request.response_format = {"type": "json_object"}
        
        # Run the test
        print(f"  Running {test_id}...", end="", flush=True)
        start = time.perf_counter()
        
        try:
            response = provider.generate(request)
            elapsed = time.perf_counter() - start
            
            if response.error:
                print(f" ERROR: {response.error}")
                result = {
                    "test_id": test_id,
                    "test_name": test.name,
                    "status": "error",
                    "error": response.error,
                    "time_to_first_token_ms": response.time_to_first_token_ms,
                    "total_time_ms": response.total_time_ms,
                    "timeout": response.total_time_ms >= test.timeout_seconds * 1000
                }
            else:
                # Evaluate the response
                eval_result = self.evaluator.evaluate(test, response.text)
                
                # Score timing
                timing_scores = self.scorer.score_timing(
                    response.time_to_first_token_ms,
                    response.total_time_ms,
                    test.timeout_seconds
                )
                
                print(f" OK (score: {eval_result['score']:.2f}, time: {response.total_time_ms:.0f}ms)")
                
                result = {
                    "test_id": test_id,
                    "test_name": test.name,
                    "status": "success",
                    "score": eval_result["score"],
                    "passed": eval_result["passed"],
                    "evaluation_details": eval_result["details"],
                    "time_to_first_token_ms": response.time_to_first_token_ms,
                    "total_time_ms": response.total_time_ms,
                    "tokens_generated": response.tokens_generated,
                    "tokens_per_second": response.tokens_per_second,
                    "timing_score": timing_scores["overall_timing"],
                    "response_preview": response.text[:500] if response.text else "",
                    "raw_criteria": eval_result.get("criteria", {})
                }
        
        except Exception as e:
            print(f" EXCEPTION: {e}")
            result = {
                "test_id": test_id,
                "test_name": test.name,
                "status": "exception",
                "error": str(e),
                "time_to_first_token_ms": 0,
                "total_time_ms": (time.perf_counter() - start) * 1000,
            }
        
        return result
    
    def run_suite(self, model_id: str, tests: List[str] = None, 
                  environment: str = "warm") -> Dict[str, Any]:
        """Run the full test suite against a model"""
        if tests is None:
            tests = list(TESTS.keys())
        
        print(f"\n{'='*60}")
        print(f"Benchmark: {model_id}")
        print(f"Environment: {environment}")
        print(f"Tests: {len(tests)}")
        print(f"Started: {datetime.now().isoformat()}")
        print(f"{'='*60}\n")
        
        results = []
        total_time = 0
        errors = 0
        passes = 0
        
        for test_id in tests:
            result = self.run_test(test_id, model_id, environment)
            results.append(result)
            total_time += result.get("total_time_ms", 0)
            if result["status"] in ("error", "exception"):
                errors += 1
            elif result.get("passed", False):
                passes += 1
        
        # Calculate aggregate scores
        successful_results = [r for r in results if r["status"] == "success"]
        avg_score = sum(r["score"] for r in successful_results) / len(successful_results) if successful_results else 0
        avg_ttf = sum(r["time_to_first_token_ms"] for r in results) / len(results) if results else 0
        avg_total = sum(r["total_time_ms"] for r in results) / len(results) if results else 0
        
        reliability = self.scorer.score_reliability(errors, len(results))
        
        summary = {
            "model": model_id,
            "environment": environment,
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(tests),
            "passed": passes,
            "failed": len(successful_results) - passes,
            "errors": errors,
            "avg_score": avg_score,
            "avg_time_to_first_token_ms": avg_ttf,
            "avg_total_time_ms": avg_total,
            "total_runtime_ms": total_time,
            "reliability_score": reliability,
            "overall_score": self.scorer.calculate_overall_score(
                avg_score,
                (1.0 if avg_total < 30000 else 0.7 if avg_total < 60000 else 0.4),
                reliability
            ),
            "results": results
        }
        
        return summary
    
    def save_results(self, summary: Dict[str, Any], output_dir: str = "outputs"):
        """Save results to JSON and generate markdown report"""
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_name = summary["model"].replace("/", "-")
        
        # Save raw JSON
        json_file = out_path / f"{model_name}_{timestamp}.json"
        with open(json_file, "w") as f:
            json.dump(summary, f, indent=2, default=str)
        print(f"\nResults saved to: {json_file}")
        
        # Generate markdown report
        md_file = out_path / f"{model_name}_{timestamp}.md"
        self._generate_markdown(summary, md_file)
        print(f"Report saved to: {md_file}")
        
        return json_file, md_file
    
    def _generate_markdown(self, summary: Dict[str, Any], path: Path):
        """Generate a human-readable markdown report"""
        with open(path, "w") as f:
            f.write(f"# Benchmark Results: {summary['model']}\n\n")
            f.write(f"**Date:** {summary['timestamp']}\n\n")
            f.write(f"**Environment:** {summary['environment']}\n\n")
            f.write(f"## Summary\n\n")
            f.write(f"| Metric | Value |\n")
            f.write(f"|--------|-------|\n")
            f.write(f"| Overall Score | {summary['overall_score']:.2f}/1.00 |\n")
            f.write(f"| Tests Passed | {summary['passed']}/{summary['total_tests']} |\n")
            f.write(f"| Errors | {summary['errors']} |\n")
            f.write(f"| Avg Accuracy Score | {summary['avg_score']:.2f} |\n")
            f.write(f"| Avg Time to First Token | {summary['avg_time_to_first_token_ms']:.0f}ms |\n")
            f.write(f"| Avg Total Time | {summary['avg_total_time_ms']:.0f}ms |\n")
            f.write(f"| Reliability | {summary['reliability_score']:.2%} |\n")
            f.write(f"| Total Runtime | {summary['total_runtime_ms']/1000:.1f}s |\n")
            f.write(f"\n## Detailed Results\n\n")
            
            for result in summary["results"]:
                status_icon = "✅" if result.get("passed") else "❌" if result["status"] == "success" else "⚠️"
                f.write(f"### {status_icon} {result['test_name']}\n\n")
                f.write(f"- **Status:** {result['status']}\n")
                if "score" in result:
                    f.write(f"- **Score:** {result['score']:.2f}\n")
                f.write(f"- **Time:** {result.get('total_time_ms', 0):.0f}ms (TTF: {result.get('time_to_first_token_ms', 0):.0f}ms)\n")
                if result.get('tokens_generated'):
                    f.write(f"- **Tokens:** {result['tokens_generated']} ({result.get('tokens_per_second', 0):.1f}/s)\n")
                if result.get('evaluation_details'):
                    f.write(f"- **Evaluation:** {result['evaluation_details']}\n")
                if result.get('error'):
                    f.write(f"- **Error:** {result['error']}\n")
                if result.get('response_preview'):
                    preview = result['response_preview'].replace('\n', ' ')[:200]
                    f.write(f"- **Preview:** {preview}...\n")
                f.write(f"\n")


def main():
    parser = argparse.ArgumentParser(description="SMF Works AI Model Benchmark")
    parser.add_argument("model", help="Model ID from config (e.g., ollama-kimik2.6)")
    parser.add_argument("--tests", nargs="+", help="Specific tests to run")
    parser.add_argument("--env", default="warm", choices=["cold_start", "warm", "sustained_load", "error_recovery"])
    parser.add_argument("--output", default="outputs", help="Output directory")
    parser.add_argument("--config", default="config.json", help="Config file path")
    
    args = parser.parse_args()
    
    harness = BenchmarkHarness(args.config)
    
    # Run the suite
    summary = harness.run_suite(
        model_id=args.model,
        tests=args.tests,
        environment=args.env
    )
    
    # Save results
    harness.save_results(summary, args.output)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Benchmark Complete")
    print(f"Overall Score: {summary['overall_score']:.2f}/1.00")
    print(f"Passed: {summary['passed']}/{summary['total_tests']}")
    print(f"Errors: {summary['errors']}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
