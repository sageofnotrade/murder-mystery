<template>
  <div class="note-element" :style="{ width: element.width + 'px', height: element.height + 'px' }">
    <button class="delete-button" @click.stop="emit('delete', element.id)">×</button>
    <div class="element-header">Note</div>
    <div class="element-body">
      <p>{{ element?.description || 'note' }}</p>
    </div>
    <div class="element-footer">note #{{ element?.id }}</div>
  </div>
</template>


<script setup>
const emit = defineEmits(['delete']);
const props = defineProps({
  element: { type: Object, required: false },
});

let resizing = false;

const startResize = (e) => {
  resizing = true;
  const startX = e.clientX;
  const startY = e.clientY;
  const startWidth = props.element.width || 160;
  const startHeight = props.element.height || 80;

  const onMouseMove = (moveEvent) => {
    if (!resizing) return;
    const newWidth = Math.max(100, startWidth + (moveEvent.clientX - startX));
    const newHeight = Math.max(60, startHeight + (moveEvent.clientY - startY));
    props.element.width = newWidth;
    props.element.height = newHeight;
  };

  const onMouseUp = () => {
    resizing = false;
    window.removeEventListener('mousemove', onMouseMove);
    window.removeEventListener('mouseup', onMouseUp);
  };

  window.addEventListener('mousemove', onMouseMove);
  window.addEventListener('mouseup', onMouseUp);
};
</script>


<style scoped>
.note-element {
  background: linear-gradient(to bottom, #f3e8ff, #fcf7ff);
  border: 2px dashed #a678d9;
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
.note-element:hover {
  transform: scale(1.02);
  z-index: 20;
}
.delete-button {
  position: absolute;
  top: 0.4em;
  right: 0.4em;
  background-color: #d9b3ff;
  border: none;
  border-radius: 50%;
  width: 1.4em;
  height: 1.4em;
  font-size: 0.8em;
  font-weight: bold;
  color: #6b3fa0;
  cursor: pointer;
  box-shadow: 0 1px 2px #aaa;
  z-index: 3;
}

.delete-button:hover {
  background-color: #a678d9;
  color: white;
}.delete-button {
  position: absolute;
  top: 0.4em;
  right: 0.4em;
  background-color: #d9b3ff;
  border: none;
  border-radius: 50%;
  width: 1.4em;
  height: 1.4em;
  font-size: 0.8em;
  font-weight: bold;
  color: #6b3fa0;
  cursor: pointer;
  box-shadow: 0 1px 2px #aaa;
  z-index: 3;
}

.delete-button:hover {
  background-color: #a678d9;
  color: white;
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

.resize-handle {
  position: absolute;
  right: 4px;
  bottom: 4px;
  width: 14px;
  height: 14px;
  background: #a678d9;
  cursor: se-resize;
  border-radius: 2px;
}

</style>
