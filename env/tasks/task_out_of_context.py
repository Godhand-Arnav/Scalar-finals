"""
Task 2 — Out-of-Context + Outdated Claims
Tactics: strip_context, backdate_article, translate_without_context
"""

from __future__ import annotations
import random
import uuid
from datetime import datetime, timedelta
from env.claim_graph import ClaimGraph, ClaimNode, EvidenceEdge
from env.tasks.task_base import BaseTask


_OOC_CLAIMS = [
    {
        "modern_text": "Massive fire destroys entire city block in Chicago.",
        "context": "Photo is from the 2017 Santa Rosa wildfire, recirculated after an unrelated Chicago incident.",
        "origin_year": 2017,
        "origin_domain": "latimes.com",
        "misuse_domain": "breakingnewsalert24.com",
        "tactics": ["strip_context", "backdate_article"],
    },
    {
        "modern_text": "Thousands protest government lockdown in Berlin — city in chaos.",
        "context": "Video is from a 2019 climate strike, labelled as COVID lockdown protest in 2021.",
        "origin_year": 2019,
        "origin_domain": "dw.com",
        "misuse_domain": "germanytruth.net",
        "tactics": ["strip_context"],
    },
    {
        "modern_text": "Shocking: Hospital overrun, bodies in hallways — healthcare system collapses.",
        "context": "Image from 2010 Haiti earthquake used in 2020 to misrepresent COVID hospital conditions.",
        "origin_year": 2010,
        "origin_domain": "reuters.com",
        "misuse_domain": "covidtruth2020.org",
        "tactics": ["strip_context", "backdate_article"],
    },
    {
        "modern_text": "Minister admits government is bankrupt in leaked audio.",
        "context": "Audio from 2015 theatrical performance, re-shared in 2024 claiming modern context.",
        "origin_year": 2015,
        "origin_domain": "theguardian.com",
        "misuse_domain": "leakedgov.info",
        "tactics": ["strip_context", "translate_without_context"],
    },
]


class OutOfContextTask(BaseTask):
    task_id = "out_of_context"
    description = (
        "The agent investigates claims where real content (images, videos, quotes) "
        "is stripped of its original context or given a false timestamp."
    )

    def generate(self, difficulty: int = 1, seed: int = 0) -> ClaimGraph:
        rng = random.Random(seed)
        template = rng.choice(_OOC_CLAIMS)

        graph_id = str(uuid.uuid4())
        root_id = "node_root"
        now = datetime.utcnow()

        root = ClaimNode(
            node_id=root_id,
            text=template["modern_text"],
            source_url=f"https://{template['misuse_domain']}/post-{rng.randint(1000,9999)}",
            domain=template["misuse_domain"],
            timestamp=now - timedelta(days=rng.randint(1, 7)),
            virality_score=rng.uniform(0.5, 0.9),
            trust_score=0.15,
            metadata={"claimed_date": str(now.date())},
        )

        graph = ClaimGraph(
            graph_id=graph_id,
            root_claim_id=root_id,
            true_label="out_of_context",
            difficulty=difficulty,
            applied_tactics=list(template["tactics"]),
        )
        graph.add_node(root)

        # ── Original source node (from origin year) ────────────────────────────
        origin_date = datetime(template["origin_year"], rng.randint(1, 12), rng.randint(1, 28))
        orig_id = "node_origin"
        orig = ClaimNode(
            node_id=orig_id,
            text=f"Original article from {template['origin_domain']} — {template['context']}",
            source_url=f"https://web.archive.org/web/{origin_date.strftime('%Y%m%d')}/https://{template['origin_domain']}/",
            domain=f"web.archive.org → {template['origin_domain']}",
            timestamp=origin_date,
            virality_score=0.05,
            trust_score=0.92,
            metadata={"archive": True, "origin_year": template["origin_year"]},
        )
        graph.add_node(orig)
        graph.add_edge(EvidenceEdge(
            edge_id="e_origin", src_id=root_id, tgt_id=orig_id,
            relation="contradicts", weight=0.95,
        ))

        # ── Propagation chain (amplifier nodes) ────────────────────────────────
        # Difficulty 2+: add re-sharing nodes with modified text
        prev_id = root_id
        for i in range(difficulty - 1):
            amp_id = f"node_share_{i}"
            amp = ClaimNode(
                node_id=amp_id,
                text=f"Re-share #{i+1}: {template['modern_text']} (translated/adapted)",
                source_url=f"https://socialmedia-mirror-{i}.net/post-{rng.randint(100,999)}",
                domain=f"socialmedia-mirror-{i}.net",
                timestamp=now - timedelta(hours=rng.randint(1, 72)),
                virality_score=rng.uniform(0.3, 0.7),
                trust_score=0.1,
            )
            graph.add_node(amp)
            graph.add_edge(EvidenceEdge(
                edge_id=f"e_share_{i}", src_id=prev_id, tgt_id=amp_id,
                relation="amplifies", weight=rng.uniform(0.6, 0.9),
            ))
            prev_id = amp_id

        if difficulty >= 3:
            graph.applied_tactics.append("translate_without_context")

        return graph

    def oracle_steps(self, graph: ClaimGraph) -> int:
        return 3 + graph.difficulty

    def has_manipulation(self, graph: ClaimGraph) -> bool:
        return True
