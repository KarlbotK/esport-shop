import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useCartStore = defineStore('cart', () => {
  const items = ref(JSON.parse(localStorage.getItem('cart') || '[]'))

  function save() {
    localStorage.setItem('cart', JSON.stringify(items.value))
  }

  function addItem(sku) {
    const exist = items.value.find(i => i.skuId === sku.id)
    if (exist) {
      exist.quantity++
    } else {
      items.value.push({
        skuId: sku.id,
        skuName: sku.skuName,
        spuId: sku.spuId,
        spuName: sku._spuName || '',
        price: sku.price,
        quantity: 1,
        attributes: sku.attributes,
      })
    }
    save()
  }

  function removeItem(skuId) {
    items.value = items.value.filter(i => i.skuId !== skuId)
    save()
  }

  function clear() {
    items.value = []
    save()
  }

  const count = computed(() => items.value.reduce((s, i) => s + i.quantity, 0))
  const total = computed(() => items.value.reduce((s, i) => s + i.price * i.quantity, 0))

  return { items, addItem, removeItem, clear, count, total }
})
