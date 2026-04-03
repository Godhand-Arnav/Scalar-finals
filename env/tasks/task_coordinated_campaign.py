"""
Task 3 — Coordinated Misinformation Campaigns
Tactics: amplify_via_bot_network, fabricate_statistic, strip_context, misattribute_quote
"""

from __future__ import annotations
import random
import uuid
from datetime import datetime, timedelta
from env.claim_graph import ClaimGraph, ClaimNode, EvidenceEdge
from env.tasks.task_base import BaseTask


_CAMPAIGN_TEMPLATES = [
    {
        "narrative": "Foreign election interference: automated accounts spreading voter fraud claims.",
        "root_text": "BREAKING: 3 million ballots destroyed in swing state — whistleblower comes forward.",
        "tactics": ["amplify_via_bot_network", "fabricate_statistic"],
        "bot_domains": ["patriot-news-flash.com", "electionwatch247.net", "votefraudalert.org"],
        "debunk_domain": "politifact.com",
        "real_source": "ap.org",
    },
    {
        "narrative": "Health disinformation campaign: coordinated anti-vaccine messaging via social media bots.",
        "root_text": "Official LEAKED memo: 90% of vaccinated patients develop autoimmune disease within 2 years.",
        "tactics": ["amplify_via_bot_network", "fabricate_statistic", "misattribute_quote"],
        "bot_domains": ["vaxdangerreport.net", "healthfreedomnow.org", "medicalsecrets.info"],
        "debunk_domain": "snopes.com",
        "real_source": "nih.gov",
    },
    {
        "narrative": "Financial market manipulation: coordinated pump-and-dump via fake crypto news.",
        "root_text": "EXCLUSIVE: Tesla and Apple both secretly investing $50B in CryptoX — insider source.",
        "tactics": ["amplify_via_bot_network", "misattribute_quote", "fabricate_statistic"],
        "bot_domains": ["cryptoinsider24.io", "marketmoveralerts.net", "investmentnewsnow.co"],
        "debunk_domain": "factcheck.org",
        "real_source": "sec.gov",
    },
]


class CoordinatedCampaignTask(BaseTask):
    task_id = "coordinated_campaign"
    description = (
        "The agent investigates coordinated bot-amplified misinformation campaigns "
        "with multiple nodes sharing the same false narrative across many domains."
    )

    def generate(self, difficulty: int = 1, seed: int = 0) -> ClaimGraph:
        rng = random.Random(seed)
        template = rng.choice(_CAMPAIGN_TEMPLATES)

        graph_id = str(uuid.uuid4())
        root_id = "node_root"
        now = datetime.utcnow()

        root = ClaimNode(
            node_id=root_id,
            text=template["root_text"],
            source_url=f"https://{template['bot_domains'][0]}/breaking-{rng.randint(1000,9999)}",
            domain=template["bot_domains"][0],
            timestamp=now - timedelta(hours=rng.randint(1, 12)),
            virality_score=rng.uniform(0.7, 0.99),
            trust_score=0.1,
            metadata={"is_bot_origin": True, "campaign": template["narrative"]},
        )

        graph = ClaimGraph(
            graph_id=graph_id,
            root_claim_id=root_id,
            true_label="misinfo",
            difficulty=difficulty,
            applied_tactics=list(template["tactics"]),
        )
        graph.add_node(root)

        # ── Bot amplifier nodes (same narrative, different domains) ────────────
        num_bots = 2 + difficulty   # scales with difficulty
        bot_ids = []
        for i in range(num_bots):
            bot_domain = template["bot_domains"][i % len(template["bot_domains"])]
            bot_id = f"node_bot_{i}"
            bot = ClaimNode(
                node_id=bot_id,
                text=f"SHARE THIS: {template['root_text']} [account #{rng.randint(1000,9999)}]",
                source_url=f"https://{bot_domain}/post-{rng.randint(10000,99999)}",
                domain=bot_domain,
                timestamp=now - timedelta(minutes=rng.randint(5, 120)),
                virality_score=rng.uniform(0.4, 0.8),
                trust_score=0.05,
                metadata={"is_bot": True, "bot_index": i},
            )
            graph.add_node(bot)
            graph.add_edge(EvidenceEdge(
                edge_id=f"e_bot_{i}", src_id=root_id, tgt_id=bot_id,
                relation="amplifies", weight=rng.uniform(0.8, 1.0),
            ))
            # Bots also co-share with each other (network)
            if i > 0:
                graph.add_edge(EvidenceEdge(
                    edge_id=f"e_cross_{i}", src_id=bot_id, tgt_id=f"node_bot_{i-1}",
                    relation="co_published", weight=rng.uniform(0.7, 0.95),
                ))
            bot_ids.append(bot_id)

        # ── Real authoritative counter-source ──────────────────────────────────
        auth_id = "node_authority"
        auth = ClaimNode(
            node_id=auth_id,
            text=f"Official statement from {template['real_source']}: no basis for circulating claims.",
            source_url=f"https://{template['real_source']}/official-statement",
            domain=template["real_source"],
            timestamp=now - timedelta(days=rng.randint(1, 5)),
            virality_score=0.08,
            trust_score=0.97,
        )
        graph.add_node(auth)
        graph.add_edge(EvidenceEdge(
            edge_id="e_auth", src_id=root_id, tgt_id=auth_id,
            relation="contradicts", weight=0.98,
        ))

        # ── Fact-check node ────────────────────────────────────────────────────
        fc_id = "node_factcheck"
        fc = ClaimNode(
            node_id=fc_id,
            text=f"Coordinated campaign detected — {template['narrative']}",
            source_url=f"https://{template['debunk_domain']}/campaign-analysis",
            domain=template["debunk_domain"],
            timestamp=now - timedelta(hours=rng.randint(6, 48)),
            virality_score=0.25,
            trust_score=0.92,
        )
        graph.add_node(fc)
        graph.add_edge(EvidenceEdge(
            edge_id="e_fc", src_id=fc_id, tgt_id=root_id,
            relation="debunks", weight=0.97,
        ))

        # ── Difficulty 4: add a realistic-looking "supporting" source ──────────
        if difficulty >= 4:
            legit_id = "node_legit_misquote"
            legit = ClaimNode(
                node_id=legit_id,
                text="Real article misquoted to support campaign narrative.",
                source_url="https://reuters.com/real-story-misrepresented",
                domain="reuters.com",
                timestamp=now - timedelta(days=90),
                virality_score=0.15,
                trust_score=0.93,
            )
            graph.add_node(legit)
            graph.add_edge(EvidenceEdge(
                edge_id="e_misquote", src_id=root_id, tgt_id=legit_id,
                relation="cites", weight=0.2,   # weak, misleading citation
            ))
            graph.applied_tactics.append("strip_context")

        return graph

    def oracle_steps(self, graph: ClaimGraph) -> int:
        # need to trace at least 2 bot nodes + authority + factcheck + submit
        return 4 + graph.difficulty

    def has_manipulation(self, graph: ClaimGraph) -> bool:
        return True
