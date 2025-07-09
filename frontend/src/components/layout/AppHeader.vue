<template>
  <header class="app-header">
    <div class="container">
      <div class="logo">
        <router-link to="/">
          <h1>大学生竞赛平台</h1>
        </router-link>
      </div>
      
      <nav class="main-nav">
        <el-menu mode="horizontal" :router="true" :ellipsis="false" class="nav-menu">
          <el-menu-item index="/">首页</el-menu-item>
          <el-menu-item index="/competitions">竞赛信息</el-menu-item>
          <el-menu-item index="/reports" v-if="isAuthenticated">我的报告</el-menu-item>
        </el-menu>
      </nav>
      
      <div class="user-actions">
        <template v-if="isAuthenticated">
          <el-dropdown @command="handleCommand">
            <span class="user-dropdown">
              {{ currentUser?.username || '用户' }}
              <el-icon><arrow-down /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                <el-dropdown-item command="reports">我的报告</el-dropdown-item>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
        <template v-else>
          <el-button type="text" @click="router.push('/login')">登录</el-button>
          <el-button type="primary" @click="router.push('/register')">注册</el-button>
        </template>
      </div>
    </div>
  </header>
</template>

<script>
import { computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { ArrowDown } from '@element-plus/icons-vue'

export default {
  name: 'AppHeader',
  components: {
    ArrowDown
  },
  setup() {
    const store = useStore()
    const router = useRouter()
    
    const isAuthenticated = computed(() => store.getters['user/isAuthenticated'])
    const currentUser = computed(() => store.getters['user/currentUser'])
    
    const handleCommand = (command) => {
      switch (command) {
        case 'profile':
          router.push('/user/profile')
          break
        case 'reports':
          router.push('/reports')
          break
        case 'logout':
          store.dispatch('user/logout')
          router.push('/')
          store.dispatch('addNotification', {
            type: 'success',
            message: '已成功退出登录',
            timeout: 3000
          })
          break
      }
    }
    
    onMounted(() => {
      if (isAuthenticated.value && !currentUser.value) {
        store.dispatch('user/fetchUserInfo')
      }
    })
    
    return {
      isAuthenticated,
      currentUser,
      handleCommand,
      router
    }
  }
}
</script>

<style lang="scss" scoped>
.app-header {
  background-color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  
  .container {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 20px;
    max-width: 1200px;
    margin: 0 auto;
    height: 60px;
  }
  
  .logo {
    h1 {
      margin: 0;
      font-size: 1.5rem;
      color: #409EFF;
    }
    
    a {
      text-decoration: none;
    }
  }
  
  .main-nav {
    flex: 1;
    margin: 0 20px;
    
    .nav-menu {
      border-bottom: none;
    }
  }
  
  .user-actions {
    display: flex;
    align-items: center;
    gap: 10px;
    
    .user-dropdown {
      display: flex;
      align-items: center;
      cursor: pointer;
      
      .el-icon {
        margin-left: 5px;
      }
    }
  }
}
</style> 