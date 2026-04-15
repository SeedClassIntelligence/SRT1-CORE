#!/usr/bin/env python3
"""
Reflex Memory System
Fast, automatic response memory for SCIA
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import re

@dataclass
class ReflexPattern:
    """Pattern for reflex memory matching"""
    pattern: str
    response: Any
    confidence: float
    usage_count: int
    last_used: datetime
    context_tags: List[str]

class ReflexMemory:
    """Fast reflex memory for immediate responses"""

    def __init__(self, max_patterns: int = 1000):
        self.patterns: Dict[str, ReflexPattern] = {}
        self.max_patterns = max_patterns
        self.response_cache = {}
        self.learning_enabled = True
        self.confidence_threshold = 0.8

        # Initialize with common patterns
        self._initialize_default_patterns()

    def _initialize_default_patterns(self):
        """Initialize with common reflex patterns"""
        default_patterns = {
            r"hello|hi|hey": "Hello! How can I assist you today?",
            r"thank you|thanks": "You're welcome! Happy to help.",
            r"goodbye|bye|see you": "Goodbye! Have a great day!",
            r"help|assist|support": "I'm here to help! What do you need assistance with?",
            r"error|problem|issue": "I understand there's an issue. Let me help you resolve it.",
            r"status|health|check": "System status: All systems operational.",
        }

        for pattern, response in default_patterns.items():
            self.add_pattern(pattern, response, confidence=0.9, context_tags=["greeting", "common"])

    def add_pattern(self, pattern: str, response: Any, confidence: float = 0.8,
                   context_tags: List[str] = None) -> bool:
        """Add a new reflex pattern"""
        pattern_id = self._generate_pattern_id(pattern)

        reflex_pattern = ReflexPattern(
            pattern=pattern,
            response=response,
            confidence=confidence,
            usage_count=0,
            last_used=datetime.now(),
            context_tags=context_tags or []
        )

        self.patterns[pattern_id] = reflex_pattern

        # Manage capacity
        if len(self.patterns) > self.max_patterns:
            self._evict_least_used()

        print(f"⚡ Added reflex pattern: {pattern[:30]}...")
        return True

    async def get_reflex_response(self, input_text: str, context: Dict[str, Any] = None) -> Optional[Any]:
        """Get immediate reflex response if pattern matches"""
        input_lower = input_text.lower().strip()

        # Check cache first
        cache_key = self._generate_cache_key(input_lower, context)
        if cache_key in self.response_cache:
            cached_response = self.response_cache[cache_key]
            if self._is_cache_valid(cached_response):
                return cached_response['response']

        # Find matching patterns
        matches = []
        for pattern_id, reflex_pattern in self.patterns.items():
            if self._pattern_matches(input_lower, reflex_pattern, context):
                matches.append((pattern_id, reflex_pattern))

        if not matches:
            return None

        # Select best match
        best_match = self._select_best_match(matches, input_lower, context)
        if best_match and best_match[1].confidence >= self.confidence_threshold:
            pattern_id, reflex_pattern = best_match

            # Update usage statistics
            reflex_pattern.usage_count += 1
            reflex_pattern.last_used = datetime.now()

            # Cache response
            self._cache_response(cache_key, reflex_pattern.response)

            print(f"⚡ Reflex response triggered: {pattern_id}")
            return reflex_pattern.response

        return None

    def _pattern_matches(self, input_text: str, reflex_pattern: ReflexPattern,
                        context: Dict[str, Any] = None) -> bool:
        """Check if input matches reflex pattern"""
        # Basic regex matching
        if re.search(reflex_pattern.pattern, input_text, re.IGNORECASE):
            # Additional context matching if provided
            if context and reflex_pattern.context_tags:
                context_tags = context.get('tags', [])
                if not any(tag in context_tags for tag in reflex_pattern.context_tags):
                    return False
            return True

        return False

    def _select_best_match(self, matches: List[tuple], input_text: str,
                          context: Dict[str, Any] = None) -> Optional[tuple]:
        """Select the best matching pattern"""
        if not matches:
            return None

        # Score matches based on multiple factors
        scored_matches = []
        for pattern_id, reflex_pattern in matches:
            score = self._calculate_match_score(reflex_pattern, input_text, context)
            scored_matches.append((score, pattern_id, reflex_pattern))

        # Return highest scoring match
        scored_matches.sort(reverse=True)
        return (scored_matches[0][1], scored_matches[0][2])

    def _calculate_match_score(self, reflex_pattern: ReflexPattern, input_text: str,
                              context: Dict[str, Any] = None) -> float:
        """Calculate match score for pattern selection"""
        score = reflex_pattern.confidence

        # Boost score for frequently used patterns
        usage_boost = min(0.1, reflex_pattern.usage_count * 0.01)
        score += usage_boost

        # Boost score for recent usage
        time_since_use = datetime.now() - reflex_pattern.last_used
        if time_since_use < timedelta(hours=1):
            score += 0.05

        # Context relevance boost
        if context and reflex_pattern.context_tags:
            context_tags = context.get('tags', [])
            relevance = len(set(context_tags) & set(reflex_pattern.context_tags))
            score += relevance * 0.02

        return min(1.0, score)

    def learn_from_interaction(self, input_text: str, expected_response: Any,
                              context: Dict[str, Any] = None) -> bool:
        """Learn new reflex patterns from interactions"""
        if not self.learning_enabled:
            return False

        # Extract potential patterns from input
        potential_patterns = self._extract_patterns(input_text)

        for pattern in potential_patterns:
            # Check if pattern already exists
            existing_pattern = self._find_similar_pattern(pattern)

            if existing_pattern:
                # Reinforce existing pattern
                existing_pattern.confidence = min(1.0, existing_pattern.confidence + 0.05)
                existing_pattern.usage_count += 1
            else:
                # Create new pattern with lower initial confidence
                self.add_pattern(
                    pattern=pattern,
                    response=expected_response,
                    confidence=0.6,  # Start with lower confidence
                    context_tags=context.get('tags', []) if context else []
                )

        print(f"🧠 Learned from interaction: {len(potential_patterns)} patterns")
        return True

    def _extract_patterns(self, input_text: str) -> List[str]:
        """Extract potential patterns from input text"""
        patterns = []

        # Extract key phrases (simplified)
        words = input_text.lower().split()

        # Single word patterns
        for word in words:
            if len(word) > 3 and word.isalpha():
                patterns.append(word)

        # Two-word patterns
        for i in range(len(words) - 1):
            if all(len(w) > 2 and w.isalpha() for w in words[i:i+2]):
                patterns.append(f"{words[i]} {words[i+1]}")

        return patterns[:5]  # Limit to 5 patterns

    def _find_similar_pattern(self, pattern: str) -> Optional[ReflexPattern]:
        """Find similar existing pattern"""
        for reflex_pattern in self.patterns.values():
            if pattern in reflex_pattern.pattern or reflex_pattern.pattern in pattern:
                return reflex_pattern
        return None

    def _generate_pattern_id(self, pattern: str) -> str:
        """Generate unique ID for pattern"""
        import hashlib
        return hashlib.md5(pattern.encode()).hexdigest()[:8]

    def _generate_cache_key(self, input_text: str, context: Dict[str, Any] = None) -> str:
        """Generate cache key for response"""
        context_str = str(sorted(context.items())) if context else ""
        return f"{input_text}:{context_str}"

    def _cache_response(self, cache_key: str, response: Any):
        """Cache response with timestamp"""
        self.response_cache[cache_key] = {
            'response': response,
            'timestamp': datetime.now(),
            'ttl': 300  # 5 minutes
        }

        # Limit cache size
        if len(self.response_cache) > 100:
            # Remove oldest entries
            sorted_cache = sorted(
                self.response_cache.items(),
                key=lambda x: x[1]['timestamp']
            )
            for key, _ in sorted_cache[:20]:  # Remove oldest 20
                del self.response_cache[key]

    def _is_cache_valid(self, cached_response: Dict[str, Any]) -> bool:
        """Check if cached response is still valid"""
        age = datetime.now() - cached_response['timestamp']
        return age.total_seconds() < cached_response['ttl']

    def _evict_least_used(self):
        """Evict least used patterns to maintain capacity"""
        if len(self.patterns) <= self.max_patterns:
            return

        # Sort by usage count and last used time
        sorted_patterns = sorted(
            self.patterns.items(),
            key=lambda x: (x[1].usage_count, x[1].last_used)
        )

        # Remove bottom 10%
        remove_count = max(1, int(len(self.patterns) * 0.1))
        for i in range(remove_count):
            if i < len(sorted_patterns):
                pattern_id = sorted_patterns[i][0]
                del self.patterns[pattern_id]

    def get_reflex_stats(self) -> Dict[str, Any]:
        """Get reflex memory statistics"""
        total_patterns = len(self.patterns)
        total_usage = sum(p.usage_count for p in self.patterns.values())
        avg_confidence = sum(p.confidence for p in self.patterns.values()) / total_patterns if total_patterns > 0 else 0

        return {
            'total_patterns': total_patterns,
            'total_usage': total_usage,
            'average_confidence': avg_confidence,
            'cache_size': len(self.response_cache),
            'learning_enabled': self.learning_enabled,
            'confidence_threshold': self.confidence_threshold
        }

    def clear_patterns(self, min_confidence: float = 0.0):
        """Clear patterns below minimum confidence"""
        patterns_to_remove = [
            pattern_id for pattern_id, pattern in self.patterns.items()
            if pattern.confidence < min_confidence
        ]

        for pattern_id in patterns_to_remove:
            del self.patterns[pattern_id]

        print(f"🧹 Cleared {len(patterns_to_remove)} low-confidence patterns")
        return len(patterns_to_remove)
