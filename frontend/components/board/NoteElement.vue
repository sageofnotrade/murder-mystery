<template>
  <div class="note-element">
    <button class="delete-button" @click.stop="emit('delete', element.id)">×</button>
    <div class="element-header">Note</div>
    <div class="element-body">
      <p>{{ element?.description || 'note' }}</p>
    </div>
    <div class="element-footer">note #{{ element?.id }}</div>
  </div>
</template>


<script setup>
const emit = defineEmits(['delete'])

defineProps({
  element: { type: Object, required: false },
});
</script>

<style scoped>
.note-element {
  background-color: #f3e8ff;
  border: 2px dashed #a678d9;
  box-shadow: 2px 4px 6px rgba(0, 0, 0, 0.15);
  font-family: 'Courier New', Courier, monospace;
  padding: 0.75rem;
  border-radius: 10px;
  position: absolute;
  width: 160px;
  min-height: 80px;
  transform: rotate(1deg);
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}
.delete-button {
  position: absolute;
  top: 4px;
  right: 6px;
  border: none;
  background:rgb(229, 208, 252);
  color: #6b3fa0;
  font-weight: bold;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  line-height: 16px;
  font-size: 14px;
  cursor: pointer;
}
.element-header {
  font-weight: bold;
  font-size: 0.9rem;
  color: #6b3fa0;
  border-bottom: 1px dashed #a678d9;
  padding-bottom: 0.2rem;
  margin-bottom: 0.3rem;
}

.element-body p {
  font-size: 0.8rem;
  color: #5a4d6d;
  margin: 0;
}

.element-footer {
  font-size: 0.7rem;
  color: #888;
  margin-top: 0.5rem;
  text-align: right;
}
</style>
