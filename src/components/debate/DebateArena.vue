<template>
  <div class="arena">
    <div class="arena-header">
      <div>
        <h2 class="arena-title">Debate Arena</h2>
        <p class="arena-topic">Topic: {{ topic }}</p>
      </div>
      <div class="round-controls">
        <button
          v-for="r in rounds"
          :key="r.round"
          :class="['round-btn', currentRound === r.round ? 'active' : '']"
          @click="currentRound = r.round"
        >
          Round {{ r.round }}
        </button>
      </div>
    </div>

    <div class="agents-grid">
      <AgentCard
        v-for="agent in currentAgents"
        :key="agent.id"
        :agent="agent"
      />
    </div>

    <div class="round-summary" v-if="currentRound > 1">
      <p class="summary-label">After round {{ currentRound }}</p>
      <div class="summary-stats">
        <div class="stat">
          <span class="stat-num">{{ shiftedCount }}</span>
          <span class="stat-label">agents shifted</span>
        </div>
        <div class="stat">
          <span class="stat-num">{{ heldCount }}</span>
          <span class="stat-label">held position</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import AgentCard from './AgentCard.vue'
import { getDebateRounds } from '../../api/mock.js'

const data = getDebateRounds()
const rounds = data.rounds
const topic = 'Economic reform debate'
const currentRound = ref(1)

const currentAgents = computed(() =>
  rounds.find(r => r.round === currentRound.value)?.agents ?? []
)

const shiftedCount = computed(() =>
  currentAgents.value.filter(a => (a.opinion_delta ?? 0) > 0).length
)

const heldCount = computed(() =>
  currentAgents.value.filter(a => (a.opinion_delta ?? 0) === 0).length
)
</script>

<style scoped>
.arena { display: flex; flex-direction: column; gap: 24px; }
.arena-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 12px;
}
.arena-title { font-size: 22px; font-weight: 500; color: #fff; }
.arena-topic { font-size: 13px; color: #555; margin-top: 4px; }
.round-controls { display: flex; gap: 8px; }
.round-btn {
  background: #111;
  border: 1px solid #2a2a2a;
  color: #666;
  padding: 6px 16px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.15s;
}
.round-btn.active {
  background: #1a1a1a;
  border-color: #444;
  color: #fff;
}
.agents-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
.round-summary {
  background: #111;
  border: 1px solid #1e1e1e;
  border-radius: 12px;
  padding: 16px 20px;
}
.summary-label { font-size: 12px; color: #555; margin-bottom: 12px; }
.summary-stats { display: flex; gap: 32px; }
.stat { display: flex; flex-direction: column; gap: 2px; }
.stat-num { font-size: 24px; font-weight: 500; color: #fff; }
.stat-label { font-size: 12px; color: #555; }
</style>