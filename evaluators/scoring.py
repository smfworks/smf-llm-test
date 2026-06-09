"""
Evaluation engine for scoring LLM responses
"""

import json
import re
from typing import Dict, Any, List
from tests.test_definitions import TestDefinition

class Evaluator:
    def evaluate(self, test: TestDefinition, response: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Evaluate a response against a test definition"""
        
        if test.evaluation_type == "exact_match":
            return self._evaluate_exact_match(test, response)
        elif test.evaluation_type == "contains":
            return self._evaluate_contains(test, response)
        elif test.evaluation_type == "code_compile":
            return self._evaluate_code_compile(test, response)
        elif test.evaluation_type == "json_valid":
            return self._evaluate_json_valid(test, response)
        elif test.evaluation_type == "rubric":
            return self._evaluate_rubric(test, response)
        else:
            return {"score": 0, "details": "Unknown evaluation type", "passed": False}
    
    def _evaluate_exact_match(self, test: TestDefinition, response: str) -> Dict[str, Any]:
        expected = test.rubric.get("expected", "") if test.rubric else ""
        passed = expected.lower() in response.lower()
        return {
            "score": 1.0 if passed else 0.0,
            "details": f"Expected '{expected}' in response: {'PASS' if passed else 'FAIL'}",
            "passed": passed
        }
    
    def _evaluate_contains(self, test: TestDefinition, response: str) -> Dict[str, Any]:
        patterns = test.expected_patterns or []
        found = [p for p in patterns if p.lower() in response.lower()]
        score = len(found) / max(len(patterns), 1)
        return {
            "score": score,
            "details": f"Found {len(found)}/{len(patterns)} expected patterns",
            "passed": score >= 0.7,
            "found_patterns": found,
            "missing_patterns": [p for p in patterns if p not in found]
        }
    
    def _evaluate_code_compile(self, test: TestDefinition, response: str) -> Dict[str, Any]:
        """Check if code is extractable and syntactically valid"""
        # Extract code from markdown fences
        code = self._extract_code(response)
        if not code:
            return {"score": 0, "details": "No code found in response", "passed": False}
        
        # Try to compile
        try:
            compile(code, "<string>", "exec")
            compiles = True
        except SyntaxError as e:
            compiles = False
        
        # Check for expected patterns
        patterns = test.expected_patterns or []
        found = [p for p in patterns if p.lower() in code.lower() or p.lower() in response.lower()]
        pattern_score = len(found) / max(len(patterns), 1)
        
        score = (0.5 if compiles else 0) + (pattern_score * 0.5)
        
        return {
            "score": score,
            "details": f"Compiles: {compiles}, Patterns: {len(found)}/{len(patterns)}",
            "passed": compiles and score >= 0.6,
            "compiles": compiles,
            "found_patterns": found,
            "code": code[:500]  # Truncated for report
        }
    
    def _evaluate_json_valid(self, test: TestDefinition, response: str) -> Dict[str, Any]:
        """Check if response contains valid JSON matching expected schema"""
        # Try to extract JSON
        json_str = self._extract_json(response)
        if not json_str:
            return {"score": 0, "details": "No JSON found in response", "passed": False}
        
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            return {"score": 0, "details": f"Invalid JSON: {e}", "passed": False}
        
        # Check expected patterns in the JSON
        patterns = test.expected_patterns or []
        found = [p for p in patterns if p.lower() in json_str.lower()]
        pattern_score = len(found) / max(len(patterns), 1)
        
        # Validate basic structure
        has_analysis = "analysis" in data and isinstance(data["analysis"], dict)
        has_recommendations = "recommendations" in data and isinstance(data["recommendations"], list)
        
        structure_score = (0.5 if has_analysis else 0) + (0.5 if has_recommendations else 0)
        
        score = (structure_score * 0.5) + (pattern_score * 0.5)
        
        return {
            "score": score,
            "details": f"Valid JSON: yes, Structure: {structure_score:.1f}, Patterns: {len(found)}/{len(patterns)}",
            "passed": score >= 0.7,
            "has_analysis": has_analysis,
            "has_recommendations": has_recommendations,
            "found_patterns": found
        }
    
    def _evaluate_rubric(self, test: TestDefinition, response: str) -> Dict[str, Any]:
        """Evaluate against rubric criteria"""
        rubric = test.rubric or {}
        results = {}
        total_weight = 0
        weighted_score = 0
        
        for criterion_name, criterion in rubric.items():
            weight = criterion.get("weight", 1.0 / len(rubric))
            total_weight += weight
            
            # Check for expected value
            expected = criterion.get("expected")
            if expected:
                found = expected.lower() in response.lower()
                criterion_score = 1.0 if found else 0.0
                results[criterion_name] = {
                    "score": criterion_score,
                    "found": found,
                    "expected": expected,
                    "description": criterion.get("description", "")
                }
            else:
                # Check description-based criteria (requires more sophisticated analysis)
                # For now, use heuristic scoring
                description = criterion.get("description", "")
                if "sentence" in description.lower():
                    # Count sentences
                    sentences = [s.strip() for s in response.split('.') if s.strip()]
                    if "exactly 3" in description.lower():
                        criterion_score = 1.0 if len(sentences) == 3 else (0.5 if 2 <= len(sentences) <= 4 else 0)
                    elif "exactly 5" in description.lower():
                        criterion_score = 1.0 if len(sentences) == 5 else (0.5 if 4 <= len(sentences) <= 6 else 0)
                    else:
                        criterion_score = 0.5
                elif "word" in description.lower() and "count" in description.lower():
                    # Estimate word count
                    words = response.split()
                    if "exactly 200" in description.lower() or "200 words" in description.lower():
                        criterion_score = 1.0 if 180 <= len(words) <= 220 else (0.5 if 160 <= len(words) <= 240 else 0)
                    elif "exactly 100" in description.lower() or "100 words" in description.lower():
                        criterion_score = 1.0 if 90 <= len(words) <= 110 else (0.5 if 80 <= len(words) <= 120 else 0)
                    else:
                        criterion_score = 0.5
                elif "all caps" in description.lower() or "uppercase" in description.lower():
                    criterion_score = 1.0 if response.upper() == response else 0.0
                elif "banned" in description.lower() or "do not use" in description.lower():
                    # Check for banned words
                    banned = ["scalable", "robust", "leverage"]
                    found_banned = [w for w in banned if w.lower() in response.lower()]
                    criterion_score = 1.0 if not found_banned else 0.0
                else:
                    criterion_score = 0.5  # Default heuristic
                
                results[criterion_name] = {
                    "score": criterion_score,
                    "description": description
                }
            
            weighted_score += criterion_score * weight
        
        final_score = weighted_score / total_weight if total_weight > 0 else 0
        
        return {
            "score": final_score,
            "details": f"Rubric score: {final_score:.2f} ({len([r for r in results.values() if r.get('score', 0) >= 0.7])}/{len(results)} criteria passed)",
            "passed": final_score >= 0.6,
            "criteria": results
        }
    
    def _extract_code(self, response: str) -> str:
        """Extract code from markdown code fences"""
        # Match ```python ... ``` or ``` ... ```
        pattern = r'```(?:python)?\n(.*?)\n```'
        matches = re.findall(pattern, response, re.DOTALL)
        if matches:
            return matches[0]
        
        # If no fences, try to find indented code
        lines = response.split('\n')
        code_lines = []
        in_code = False
        for line in lines:
            if line.startswith('    ') or line.startswith('\t'):
                code_lines.append(line.strip())
                in_code = True
            elif in_code and not line.strip():
                code_lines.append('')
            elif in_code:
                break
        
        if code_lines:
            return '\n'.join(code_lines)
        
        return ""
    
    def _extract_json(self, response: str) -> str:
        """Extract JSON from response"""
        # Remove markdown fences
        cleaned = re.sub(r'```json\s*', '', response)
        cleaned = re.sub(r'```\s*', '', cleaned)
        cleaned = cleaned.strip()
        
        # Find JSON object
        try:
            # Try to find first { and matching }
            start = cleaned.find('{')
            if start != -1:
                # Simple brace counting
                depth = 0
                for i, char in enumerate(cleaned[start:]):
                    if char == '{':
                        depth += 1
                    elif char == '}':
                        depth -= 1
                        if depth == 0:
                            return cleaned[start:start+i+1]
        except:
            pass
        
        return cleaned


class PerformanceScorer:
    """Calculate performance scores from timing data"""
    
    @staticmethod
    def score_timing(ttf_ms: float, total_ms: float, timeout_seconds: int) -> Dict[str, float]:
        """Score timing performance"""
        timeout_ms = timeout_seconds * 1000
        
        # TTF score: faster is better
        if ttf_ms <= 500:
            ttf_score = 1.0
        elif ttf_ms <= 2000:
            ttf_score = 0.8
        elif ttf_ms <= 5000:
            ttf_score = 0.5
        else:
            ttf_score = 0.2
        
        # Total time score: within timeout is good, faster is better
        if total_ms <= timeout_ms * 0.3:
            time_score = 1.0
        elif total_ms <= timeout_ms * 0.6:
            time_score = 0.8
        elif total_ms <= timeout_ms:
            time_score = 0.5
        else:
            time_score = 0.0  # Timeout
        
        return {
            "ttf_score": ttf_score,
            "time_score": time_score,
            "overall_timing": (ttf_score + time_score) / 2
        }
    
    @staticmethod
    def score_reliability(error_count: int, total_runs: int) -> float:
        """Score reliability based on error rate"""
        if total_runs == 0:
            return 0.0
        success_rate = (total_runs - error_count) / total_runs
        return success_rate
    
    @staticmethod
    def calculate_overall_score(accuracy: float, timing: float, reliability: float, weights=None) -> float:
        """Calculate weighted overall score"""
        if weights is None:
            weights = {"accuracy": 0.5, "timing": 0.25, "reliability": 0.25}
        
        return (
            accuracy * weights["accuracy"] +
            timing * weights["timing"] +
            reliability * weights["reliability"]
        )
