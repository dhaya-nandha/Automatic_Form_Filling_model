import sys
from pathlib import Path
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

sys.path.append(str(Path(__file__).resolve().parent.parent))
import config

class SemanticFieldMatcher:
    """Deep Learning Field Matcher using Sentence Transformers & Cosine Similarity"""

    def __init__(self):
        self.model = None
        self._load_model()
        self.canonical_embeddings = {}
        self._precompute_canonical_embeddings()

    def _load_model(self):
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(config.EMBEDDING_MODEL_NAME)
        except Exception as e:
            print(f"[FieldMatcher] sentence-transformers model loading fallback: {e}")
            self.model = None

    def _precompute_canonical_embeddings(self):
        if not self.model:
            return

        for canonical_key, aliases in config.CANONICAL_SCHEMA.items():
            # Combine canonical key and aliases into descriptive search strings
            phrases = [canonical_key.replace("_", " ")] + aliases
            embeddings = self.model.encode(phrases, convert_to_tensor=True)
            self.canonical_embeddings[canonical_key] = embeddings

    def match_label_to_canonical(self, label: str) -> Tuple[Optional[str], float]:
        """
        Given a form label (e.g. 'Candidate Phone Number'), returns (best_canonical_key, score).
        """
        if not label or not label.strip():
            return None, 0.0

        label_clean = label.strip().lower()

        # 1. Exact string / regex shortcut match
        for key, aliases in config.CANONICAL_SCHEMA.items():
            if label_clean in aliases or label_clean == key.replace("_", " "):
                return key, 1.0

        # 2. Embedding Cosine Similarity match
        if self.model and self.canonical_embeddings:
            from sentence_transformers import util
            label_embedding = self.model.encode(label_clean, convert_to_tensor=True)
            
            best_key = None
            highest_score = 0.0

            for key, key_embeddings in self.canonical_embeddings.items():
                scores = util.cos_sim(label_embedding, key_embeddings)
                max_score = float(scores.max())
                if max_score > highest_score:
                    highest_score = max_score
                    best_key = key

            return best_key, highest_score

        # 3. Keyword / Substring Fallback Matcher
        best_key = None
        highest_score = 0.0
        for key, aliases in config.CANONICAL_SCHEMA.items():
            for alias in aliases:
                if alias in label_clean or label_clean in alias:
                    score = len(alias) / max(len(label_clean), len(alias))
                    if score > highest_score:
                        highest_score = score
                        best_key = key

        return best_key, highest_score

    def match_and_fill(
        self,
        form_fields: List[Dict[str, Any]],
        user_profile: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Processes list of detected form fields against user profile data.
        Returns mapped results with AUTO_FILL, INFERRED, or NEEDS_REVIEW status.
        """
        results = []

        for field in form_fields:
            field_id = field.get("field_id", "")
            label = field.get("label", "")
            field_type = field.get("field_type", "text")

            matched_key, sim_score = self.match_label_to_canonical(label)

            res = {
                "field_id": field_id,
                "label": label,
                "field_type": field_type,
                "matched_canonical_key": matched_key,
                "derived_value": None,
                "similarity_score": round(sim_score, 4),
                "action": "NEEDS_REVIEW",
                "source_document": None,
                "gform_index": field.get("gform_index"),
                "selector": field.get("selector")
            }

            # Check direct profile hit
            if matched_key and matched_key in user_profile:
                profile_item = user_profile[matched_key]
                if sim_score >= config.HIGH_CONFIDENCE_THRESHOLD:
                    res["derived_value"] = profile_item["value"]
                    res["action"] = "AUTO_FILL"
                    res["source_document"] = profile_item.get("source")
                elif sim_score >= config.MEDIUM_CONFIDENCE_THRESHOLD:
                    res["derived_value"] = profile_item["value"]
                    res["action"] = "INFERRED"
                    res["source_document"] = profile_item.get("source")
            else:
                # Attempt rule-based value derivation (e.g. Age from DOB, First/Last Name from Full Name)
                derived_val, derived_key, source = self._attempt_inference(matched_key, label, user_profile)
                if derived_val:
                    res["matched_canonical_key"] = derived_key or matched_key
                    res["derived_value"] = derived_val
                    res["action"] = "INFERRED"
                    res["source_document"] = source

            results.append(res)

        return results

    def _attempt_inference(
        self,
        matched_key: Optional[str],
        label: str,
        user_profile: Dict[str, Dict[str, Any]]
    ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        label_lower = label.lower()

        # Derive Age from DOB
        if (matched_key == "age" or "age" in label_lower) and "dob" in user_profile:
            dob_str = user_profile["dob"]["value"]
            source = user_profile["dob"].get("source")
            age = self._calculate_age(dob_str)
            if age is not None:
                return str(age), "age", source

        # Derive First Name from Full Name
        if (matched_key == "first_name" or "first name" in label_lower) and "full_name" in user_profile:
            full_name = user_profile["full_name"]["value"]
            source = user_profile["full_name"].get("source")
            parts = full_name.split()
            if parts:
                return parts[0], "first_name", source

        # Derive Last Name from Full Name
        if (matched_key == "last_name" or "last name" in label_lower) and "full_name" in user_profile:
            full_name = user_profile["full_name"]["value"]
            source = user_profile["full_name"].get("source")
            parts = full_name.split()
            if len(parts) > 1:
                return parts[-1], "last_name", source

        return None, None, None

    @staticmethod
    def _calculate_age(dob_str: str) -> Optional[int]:
        for fmt in ("%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%d", "%d-%m-%Y", "%B %d, %Y"):
            try:
                dt = datetime.strptime(dob_str, fmt)
                today = datetime.today()
                return today.year - dt.year - ((today.month, today.day) < (dt.month, dt.day))
            except ValueError:
                continue
        return None

# Type aliases for clean signatures
Tuple_Match = Any
Tuple_Inference = Any
