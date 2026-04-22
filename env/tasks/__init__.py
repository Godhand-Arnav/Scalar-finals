"""
env/tasks/__init__.py — Task registry for FORGE.

Eight programmatic task generators, each with:
  - generate(difficulty, seed) -> ClaimGraph
  - grade(trace, graph)        -> float  [0.001, 0.999]
  - oracle_steps(graph)        -> int
  - has_manipulation(graph)    -> bool

All tasks are fully synthetic / procedural — no real data required.
"""

from __future__ import annotations
import random
from typing import Any, Dict, List, Optional

from env.claim_graph import ClaimGraph, ClaimEdge


# ─── Base Task ────────────────────────────────────────────────────────────────

class BaseTask:
    """Abstract base for all FORGE tasks."""

    # Key tools whose presence in the trace earns partial credit
    KEY_TOOLS: List[str] = []
    ORACLE_STEP_COUNT: int = 5

    def generate(self, difficulty: int = 1, seed: Optional[int] = None) -> ClaimGraph:
        raise NotImplementedError

    def grade(self, trace: List[Dict[str, Any]], graph: ClaimGraph) -> float:
        """
        Programmatic grader: partial credit for using key tools + verdict bonus.
        Returns a float strictly in (0.001, 0.999).
        """
        if not trace:
            return 0.001

        actions_used = {step.get("action", "") for step in trace}
        verdict_action = next(
            (s.get("action", "") for s in reversed(trace)
             if s.get("action", "").startswith("submit_verdict_")),
            None,
        )

        # Tool coverage score (up to 0.5)
        key_hit = sum(1 for t in self.KEY_TOOLS if t in actions_used)
        tool_score = (key_hit / max(len(self.KEY_TOOLS), 1)) * 0.5

        # Verdict correctness (up to 0.499)
        correct_label = graph.true_label if graph else "real"
        expected_action = f"submit_verdict_{correct_label}"
        verdict_score = 0.499 if verdict_action == expected_action else 0.0

        total = tool_score + verdict_score
        return min(max(total, 0.001), 0.999)

    def oracle_steps(self, graph: ClaimGraph) -> int:  # noqa: ARG002
        return self.ORACLE_STEP_COUNT

    def has_manipulation(self, graph: ClaimGraph) -> bool:
        if graph is None:
            return False
        return bool(graph.applied_tactics)


# ─── Task 1: Fabricated Statistics ───────────────────────────────────────────

class FabricatedStatsTask(BaseTask):
    KEY_TOOLS = ["entity_link", "cross_reference"]
    ORACLE_STEP_COUNT = 4

    def generate(self, difficulty: int = 1, seed: Optional[int] = None) -> ClaimGraph:
        rng = random.Random(seed)
        graph = ClaimGraph(true_label="fabricated")
        graph.applied_tactics.add("fabricated_statistic")

        root = ClaimGraph.make_node(
            text=f"Studies show {rng.randint(60, 99)}% of people who take "
                 f"supplement X see {rng.randint(40, 90)}% improvement in 30 days.",
            domain=rng.choice(["healthnews24.net", "naturalmeds.org", "wellnessdaily.co"]),
            trust_score=rng.uniform(0.1, 0.35),
            virality_score=rng.uniform(0.6, 0.95),
        )
        graph.add_node(root, is_root=True)

        # Contradicting authority node
        authority = ClaimGraph.make_node(
            text="No peer-reviewed study supports those efficacy claims.",
            domain="pubmed.ncbi.nlm.nih.gov",
            trust_score=0.95,
            virality_score=0.1,
        )
        graph.add_node(authority)
        graph.add_edge(ClaimEdge(root.node_id, authority.node_id, relation="contradicts"))

        # Bot-amplifier nodes
        n_bots = difficulty
        for i in range(n_bots):
            bot = ClaimGraph.make_node(
                text=f"Share this! Supplement X works! #{i}",
                domain=f"bot{i}.social",
                trust_score=0.05,
                virality_score=0.9,
                metadata={"is_bot": True},
            )
            graph.add_node(bot)
            graph.add_edge(ClaimEdge(root.node_id, bot.node_id, relation="amplifies"))

        return graph


# ─── Task 2: Out-of-Context ───────────────────────────────────────────────────

class OutOfContextTask(BaseTask):
    KEY_TOOLS = ["trace_origin", "temporal_audit"]
    ORACLE_STEP_COUNT = 4

    def generate(self, difficulty: int = 1, seed: Optional[int] = None) -> ClaimGraph:
        rng = random.Random(seed)
        graph = ClaimGraph(true_label="out_of_context")
        graph.applied_tactics.add("image_recontextualisation")

        root = ClaimGraph.make_node(
            text="Shocking footage shows flooding in City X caused by government negligence!",
            domain=rng.choice(["breakingnews.tv", "viral-clips.net", "realvid.io"]),
            trust_score=rng.uniform(0.2, 0.4),
            virality_score=rng.uniform(0.7, 0.99),
            timestamp="2024-01-15",
        )
        graph.add_node(root, is_root=True)

        # Original source with correct context
        original = ClaimGraph.make_node(
            text="Footage from 2018 flooding in a different country — misattributed.",
            domain="archive.org",
            trust_score=0.9,
            virality_score=0.05,
            metadata={"origin_year": 2018},
        )
        graph.add_node(original)
        graph.add_edge(ClaimEdge(root.node_id, original.node_id, relation="contradicts"))

        for i in range(difficulty - 1):
            supp = ClaimGraph.make_node(
                text=f"Secondary outlet {i+1} republished without verification.",
                domain=f"tabloid{i}.news",
                trust_score=0.3,
                virality_score=0.6,
                metadata={"is_bot": i % 2 == 0},
            )
            graph.add_node(supp)
            graph.add_edge(ClaimEdge(root.node_id, supp.node_id, relation="amplifies"))

        return graph


# ─── Task 3: Coordinated Campaign ────────────────────────────────────────────

class CoordinatedCampaignTask(BaseTask):
    KEY_TOOLS = ["query_source", "network_cluster", "flag_manipulation"]
    ORACLE_STEP_COUNT = 5

    def generate(self, difficulty: int = 1, seed: Optional[int] = None) -> ClaimGraph:
        rng = random.Random(seed)
        graph = ClaimGraph(true_label="misinfo")
        graph.applied_tactics.add("bot_amplification")
        graph.applied_tactics.add("coordinated_inauthentic_behaviour")

        root = ClaimGraph.make_node(
            text=rng.choice([
                "BREAKING: Government announces secret vaccine recall!",
                "EXPOSED: Climate data has been fabricated since 2010!",
                "URGENT: New law will ban cash transactions by next month!",
            ]),
            domain=rng.choice(["patriot-alert.com", "truth-exposer.net", "real-news24.org"]),
            trust_score=rng.uniform(0.05, 0.25),
            virality_score=rng.uniform(0.85, 0.99),
        )
        graph.add_node(root, is_root=True)

        n_bots = 2 + difficulty
        for i in range(n_bots):
            bot = ClaimGraph.make_node(
                text=f"Bot account {i}: SHARE THIS NOW!!! #WakeUp",
                domain=f"account{rng.randint(1000,9999)}.social",
                trust_score=0.02,
                virality_score=0.95,
                metadata={"is_bot": True, "cluster_id": "c1"},
            )
            graph.add_node(bot)
            graph.add_edge(ClaimEdge(root.node_id, bot.node_id, relation="amplifies"))

        debunk = ClaimGraph.make_node(
            text="Claim is false — verified by multiple credible agencies.",
            domain="factcheck.org",
            trust_score=0.95,
            virality_score=0.1,
        )
        graph.add_node(debunk)
        graph.add_edge(ClaimEdge(root.node_id, debunk.node_id, relation="debunks"))

        return graph


# ─── Task 4: Satire News ──────────────────────────────────────────────────────

class SatireNewsTask(BaseTask):
    KEY_TOOLS = ["request_context", "cross_reference"]
    ORACLE_STEP_COUNT = 3

    def generate(self, difficulty: int = 1, seed: Optional[int] = None) -> ClaimGraph:
        rng = random.Random(seed)
        graph = ClaimGraph(true_label="satire")
        # Satire is not adversarial manipulation

        headlines = [
            "Nation's Dogs Demand Right to Vote, Promise Better Treat Policy",
            "Scientists Confirm Monday Is The Universe's Most Malevolent Day",
            "Local Man Wins Argument On Internet, Plans Parade",
            "Congress Passes Law Requiring All Emails End With 'Warm Regards'",
        ]
        root = ClaimGraph.make_node(
            text=rng.choice(headlines),
            domain=rng.choice(["theonion.com", "babylonbee.com", "thebeaverton.com"]),
            trust_score=rng.uniform(0.4, 0.65),
            virality_score=rng.uniform(0.5, 0.85),
        )
        graph.add_node(root, is_root=True)

        clarification = ClaimGraph.make_node(
            text="This is a satirical publication; content is not intended as factual.",
            domain="mediabiasfactcheck.com",
            trust_score=0.85,
            virality_score=0.05,
        )
        graph.add_node(clarification)
        graph.add_edge(ClaimEdge(root.node_id, clarification.node_id, relation="supports"))

        if difficulty >= 2:
            confused = ClaimGraph.make_node(
                text="People are sharing this as real news on social media.",
                domain="socialmediatracker.io",
                trust_score=0.6,
                virality_score=0.7,
            )
            graph.add_node(confused)
            graph.add_edge(ClaimEdge(root.node_id, confused.node_id, relation="amplifies"))

        return graph


# ─── Task 5: Verified Fact ────────────────────────────────────────────────────

class VerifiedFactTask(BaseTask):
    KEY_TOOLS = ["cross_reference", "entity_link"]
    ORACLE_STEP_COUNT = 3

    def generate(self, difficulty: int = 1, seed: Optional[int] = None) -> ClaimGraph:
        rng = random.Random(seed)
        graph = ClaimGraph(true_label="real")
        # Verified facts have no manipulation tactics

        claims = [
            "NASA's James Webb Space Telescope launched on December 25, 2021.",
            "The human body contains approximately 37 trillion cells.",
            "The Eiffel Tower was completed in 1889 for the World's Fair.",
            "DNA was first described by Watson and Crick in 1953.",
        ]
        root = ClaimGraph.make_node(
            text=rng.choice(claims),
            domain=rng.choice(["reuters.com", "apnews.com", "bbc.com"]),
            trust_score=rng.uniform(0.75, 0.95),
            virality_score=rng.uniform(0.3, 0.6),
        )
        graph.add_node(root, is_root=True)

        supporting = ClaimGraph.make_node(
            text="Confirmed by multiple encyclopedic and primary sources.",
            domain="wikipedia.org",
            trust_score=0.85,
            virality_score=0.2,
        )
        graph.add_node(supporting)
        graph.add_edge(ClaimEdge(root.node_id, supporting.node_id, relation="supports"))

        if difficulty >= 3:
            # Add a misleading secondary source to challenge the agent
            misleading = ClaimGraph.make_node(
                text="Some amateur blogs dispute the established timeline.",
                domain="randomforum.net",
                trust_score=0.2,
                virality_score=0.3,
            )
            graph.add_node(misleading)
            graph.add_edge(ClaimEdge(root.node_id, misleading.node_id, relation="supports"))

        return graph


# ─── Task 6: Politifact Liar ──────────────────────────────────────────────────

class PolitifactLiarTask(BaseTask):
    KEY_TOOLS = ["query_source", "cross_reference", "entity_link"]
    ORACLE_STEP_COUNT = 5

    _CLAIMS = [
        ("Politicians voted to give themselves a 47% pay raise.", "fabricated"),
        ("Immigrants commit crime at higher rates than native-born citizens.", "misinfo"),
        ("Our economy has the strongest growth in 50 years.", "misinfo"),
        ("Unemployment is at its lowest level in recorded history.", "real"),
        ("The opposition party supported this policy before opposing it.", "out_of_context"),
    ]

    def generate(self, difficulty: int = 1, seed: Optional[int] = None) -> ClaimGraph:
        rng = random.Random(seed)
        claim_text, label = rng.choice(self._CLAIMS)
        graph = ClaimGraph(true_label=label)

        if label != "real":
            graph.applied_tactics.add("political_misattribution")

        root = ClaimGraph.make_node(
            text=claim_text,
            domain=rng.choice(["campaign-hq.com", "political-news.org", "voter-voice.net"]),
            trust_score=rng.uniform(0.2, 0.55),
            virality_score=rng.uniform(0.5, 0.85),
        )
        graph.add_node(root, is_root=True)

        fact_checker = ClaimGraph.make_node(
            text=f"PolitiFact rates this claim: {label.upper().replace('_', ' ')}.",
            domain="politifact.com",
            trust_score=0.9,
            virality_score=0.2,
        )
        graph.add_node(fact_checker)
        relation = "supports" if label == "real" else "contradicts"
        graph.add_edge(ClaimEdge(root.node_id, fact_checker.node_id, relation=relation))

        for i in range(difficulty - 1):
            amplifier = ClaimGraph.make_node(
                text=f"Campaign account {i+1} boosted this message.",
                domain=f"campaign-social-{i}.net",
                trust_score=0.3,
                virality_score=0.7,
                metadata={"is_bot": difficulty >= 3},
            )
            graph.add_node(amplifier)
            graph.add_edge(ClaimEdge(root.node_id, amplifier.node_id, relation="amplifies"))

        return graph


# ─── Task 7: Image Forensics ──────────────────────────────────────────────────

class ImageForensicsTask(BaseTask):
    KEY_TOOLS = ["trace_origin", "temporal_audit", "entity_link"]
    ORACLE_STEP_COUNT = 5

    def generate(self, difficulty: int = 1, seed: Optional[int] = None) -> ClaimGraph:
        rng = random.Random(seed)
        label = rng.choice(["fabricated", "out_of_context"])
        graph = ClaimGraph(true_label=label)
        graph.applied_tactics.add("image_manipulation" if label == "fabricated" else "image_recontextualisation")

        ela_score = rng.uniform(0.72, 0.95) if label == "fabricated" else rng.uniform(0.1, 0.4)
        root = ClaimGraph.make_node(
            text="Image purportedly shows dramatic event, widely shared on social media.",
            domain=rng.choice(["viralpost.net", "photoevidence.org", "eyewitness-media.com"]),
            trust_score=rng.uniform(0.15, 0.4),
            virality_score=rng.uniform(0.7, 0.99),
            metadata={"ela_score": ela_score, "diffusion_signature": label == "fabricated"},
            timestamp="2024-03-10",
        )
        graph.add_node(root, is_root=True)

        forensic = ClaimGraph.make_node(
            text=(
                f"ELA score {ela_score:.2f} — {'manipulation detected' if ela_score > 0.7 else 'no manipulation'}."
            ),
            domain="forensicanalysis.io",
            trust_score=0.9,
            virality_score=0.05,
            metadata={"origin_year": 2019 if label == "out_of_context" else 2024},
        )
        graph.add_node(forensic)
        graph.add_edge(ClaimEdge(root.node_id, forensic.node_id, relation="contradicts" if label == "fabricated" else "debunks"))

        if difficulty >= 2:
            graph.applied_tactics.add("backdate_article")
            metadata_node = ClaimGraph.make_node(
                text="EXIF metadata shows image creation date mismatch.",
                domain="exifanalyzer.net",
                trust_score=0.85,
                virality_score=0.05,
            )
            graph.add_node(metadata_node)
            graph.add_edge(ClaimEdge(root.node_id, metadata_node.node_id, relation="contradicts"))

        return graph


# ─── Task 8: SEC Fraud ────────────────────────────────────────────────────────

class SecFraudTask(BaseTask):
    KEY_TOOLS = ["query_source", "cross_reference", "entity_link"]
    ORACLE_STEP_COUNT = 4

    def generate(self, difficulty: int = 1, seed: Optional[int] = None) -> ClaimGraph:
        rng = random.Random(seed)
        graph = ClaimGraph(true_label="fabricated")
        graph.applied_tactics.add("domain_spoofing")
        graph.applied_tactics.add("impersonation")

        ticker = rng.choice(["XMPL", "FRGN", "TRDR", "INVT"])
        root = ClaimGraph.make_node(
            text=(
                f"Official SEC Filing: {ticker} Corp announces 300% dividend increase "
                f"and share buyback worth $2B. File now at sec-gov.net/filings/{ticker}"
            ),
            domain="sec-gov.net",   # spoofed domain
            trust_score=rng.uniform(0.05, 0.2),
            virality_score=rng.uniform(0.6, 0.9),
            metadata={"spoofed_domain": True},
        )
        graph.add_node(root, is_root=True)

        real_sec = ClaimGraph.make_node(
            text=f"No such filing found for {ticker} on SEC EDGAR (sec.gov).",
            domain="sec.gov",
            trust_score=0.99,
            virality_score=0.05,
        )
        graph.add_node(real_sec)
        graph.add_edge(ClaimEdge(root.node_id, real_sec.node_id, relation="debunks"))

        if difficulty >= 2:
            newsletter = ClaimGraph.make_node(
                text=f"Invest in {ticker} now! Insider tip — HUGE gains incoming!",
                domain=f"stocktips-{rng.randint(1,99)}.biz",
                trust_score=0.1,
                virality_score=0.85,
                metadata={"is_bot": True},
            )
            graph.add_node(newsletter)
            graph.add_edge(ClaimEdge(root.node_id, newsletter.node_id, relation="amplifies"))

        return graph


# ─── Task Registry ────────────────────────────────────────────────────────────

TASK_REGISTRY: Dict[str, type] = {
    "fabricated_stats": FabricatedStatsTask,
    "out_of_context": OutOfContextTask,
    "coordinated_campaign": CoordinatedCampaignTask,
    "satire_news": SatireNewsTask,
    "verified_fact": VerifiedFactTask,
    "politifact_liar": PolitifactLiarTask,
    "image_forensics": ImageForensicsTask,
    "sec_fraud": SecFraudTask,
}
