const safe = (val, fallback) => val ?? fallback

export const getDebateRounds = () => ({
    simulation_id: 'abc123',
    rounds: [
        {
            round: 1,
            agents: [
                { id: 'agent_1', name: 'The Skeptic', persona: 'Analytical, hard to convince', opinion: 'I disagree with the premise entirely.', score: 3.2, opinion_delta: 0.0, stance: 'against' },
                { id: 'agent_2', name: 'The Optimist', persona: 'Sees the best in everything', opinion: 'This is a great opportunity for everyone.', score: 7.8, opinion_delta: 0.0, stance: 'for' },
                { id: 'agent_3', name: 'The Realist', persona: 'Data-driven and cautious', opinion: 'The evidence is mixed at best.', score: 5.0, opinion_delta: 0.0, stance: 'neutral' },
                { id: 'agent_4', name: 'The Contrarian', persona: 'Challenges every assumption', opinion: 'Everyone is missing the real issue here.', score: 4.5, opinion_delta: 0.0, stance: 'against' }
            ]
        },
        {
            round: 2,
            agents: [
                { id: 'agent_1', name: 'The Skeptic', persona: 'Analytical, hard to convince', opinion: 'The counter-argument has some merit.', score: 4.1, opinion_delta: 0.9, stance: 'neutral' },
                { id: 'agent_2', name: 'The Optimist', persona: 'Sees the best in everything', opinion: 'I am even more convinced now.', score: 8.2, opinion_delta: 0.4, stance: 'for' },
                { id: 'agent_3', name: 'The Realist', persona: 'Data-driven and cautious', opinion: 'New data shifts my view slightly.', score: 5.8, opinion_delta: 0.8, stance: 'neutral' },
                { id: 'agent_4', name: 'The Contrarian', persona: 'Challenges every assumption', opinion: 'I stand by my original point entirely.', score: 4.5, opinion_delta: 0.0, stance: 'against' }
            ]
        }
    ]
})

export const getSentimentHistory = () => ({
    simulation_id: 'abc123',
    ticks: [
        { tick: 1, positive: 0.2, neutral: 0.5, negative: 0.3 },
        { tick: 2, positive: 0.35, neutral: 0.4, negative: 0.25 },
        { tick: 3, positive: 0.5, neutral: 0.35, negative: 0.15 },
        { tick: 4, positive: 0.6, neutral: 0.3, negative: 0.1 },
        { tick: 5, positive: 0.55, neutral: 0.35, negative: 0.1 }
    ]
})

export const getReport = () => ({
    simulation_id: 'abc123',
    topic: 'Economic reform debate',
    summary: '3 of 4 agents shifted opinion by round 2.',
    agents_shifted: 3,
    agents_held: 1,
    decisive_arguments: [
        { agent_id: 'agent_2', argument: 'The economic data clearly shows long-term gains outweigh short-term costs.', influenced_agents: [ 'agent_1', 'agent_3' ] }
    ],
    predicted_trajectory: 'Public opinion likely shifts toward moderate acceptance within 2–3 weeks.',
    agent_summaries: [
        { agent_id: 'agent_1', name: 'The Skeptic', shifted: true, final_stance: 'neutral', key_moment: 'Round 2, challenged by agent_2' },
        { agent_id: 'agent_2', name: 'The Optimist', shifted: false, final_stance: 'for', key_moment: 'Held position throughout' },
        { agent_id: 'agent_3', name: 'The Realist', shifted: true, final_stance: 'neutral', key_moment: 'Round 2, new data presented' },
        { agent_id: 'agent_4', name: 'The Contrarian', shifted: false, final_stance: 'against', key_moment: 'Refused to shift despite pressure' }
    ]
})

export const postInject = (event) => ({
    injected_at_tick: 14,
    reactions: [
        { agent_id: 'agent_1', name: 'The Skeptic', opinion_before: 'I disagree entirely.', opinion_after: 'This changes things significantly.', delta: 2.3, shifted: true },
        { agent_id: 'agent_2', name: 'The Optimist', opinion_before: 'I fully support this.', opinion_after: 'I fully support this.', delta: 0.0, shifted: false },
        { agent_id: 'agent_3', name: 'The Realist', opinion_before: 'The evidence is mixed.', opinion_after: 'This new event tips the balance.', delta: 1.1, shifted: true },
        { agent_id: 'agent_4', name: 'The Contrarian', opinion_before: 'Everyone is missing the point.', opinion_after: 'Everyone is still missing the point.', delta: 0.0, shifted: false }
    ]
})