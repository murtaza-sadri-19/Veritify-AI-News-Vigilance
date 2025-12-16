import logging
from typing import List, Dict, Any

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer, util
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

from ..utils.text import sentence_aware_truncate_for_mnli, sanitize_text

logger = logging.getLogger(__name__)

# ── Global heavy models (loaded once) ─────────────────────────────

_TFIDF_VECTORIZER = TfidfVectorizer(
    max_features=2000,
    stop_words="english",
    ngram_range=(1, 2),
)

_MPNet_MODEL = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

_MNLI_TOKENIZER = AutoTokenizer.from_pretrained("facebook/bart-large-mnli")
_MNLI_MODEL = AutoModelForSequenceClassification.from_pretrained(
    "facebook/bart-large-mnli"
)
_MNLI_MODEL.eval()

_LABEL_MAP = ["CONTRADICTION", "NEUTRAL", "ENTAILMENT"]


class RelevanceAndEntailmentScorer:
    """
    Core batch scoring engine.
    - No per-article computation
    - No hardcoded thresholds
    - Context-preserving
    """

    # ─────────────────────────────────────────────────────────────
    # 1. Lexical (TF-IDF) — SOFT PRUNING ONLY
    # ─────────────────────────────────────────────────────────────

    @staticmethod
    def batch_tfidf_lexical(context, claim: str, article_texts: List[str]) -> List[float]:
        texts = [sanitize_text(claim)] + [sanitize_text(t) for t in article_texts]

        try:
            tfidf = _TFIDF_VECTORIZER.fit_transform(texts)
            claim_vec = tfidf[0:1]
            article_vecs = tfidf[1:]
            scores = cosine_similarity(claim_vec, article_vecs)[0].tolist()
        except Exception as e:
            logger.warning(f"TF-IDF failed, defaulting to zeros: {e}")
            scores = [0.0] * len(article_texts)

        context.lexical_scores = scores
        context.distributions["lexical_scores"] = scores
        return scores

    # ─────────────────────────────────────────────────────────────
    # 2. Semantic Alignment (MPNet) — PRIMARY FILTER
    # ─────────────────────────────────────────────────────────────

    @staticmethod
    def batch_semantic_mpnet(context, claim: str, article_texts: List[str]) -> List[float]:
        try:
            logger.debug(f"Encoding claim: '{claim[:60]}...'")
            claim_emb = _MPNet_MODEL.encode(
                [claim], convert_to_tensor=True, normalize_embeddings=True
            )[0]

            logger.debug(f"Encoding {len(article_texts)} articles for semantic matching")
            article_embs = _MPNet_MODEL.encode(
                article_texts,
                convert_to_tensor=True,
                normalize_embeddings=True,
            )

            scores = util.cos_sim(claim_emb, article_embs)[0].cpu().numpy().tolist()
            logger.debug(f"Semantic scores: min={min(scores):.3f}, max={max(scores):.3f}, mean={np.mean(scores):.3f}")

        except Exception as e:
            logger.error(f"MPNet embedding failed: {e}")
            scores = [0.0] * len(article_texts)

        context.semantic_scores = scores
        context.distributions["semantic_scores"] = scores

        # Percentile-based adaptive threshold
        arr = np.array(scores, dtype=float)
        if len(arr) == 0:
            threshold = 0.0
            percentile = 0
        else:
            percentile = 75 if len(arr) > 10 else 60
            threshold = float(np.percentile(arr, percentile))

        context.semantic_threshold = threshold
        context.thresholds["semantic"] = {
            "percentile": percentile,
            "threshold": threshold,
            "min": float(arr.min()) if len(arr) else 0.0,
            "max": float(arr.max()) if len(arr) else 0.0,
            "median": float(np.median(arr)) if len(arr) else 0.0,
        }

        return scores

    @staticmethod
    def get_semantic_candidates(context, article_texts: List[str]) -> List[int]:
        scores = context.semantic_scores or []
        if not scores:
            context.candidate_indices = []
            return []

        threshold = context.semantic_threshold
        indices = [i for i, s in enumerate(scores) if s >= threshold]

        # Guarantee minimum semantic signal
        if len(indices) < 3:
            top_k = min(3, len(scores))
            indices = list(np.argsort(scores)[-top_k:])

        context.candidate_indices = indices
        context.debug.setdefault("selection", {})["semantic_candidates"] = {
            "indices": indices,
            "threshold": threshold,
        }
        return indices

    # ─────────────────────────────────────────────────────────────
    # 3. Logical Entailment (BART-MNLI)
    # ─────────────────────────────────────────────────────────────

    @staticmethod
    def run_entailment(context, claim: str, article_texts: List[str], candidate_indices: List[int]) -> None:
        if not candidate_indices:
            logger.warning("No candidate indices for entailment; skipping")
            context.entailment_labels = []
            context.entailment_confidences = []
            return

        # ✅ BOUNDS VALIDATION: Filter out-of-range indices before processing
        valid_indices = [idx for idx in candidate_indices if 0 <= idx < len(article_texts)]
        if not valid_indices:
            logger.warning(
                f"No valid candidate indices. Requested {candidate_indices}, "
                f"but only {len(article_texts)} articles available."
            )
            context.entailment_labels = []
            context.entailment_confidences = []
            return
        
        logger.debug(f"Running entailment on {len(valid_indices)} candidates")

        premises, hypotheses = [], []

        for idx in valid_indices:
            try:
                premises.append(
                    sentence_aware_truncate_for_mnli(
                        article_texts[idx], max_tokens=256, tokenizer=_MNLI_TOKENIZER
                    )
                )
                hypotheses.append(
                    sentence_aware_truncate_for_mnli(
                        claim, max_tokens=128, tokenizer=_MNLI_TOKENIZER
                    )
                )
            except Exception as e:
                logger.warning(f"Failed to prepare article at index {idx}: {e}")
                continue

        try:
            logger.debug(f"Tokenizing {len(premises)} premise-hypothesis pairs")
            inputs = _MNLI_TOKENIZER(
                premises,
                hypotheses,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=384,
            )

            logger.debug("Running BART-MNLI model inference")
            with torch.no_grad():
                logits = _MNLI_MODEL(**inputs).logits
                probs = torch.softmax(logits, dim=-1)

            labels, confidences = [], []
            for row in probs:
                idx = int(torch.argmax(row))
                labels.append(_LABEL_MAP[idx])
                confidences.append(float(row[idx]))
            
            logger.debug(f"Entailment results: {dict(zip(labels, [f'{c:.2%}' for c in confidences]))}")

        except Exception as e:
            logger.error(f"MNLI failed: {e}")
            raise

        # ✅ Track which indices produced these labels (for evidence building)
        context.entailment_labels = labels
        context.entailment_confidences = confidences
        context.valid_candidate_indices = valid_indices
        logger.debug(f"Stored {len(labels)} entailment labels")

    # ─────────────────────────────────────────────────────────────
    # 4. Verdict Aggregation — FIXED CONFIDENCE LOGIC
    # ─────────────────────────────────────────────────────────────

    @staticmethod
    def aggregate_verdict(context) -> Dict[str, Any]:
        labels = context.entailment_labels or []
        confs = context.entailment_confidences or []

        if not labels:
            logger.warning("No entailment labels to aggregate")
            context.verdict = "INSUFFICIENT"
            context.confidence = 0.0
            return {"verdict": "INSUFFICIENT", "confidence": 0.0}

        contradictions = [c for l, c in zip(labels, confs) if l == "CONTRADICTION"]
        entailments = [c for l, c in zip(labels, confs) if l == "ENTAILMENT"]
        neutrals = [c for l, c in zip(labels, confs) if l == "NEUTRAL"]
        
        logger.debug(f"Aggregating: {len(entailments)} entailment(s), {len(contradictions)} contradiction(s), {len(neutrals)} neutral")

        if contradictions and not entailments:
            verdict = "FALSE"
            confidence = float(np.mean(contradictions))
            logger.info(f"Verdict: FALSE (based on {len(contradictions)} contradictions)")

        elif entailments and not contradictions:
            verdict = "TRUE"
            confidence = float(np.mean(entailments))
            logger.info(f"Verdict: TRUE (based on {len(entailments)} entailments)")

        elif contradictions and entailments:
            verdict = "PARTIALLY FALSE"
            confidence = float(np.mean(contradictions + entailments))
            logger.info(f"Verdict: PARTIALLY FALSE (mixed: {len(entailments)} entailments, {len(contradictions)} contradictions)")

        else:
            verdict = "INSUFFICIENT"
            confidence = 0.0
            logger.info(f"Verdict: INSUFFICIENT (no clear signal)")

        context.verdict = verdict
        context.confidence = confidence
        return {"verdict": verdict, "confidence": confidence}