import json
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from backend.utils.llm_client import call_llm_json
from backend.utils.graph_utils import query_graph
import networkx as nx

# ── Deffuant Model Parameters ─────────────────────────────────────
BASE_MU = 0.3
CONFIDENCE_THRESHOLD = 3.0
MAX_EVIDENCE_MULTIPLIER = 1.5

def calculate_evidence_multiplier(evidence: list[dict]) -> float:
    if not evidence:
        return 1.0
    avg_citations = sum(e.get("citations", 1) for e in evidence) / len(evidence)
    multiplier = 1.0 + (min(avg_citations, 10) / 10) * (MAX_EVIDENCE_MULTIPLIER - 1.0)
    return round(min(multiplier, MAX_EVIDENCE_MULTIPLIER), 3)

def deffuant_update(
    opinion_i: float,
    opinion_j: float,
    resistance_i: float,
    evidence_multiplier: float
) -> tuple[float, float]:
    gap = abs(opinion_i - opinion_j)
    if gap >= CONFIDENCE_THRESHOLD:
        return opinion_i, 0.0
    effective_mu = BASE_MU * (1 - resistance_i) * evidence_multiplier
    delta = effective_mu * (opinion_j - opinion_i)
    new_opinion = round(max(1.0, min(10.0, opinion_i + delta)), 2)
    actual_delta = abs(new_opinion - opinion_i)
    return new_opinion, actual_delta

def derive_stance(score: float) -> str:
    if score <= 3.5:
        return "against"
    elif score >= 6.5:
        return "for"
    else:
        return "neutral"

async def run_single_agent_round(
    agent: dict,
    all_agents: list[dict],
    topic: str,
    G: nx.DiGraph,
    round_num: int
) -> dict:
    # Step 1 — Pull evidence from knowledge graph
    keywords = agent.get("key_beliefs", []) + agent.get("known_entities", [])
    evidence = query_graph(G, keywords, top_n=5)

    evidence_context = "\n".join([
        f"- {e['name']}: {e['description'][:150]} [source: {e['source'][:60]}] (cited {e['citations']}x)"
        for e in evidence
    ])

    # Step 2 — Read opponents
    opponents = [a for a in all_agents if a["id"] != agent["id"]]
    opponent_context = "\n".join([
        f"- {o['name']} ({o['stance']}, score {o['score']}): {o['opinion']}"
        for o in opponents[:6]
    ])

    # Step 3 — Find all opponents within threshold
    within_threshold = [
        opp for opp in opponents
        if abs(agent["score"] - opp["score"]) < CONFIDENCE_THRESHOLD
    ]

    # Step 4 — Weighted average Deffuant update
    evidence_multiplier = calculate_evidence_multiplier(evidence)
    old_score = agent["score"]

    if within_threshold:
        weights = [
            1.0 / (abs(agent["score"] - opp["score"]) + 0.1)
            for opp in within_threshold
        ]
        total_weight = sum(weights)
        weighted_avg = sum(
            opp["score"] * w for opp, w in zip(within_threshold, weights)
        ) / total_weight

        new_score, delta = deffuant_update(
            opinion_i=old_score,
            opinion_j=weighted_avg,
            resistance_i=agent.get("persuasion_resistance", 0.5),
            evidence_multiplier=evidence_multiplier
        )

        influential_opponent = min(
            within_threshold,
            key=lambda o: abs(agent["score"] - o["score"])
        )
        min_gap = abs(agent["score"] - influential_opponent["score"])
    else:
        new_score = old_score
        delta = 0.0
        influential_opponent = None
        min_gap = float('inf')

    # Step 5 — Derive stance and shift BEFORE calling LLM
    new_stance = derive_stance(new_score)
    shifted = delta > 0.05  # was 0.3 — too high for high-resistance agents

    # Step 6 — LLM generates argument text reflecting math-decided outcome
    system = """You are simulating a realistic human debater grounded in real evidence.
Your opinion shift has already been mathematically calculated.
Your job is to generate realistic argument text that reflects this outcome.
Respond in valid JSON only."""

    opponent_name = influential_opponent['name'] if influential_opponent else 'the group'
    shift_direction = f"You moved toward {opponent_name}'s position" if influential_opponent and shifted else "You held your position firm"

    prompt = f"""You are {agent['name']}, representing {agent.get('stakeholder_name', 'yourself')}.
Background: {agent['persona']}
Persuasion resistance: {agent.get('persuasion_resistance', 0.5)} (0=easily convinced, 1=never)

Topic: {topic}
Round: {round_num}

Your current position:
- Opinion: {agent['opinion']}
- Score: {old_score}/10
- Stance: {agent['stance']}

Evidence available from real sources:
{evidence_context}

What other debaters said:
{opponent_context}

Mathematical outcome (already decided):
- Your new score: {new_score}/10
- Opinion shifted: {shifted}
- {shift_direction}

Generate argument text that reflects this outcome naturally.

Respond in this exact JSON format:
{{
    "argument": "your argument this round citing specific evidence",
    "responding_to": "{opponent_name}",
    "new_opinion": "your updated opinion in 2 sentences reflecting score {new_score}",
    "shift_reason": "why you {'moved slightly' if shifted else 'held firm'} on this issue",
    "key_evidence_used": ["evidence point 1", "evidence point 2"]
}}"""

    try:
        result = await call_llm_json(prompt, system)
        response = json.loads(result)

        updated_agent = agent.copy()
        updated_agent["opinion"] = response.get("new_opinion", agent["opinion"])
        updated_agent["score"] = new_score
        updated_agent["stance"] = new_stance
        updated_agent["opinion_delta"] = delta
        updated_agent["last_argument"] = response.get("argument", "")
        updated_agent["shifted"] = shifted
        updated_agent["shift_reason"] = response.get("shift_reason", "")
        updated_agent["key_evidence_used"] = response.get("key_evidence_used", [])
        updated_agent["responding_to"] = response.get("responding_to", "")
        updated_agent["evidence_multiplier"] = evidence_multiplier
        updated_agent["deffuant_gap"] = round(min_gap, 2) if influential_opponent else None

        return updated_agent

    except Exception as e:
        print(f"[DebateEngine] Error in round {round_num} for {agent['name']}: {e}")
        return agent

async def run_debate_round(
    agents: list[dict],
    topic: str,
    G: nx.DiGraph,
    round_num: int
) -> list[dict]:
    print(f"[DebateEngine] Running round {round_num} with {len(agents)} agents...")
    tasks = [
        run_single_agent_round(agent, agents, topic, G, round_num)
        for agent in agents
    ]
    updated_agents = await asyncio.gather(*tasks)
    return list(updated_agents)

async def run_debate(
    topic: str,
    agents: list[dict],
    G: nx.DiGraph,
    num_rounds: int = 3
) -> dict:
    print(f"[DebateEngine] Starting debate on: {topic}")
    print(f"[DebateEngine] {len(agents)} agents, {num_rounds} rounds")
    print(f"[DebateEngine] Deffuant params: mu={BASE_MU}, threshold={CONFIDENCE_THRESHOLD}")

    all_rounds = []
    current_agents = agents.copy()

    for round_num in range(1, num_rounds + 1):
        updated_agents = await run_debate_round(current_agents, topic, G, round_num)

        round_result = {
            "round": round_num,
            "agents": [
                {
                    "id": a["id"],
                    "name": a["name"],
                    "persona": a["persona"],
                    "opinion": a["opinion"],
                    "score": a["score"],
                    "opinion_delta": a["opinion_delta"],
                    "stance": a["stance"],
                    "stakeholder_name": a.get("stakeholder_name"),
                    "stakeholder_category": a.get("stakeholder_category"),
                    "deffuant_gap": a.get("deffuant_gap"),
                    "evidence_multiplier": a.get("evidence_multiplier"),
                }
                for a in updated_agents
            ]
        }

        all_rounds.append(round_result)
        current_agents = updated_agents

        shifts = sum(1 for a in updated_agents if a.get("shifted", False))
        avg_delta = sum(a.get("opinion_delta", 0) for a in updated_agents) / len(updated_agents)
        print(f"[DebateEngine] Round {round_num} complete. Shifts: {shifts}/{len(updated_agents)} | Avg delta: {avg_delta:.3f}")

    return {
        "rounds": all_rounds,
        "final_agents": current_agents
    }