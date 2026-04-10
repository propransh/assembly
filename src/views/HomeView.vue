<template>
  <div class="home">
    <div class="hero">
      <h1 class="logo">Assembly</h1>
      <p class="tagline">Simulate how thousands of minds debate any topic.</p>
    </div>

    <div class="input-card">
      <label class="input-label">01 / Enter your topic</label>
      <textarea
        v-model="prompt"
        class="prompt-input"
        placeholder="e.g. Should AI be regulated by governments?"
        rows="4"
      />

      <div class="options-row">
        <div class="option-group">
          <label class="option-label">Agent count</label>
          <div class="option-pills">
            <button
              v-for="count in agentOptions"
              :key="count"
              :class="['pill', selectedCount === count ? 'pill-active' : '']"
              @click="selectedCount = count"
            >
              {{ count }}
            </button>
          </div>
        </div>

        <div class="option-group">
          <label class="option-label">Debate rounds</label>
          <div class="option-pills">
            <button
              v-for="round in roundOptions"
              :key="round"
              :class="['pill', selectedRounds === round ? 'pill-active' : '']"
              @click="selectedRounds = round"
            >
              {{ round }}
            </button>
          </div>
        </div>
      </div>

      <button
        class="start-btn"
        :disabled="!prompt.trim()"
        @click="startSimulation"
      >
        Start simulation →
      </button>
    </div>

    <div class="how-it-works">
      <div class="step" v-for="step in steps" :key="step.num">
        <span class="step-num">{{ step.num }}</span>
        <div>
          <p class="step-title">{{ step.title }}</p>
          <p class="step-desc">{{ step.desc }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const prompt = ref('')
const selectedCount = ref(100)
const selectedRounds = ref(3)

const agentOptions = [10, 100, 500, 1000]
const roundOptions = [2, 3, 5, 10]

const steps = [
  { num: '01', title: 'Enter a topic', desc: 'Any question, policy, or scenario you want to simulate.' },
  { num: '02', title: 'Agents are created', desc: 'Thousands of agents with unique personalities and opinions.' },
  { num: '03', title: 'They debate', desc: 'Agents argue, defend, and try to convince each other.' },
  { num: '04', title: 'You decide', desc: "Read the God's Eye report and make your call." }
]

const startSimulation = () => {
  if (!prompt.value.trim()) return
  router.push({
    path: '/debate',
    query: { topic: prompt.value, agents: selectedCount.value, rounds: selectedRounds.value }
  })
}
</script>

<style scoped>
.home { display: flex; flex-direction: column; gap: 40px; }
.hero { text-align: center; padding: 20px 0; }
.logo { font-size: 48px; font-weight: 500; color: #fff; letter-spacing: -1px; }
.tagline { font-size: 16px; color: #555; margin-top: 8px; }

.input-card {
  background: #111;
  border: 1px solid #222;
  border-radius: 16px;
  padding: 28px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.input-label { font-size: 12px; color: #555; letter-spacing: 0.05em; }
.prompt-input {
  background: #0a0a0a;
  border: 1px solid #222;
  border-radius: 10px;
  color: #fff;
  font-size: 15px;
  padding: 14px;
  resize: none;
  font-family: sans-serif;
  line-height: 1.6;
  outline: none;
  transition: border-color 0.2s;
}
.prompt-input:focus { border-color: #444; }
.prompt-input::placeholder { color: #333; }

.options-row { display: flex; gap: 32px; flex-wrap: wrap; }
.option-group { display: flex; flex-direction: column; gap: 8px; }
.option-label { font-size: 12px; color: #555; }
.option-pills { display: flex; gap: 6px; }
.pill {
  background: #0a0a0a;
  border: 1px solid #222;
  color: #555;
  padding: 5px 14px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.15s;
}
.pill-active { background: #1a1a1a; border-color: #444; color: #fff; }

.start-btn {
  background: #fff;
  color: #000;
  border: none;
  border-radius: 10px;
  padding: 14px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.2s;
}
.start-btn:disabled { opacity: 0.2; cursor: not-allowed; }
.start-btn:hover:not(:disabled) { opacity: 0.9; }

.how-it-works {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}
.step {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 16px;
  background: #111;
  border: 1px solid #1a1a1a;
  border-radius: 12px;
}
.step-num { font-size: 11px; color: #333; }
.step-title { font-size: 13px; font-weight: 500; color: #fff; margin: 0; }
.step-desc { font-size: 12px; color: #555; margin: 4px 0 0; line-height: 1.5; }
</style>