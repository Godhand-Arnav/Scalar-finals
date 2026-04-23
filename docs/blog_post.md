# Unmasking the Truth: How FORGE-MA Tackles Coordinated Misinformation 

*By the FORGE-MA Engineering Team*

In an era where digital deception travels faster than fact, traditional fact-checking mechanisms are no longer sufficient. Misinformation is rarely a solitary lie; it is often a coordinated network of cherry-picked statistics, out-of-context quotes, and synthetic amplifications designed to bypass conventional filters.

Enter **FORGE-MA (Forensic RL Graph Environment - Multi-Agent)**. Built originally as a single-agent prototype, we have completely overhauled the architecture for this hackathon to introduce a **Society of Thought**—a multi-agent system where specialized AI roles collaborate, debate, and verify claims through a Graph Neural Network (GNN) lens.

## The Society of Thought

At the heart of FORGE-MA is a rigorous separation of concerns. A single LLM is prone to hallucination and confirmation bias. By dividing the labor, we achieve forensic precision:
- **The Forensic Auditor** scours the web for primary source documents and raw data.
- **The Context Historian** evaluates the temporal alignment of quotes, catching instances where a statement from 2014 is weaponized in 2024.
- **The Narrative Critic** looks for rhetorical manipulation and logical fallacies.
- **The GIN Specialist** (Graph Isomorphism Network) analyzes the topological spread of the claim, detecting bot-like amplification clusters that SAGEConv models traditionally miss.

## The Plandemic Case Study

To prove the efficacy of our system, we deployed FORGE-MA against the "Plandemic" phenomenon—a notorious example of a coordinated campaign that rapidly saturated social media with overlapping, fabricated health claims.

Our environment dynamically generates a `ClaimGraph` representing these claims. When presented with the assertion that *“wearing masks activates the coronavirus,”* the FORGE-MA agents autonomously execute a sequence of actions:
1. `cross_reference` the core claim against reputable epidemiological databases.
2. `network_cluster` the domains amplifying the claim, instantly flagging the synthetic amplification network.
3. `submit_verdict` with high confidence that the claim is a fabricated component of a coordinated campaign.

## Overcoming Training Hurdles

A major technical milestone for our team was implementing a robust curriculum learning pipeline via Proximal Policy Optimization (PPO). During our 50-generation pre-training run, we monitored the Blue Team (GIN Specialist) as it learned to differentiate between organic viral trends and artificial bot networks.

The results speak for themselves: the model’s online loss converged dramatically from **`66.74` down to `0.78`**. This isn't theoretical improvement—these are the actual checkpoints (`gin_model.pt` and `hae_model.pt`) powering the live demonstration today.

## Looking Forward

FORGE-MA is more than a hackathon project; it is a foundational step toward machine-speed truth verification. By exporting our findings into STIX 2.1 compliant bundles, we ensure that the intelligence gathered by our agents can be immediately ingested by threat intelligence platforms worldwide.

We are proud of what we've built, and we invite you to explore the dashboard, run the agents, and watch as they untangle the web of misinformation in real-time.
