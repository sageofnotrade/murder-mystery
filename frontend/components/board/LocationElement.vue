<template>
  <div class="location-element">
    <button class="delete-button" @click.stop="emit('delete', element.id)">×</button>
    <div class="element-header">Location</div>
    <div class="element-body">
      <p>{{ element?.description || 'location' }}</p>
    </div>
    <div class="element-footer">location #{{ element?.id }}</div>
  </div>
</template>

<script setup>
const emit = defineEmits(['delete'])

defineProps({
  element: { type: Object, required: false },
});
</script>

<style scoped>
.location-element {
  background-color: #fff9cc;
  border: 2px dashed #b58b00;
  box-shadow: 3px 5px 10px rgba(0, 0, 0, 0.1);
  font-family: 'Courier New', Courier, monospace;
  padding: 1em;
  padding-top: 2em;
  border-radius: 12px;
  position: absolute;
  width: 12em;
  height: 10em;
  min-width: 10em;
  min-height: 8em;
  max-width: 20em;
  max-height: 20em;
  resize: both;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  gap: 0.3em;
  transition: transform 0.2s ease-in-out;
}

.location-element:hover {
  transform: scale(1.02);
  z-index: 20;
}

.delete-button {
  position: absolute;
  top: 4px;
  right: 6px;
  border: none;
  background: rgb(248, 239, 157); /* original yellow shade */
  color: #b58b00;
  font-weight: bold;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  line-height: 16px;
  font-size: 14px;
  cursor: pointer;
  z-index: 3;
}

.delete-button:hover {
  background-color: #b58b00;
  color: white;
}

.element-header {
  font-weight: bold;
  font-size: 1em;
  color: #b58b00;
  border-bottom: 1px dashed #b58b00;
  padding-bottom: 0.3em;
  margin-bottom: 0.3em;
}

.element-body p {
  font-size: 0.9em;
  color: #6c5a00;
  margin: 0;
}

.element-footer {
  font-size: 0.8em;
  color: #888;
  margin-top: auto;
  text-align: right;
}
</style>
