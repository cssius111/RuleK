<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup lang="ts">
// App.vue - 根组件，只负责显示路由内容
</script>

<style>
#app {
  min-height: 100vh;
  background: #0a0a0a;
  position: relative;
  overflow: hidden;
}

/* 添加恐怖纹理背景 */
#app::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 20% 50%, rgba(139, 0, 0, 0.3) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(220, 20, 60, 0.2) 0%, transparent 50%),
    radial-gradient(circle at 40% 20%, rgba(139, 0, 0, 0.2) 0%, transparent 50%);
  pointer-events: none;
  animation: pulse-darkness 8s ease-in-out infinite;
}

@keyframes pulse-darkness {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}
</style>
