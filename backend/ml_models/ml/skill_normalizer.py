"""
Skill normalization and synonym handling utilities.
"""

import json
import re
from pathlib import Path
from typing import Dict, Iterable, List, Set


def _load_synonyms() -> Dict[str, Dict[str, str]]:
    base_dir = Path(__file__).resolve().parent / "skill_taxonomy"
    path = base_dir / "synonyms.json"
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    return {
        "abbrev_map": data.get("abbrev_map", {}),
        "canonical_map": data.get("canonical_map", {}),
    }


class SkillNormalizer:
    _synonyms_cache: Dict[str, Dict[str, str]] | None = None

    @classmethod
    def _synonyms(cls) -> Dict[str, Dict[str, str]]:
        if cls._synonyms_cache is None:
            cls._synonyms_cache = _load_synonyms()
        return cls._synonyms_cache

    @staticmethod
    def _clean(token: str) -> str:
        text = token.strip().lower()
        text = re.sub(r"\s+", " ", text)
        return text

    @classmethod
    def normalize_skill(cls, token: str) -> str:
        text = cls._clean(token)
        synonyms = cls._synonyms()
        abbrev_map = synonyms.get("abbrev_map", {})
        canonical_map = synonyms.get("canonical_map", {})
        if text in abbrev_map:
            text = abbrev_map[text]
        if text in canonical_map:
            text = canonical_map[text]
        return text

    @classmethod
    def normalize_list(cls, skills: Iterable[str]) -> List[str]:
        seen: Set[str] = set()
        result: List[str] = []
        for skill in skills:
            normalized = cls.normalize_skill(skill)
            if normalized and normalized not in seen:
                seen.add(normalized)
                result.append(normalized)
        return result

    @classmethod
    def normalize_domains(cls, skills_by_domain: Dict[str, List[str]]) -> Dict[str, List[str]]:
        normalized: Dict[str, List[str]] = {}
        for domain, skills in skills_by_domain.items():
            normalized_skills = cls.normalize_list(skills)
            if normalized_skills:
                normalized[domain] = normalized_skills
        return normalized

    @classmethod
    def merge_into_other(cls, skills_by_domain: Dict[str, List[str]], extra_skills: Iterable[str]) -> Dict[str, List[str]]:
        merged = {k: list(v) for k, v in skills_by_domain.items()}
        merged.setdefault("other", [])
        merged["other"].extend(cls.normalize_list(extra_skills))
        merged["other"] = cls.normalize_list(merged["other"])
        return merged
