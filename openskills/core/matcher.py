"""
Skill Matcher - Matches user queries to infographic-skills.

The matcher uses various strategies to find the most relevant infographic-skills
for a given user input.
"""

import re
from dataclasses import dataclass

from openskills.models.metadata import SkillMetadata


@dataclass
class MatchResult:
    """Result of a skill match with score."""
    metadata: SkillMetadata
    score: float
    matched_by: str  # What triggered the match


class SkillMatcher:
    """
    Skill matching engine.

    Implements multiple matching strategies:
    1. Exact trigger match - highest priority
    2. Partial trigger match - medium priority
    3. Name match - medium priority
    4. Description keyword match - lower priority

    Future improvements could include:
    - Semantic similarity using embeddings
    - LLM-based intent classification
    """

    # Scoring weights
    EXACT_TRIGGER_SCORE = 1.0
    PARTIAL_TRIGGER_SCORE = 0.8
    NAME_MATCH_SCORE = 0.7
    DESCRIPTION_MATCH_SCORE = 0.5
    TAG_MATCH_SCORE = 0.4

    def __init__(self, min_score: float = 0.3):
        """
        Initialize the matcher.

        Args:
            min_score: Minimum score threshold for a match
        """
        self.min_score = min_score

    def match(
        self,
        query: str,
        metadata_list: list[SkillMetadata],
        limit: int = 5,
    ) -> list[SkillMetadata]:
        """
        Match a query against skill metadata.

        Args:
            query: User input to match
            metadata_list: List of skill metadata to search
            limit: Maximum number of results to return

        Returns:
            List of matching metadata, sorted by score (highest first)
        """
        results: list[MatchResult] = []

        for metadata in metadata_list:
            result = self._score_match(query, metadata)
            if result and result.score >= self.min_score:
                results.append(result)

        # Sort by score descending
        results.sort(key=lambda r: r.score, reverse=True)

        return [r.metadata for r in results[:limit]]

    def _score_match(self, query: str, metadata: SkillMetadata) -> MatchResult | None:
        """
        Score how well a query matches a skill.

        Args:
            query: User input
            metadata: Skill metadata to match against

        Returns:
            MatchResult with score, or None if no match
        """
        query_lower = query.lower().strip()
        best_score = 0.0
        matched_by = ""

        # Check exact trigger match
        for trigger in metadata.triggers:
            trigger_lower = trigger.lower()
            if trigger_lower == query_lower:
                return MatchResult(metadata, self.EXACT_TRIGGER_SCORE, f"exact trigger: {trigger}")

            # Check if trigger is contained in query
            if trigger_lower in query_lower:
                # Give higher score for longer triggers (more specific matches)
                score = self.PARTIAL_TRIGGER_SCORE
                if score > best_score:
                    best_score = score
                    matched_by = f"partial trigger: {trigger}"

            # Check if all words in trigger appear in query (for multi-word triggers)
            trigger_words = set(self._tokenize(trigger_lower))
            query_words = set(self._tokenize(query_lower))
            if trigger_words and trigger_words.issubset(query_words):
                score = self.PARTIAL_TRIGGER_SCORE * 0.9  # Slightly lower than substring match
                if score > best_score:
                    best_score = score
                    matched_by = f"trigger words: {trigger}"

        # Check name match
        name_lower = metadata.name.lower().replace("-", " ").replace("_", " ")
        name_words = set(self._tokenize(name_lower))
        query_words = set(self._tokenize(query_lower))

        if name_lower in query_lower or query_lower in name_lower:
            score = self.NAME_MATCH_SCORE
            if score > best_score:
                best_score = score
                matched_by = f"name: {metadata.name}"
        elif name_words and name_words.issubset(query_words):
            score = self.NAME_MATCH_SCORE * 0.9
            if score > best_score:
                best_score = score
                matched_by = f"name words: {metadata.name}"

        # Check description keywords
        desc_words = self._extract_keywords(metadata.description)
        query_word_set = set(self._tokenize(query_lower))
        common_words = desc_words & query_word_set

        if common_words:
            # Score based on overlap ratio
            overlap_ratio = len(common_words) / max(len(desc_words), 1)
            score = self.DESCRIPTION_MATCH_SCORE * (0.5 + overlap_ratio * 0.5)
            if score > best_score:
                best_score = score
                matched_by = f"description keywords: {', '.join(common_words)}"

        # Check tags
        for tag in metadata.tags:
            if tag.lower() in query_lower:
                score = self.TAG_MATCH_SCORE
                if score > best_score:
                    best_score = score
                    matched_by = f"tag: {tag}"

        if best_score > 0:
            return MatchResult(metadata, best_score, matched_by)

        return None

    def _extract_keywords(self, text: str) -> set[str]:
        """Extract significant keywords from text."""
        words = self._tokenize(text.lower())
        # Filter out common stop words
        stop_words = {
            "a", "an", "the", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "may", "might", "must", "shall",
            "can", "need", "dare", "ought", "used", "to", "of", "in",
            "for", "on", "with", "at", "by", "from", "as", "into",
            "through", "during", "before", "after", "above", "below",
            "between", "under", "again", "further", "then", "once",
            "here", "there", "when", "where", "why", "how", "all",
            "each", "few", "more", "most", "other", "some", "such",
            "no", "nor", "not", "only", "own", "same", "so", "than",
            "too", "very", "just", "and", "but", "if", "or", "because",
            "this", "that", "these", "those", "it", "its",
        }
        return {w for w in words if len(w) > 2 and w not in stop_words}

    def _tokenize(self, text: str) -> list[str]:
        """Tokenize text into words."""
        # Split on non-alphanumeric characters (supports Unicode including CJK)
        # For CJK characters, we treat each character as a potential token
        tokens = []

        # Match word characters (including Unicode letters/numbers)
        words = re.findall(r"[\w]+", text, re.UNICODE)
        for word in words:
            # Check if word contains CJK characters
            if re.search(r"[\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af]", word):
                # For CJK, also add individual characters and bigrams
                tokens.append(word)
                for i in range(len(word)):
                    tokens.append(word[i])
                    if i + 1 < len(word):
                        tokens.append(word[i:i+2])
            else:
                tokens.append(word)

        return tokens

    def find_best_match(
        self,
        query: str,
        metadata_list: list[SkillMetadata],
    ) -> SkillMetadata | None:
        """
        Find the single best matching skill.

        Args:
            query: User input
            metadata_list: List of skill metadata to search

        Returns:
            The best matching metadata, or None if no match
        """
        matches = self.match(query, metadata_list, limit=1)
        return matches[0] if matches else None
