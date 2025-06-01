<template>
  <div class="board-page">
    <DetectiveBoard />
  </div>
</template>

<script setup>
import DetectiveBoard from '@/components/board/DetectiveBoard.vue';
</script>

<style scoped>
.board-page {
  width: 100vw;
  height: 100vh;
  background: #fafafa;
  display: flex;
  align-items: stretch;
  justify-content: stretch;
}
</style> 