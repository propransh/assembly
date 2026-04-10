<template>
  <div class="agent-card" :class="`stance-${safe(agent.stance, 'neutral')}`">
    <div class="agent-header">
      <div class="agent-identity">
        <div class="agent-avatar">{{ initials(agent.name) }}</div>
        <div>
          <p class="agent-name">{{ safe(agent.name, 'Unknown Agent') }}</p>
          <p class="agent-persona">{{ safe(agent.persona, '') }}</p>
        </div>
      </div>
      <div class="score-badge">{{ safe(agent.score, 0).toFixed(1) }}</div>
    </div>

    <p class="agent-opinion">{{ safe(agent.opinion, '...') }}</p>

    <div class="agent-footer">
      <span class="stance-pill" :class="`pill-${safe(agent.stance, 'neutral')}`">
        {{ safe(agent.stance, 'neutral') }}
      </span>
      <span class="delta" v-if="safe(agent.opinion_delta, 0) > 0">
        +{{ safe(agent.opinion_delta, 0).toFixed(1) }} shifted
      </span>
      <span class="no-shift" v-else>held position</span>
    </div>
  </div>
</template>

<script setup>
defineProps({ agent: Object })

const safe = (val, fallback) => val ?? fallback

const initials = (name) => {
  if (!name) return '?'
  return name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase()
}
</script>

<style scoped>
.agent-card {
  background: #111;
  border: 1px solid #222;
  border-radius: 12px;
  padding: 18px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  transition: border-color 0.2s;
}
.stance-for    { border-left: 3px solid #1D9E75; }
.stance-against { border-left: 3px solid #E24B4A; }
.stance-neutral { border-left: 3px solid #888; }

.agent-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}
.agent-identity { display: flex; align-items: center; gap: 10px; }
.agent-avatar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: #1e1e1e;
  border: 1px solid #333;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 500;
  color: #aaa;
  flex-shrink: 0;
}
.agent-name { font-size: 14px; font-weight: 500; color: #fff; margin: 0; }
.agent-persona { font-size: 11px; color: #555; margin: 2px 0 0; }
.score-badge {
  font-size: 13px;
  background: #1a1a1a;
  color: #777;
  padding: 3px 10px;
  border-radius: 20px;
  border: 1px solid #2a2a2a;
}
.agent-opinion {
  font-size: 13px;
  color: #bbb;
  line-height: 1.6;
  margin: 0;
}
.agent-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.stance-pill {
  font-size: 11px;
  padding: 2px 10px;
  border-radius: 20px;
  font-weight: 500;
}
.pill-for     { background: #0a2e1e; color: #1D9E75; }
.pill-against { background: #2e0a0a; color: #E24B4A; }
.pill-neutral { background: #1e1e1e; color: #888; }
.delta   { font-size: 12px; color: #1D9E75; }
.no-shift { font-size: 12px; color: #444; }
</style>