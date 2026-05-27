<template>
  <div class="page">
    <div class="container">
      <h1 class="page-title">🤖 AI 推荐助手</h1>
      <p style="color:var(--text-light);margin-bottom:20px;font-size:14px;">
        告诉我你的预算、玩的游戏、偏好的品牌，AI 帮你挑选最合适的电竞装备。<br/>
        试试："我想买个500以内的无线鼠标，主要玩CS2，手偏大"
      </p>
      <div class="chat-container">
        <div class="chat-messages" ref="chatBox">
          <div v-if="messages.length === 0" style="text-align:center;color:#ccc;padding:40px;">
            开始你的第一次对话
          </div>
          <div v-for="(m, i) in messages" :key="i" :class="['chat-msg', m.role]">
            {{ m.content }}
          </div>
          <div v-if="loading" class="chat-msg assistant" style="opacity:0.6;">思考中...</div>
        </div>
        <div class="chat-input">
          <input v-model="input" placeholder="描述你的需求，例如：推荐一款打CS2的鼠标" @keyup.enter="send" />
          <button @click="send" :disabled="loading || !input.trim()">发送</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { chatRecommend } from '../api/index.js'

const messages = ref([])
const input = ref('')
const loading = ref(false)
const chatBox = ref(null)

async function send() {
  const text = input.value.trim()
  if (!text || loading.value) return
  messages.value.push({ role: 'user', content: text })
  input.value = ''
  loading.value = true
  await nextTick()
  if (chatBox.value) chatBox.value.scrollTop = chatBox.value.scrollHeight
  try {
    const res = await chatRecommend(text)
    messages.value.push({ role: 'assistant', content: res.data?.reply || '抱歉，暂时无法回答。' })
  } catch (e) {
    messages.value.push({ role: 'assistant', content: '抱歉，AI 服务暂时不可用：' + e.message })
  } finally {
    loading.value = false
    await nextTick()
    if (chatBox.value) chatBox.value.scrollTop = chatBox.value.scrollHeight
  }
}
</script>
