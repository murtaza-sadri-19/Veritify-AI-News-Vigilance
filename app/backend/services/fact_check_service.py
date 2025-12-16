import logging
import os
from typing import Dict, Optional, Any, List

from .utils.text import sanitize_text
from .analysis.article_analyzer import NewsArticleAnalyzer
from .news_fetcher import NewsFetcher
from .relevance.scorer import RelevanceAndEntailmentScorer

logger = logging.getLogger(__name__)


def classify_claim_type(claim: str) -> str:
    """
    Very lightweight claim-type classifier.
    Returns: FACTUAL | OPINION | PREDICTIVE
    """
    text = claim.lower()
    if any(
        kw in text
        for kw in [
            "i think",
            "in my opinion",
            "should",
            "must",
            "better",
            "worse",
            "good",
            "bad",
        ]
    ):
        return "OPINION"
    if any(
        kw in text
        for kw in [
            "will happen",
            "is going to happen",
            "likely to",
            "expected to",
            "forecast",
            "prediction",
        ]
    ):
        return "PREDICTIVE"
    return "FACTUAL"


class FactCheckService(NewsFetcher):
    """Core orchestrator for fact-checking pipeline."""

    def __init__(self):
        super().__init__()
        self.rapidapi_key = os.getenv("NEWS_API_KEY")
        self.article_analyzer = NewsArticleAnalyzer()
        self.scorer = RelevanceAndEntailmentScorer()

        if not self.rapidapi_key:
            logger.warning("NEWS_API_KEY not configured - service will return mock responses")

    # ── Public API ────────────────────────────────────────────────

    def check_claim(self, claim: str, context) -> Dict[str, Any]:
        """
        Orchestrate claim checking.
        Accepts and populates RequestContext. Never recomputes embeddings here.
        """
        clean_claim = sanitize_text(claim)
        context.claim_text = clean_claim
        context.claim_type = classify_claim_type(clean_claim)

        debug_info: Dict[str, Any] = {}
        context.debug = debug_info

        logger.info("="*80)
        logger.info(f"[CLAIM] {clean_claim[:150]}")
        logger.info(f"[TYPE] {context.claim_type}")
        logger.info("="*80)

        if not self.rapidapi_key:
            logger.warning("No API key configured, returning mock response")
            return self._generate_non_factual_or_mock_response(clean_claim, context)

        # Step 1: fetch fact-check results
        logger.info("[STEP 1] Searching fact-checker APIs...")
        fact_check_results = self._search_fact_checker_api(clean_claim, debug_info)
        if fact_check_results:
            logger.info(f"  → Found {len(fact_check_results.get('results', []))} fact-check results")
        else:
            logger.info("  → No fact-check results")

        # Step 2: fetch candidate news articles (two-stage within NewsFetcher)
        logger.info("[STEP 2] Fetching news articles...")
        news_results = self._search_realtime_news_api(clean_claim, context, debug_info)

        # If not factual, skip entailment, return contextual only
        if context.claim_type != "FACTUAL":
            logger.warning(f"[SKIP] Non-factual claim ({context.claim_type}); skipping entailment")
            return self._build_contextual_only_response(
                clean_claim,
                fact_check_results,
                news_results,
                context,
            )

        # Factual: run semantic + entailment pipeline, respecting error boundaries
        articles_meta = (news_results or {}).get("articles") or []
        article_texts = [
            f"{a.get('title', '')}. {a.get('snippet', '')}".strip()
            for a in articles_meta
        ]
        logger.info(f"[STEP 3] Processing {len(article_texts)} articles for entailment analysis...")

        verdict_payload: Dict[str, Any]
        try:
            # Semantic alignment (batch)
            logger.info("  → Running semantic similarity scoring (MPNet)...")
            self.scorer.batch_semantic_mpnet(context, clean_claim, article_texts)
            candidate_indices = context.candidate_indices or self.scorer.get_semantic_candidates(
                context, article_texts
            )
            logger.info(f"  → Selected {len(candidate_indices)} semantically-similar articles for entailment")

            # Entailment (batch) with graceful downgrade on failure
            logger.info("  → Running entailment classification (BART-MNLI)...")
            self.scorer.run_entailment(
                context,
                clean_claim,
                article_texts,
                candidate_indices,
            )
            labels = context.entailment_labels or []
            confs = context.entailment_confidences or []
            if labels:
                for idx, (label, conf) in enumerate(zip(labels, confs)):
                    logger.info(f"    Article {idx+1}: {label} (confidence: {conf:.2%})")
            
            logger.info("  → Aggregating verdict from entailment signals...")
            verdict_payload = self.scorer.aggregate_verdict(context)
            logger.info(f"[VERDICT] {verdict_payload['verdict']} (confidence: {verdict_payload['confidence']:.2%})")
        except Exception as e:
            # Error boundary: downgrade to semantic-only
            logger.error(f"Entailment pipeline failed, downgrading to semantic-only: {e}")
            context.verdict = "INSUFFICIENT"
            context.confidence = 0.0
            verdict_payload = {"verdict": "INSUFFICIENT", "confidence": 0.0}
            logger.warning(f"[VERDICT] INSUFFICIENT (error occurred)")

        evidence = self._build_evidence(articles_meta, context)
        logger.info(f"[EVIDENCE] Built {len(evidence)} evidence items")
        logger.info("="*80)
        response = {
            "verdict": verdict_payload["verdict"],
            "confidence": verdict_payload["confidence"],
            "evidence": evidence,
            "claim_text": clean_claim,
        }
        return response

    # ── Helpers ──────────────────────────────────────────────────

    def _build_contextual_only_response(
        self,
        claim: str,
        fact_check_results: Optional[Dict[str, Any]],
        news_results: Optional[Dict[str, Any]],
        context,
    ) -> Dict[str, Any]:
        """
        For OPINION / PREDICTIVE claims:
        - No truth score
        - No verdict
        - Only contextual articles + explanation
        """
        sources: List[Dict[str, Any]] = []

        if fact_check_results and fact_check_results.get("results"):
            for result in fact_check_results["results"][:5]:
                sources.append(
                    {
                        "title": result.get("title", "Fact-check result"),
                        "url": result.get("url", ""),
                        "date": result.get("date", ""),
                        "source": result.get("source", "fact-checker"),
                    }
                )

        if news_results and news_results.get("articles"):
            for item in news_results["articles"][:10]:
                sources.append(
                    {
                        "title": item.get("title", "News Article"),
                        "url": item.get("url", ""),
                        "date": item.get("published_datetime_utc", ""),
                        "source": item.get("source_name", "news"),
                        "snippet": item.get("snippet", ""),
                    }
                )

        explanation = (
            f"This claim was classified as {context.claim_type}, so no truth verdict "
            "or numeric confidence is provided. Instead, related coverage is returned "
            "to help understand the context."
        )

        return {
            "claim_text": claim,
            "claim_type": context.claim_type,
            "verdict": None,
            "confidence": None,
            "evidence": sources,
            "explanation": explanation,
        }

    def _build_evidence(self, articles_meta: List[Dict[str, Any]], context) -> List[Dict[str, Any]]:
        """
        Build evidence list from candidate articles and entailment signals.
        """
        labels = context.entailment_labels or []
        confs = context.entailment_confidences or []
        indices = getattr(context, 'valid_candidate_indices', None) or context.candidate_indices or []
        semantic_scores = context.semantic_scores or []

        evidence: List[Dict[str, Any]] = []
        for local_idx, article_idx in enumerate(indices):
            # Bounds check on articles_meta
            if article_idx >= len(articles_meta):
                logger.warning(f"Article index {article_idx} out of range (only {len(articles_meta)} articles)")
                continue

            a = articles_meta[article_idx]
            # Bounds check on labels/confs
            label = labels[local_idx] if local_idx < len(labels) else None
            conf = confs[local_idx] if local_idx < len(confs) else None
            
            # Bounds check on semantic_scores
            semantic_score = semantic_scores[article_idx] if article_idx < len(semantic_scores) else None

            evidence.append(
                {
                    "title": a.get("title", ""),
                    "url": a.get("url", ""),
                    "source": a.get("source_name", "news"),
                    "published_date": a.get("published_datetime_utc", ""),
                    "snippet": a.get("snippet", ""),
                    "entailment_label": label,
                    "entailment_confidence": conf,
                    "semantic_score": semantic_score,
                }
            )
        return evidence

    def _generate_non_factual_or_mock_response(self, claim: str, context) -> Dict[str, Any]:
        """
        Used when API key is missing; still respects claim type behavior.
        """
        explanation = (
            "NEWS_API_KEY not configured. This is a demo response. "
            "Configure your API key to get real fact-checking results."
        )
        if context.claim_type == "FACTUAL":
            return {
                "claim_text": claim,
                "claim_type": context.claim_type,
                "verdict": "INSUFFICIENT",
                "confidence": 0.0,
                "evidence": [],
                "explanation": explanation,
            }
        else:
            return {
                "claim_text": claim,
                "claim_type": context.claim_type,
                "verdict": None,
                "confidence": None,
                "evidence": [],
                "explanation": explanation,
            }