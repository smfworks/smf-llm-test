"""
Base provider interface for LLM benchmarking
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
import time

@dataclass
class LLMResponse:
    text: str
    time_to_first_token_ms: float
    total_time_ms: float
    tokens_generated: Optional[int] = None
    tokens_per_second: Optional[float] = None
    error: Optional[str] = None
    raw_metadata: Optional[Dict[str, Any]] = None

@dataclass
class ToolCall:
    name: str
    parameters: Dict[str, Any]

@dataclass
class LLMRequest:
    prompt: str
    system_prompt: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: float = 0.7
    tools: Optional[List[Dict[str, Any]]] = None
    tool_choice: Optional[str] = None
    response_format: Optional[Dict[str, Any]] = None
    context_document: Optional[str] = None

class BaseProvider(ABC):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model = config.get("model")
        self.timeout = config.get("timeout", 60)
    
    @abstractmethod
    def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate a response from the LLM"""
        pass
    
    @abstractmethod
    def supports_tools(self) -> bool:
        """Whether this provider supports function/tool calling"""
        pass
    
    @abstractmethod
    def supports_json_mode(self) -> bool:
        """Whether this provider supports structured JSON output"""
        pass
    
    @abstractmethod
    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost in USD for the request"""
        pass
    
    def _time_call(self, callable_fn) -> tuple[Any, float, float]:
        """Time a function call, returning (result, time_to_first, total_time)"""
        start = time.perf_counter()
        # For streaming providers, time_to_first is measured differently
        # For non-streaming, it's approximately total_time
        result = callable_fn()
        end = time.perf_counter()
        total_ms = (end - start) * 1000
        # Non-streaming: approximate ttf as a fraction of total
        ttf_ms = total_ms * 0.1  # Rough heuristic
        return result, ttf_ms, total_ms
