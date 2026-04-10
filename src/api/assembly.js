const BASE = 'http://localhost:5001'

export const getDebateRounds = (id) =>
    fetch(`${ BASE }/api/debate/rounds?simulation_id=${ id }`).then(r => r.json())

export const getReport = (id) =>
    fetch(`${ BASE }/api/report/${ id }`).then(r => r.json())

export const getSentimentHistory = (id) =>
    fetch(`${ BASE }/api/sentiment/history/${ id }`).then(r => r.json())

export const postInject = (id, event) =>
    fetch(`${ BASE }/api/inject`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ simulation_id: id, event })
    }).then(r => r.json())