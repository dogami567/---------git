<template>
  <div class="user-profile-page">
    <div class="container">
      <h1 class="page-title">个人中心</h1>
      
      <div class="profile-container">
        <el-tabs v-model="activeTab" class="profile-tabs">
          <el-tab-pane label="个人信息" name="info">
            <el-card class="profile-card">
              <template #header>
                <div class="card-header">
                  <h2>个人信息</h2>
                  <el-button type="primary" @click="editMode = !editMode">
                    {{ editMode ? '取消' : '编辑' }}
                  </el-button>
                </div>
              </template>
              
              <div v-if="loading" class="loading-container">
                <el-skeleton :rows="5" animated />
              </div>
              
              <el-form
                v-else
                ref="profileFormRef"
                :model="profileForm"
                :rules="rules"
                label-position="top"
                :disabled="!editMode"
              >
                <el-form-item label="用户名" prop="username">
                  <el-input v-model="profileForm.username" />
                </el-form-item>
                
                <el-form-item label="邮箱" prop="email">
                  <el-input v-model="profileForm.email" type="email" />
                </el-form-item>
                
                <el-form-item label="姓名" prop="full_name">
                  <el-input v-model="profileForm.full_name" />
                </el-form-item>
                
                <el-form-item label="学校" prop="school">
                  <el-input v-model="profileForm.school" />
                </el-form-item>
                
                <el-form-item label="专业" prop="major">
                  <el-input v-model="profileForm.major" />
                </el-form-item>
                
                <el-form-item v-if="editMode">
                  <el-button type="primary" @click="updateProfile" :loading="updateLoading">
                    保存修改
                  </el-button>
                </el-form-item>
              </el-form>
            </el-card>
            
            <el-card class="profile-card">
              <template #header>
                <div class="card-header">
                  <h2>修改密码</h2>
                </div>
              </template>
              
              <el-form
                ref="passwordFormRef"
                :model="passwordForm"
                :rules="passwordRules"
                label-position="top"
              >
                <el-form-item label="当前密码" prop="current_password">
                  <el-input 
                    v-model="passwordForm.current_password" 
                    type="password" 
                    show-password 
                  />
                </el-form-item>
                
                <el-form-item label="新密码" prop="new_password">
                  <el-input 
                    v-model="passwordForm.new_password" 
                    type="password" 
                    show-password 
                  />
                </el-form-item>
                
                <el-form-item label="确认新密码" prop="confirm_password">
                  <el-input 
                    v-model="passwordForm.confirm_password" 
                    type="password" 
                    show-password 
                  />
                </el-form-item>
                
                <el-form-item>
                  <el-button type="primary" @click="changePassword" :loading="passwordLoading">
                    修改密码
                  </el-button>
                </el-form-item>
              </el-form>
            </el-card>
          </el-tab-pane>
          
          <el-tab-pane label="我的订阅" name="subscriptions">
            <el-card class="profile-card">
              <template #header>
                <div class="card-header">
                  <h2>我的订阅</h2>
                </div>
              </template>
              
              <div v-if="subscriptionsLoading" class="loading-container">
                <el-skeleton :rows="5" animated />
              </div>
              
              <div v-else-if="subscriptions.length > 0" class="subscriptions-list">
                <el-table :data="subscriptions" style="width: 100%">
                  <el-table-column prop="competition.title" label="竞赛名称">
                    <template #default="{ row }">
                      <router-link :to="`/competition/${row.competition_id}`">
                        {{ row.competition?.title }}
                      </router-link>
                    </template>
                  </el-table-column>
                  
                  <el-table-column prop="competition.category.name" label="类别" width="120" />
                  
                  <el-table-column prop="competition.status" label="状态" width="120">
                    <template #default="{ row }">
                      <el-tag :type="getStatusType(row.competition?.status)">
                        {{ getStatusText(row.competition?.status) }}
                      </el-tag>
                    </template>
                  </el-table-column>
                  
                  <el-table-column prop="created_at" label="订阅时间" width="180">
                    <template #default="{ row }">
                      {{ formatDate(row.created_at) }}
                    </template>
                  </el-table-column>
                  
                  <el-table-column label="操作" width="120">
                    <template #default="{ row }">
                      <el-button 
                        type="danger" 
                        size="small" 
                        @click="unsubscribe(row.id)"
                        :loading="row.loading"
                      >
                        取消订阅
                      </el-button>
                    </template>
                  </el-table-column>
                </el-table>
                
                <div class="pagination-container" v-if="totalSubscriptions > 0">
                  <el-pagination
                    v-model:current-page="subscriptionsPage"
                    v-model:page-size="subscriptionsPageSize"
                    :page-sizes="[10, 20, 30, 50]"
                    layout="total, sizes, prev, pager, next, jumper"
                    :total="totalSubscriptions"
                    @size-change="handleSubscriptionsSizeChange"
                    @current-change="handleSubscriptionsPageChange"
                  />
                </div>
              </div>
              
              <el-empty v-else description="暂无订阅" />
            </el-card>
          </el-tab-pane>
          
          <el-tab-pane label="我的报告" name="reports">
            <el-card class="profile-card">
              <template #header>
                <div class="card-header">
                  <h2>我的报告</h2>
                  <el-button type="primary" @click="$router.push('/reports')">
                    生成新报告
                  </el-button>
                </div>
              </template>
              
              <div v-if="reportsLoading" class="loading-container">
                <el-skeleton :rows="5" animated />
              </div>
              
              <div v-else-if="reports.length > 0" class="reports-list">
                <el-table :data="reports" style="width: 100%">
                  <el-table-column prop="title" label="报告标题" />
                  
                  <el-table-column prop="format" label="格式" width="120">
                    <template #default="{ row }">
                      <el-tag>{{ formatType(row.format) }}</el-tag>
                    </template>
                  </el-table-column>
                  
                  <el-table-column prop="created_at" label="生成时间" width="180">
                    <template #default="{ row }">
                      {{ formatDate(row.created_at) }}
                    </template>
                  </el-table-column>
                  
                  <el-table-column label="操作" width="200">
                    <template #default="{ row }">
                      <el-button 
                        type="primary" 
                        size="small" 
                        @click="viewReport(row.id)"
                      >
                        查看
                      </el-button>
                      <el-button 
                        type="danger" 
                        size="small" 
                        @click="deleteReport(row.id)"
                        :loading="row.loading"
                      >
                        删除
                      </el-button>
                    </template>
                  </el-table-column>
                </el-table>
                
                <div class="pagination-container" v-if="totalReports > 0">
                  <el-pagination
                    v-model:current-page="reportsPage"
                    v-model:page-size="reportsPageSize"
                    :page-sizes="[10, 20, 30, 50]"
                    layout="total, sizes, prev, pager, next, jumper"
                    :total="totalReports"
                    @size-change="handleReportsSizeChange"
                    @current-change="handleReportsPageChange"
                  />
                </div>
              </div>
              
              <el-empty v-else description="暂无报告" />
            </el-card>
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, watch } from 'vue'
import { useStore } from 'vuex'
import { useRouter, useRoute } from 'vue-router'
import { ElMessageBox } from 'element-plus'

export default {
  name: 'UserProfilePage',
  setup() {
    const store = useStore()
    const router = useRouter()
    const route = useRoute()
    
    // 表单引用
    const profileFormRef = ref(null)
    const passwordFormRef = ref(null)
    
    // 页面状态
    const activeTab = ref('info')
    const editMode = ref(false)
    const loading = ref(true)
    const updateLoading = ref(false)
    const passwordLoading = ref(false)
    
    // 个人信息表单
    const profileForm = reactive({
      username: '',
      email: '',
      full_name: '',
      school: '',
      major: ''
    })
    
    // 修改密码表单
    const passwordForm = reactive({
      current_password: '',
      new_password: '',
      confirm_password: ''
    })
    
    // 订阅相关
    const subscriptions = ref([])
    const subscriptionsLoading = ref(false)
    const subscriptionsPage = ref(1)
    const subscriptionsPageSize = ref(10)
    const totalSubscriptions = ref(0)
    
    // 报告相关
    const reports = ref([])
    const reportsLoading = ref(false)
    const reportsPage = ref(1)
    const reportsPageSize = ref(10)
    const totalReports = ref(0)
    
    // 表单验证规则
    const rules = {
      username: [
        { required: true, message: '请输入用户名', trigger: 'blur' },
        { min: 3, max: 20, message: '用户名长度应在3-20个字符之间', trigger: 'blur' }
      ],
      email: [
        { required: true, message: '请输入邮箱地址', trigger: 'blur' },
        { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
      ]
    }
    
    // 密码验证规则
    const validatePass = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请输入新密码'))
      } else if (value.length < 6) {
        callback(new Error('密码长度至少为6个字符'))
      } else {
        if (passwordForm.confirm_password !== '') {
          passwordFormRef.value.validateField('confirm_password')
        }
        callback()
      }
    }
    
    const validateConfirmPass = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请再次输入新密码'))
      } else if (value !== passwordForm.new_password) {
        callback(new Error('两次输入的密码不一致'))
      } else {
        callback()
      }
    }
    
    const passwordRules = {
      current_password: [
        { required: true, message: '请输入当前密码', trigger: 'blur' }
      ],
      new_password: [
        { validator: validatePass, trigger: 'blur' }
      ],
      confirm_password: [
        { validator: validateConfirmPass, trigger: 'blur' }
      ]
    }
    
    // 加载用户信息
    const loadUserInfo = async () => {
      loading.value = true
      try {
        const user = await store.dispatch('user/fetchUserInfo')
        if (user) {
          profileForm.username = user.username || ''
          profileForm.email = user.email || ''
          profileForm.full_name = user.full_name || ''
          profileForm.school = user.school || ''
          profileForm.major = user.major || ''
        }
      } catch (error) {
        console.error('Failed to load user info:', error)
        store.dispatch('addNotification', {
          type: 'error',
          message: '获取用户信息失败',
          timeout: 5000
        })
      } finally {
        loading.value = false
      }
    }
    
    // 更新个人信息
    const updateProfile = async () => {
      try {
        const valid = await profileFormRef.value.validate()
        if (!valid) return
        
        updateLoading.value = true
        await store.dispatch('user/updateProfile', { ...profileForm })
        
        editMode.value = false
        store.dispatch('addNotification', {
          type: 'success',
          message: '个人信息更新成功',
          timeout: 3000
        })
      } catch (error) {
        console.error('Failed to update profile:', error)
        store.dispatch('addNotification', {
          type: 'error',
          message: error.response?.data?.detail || '更新个人信息失败',
          timeout: 5000
        })
      } finally {
        updateLoading.value = false
      }
    }
    
    // 修改密码
    const changePassword = async () => {
      try {
        const valid = await passwordFormRef.value.validate()
        if (!valid) return
        
        passwordLoading.value = true
        await store.dispatch('user/changePassword', {
          current_password: passwordForm.current_password,
          new_password: passwordForm.new_password
        })
        
        // 清空表单
        passwordFormRef.value.resetFields()
        
        store.dispatch('addNotification', {
          type: 'success',
          message: '密码修改成功',
          timeout: 3000
        })
      } catch (error) {
        console.error('Failed to change password:', error)
        store.dispatch('addNotification', {
          type: 'error',
          message: error.response?.data?.detail || '密码修改失败',
          timeout: 5000
        })
      } finally {
        passwordLoading.value = false
      }
    }
    
    // 加载订阅列表
    const loadSubscriptions = async () => {
      subscriptionsLoading.value = true
      try {
        const params = {
          page: subscriptionsPage.value,
          page_size: subscriptionsPageSize.value
        }
        
        const result = await store.dispatch('subscription/fetchUserSubscriptions', params)
        subscriptions.value = result.items || []
        totalSubscriptions.value = result.total || 0
      } catch (error) {
        console.error('Failed to load subscriptions:', error)
        store.dispatch('addNotification', {
          type: 'error',
          message: '获取订阅列表失败',
          timeout: 5000
        })
      } finally {
        subscriptionsLoading.value = false
      }
    }
    
    // 取消订阅
    const unsubscribe = async (subscriptionId) => {
      try {
        await ElMessageBox.confirm('确定要取消此订阅吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        // 设置加载状态
        const subscription = subscriptions.value.find(s => s.id === subscriptionId)
        if (subscription) {
          subscription.loading = true
        }
        
        await store.dispatch('subscription/unsubscribeCompetition', subscriptionId)
        
        // 重新加载订阅列表
        loadSubscriptions()
        
        store.dispatch('addNotification', {
          type: 'success',
          message: '已取消订阅',
          timeout: 3000
        })
      } catch (error) {
        if (error !== 'cancel') {
          console.error('Failed to unsubscribe:', error)
          store.dispatch('addNotification', {
            type: 'error',
            message: '取消订阅失败',
            timeout: 5000
          })
        }
      }
    }
    
    // 加载报告列表
    const loadReports = async () => {
      reportsLoading.value = true
      try {
        const params = {
          page: reportsPage.value,
          page_size: reportsPageSize.value
        }
        
        const result = await store.dispatch('report/fetchUserReports', params)
        reports.value = result.items || []
        totalReports.value = result.total || 0
      } catch (error) {
        console.error('Failed to load reports:', error)
        store.dispatch('addNotification', {
          type: 'error',
          message: '获取报告列表失败',
          timeout: 5000
        })
      } finally {
        reportsLoading.value = false
      }
    }
    
    // 查看报告
    const viewReport = (reportId) => {
      router.push(`/reports/${reportId}`)
    }
    
    // 删除报告
    const deleteReport = async (reportId) => {
      try {
        await ElMessageBox.confirm('确定要删除此报告吗？此操作不可恢复。', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        // 设置加载状态
        const report = reports.value.find(r => r.id === reportId)
        if (report) {
          report.loading = true
        }
        
        await store.dispatch('report/deleteReport', reportId)
        
        // 重新加载报告列表
        loadReports()
        
        store.dispatch('addNotification', {
          type: 'success',
          message: '报告已删除',
          timeout: 3000
        })
      } catch (error) {
        if (error !== 'cancel') {
          console.error('Failed to delete report:', error)
          store.dispatch('addNotification', {
            type: 'error',
            message: '删除报告失败',
            timeout: 5000
          })
        }
      }
    }
    
    // 分页处理
    const handleSubscriptionsSizeChange = (size) => {
      subscriptionsPageSize.value = size
      loadSubscriptions()
    }
    
    const handleSubscriptionsPageChange = (page) => {
      subscriptionsPage.value = page
      loadSubscriptions()
    }
    
    const handleReportsSizeChange = (size) => {
      reportsPageSize.value = size
      loadReports()
    }
    
    const handleReportsPageChange = (page) => {
      reportsPage.value = page
      loadReports()
    }
    
    // 格式化日期
    const formatDate = (dateString) => {
      if (!dateString) return '未知'
      
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    }
    
    // 获取竞赛状态类型
    const getStatusType = (status) => {
      switch (status) {
        case 'upcoming': return 'warning'
        case 'ongoing': return 'success'
        case 'ended': return 'info'
        default: return 'info'
      }
    }
    
    // 获取竞赛状态文本
    const getStatusText = (status) => {
      switch (status) {
        case 'upcoming': return '即将开始'
        case 'ongoing': return '正在进行'
        case 'ended': return '已结束'
        default: return '未知状态'
      }
    }
    
    // 格式化报告类型
    const formatType = (format) => {
      switch (format) {
        case 'PDF': return 'PDF'
        case 'DOCX': return 'Word'
        case 'MARKDOWN': return 'Markdown'
        default: return format
      }
    }
    
    // 监听标签页变化
    watch(activeTab, (newTab) => {
      if (newTab === 'subscriptions') {
        loadSubscriptions()
      } else if (newTab === 'reports') {
        loadReports()
      }
    })
    
    // 初始化
    onMounted(() => {
      loadUserInfo()
      
      // 检查URL参数，决定激活哪个标签页
      const tab = route.query.tab
      if (tab && ['info', 'subscriptions', 'reports'].includes(tab)) {
        activeTab.value = tab
      }
    })
    
    return {
      profileFormRef,
      passwordFormRef,
      activeTab,
      editMode,
      loading,
      updateLoading,
      passwordLoading,
      profileForm,
      passwordForm,
      rules,
      passwordRules,
      subscriptions,
      subscriptionsLoading,
      subscriptionsPage,
      subscriptionsPageSize,
      totalSubscriptions,
      reports,
      reportsLoading,
      reportsPage,
      reportsPageSize,
      totalReports,
      updateProfile,
      changePassword,
      unsubscribe,
      viewReport,
      deleteReport,
      handleSubscriptionsSizeChange,
      handleSubscriptionsPageChange,
      handleReportsSizeChange,
      handleReportsPageChange,
      formatDate,
      getStatusType,
      getStatusText,
      formatType
    }
  }
}
</script>

<style lang="scss" scoped>
.user-profile-page {
  padding: 20px 0;
  
  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
  }
  
  .page-title {
    margin-bottom: 30px;
    color: #303133;
  }
  
  .profile-container {
    .profile-tabs {
      background-color: #fff;
      border-radius: 8px;
      box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
      padding: 20px;
    }
    
    .profile-card {
      margin-bottom: 20px;
      
      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        
        h2 {
          margin: 0;
          font-size: 1.2rem;
        }
      }
    }
    
    .loading-container {
      padding: 20px 0;
    }
    
    .pagination-container {
      margin-top: 20px;
      display: flex;
      justify-content: center;
    }
  }
}

@media (max-width: 768px) {
  .user-profile-page .profile-container {
    .card-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 10px;
      
      button {
        width: 100%;
      }
    }
  }
}
</style> 