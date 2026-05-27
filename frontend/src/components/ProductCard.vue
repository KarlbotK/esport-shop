<template>
  <div class="card product-card" @click="$router.push(`/product/${id}`)">
    <div class="product-img-placeholder" :style="{ background: `linear-gradient(135deg, #${bgColor}, #${bgColor}88)` }">
      <span class="img-text">{{ displayName.slice(0, 4) }}</span>
    </div>
    <div class="card-body">
      <div class="product-name">{{ displayName }}</div>
      <div class="product-price">
        <span class="unit">¥</span>{{ displayPrice }}
      </div>
      <div class="product-meta">{{ spu._brand || spu.brandName || '' }} · {{ spu._category || '' }}</div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({ spu: Object })

const id = computed(() => props.spu.id || props.spu.spuId)
const displayName = computed(() => props.spu.name || props.spu.spuName || '')
const displayPrice = computed(() => props.spu._minPrice || props.spu.minPrice || '--')

const bgColor = ['f97316','ef4444','8b5cf6','3b82f6','10b981','f59e0b'][Math.floor(Math.random() * 6)]
</script>
