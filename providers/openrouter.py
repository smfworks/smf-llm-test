"""
OpenRouter provider for benchmarking
OpenRouter is OpenAI API-compatible — we use the openai client with their base URL.
"""

import os
import time
from typing import Dict, Any, Optional
from openai import OpenAI
from .base import BaseProvider, LLMRequest, LLMResponse

class OpenRouterProvider(BaseProvider):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        api_key = config.get("api_key") or os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OpenRouter API key required. Set OPENROUTER_API_KEY env var or api_key in config.")
        
        base_url = config.get("base_url", "https://openrouter.ai/api/v1")
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.site_url = config.get("site_url", "https://smfworks.com")
        self.site_name = config.get("site_name", "SMF Works Benchmark")
    
    def generate(self, request: LLMRequest) -> LLMResponse:
        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        
        user_content = request.prompt
        if request.context_document:
            user_content = f"Context:\n{request.context_document}\n\n{request.prompt}"
        messages.append({"role": "user", "content": user_content})
        
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": request.temperature,
            "stream": True,
            "extra_headers": {
                "HTTP-Referer": self.site_url,
                "X-Title": self.site_name,
            }
        }
        
        if request.max_tokens:
            kwargs["max_tokens"] = request.max_tokens
        
        if request.tools:
            kwargs["tools"] = request.tools
            kwargs["tool_choice"] = request.tool_choice or "auto"
        
        if request.response_format:
            kwargs["response_format"] = request.response_format
        
        start_time = time.perf_counter()
        first_token_time = None
        full_text = ""
        tool_calls = []
        
        try:
            stream = self.client.chat.completions.create(**kwargs)
            
            for chunk in stream:
                if first_token_time is None and chunk.choices[0].delta.content:
                    first_token_time = time.perf_counter()
                
                if chunk.choices[0].delta.content:
                    full_text += chunk.choices[0].delta.content
                
                if chunk.choices[0].delta.tool_calls:
                    for tc in chunk.choices[0].delta.tool_calls:
                        tool_calls.append(tc)
            
            end_time = time.perf_counter()
            total_ms = (end_time - start_time) * 1000
            ttf_ms = (first_token_time - start_time) * 1000 if first_token_time else total_ms * 0.1
            
            output_tokens = len(full_text) // 4 if full_text else 0
            
            tokens_per_sec = None
            if output_tokens > 0 and first_token_time:
                gen_time = end_time - first_token_time
                if gen_time > 0:
                    tokens_per_sec = output_tokens / gen_time
            
            return LLMResponse(
                text=full_text.strip(),
                time_to_first_token_ms=ttf_ms,
                total_time_ms=total_ms,
                tokens_generated=output_tokens,
                tokens_per_second=tokens_per_sec,
                raw_metadata={"tool_calls": len(tool_calls)}
            )
            
        except Exception as e:
            return LLMResponse(
                text="",
                time_to_first_token_ms=0,
                total_time_ms=0,
                error=str(e)
            )
    
    def supports_tools(self) -> bool:
        return True
    
    def supports_json_mode(self) -> bool:
        return True
    
    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        # OpenRouter pricing varies by model — use generic fallback
        # Pricing in tokens per dollar (rough estimates for frontier models)
        pricing = {
            "meta-llama/llama-4-maverick": {"input": 0.22, "output": 0.17},
            "mistralai/mistral-large-3": {"input": 2.00, "output": 6.00},
            "cohere/command-r-plus": {"input": 3.00, "output": 15.00},
            "google/gemini-2.5-pro": {"input": 1.25, "output": 10.00},
            "minimax/minimax-m3": {"input": 0.50, "output": 2.00},
        }
        model_pricing = pricing.get(self.model, {"input": 2.00, "output": 6.00})
        input_cost = (input_tokens / 1000) * model_pricing["input"] / 100
        output_cost = (output_tokens / 1000) * model_pricing["output"] / 100
        return input_cost + output_cost
