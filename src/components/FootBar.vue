<script setup>
import constant from '@/assets/data/constant.json'
const version = constant.version
</script>

<template>
  <footer class="flex">
    <div class="flex frow gover">
      <div class="flex frow">
        <img src="@/assets/img/beian.png" height="16" width="16">
        <a href="https://beian.mps.gov.cn/#/query/webSearch?code=44030002010323" rel="noreferrer" target="_blank">粤公网安备44030002010323号</a>
      </div>
      <a href="https://beian.miit.gov.cn" target="_blank">粤ICP备2026011370号-1</a>
    </div>
    <div class="flex frow webv">
      <router-link to="/version">版本 {{ version }}</router-link>
      <router-link to="/privacy">隐私条款</router-link>
    </div>
  </footer>
  
</template>

<style lang="less" scoped>
footer {
  position: fixed;
  width: 100%;
  height: 36px;
  background-color: #712cf9;
  bottom: 0;
  flex-flow: row nowrap;
}
a, a:focus, a:active, a:hover {
  text-decoration: none;
  color: whitesmoke;
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
  font-size: 16px;
  line-height: 1rem;
}
.gover, .webv {
  gap: 20px;
  width: 100%;
  align-items: center;
  justify-content: center;
  flex-grow: 1;
}

@media (max-width:635px) {
  footer {
    flex-flow: row wrap;
  }
}
</style>