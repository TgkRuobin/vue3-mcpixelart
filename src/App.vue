<script setup>
import { onMounted } from 'vue';
import { Toast } from 'bootstrap';

onMounted(() => {
  const toastElement = document.getElementById('liveToast');
  // 设置 10 秒（10000 毫秒）后自动消失，并启用自动隐藏
  const toast = new Toast(toastElement, {
    delay: 10000,
    autohide: true
  });
  
  // 延迟半秒弹出，避免页面加载瞬间显得太突兀
  setTimeout(() => {
    toast.show();
  }, 500);
});

import { provide } from 'vue';
import Layout from './components/Layout.vue'

import { transplant } from './utils/transplant'
transplant()

import { useUserStore } from './store/user'
const userStore = useUserStore()
userStore.init()

import { useSettingStore } from './store/setting'
const setting = useSettingStore()
setting.init() //初始化setting

import GlobalModal from './components/GlobalModal.vue'
import { useModal } from './utils/globalModal'
const { modalStatus, closeModal, showModal } = useModal()
provide('globalModal', showModal)

import ShareModal from './components/ShareModal.vue'
import { useShare } from './utils/shareModal'
const { shareStatus, closeShare, showShare } = useShare()
provide('shareModal', showShare)

import Waiting from './components/Waiting.vue'
import { useWait } from './utils/waitModal'
const {  waitStatus, closeWait, showWait } = useWait()
provide('waitTask', showWait)

import UserInfo from './components/UserInfo.vue'
import { useUser } from './utils/userModal'
const { userStatus, closeUser, showUser } = useUser()
provide('userInfo', showUser)

// import { apiGetTest, apiPostTest } from './api/test'
// apiPostTest({po: [['s1','s2'], ['s3', 's4']]})
// apiGetTest({fname: 'css'})
</script>

<template>
  <Layout>
    <template #default>
      <router-view v-slot="{ Component }">
        <keep-alive>
          <component :is="Component" />
        </keep-alive>
      </router-view>
    </template>
  </Layout>
  <Waiting @customClose="closeWait" :status="waitStatus"></Waiting>
  <GlobalModal @customClose="closeModal" :status="modalStatus"></GlobalModal>
  <ShareModal @customClose="closeShare" :status="shareStatus"></ShareModal>
  <UserInfo @customClose="closeUser" :status="userStatus"></UserInfo>
  <div class="toast-container position-fixed bottom-0 end-0 p-3">
    <div id="liveToast" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
      <div class="toast-header">
        <strong class="me-auto">站长的Java生存服</strong>
        <small>推荐</small>
        <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
      </div>
      <div class="toast-body">
        一辈子的存档计划
        <div class="mt-2 pt-2 border-top">
          <a href="https://skin.mcpixelart.com" target="_blank" class="btn btn-primary btn-sm">前往查看</a>
        </div>
      </div>
    </div>
  </div>
</template>