<template>
  <div class="login-page">
    <div class="container">
      <div class="login-card">
        <h2 class="login-title">登录</h2>
        
        <el-form 
          ref="loginFormRef" 
          :model="loginForm" 
          :rules="rules" 
          label-position="top"
          @submit.prevent="handleLogin"
        >
          <el-form-item label="用户名/邮箱" prop="username">
            <el-input 
              v-model="loginForm.username" 
              placeholder="请输入用户名或邮箱" 
              prefix-icon="User"
            />
          </el-form-item>
          
          <el-form-item label="密码" prop="password">
            <el-input 
              v-model="loginForm.password" 
              type="password" 
              placeholder="请输入密码" 
              prefix-icon="Lock"
              show-password
            />
          </el-form-item>
          
          <div class="form-options">
            <el-checkbox v-model="loginForm.remember">记住我</el-checkbox>
            <router-link to="/forgot-password" class="forgot-link">忘记密码？</router-link>
          </div>
          
          <el-form-item>
            <el-button 
              type="primary" 
              native-type="submit" 
              :loading="isLoading" 
              class="login-button"
            >
              登录
            </el-button>
          </el-form-item>
        </el-form>
        
        <div class="register-link">
          还没有账号？ <router-link to="/register">立即注册</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed } from 'vue'
import { useStore } from 'vuex'
import { useRouter, useRoute } from 'vue-router'
// eslint-disable-next-line no-unused-vars
import { User, Lock } from '@element-plus/icons-vue'

export default {
  name: 'LoginPage',
  setup() {
    const store = useStore()
    const router = useRouter()
    const route = useRoute()
    const loginFormRef = ref(null)
    
    const loginForm = reactive({
      username: '',
      password: '',
      remember: false
    })
    
    const rules = {
      username: [
        { required: true, message: '请输入用户名或邮箱', trigger: 'blur' }
      ],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, message: '密码长度至少为6个字符', trigger: 'blur' }
      ]
    }
    
    const isLoading = computed(() => store.getters['user/isLoading'])
    
    const handleLogin = async () => {
      try {
        const valid = await loginFormRef.value.validate()
        if (!valid) return
        
        await store.dispatch('user/login', {
          username: loginForm.username,
          password: loginForm.password
        })
        
        // 登录成功，获取重定向地址
        const redirectPath = route.query.redirect || '/'
        router.push(redirectPath)
        
        store.dispatch('addNotification', {
          type: 'success',
          message: '登录成功',
          timeout: 3000
        })
      } catch (error) {
        console.error('Login error:', error)
        store.dispatch('addNotification', {
          type: 'error',
          message: error.response?.data?.detail || '登录失败，请检查用户名和密码',
          timeout: 5000
        })
      }
    }
    
    return {
      loginFormRef,
      loginForm,
      rules,
      isLoading,
      handleLogin
    }
  }
}
</script>

<style lang="scss" scoped>
.login-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 80vh;
  
  .login-card {
    background-color: #fff;
    border-radius: 8px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    padding: 40px;
    width: 100%;
    max-width: 450px;
    
    .login-title {
      text-align: center;
      margin-bottom: 30px;
      color: #303133;
    }
    
    .form-options {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      
      .forgot-link {
        font-size: 0.9rem;
      }
    }
    
    .login-button {
      width: 100%;
      padding: 12px 20px;
      font-size: 1rem;
    }
    
    .register-link {
      margin-top: 20px;
      text-align: center;
      font-size: 0.9rem;
      color: #606266;
      
      a {
        font-weight: 500;
      }
    }
  }
}

@media (max-width: 576px) {
  .login-page .login-card {
    padding: 30px 20px;
  }
}
</style> 