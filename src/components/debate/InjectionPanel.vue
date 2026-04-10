<template>
  <div class="injection-panel" :class="{ open: isOpen }">
    <button class="toggle-btn" @click="isOpen = !isOpen">
      {{ isOpen ? '✕' : '⚡ Inject event' }}
    </button>

    <div class="panel-body" v-if="isOpen">
      <p class="panel-label">Inject a breaking event</p>
      <p class="panel-hint">All agents will react based on their personality.</p>

      <textarea
        v-model="eventText"
        class="event-input"
        placeholder="e.g. Government just announced a total AI ban..."
        rows="3"
      />

      <button
        class="inject-btn"
        :disabled="!eventText.trim()"
        @click="inject"
      >
        Inject now →
      </button>

      <div class="reactions" v-if="reactions.length">
        <p class="reactions-label">Agent reactions</p>
        <div
          class="reaction"
          v-for="r in reactions"
          :key="r.agent_id"
        >
          <div class="reaction-top">
            <span class="reaction-name">{{ r.name }}</span>
            <span class="reaction-badge" :class="r.shifted ? 'shifted' : 'held'">
              {{ r.shifted ? `+${(r.delta ?? 0).toFixed(1)} shifted` : 'held' }}
            </span>
          </div>
          <p class="reaction-before">Before: "{{ r.opinion_before }}"</p>
          <p class="reaction-after">After: "{{ r.opinion_after }}"</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { postInject } from '../../api/mock.js'

const isOpen = ref(false)
const eventText = ref('')
const reactions = ref([])

const inject = () => {
  if (!eventText.value.trim()) return
  const result = postInject(eventText.value)
  reactions.value = result.reactions ?? []
  eventText.value = ''
}
</script>

<style scoped>
.injection-panel {
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: auto;
  z-index: 1000;
}
.injection-panel.open { width: 320px; }

.toggle-btn {
  background: #fff;
  color: #000;
  border: none;
  padding: 10px 18px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
}

.panel-body {
  background: #111;
  border: 1px solid #222;
  border-radius: 16px;
  padding: 16px;
  margin-top: 8px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 70vh;
  overflow-y: auto;
}
.panel-label { font-size: 14px; font-weight: 500; color: #fff; }
.panel-hint { font-size: 12px; color: #555; margin-top: -8px; }

.event-input {
  background: #0a0a0a;
  border: 1px solid #222;
  border-radius: 10px;
  color: #fff;
  font-size: 13px;
  padding: 10px 12px;
  resize: none;
  font-family: sans-serif;
  line-height: 1.5;
  outline: none;
}
.event-input:focus { border-color: #444; }
.event-input::placeholder { color: #333; }

.inject-btn {
  background: #fff;
  color: #000;
  border: none;
  border-radius: 8px;
  padding: 10px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
}
.inject-btn:disabled { opacity: 0.2; cursor: not-allowed; }

.reactions { display: flex; flex-direction: column; gap: 8px; }
.reactions-label { font-size: 11px; color: #444; }
.reaction {
  background: #0f0f0f;
  border-radius: 10px;
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.reaction-top { display: flex; justify-content: space-between; align-items: center; }
.reaction-name { font-size: 13px; font-weight: 500; color: #fff; }
.reaction-badge { font-size: 11px; padding: 2px 8px; border-radius: 20px; }
.shifted { background: #0a2e1e; color: #1D9E75; }
.held { background: #1a1a1a; color: #555; }
.reaction-before { font-size: 11px; color: #444; }
.reaction-after { font-size: 12px; color: #aaa; }
</style>