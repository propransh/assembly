import json
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from backend.utils.llm_client import call_llm_json
from backend.utils.graph_utils import get_most_influential, get_nodes_by_type
import networkx as nx

# Category defaults — only resistance and influence, never stance
STAKEHOLDER_CATEGORIES = {
    "tech_company":       {"persuasion_resistance": 0.75, "influence_weight": 0.90},
    "government":         {"persuasion_resistance": 0.85, "influence_weight": 0.95},
    "civil_society":      {"persuasion_resistance": 0.60, "influence_weight": 0.65},
    "academic":           {"persuasion_resistance": 0.50, "influence_weight": 0.70},
    "labor_union":        {"persuasion_resistance": 0.70, "influence_weight": 0.60},
    "consumer":           {"persuasion_resistance": 0.30, "influence_weight": 0.40},
    "media":              {"persuasion_resistance": 0.60, "influence_weight": 0.55},
    "investor":           {"persuasion_resistance": 0.65, "influence_weight": 0.75},
    "affected_community": {"persuasion_resistance": 0.55, "influence_weight": 0.50},
    "international_body": {"persuasion_resistance": 0.80, "influence_weight": 0.85},
}

MAX_CATEGORY_SHARE = 0.30  # No single category can exceed 30% of agents
MIN_AGENTS = 10

async def classify_and_position_entities(
    topic: str,
    entities: list[dict],
    graph_context: str
) -> list[dict]:
    """
    Classify entities into stakeholder categories AND determine
    their real position on the topic from graph data.
    No stance is predefined — LLM reads the graph to find real positions.
    """

    entity_list = "\n".join([
        f"- {e['name']} (influence: {e.get('influence_score', 0):.3f}, citations: {e.get('citations', 1)})"
        for e in entities[:35]
    ])

    system = """You are an expert at identifying stakeholders and their real-world positions.
Given entities from a knowledge graph about a topic, classify each real stakeholder
and determine their ACTUAL known position based on the graph evidence.
Never assume a position — derive it from the graph context provided.
Respond in valid JSON only."""

    proposition = topic if topic.endswith("?") else f"{topic}?"
    prompt = f"""Proposition being debated: {proposition}

IMPORTANT: stance must always be relative to the proposition itself.
- "for" = this entity SUPPORTS the proposition
- "against" = this entity OPPOSES the proposition
- "neutral" = this entity has no clear position

Entities from knowledge graph:
{entity_list}

Real-world knowledge graph context (use this to determine actual positions):
{graph_context}

For each entity that is a real stakeholder, classify it and determine its actual position
on the topic based ONLY on what the knowledge graph tells you.

Respond in this exact JSON format:
{{
    "stakeholders": [
        {{
            "name": "entity name exactly as given",
            "category": "tech_company/government/civil_society/academic/labor_union/consumer/media/investor/affected_community/international_body",
            "real_position": "their actual known position on this specific topic based on graph evidence in 1-2 sentences",
            "stance": "for/against/neutral",
            "stake": "why this entity has a genuine interest in this topic outcome",
            "relevance_score": 0.85
        }}
    ]
}}

Rules:
- Only include real organizations, institutions, governments, or known groups
- Skip abstract concepts, vague terms, or events
- Derive stance from graph evidence — never assume based on category
- relevance_score is 0.0-1.0 based on how central this entity is to the topic
- Maximum 20 stakeholders
- A tech company could be FOR regulation if the graph shows evidence of that
- stance must reflect their position ON THE PROPOSITION, not their general sentiment about the subject matter
- Example: TikTok would be "against" a TikTok ban. U.S. Government would be "for" a TikTok ban."""

    try:
        result = await call_llm_json(prompt, system)
        parsed = json.loads(result)
        return parsed.get("stakeholders", [])
    except Exception as e:
        print(f"[StakeholderIdentifier] Classification error: {e}")
        return []

def enforce_diversity(stakeholders: list[dict], num_agents: int) -> list[dict]:
    """
    Ensure no single category dominates.
    Cap any category at MAX_CATEGORY_SHARE of total agents.
    Returns ranked diverse list.
    """
    max_per_category = max(1, int(num_agents * MAX_CATEGORY_SHARE))

    # Sort by relevance score descending
    sorted_s = sorted(stakeholders, key=lambda x: x.get("relevance_score", 0.5), reverse=True)

    category_counts = {}
    selected = []

    for s in sorted_s:
        cat = s.get("category", "civil_society")
        count = category_counts.get(cat, 0)
        if count < max_per_category:
            selected.append(s)
            category_counts[cat] = count + 1

    return selected

def fill_to_count(stakeholders: list[dict], num_agents: int) -> list[dict]:
    """
    If we have fewer stakeholders than agents needed,
    create representatives of the same stakeholders with slightly
    different roles to fill the count.
    """
    if len(stakeholders) >= num_agents:
        return stakeholders[:num_agents]

    filled = stakeholders.copy()
    i = 0
    while len(filled) < num_agents:
        base = stakeholders[i % len(stakeholders)]
        filled.append({
            **base,
            "name": f"{base['name']} (representative {i // len(stakeholders) + 2})",
            "real_position": f"A representative perspective aligned with {base['name']}'s position: {base['real_position']}"
        })
        i += 1

    return filled

async def identify_stakeholders(
    topic: str,
    G: nx.DiGraph,
    num_agents: int = 20
) -> list[dict]:
    """
    Main function — identifies real stakeholders from knowledge graph.
    Returns enriched stakeholder list ready for persona generation.
    """
    # Enforce minimum
    num_agents = max(num_agents, MIN_AGENTS)
    print(f"[StakeholderIdentifier] Identifying stakeholders for: {topic} ({num_agents} agents)")

    # Pull entities from graph
    influential = get_most_influential(G, top_n=40)
    orgs = get_nodes_by_type(G, "org")
    people = get_nodes_by_type(G, "person")

    all_entities = influential.copy()
    for e in orgs + people:
        if not any(x["name"] == e["name"] for x in all_entities):
            all_entities.append(e)

    # Build graph context string for LLM to read real positions from
    graph_context = "\n".join([
        f"- {n['name']}: {n.get('description', '')[:120]} [cited {n.get('citations', 1)}x]"
        for n in influential[:20]
    ])

    # Classify entities and get real positions
    raw_stakeholders = await classify_and_position_entities(topic, all_entities, graph_context)

    if not raw_stakeholders:
        print("[StakeholderIdentifier] No stakeholders identified, using graph entities as fallback")
        raw_stakeholders = [
            {
                "name": e["name"],
                "category": "civil_society",
                "real_position": f"Has a stake in {topic}",
                "stance": "neutral",
                "stake": "Identified from knowledge graph",
                "relevance_score": e.get("influence_score", 0.5)
            }
            for e in influential[:15]
        ]

    # Enforce diversity — no category dominates
    diverse = enforce_diversity(raw_stakeholders, num_agents)

    # Fill to required count if needed
    filled = fill_to_count(diverse, num_agents)

    # Enrich with category weights
    enriched = []
    for s in filled:
        category = s.get("category", "civil_society")
        defaults = STAKEHOLDER_CATEGORIES.get(category, STAKEHOLDER_CATEGORIES["civil_society"])
        enriched.append({
            **s,
            "persuasion_resistance": defaults["persuasion_resistance"],
            "influence_weight": defaults["influence_weight"],
        })

    print(f"[StakeholderIdentifier] Identified {len(enriched)} stakeholders across {len(set(s['category'] for s in enriched))} categories")
    for s in enriched:
        print(f"  → {s['name']} [{s['category']}] stance: {s['stance']}")

    return enriched