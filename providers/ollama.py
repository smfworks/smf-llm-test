"""
Ollama provider for benchmarking
"""

import requests
import json
import time
from typing import Dict, Any, Optional
from .base import BaseProvider, LLMRequest, LLMResponse

class OllamaProvider(BaseProvider):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get("base_url", "http://localhost:11434")
    
    def generate(self, request: LLMRequest) -> LLMResponse:
        # Build prompt with context document if provided
        full_prompt = request.prompt
        if request.context_document:
            full_prompt = f"Context:\n{request.context_document}\n\n{request.prompt}"
        
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": True,
            "options": {
                "temperature": request.temperature,
            }
        }
        
        if request.system_prompt:
            payload["system"] = request.system_prompt
        
        if request.max_tokens:
            payload["options"]["num_predict"] = request.max_tokens
        
        # Add format constraint for JSON mode
        if request.response_format:
            payload["format"] = request.response_format
        
        start_time = time.perf_counter()
        first_token_time = None
        full_text = ""
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                stream=True,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode('utf-8'))
                        if "response" in data:
                            if first_token_time is None:
                                first_token_time = time.perf_counter()
                            full_text += data["response"]
                        
                        # Check if done
                        if data.get("done", False):
                            end_time = time.perf_counter()
                            total_ms = (end_time - start_time) * 1000
                            ttf_ms = (first_token_time - start_time) * 1000 if first_token_time else total_ms * 0.1
                            
                            # Extract token counts if available
                            eval_count = data.get("eval_count", 0)
                            prompt_eval_count = data.get("prompt_eval_count", 0)
                            total_tokens = eval_count + prompt_eval_count
                            
                            tokens_per_sec = None
                            if eval_count and eval_count > 0 and first_token_time:
                                gen_time = end_time - first_token_time
                                if gen_time > 0:
                                    tokens_per_sec = eval_count / gen_time
                            
                            return LLMResponse(
                                text=full_text.strip(),
                                time_to_first_token_ms=ttf_ms,
                                total_time_ms=total_ms,
                                tokens_generated=eval_count,
                                tokens_per_second=tokens_per_sec,
                                raw_metadata=data
                            )
                    except json.JSONDecodeError:
                        continue
            
            # If we get here without done flag
            end_time = time.perf_counter()
            return LLMResponse(
                text=full_text.strip(),
                time_to_first_token_ms=(first_token_time - start_time) * 1000 if first_token_time else 0,
                total_time_ms=(end_time - start_time) * 1000,
                error="Stream ended without completion flag"
            )
            
        except requests.exceptions.Timeout:
            return LLMResponse(
                text="",
                time_to_first_token_ms=0,
                total_time_ms=self.timeout * 1000,
                error=f"Timeout after {self.timeout}s"
            )
        except requests.exceptions.ConnectionError:
            return LLMResponse(
                text="",
                time_to_first_token_ms=0,
                total_time_ms=0,
                error=f"Connection failed to {self.base_url}"
            )
        except Exception as e:
            return LLMResponse(
                text="",
                time_to_first_token_ms=0,
                total_time_ms=0,
                error=str(e)
            )
    
    def supports_tools(self) -> bool:
        # Ollama has tool support in newer versions but it's limited
        return False
    
    def supports_json_mode(self) -> bool:
        return True
    
    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        # Ollama is self-hosted, cost is electricity/hardware amortization
        # Rough estimate: $0.0001 per 1K tokens for local inference on consumer GPU
        total_tokens = input_tokens + output_tokens
        return (total_tokens / 1000) * 0.0001
