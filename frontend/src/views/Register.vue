<template>
  <div class="register-page">
    <div class="container">
      <div class="register-card">
        <h2 class="register-title">注册</h2>
        
        <el-form 
          ref="registerFormRef" 
          :model="registerForm" 
          :rules="rules" 
          label-position="top"
          @submit.prevent="handleRegister"
        >
          <el-form-item label="用户名" prop="username">
            <el-input 
              v-model="registerForm.username" 
              placeholder="请输入用户名" 
              prefix-icon="User"
            />
          </el-form-item>
          
          <el-form-item label="邮箱" prop="email">
            <el-input 
              v-model="registerForm.email" 
              type="email" 
              placeholder="请输入邮箱" 
              prefix-icon="Message"
            />
          </el-form-item>
          
          <el-form-item label="密码" prop="password">
            <el-input 
              v-model="registerForm.password" 
              type="password" 
              placeholder="请输入密码" 
              prefix-icon="Lock"
              show-password
            />
          </el-form-item>
          
          <el-form-item label="确认密码" prop="confirmPassword">
            <el-input 
              v-model="registerForm.confirmPassword" 
              type="password" 
              placeholder="请再次输入密码" 
              prefix-icon="Lock"
              show-password
            />
          </el-form-item>
          
          <el-form-item>
            <el-checkbox v-model="registerForm.agreement" label="我已阅读并同意" />
            <a href="#" @click.prevent="showTerms">用户协议</a>
            <span>和</span>
            <a href="#" @click.prevent="showPrivacy">隐私政策</a>
          </el-form-item>
          
          <el-form-item>
            <el-button 
              type="primary" 
              native-type="submit" 
              :loading="isLoading" 
              class="register-button"
              :disabled="!registerForm.agreement"
            >
              注册
            </el-button>
          </el-form-item>
        </el-form>
        
        <div class="login-link">
          已有账号？ <router-link to="/login">立即登录</router-link>
        </div>
      </div>
    </div>
    
    <!-- 用户协议对话框 -->
    <el-dialog
      v-model="termsDialogVisible"
      title="用户协议"
      width="70%"
    >
      <div class="terms-content">
        <h3>大学生竞赛平台用户协议</h3>
        <p>欢迎使用大学生竞赛平台！本协议是您与大学生竞赛平台之间关于使用本平台服务的协议。</p>
        <p>1. 用户在注册和使用本平台时，必须遵守中华人民共和国相关法律法规。</p>
        <p>2. 用户应当妥善保管账号和密码，对账号下的所有行为负责。</p>
        <p>3. 用户不得利用本平台从事违法活动或损害他人合法权益的行为。</p>
        <p>4. 平台保留对违规用户采取限制或终止服务的权利。</p>
        <p>5. 本协议的解释权归大学生竞赛平台所有。</p>
      </div>
    </el-dialog>
    
    <!-- 隐私政策对话框 -->
    <el-dialog
      v-model="privacyDialogVisible"
      title="隐私政策"
      width="70%"
    >
      <div class="privacy-content">
        <h3>大学生竞赛平台隐私政策</h3>
        <p>我们非常重视您的隐私保护，本政策说明了我们如何收集、使用和保护您的个人信息。</p>
        <p>1. 我们收集的信息：注册信息、使用记录、设备信息等。</p>
        <p>2. 信息使用：提供服务、改进产品、用户分析等。</p>
        <p>3. 信息保护：我们采用加密等技术手段保护您的信息安全。</p>
        <p>4. 信息共享：除法律要求或经您同意外，我们不会向第三方分享您的个人信息。</p>
        <p>5. 您的权利：您有权访问、更正、删除您的个人信息。</p>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, computed } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
// eslint-disable-next-line no-unused-vars
import { User, Message, Lock } from '@element-plus/icons-vue'

export default {
  name: 'RegisterPage',
  setup() {
    const store = useStore()
    const router = useRouter()
    const registerFormRef = ref(null)
    
    const registerForm = reactive({
      username: '',
      email: '',
      password: '',
      confirmPassword: '',
      agreement: false
    })
    
    const termsDialogVisible = ref(false)
    const privacyDialogVisible = ref(false)
    
    const validatePass = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请输入密码'))
      } else if (value.length < 6) {
        callback(new Error('密码长度至少为6个字符'))
      } else {
        if (registerForm.confirmPassword !== '') {
          registerFormRef.value.validateField('confirmPassword')
        }
        callback()
      }
    }
    
    const validateConfirmPass = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请再次输入密码'))
      } else if (value !== registerForm.password) {
        callback(new Error('两次输入的密码不一致'))
      } else {
        callback()
      }
    }
    
    const rules = {
      username: [
        { required: true, message: '请输入用户名', trigger: 'blur' },
        { min: 3, max: 20, message: '用户名长度应在3-20个字符之间', trigger: 'blur' }
      ],
      email: [
        { required: true, message: '请输入邮箱地址', trigger: 'blur' },
        { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
      ],
      password: [
        { validator: validatePass, trigger: 'blur' }
      ],
      confirmPassword: [
        { validator: validateConfirmPass, trigger: 'blur' }
      ]
    }
    
    const isLoading = computed(() => store.getters['user/isLoading'])
    
    const handleRegister = async () => {
      try {
        const valid = await registerFormRef.value.validate()
        if (!valid) return
        
        // 调用注册API
        await store.dispatch('user/register', {
          username: registerForm.username,
          email: registerForm.email,
          password: registerForm.password
        })
        
        // 注册成功，显示提示并跳转到登录页
        store.dispatch('addNotification', {
          type: 'success',
          message: '注册成功，请登录',
          timeout: 3000
        })
        
        router.push('/login')
      } catch (error) {
        console.error('Registration error:', error)
        store.dispatch('addNotification', {
          type: 'error',
          message: error.response?.data?.detail || '注册失败，请稍后重试',
          timeout: 5000
        })
      }
    }
    
    const showTerms = () => {
      termsDialogVisible.value = true
    }
    
    const showPrivacy = () => {
      privacyDialogVisible.value = true
    }
    
    return {
      registerFormRef,
      registerForm,
      rules,
      isLoading,
      termsDialogVisible,
      privacyDialogVisible,
      handleRegister,
      showTerms,
      showPrivacy
    }
  }
}
</script>

<style lang="scss" scoped>
.register-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 80vh;
  padding: 40px 0;
  
  .register-card {
    background-color: #fff;
    border-radius: 8px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    padding: 40px;
    width: 100%;
    max-width: 500px;
    
    .register-title {
      text-align: center;
      margin-bottom: 30px;
      color: #303133;
    }
    
    .register-button {
      width: 100%;
      padding: 12px 20px;
      font-size: 1rem;
    }
    
    .login-link {
      margin-top: 20px;
      text-align: center;
      font-size: 0.9rem;
      color: #606266;
      
      a {
        font-weight: 500;
      }
    }
    
    a {
      color: #409EFF;
      text-decoration: none;
      
      &:hover {
        text-decoration: underline;
      }
    }
  }
}

.terms-content,
.privacy-content {
  max-height: 400px;
  overflow-y: auto;
  padding: 10px;
  
  h3 {
    margin-top: 0;
    margin-bottom: 20px;
  }
  
  p {
    margin-bottom: 15px;
    line-height: 1.6;
  }
}

@media (max-width: 576px) {
  .register-page .register-card {
    padding: 30px 20px;
  }
}
</style> 