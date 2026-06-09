#!/usr/bin/env python3
"""
Multimodal Benchmark Runner
Execute the 15-test multimodal suite against configured models.
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.multimodal_test_definitions import MULTIMODAL_TEST_SUITE, MULTIMODAL_TESTS_BY_ID
from providers.multimodal import MultimodalRequest, build_multimodal_payload
from evaluators.multimodal_custom import get_custom_evaluator, has_custom_evaluator

# Import existing provider infrastructure
from providers.openrouter import OpenRouterProvider
from providers.openai import OpenAIProvider
from providers.ollama import OllamaProvider

class MultimodalBenchmarkRunner:
    def __init__(self, config_path: str = "config.json"):
        self.config = self._load_config(config_path)
        self.results = {}
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def _load_config(self, path: str) -> dict:
        with open(path, 'r') as f:
            return json.load(f)
    
    def get_model_config(self, model_id: str) -> dict:
        return self.config.get("models", {}).get(model_id, {})
    
    def run_test(self, model_id: str, test_def, provider_instance) -> dict:
        """Run a single multimodal test."""
        print(f"  Running {test_def.id}: {test_def.name} (modality: {test_def.modality.value})", flush=True)
        
        # Build multimodal request
        request = MultimodalRequest(
            prompt=test_def.prompt,
            image_path=test_def.primary_asset if test_def.modality.value == "image" else None,
            video_path=test_def.primary_asset if test_def.modality.value == "video" else None,
            audio_path=test_def.primary_asset if test_def.modality.value == "audio" else None,
            text_context_path=test_def.secondary_asset if test_def.modality.value == "pair" else None,
            max_tokens=4096,
            temperature=0.7
        )
        
        # Handle video-as-frames for non-Gemini models
        if test_def.modality.value == "video" and "gemini" not in model_id.lower():
            # Extract frames and treat as image sequence
            from providers.multimodal import extract_video_frames
            try:
                frames = extract_video_frames(test_def.primary_asset, frame_count=3)
                # For non-Gemini, we'll send frames as images
                print(f"    Extracted {len(frames)} frames from video")
            except Exception as e:
                print(f"    Frame extraction failed: {e}")
                frames = []
        
        # Build provider-specific payload
        model_config = self.get_model_config(model_id)
        provider_type = model_config.get("provider", "openrouter")
        
        start_time = time.time()
        
        try:
            # Call provider using underlying client for multimodal
            if provider_type in ["openrouter", "openai"]:
                messages = build_multimodal_payload(provider_type, request)
                
                kwargs = {
                    "model": model_config.get("model"),
                    "messages": messages,
                    "max_tokens": 4096,
                    "temperature": 0.7,
                    "extra_headers": {
                        "HTTP-Referer": "https://smfworks.com",
                        "X-Title": "SMF Works Multimodal Benchmark",
                    }
                }
                
                completion = provider_instance.client.chat.completions.create(**kwargs)
                response = completion.choices[0].message.content
                
            elif provider_type == "ollama":
                payload = build_multimodal_payload("ollama", request)
                response = provider_instance.generate(payload)
            else:
                raise ValueError(f"Unsupported provider type: {provider_type}")
            
            elapsed = time.time() - start_time
            
            # Evaluate response
            if has_custom_evaluator(test_def.id):
                evaluator = get_custom_evaluator(test_def.id)
                # Load ground truth
                gt_path = test_def.ground_truth_path
                ground_truth = {}
                if gt_path and os.path.exists(gt_path):
                    with open(gt_path, 'r') as f:
                        ground_truth = json.load(f)
                
                scores = evaluator(response, ground_truth)
                
                # Calculate weighted score
                weights = {c["name"]: c["weight"] for c in test_def.evaluation_criteria}
                total_score = sum(scores.get(k, 0) * weights.get(k, 0) for k in scores)
                
                result = {
                    "test_id": test_def.id,
                    "passed": total_score >= 0.5,
                    "score": round(total_score, 4),
                    "details": scores,
                    "time": round(elapsed, 2),
                    "response_preview": response[:200] + "..." if len(response) > 200 else response,
                    "error": None
                }
            else:
                # Standard text evaluation (simplified — reuse existing rubric logic)
                result = {
                    "test_id": test_def.id,
                    "passed": None,  # Requires human/automated rubric evaluation
                    "score": None,
                    "time": round(elapsed, 2),
                    "response_preview": response[:200] + "..." if len(response) > 200 else response,
                    "error": None
                }
            
            return result
            
        except Exception as e:
            elapsed = time.time() - start_time
            return {
                "test_id": test_def.id,
                "passed": False,
                "score": 0.0,
                "time": round(elapsed, 2),
                "error": str(e)
            }
    
    def run_benchmark(self, model_id: str, output_dir: str = "outputs") -> dict:
        """Run full 15-test multimodal benchmark against one model."""
        print(f"\n{'='*60}")
        print(f"Multimodal Benchmark: {model_id}")
        print(f"{'='*60}")
        
        model_config = self.get_model_config(model_id)
        provider_type = model_config.get("provider", "openrouter")
        
        # Initialize provider
        if provider_type == "openrouter":
            provider = OpenRouterProvider({
                "api_key": os.getenv("OPENROUTER_API_KEY"),
                "base_url": model_config.get("base_url", "https://openrouter.ai/api/v1"),
                "model": model_config.get("model"),
                "site_url": "https://smfworks.com",
                "site_name": "SMF Works Multimodal Benchmark"
            })
        elif provider_type == "openai":
            provider = OpenAIProvider({
                "api_key": os.getenv("OPENAI_API_KEY"),
                "model": model_config.get("model")
            })
        elif provider_type == "ollama":
            provider = OllamaProvider({
                "base_url": model_config.get("base_url", "http://localhost:11434"),
                "model": model_config.get("model")
            })
        else:
            raise ValueError(f"Unsupported provider: {provider_type}")
        
        results = []
        total_score = 0
        passed_count = 0
        
        for test in MULTIMODAL_TEST_SUITE:
            result = self.run_test(model_id, test, provider)
            results.append(result)
            
            if result["score"] is not None:
                total_score += result["score"]
                if result["passed"]:
                    passed_count += 1
            
            # Rate limiting pause
            time.sleep(1)
        
        overall = total_score / len(MULTIMODAL_TEST_SUITE) if results else 0
        
        summary = {
            "model": model_id,
            "timestamp": self.timestamp,
            "overall_score": round(overall, 4),
            "passed": passed_count,
            "total": len(MULTIMODAL_TEST_SUITE),
            "results": results
        }
        
        # Save output
        os.makedirs(output_dir, exist_ok=True)
        output_file = f"{output_dir}/multimodal-{model_id}_{self.timestamp}.json"
        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\nOverall Score: {overall:.4f}")
        print(f"Passed: {passed_count}/{len(MULTIMODAL_TEST_SUITE)}")
        print(f"Results saved to: {output_file}")
        
        return summary


def main():
    if len(sys.argv) < 2:
        print("Usage: python run_multimodal.py <model_id>")
        print("\nAvailable models:")
        runner = MultimodalBenchmarkRunner()
        for model_id in runner.config.get("models", {}):
            if any(x in model_id for x in ["gpt4o", "gemini", "claude", "qwen2-vl", "nemotron-3-nano", "minimax"]):
                print(f"  - {model_id}")
        sys.exit(1)
    
    model_id = sys.argv[1]
    runner = MultimodalBenchmarkRunner()
    runner.run_benchmark(model_id)


if __name__ == "__main__":
    main()
