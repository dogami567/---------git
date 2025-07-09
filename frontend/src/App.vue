<template>
  <el-config-provider>
    <div class="app">
      <app-header />
      <div class="main-content">
        <router-view />
      </div>
      <app-footer />
      <notifications />
      <loading-indicator />
    </div>
  </el-config-provider>
</template>

<script>
import { onMounted } from 'vue'
import { useStore } from 'vuex'
import AppHeader from '@/components/layout/AppHeader.vue'
import AppFooter from '@/components/layout/AppFooter.vue'
import Notifications from '@/components/common/Notifications.vue'
import LoadingIndicator from '@/components/common/LoadingIndicator.vue'

export default {
  name: 'App',
  components: {
    AppHeader,
    AppFooter,
    Notifications,
    LoadingIndicator
  },
  setup() {
    const store = useStore()
    
    onMounted(async () => {
      // 如果有token，则获取用户信息
      if (store.getters['user/isAuthenticated']) {
        try {
          await store.dispatch('user/fetchUserInfo')
        } catch (error) {
          console.error('获取用户信息失败:', error)
        }
      }
    })
  }
}
</script>

<style lang="scss">
.app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.main-content {
  flex: 1;
  padding: 20px;
}
</style> 