"""
claim_graph.py — Evidence graph data structure for FORGE.

ClaimGraph: directed graph where nodes are information sources and
edges represent support, contradiction, or amplification relationships.
"""

from __future__ import annotations
import hashlib
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set


# ─── ClaimNode ────────────────────────────────────────────────────────────────

@dataclass
class ClaimNode:
    """A single node in the claim evidence graph."""
    node_id: str
    text: str
    domain: str = "unknown"
    trust_score: float = 0.5
    virality_score: float = 0.5
    retrieved: bool = False
    embedding: Optional[Any] = None          # numpy array set after embed
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: Optional[str] = None


# ─── ClaimEdge ────────────────────────────────────────────────────────────────

@dataclass
class ClaimEdge:
    """A directed edge between two nodes."""
    source_id: str
    target_id: str
    relation: str = "supports"    # supports | contradicts | debunks | amplifies
    discovered: bool = False
    weight: float = 1.0


# ─── ClaimGraph ───────────────────────────────────────────────────────────────

class ClaimGraph:
    """
    Directed evidence graph.

    Attributes
    ----------
    root          : Root ClaimNode (the claim under investigation).
    nodes         : dict[node_id, ClaimNode]
    edges         : list[ClaimEdge]
    true_label    : Ground-truth label (real | misinfo | satire |
                    out_of_context | fabricated).
    applied_tactics : set of adversarial tactics applied during generation.
    """

    def __init__(self, true_label: str = "real"):
        self.true_label: str = true_label
        self.nodes: Dict[str, ClaimNode] = {}
        self.edges: List[ClaimEdge] = []
        self.applied_tactics: Set[str] = set()
        self._root_id: Optional[str] = None
        # adjacency: node_id -> list of edges going OUT from that node
        self._adj: Dict[str, List[ClaimEdge]] = {}

    # ── Root accessor ─────────────────────────────────────────────────────────

    @property
    def root(self) -> Optional[ClaimNode]:
        return self.nodes.get(self._root_id)

    @property
    def root_claim_id(self) -> Optional[str]:
        return self._root_id

    # ── Node helpers ──────────────────────────────────────────────────────────

    def add_node(self, node: ClaimNode, is_root: bool = False) -> None:
        self.nodes[node.node_id] = node
        if is_root:
            self._root_id = node.node_id
        if node.node_id not in self._adj:
            self._adj[node.node_id] = []

    def add_edge(self, edge: ClaimEdge) -> None:
        self.edges.append(edge)
        self._adj.setdefault(edge.source_id, []).append(edge)

    def mark_retrieved(self, node_id: str) -> None:
        if node_id in self.nodes:
            self.nodes[node_id].retrieved = True

    def discover_edges_from(self, node_id: str) -> List[ClaimEdge]:
        """Mark all undiscovered edges from node_id as discovered and return them."""
        revealed: List[ClaimEdge] = []
        for edge in self._adj.get(node_id, []):
            if not edge.discovered:
                edge.discovered = True
                # Auto-mark the target as retrieved so coverage updates
                target = self.nodes.get(edge.target_id)
                if target and not target.retrieved:
                    target.retrieved = True
                revealed.append(edge)
        return revealed

    # ── Graph metrics ─────────────────────────────────────────────────────────

    @property
    def evidence_coverage(self) -> float:
        """Fraction of nodes that have been retrieved."""
        total = len(self.nodes)
        if total == 0:
            return 0.0
        retrieved = sum(1 for n in self.nodes.values() if n.retrieved)
        return min(1.0, retrieved / total)

    @property
    def source_diversity_entropy(self) -> float:
        """Shannon entropy over unique source domains (normalised to [0,1])."""
        import math
        domains = [n.domain for n in self.nodes.values() if n.retrieved]
        if not domains:
            return 0.0
        unique = set(domains)
        if len(unique) <= 1:
            return 0.0
        # Uniform distribution over domains for simplicity
        n = len(unique)
        return min(1.0, math.log(n) / math.log(max(n, 5)))

    @property
    def contradiction_surface_area(self) -> int:
        """Number of discovered contradiction/debunking edges."""
        return sum(
            1 for e in self.edges
            if e.discovered and e.relation in ("contradicts", "debunks")
        )

    @property
    def network_diameter(self) -> int:
        """Longest shortest path from root (BFS)."""
        if not self._root_id:
            return 0
        visited: Set[str] = {self._root_id}
        queue = [(self._root_id, 0)]
        max_dist = 0
        while queue:
            nid, dist = queue.pop(0)
            max_dist = max(max_dist, dist)
            for edge in self._adj.get(nid, []):
                if edge.target_id not in visited:
                    visited.add(edge.target_id)
                    queue.append((edge.target_id, dist + 1))
        return max_dist

    # ── Hashing (for tool cache keys) ─────────────────────────────────────────

    def wl_hash(self) -> str:
        """Weisfeiler-Lehman-style structural hash for use as a cache key."""
        parts = []
        for nid in sorted(self.nodes.keys()):
            node = self.nodes[nid]
            parts.append(f"{nid}:{int(node.retrieved)}")
        for edge in sorted(self.edges, key=lambda e: (e.source_id, e.target_id)):
            parts.append(f"{edge.source_id}->{edge.target_id}:{int(edge.discovered)}")
        raw = "|".join(parts)
        return hashlib.md5(raw.encode()).hexdigest()[:12]

    # ── Serialisation ─────────────────────────────────────────────────────────

    def to_dict(self) -> Dict[str, Any]:
        return {
            "true_label": self.true_label,
            "root_id": self._root_id,
            "num_nodes": len(self.nodes),
            "num_edges": len(self.edges),
            "evidence_coverage": round(self.evidence_coverage, 4),
            "source_diversity": round(self.source_diversity_entropy, 4),
            "contradiction_surface_area": self.contradiction_surface_area,
            "applied_tactics": list(self.applied_tactics),
            "nodes": [
                {
                    "node_id": n.node_id,
                    "domain": n.domain,
                    "retrieved": n.retrieved,
                    "trust_score": n.trust_score,
                }
                for n in self.nodes.values()
            ],
        }

    # ── Factory helpers ───────────────────────────────────────────────────────

    @staticmethod
    def make_node(
        text: str,
        domain: str = "unknown",
        trust_score: float = 0.5,
        virality_score: float = 0.5,
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[str] = None,
    ) -> ClaimNode:
        return ClaimNode(
            node_id=str(uuid.uuid4())[:8],
            text=text,
            domain=domain,
            trust_score=trust_score,
            virality_score=virality_score,
            metadata=metadata or {},
            timestamp=timestamp,
        )
