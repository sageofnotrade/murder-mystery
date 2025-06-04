<template>
  <div class="space-y-4">
    <TransitionGroup name="fade" tag="div" class="space-y-2 border-t border-gray-700 pt-4">
      <div
        v-for="(item, index) in history"
        :key="index"
        class="bg-gray-800 text-white p-3 rounded shadow border border-gray-600"
      >
        {{ item.text }}
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup>
defineProps({
  history: Array
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: all 0.5s ease;
}
.fade-enter-from {
  opacity: 0;
  transform: translateY(6px);
}
.fade-enter-to {
  opacity: 1;
  transform: translateY(0);
}
</style>
