<template>
  <div class="competition-card" @click="navigateToDetail">
    <div class="competition-header">
      <h3 class="competition-title">{{ competition.title }}</h3>
      <el-tag :type="getStatusType(competition.status)" size="small">{{ getStatusText(competition.status) }}</el-tag>
    </div>
    
    <div class="competition-info">
      <div class="info-item">
        <el-icon><Calendar /></el-icon>
        <span>{{ formatDate(competition.registration_deadline) }}</span>
      </div>
      
      <div class="info-item">
        <el-icon><School /></el-icon>
        <span>{{ competition.organizer }}</span>
      </div>
      
      <div class="info-item">
        <el-icon><User /></el-icon>
        <span>{{ competition.level }}</span>
      </div>
    </div>
    
    <p class="competition-description">{{ truncateDescription(competition.description) }}</p>
    
    <div class="competition-footer">
      <div class="tags">
        <el-tag v-for="tag in competition.tags" :key="tag" size="small" effect="plain">{{ tag }}</el-tag>
      </div>
      
      <div class="actions">
        <slot name="actions">
          <el-button 
            type="primary" 
            size="small" 
            @click.stop="toggleSubscription"
            :loading="subscribeLoading"
          >
            {{ isSubscribed ? '已订阅' : '订阅' }}
          </el-button>
        </slot>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { Calendar, School, User } from '@element-plus/icons-vue'

export default {
  name: 'CompetitionCard',
  components: {
    Calendar,
    School,
    User
  },
  props: {
    competition: {
      type: Object,
      required: true
    }
  },
  setup(props) {
    const store = useStore()
    const router = useRouter()
    
    const isSubscribed = ref(false)
    const subscribeLoading = ref(false)
    
    const isAuthenticated = computed(() => store.getters['user/isAuthenticated'])
    
    const navigateToDetail = () => {
      router.push(`/competition/${props.competition.id}`)
    }
    
    const toggleSubscription = async (event) => {
      event.stopPropagation()
      
      if (!isAuthenticated.value) {
        router.push({
          path: '/login',
          query: { redirect: router.currentRoute.value.fullPath }
        })
        return
      }
      
      subscribeLoading.value = true
      
      try {
        if (isSubscribed.value) {
          // 查找订阅ID并取消订阅
          const subscriptions = await store.dispatch('subscription/fetchUserSubscriptions')
          const subscription = subscriptions.find(s => s.competition_id === props.competition.id)
          
          if (subscription) {
            await store.dispatch('subscription/unsubscribeCompetition', subscription.id)
            isSubscribed.value = false
            store.dispatch('addNotification', {
              type: 'success',
              message: '已取消订阅',
              timeout: 3000
            })
          }
        } else {
          // 订阅竞赛
          await store.dispatch('subscription/subscribeCompetition', props.competition.id)
          isSubscribed.value = true
          store.dispatch('addNotification', {
            type: 'success',
            message: '订阅成功',
            timeout: 3000
          })
        }
      } catch (error) {
        console.error('Failed to handle subscription:', error)
        store.dispatch('addNotification', {
          type: 'error',
          message: isSubscribed.value ? '取消订阅失败' : '订阅失败',
          timeout: 5000
        })
      } finally {
        subscribeLoading.value = false
      }
    }
    
    const truncateDescription = (description) => {
      if (!description) return ''
      return description.length > 100 ? description.substring(0, 100) + '...' : description
    }
    
    const formatDate = (dateString) => {
      if (!dateString) return '未设置'
      
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-CN')
    }
    
    const getStatusType = (status) => {
      const statusMap = {
        'upcoming': 'warning',
        'ongoing': 'success',
        'ended': 'info',
        'canceled': 'danger'
      }
      
      return statusMap[status] || 'info'
    }
    
    const getStatusText = (status) => {
      const statusTextMap = {
        'upcoming': '即将开始',
        'ongoing': '进行中',
        'ended': '已结束',
        'canceled': '已取消'
      }
      
      return statusTextMap[status] || '未知状态'
    }
    
    const checkSubscriptionStatus = async () => {
      if (isAuthenticated.value && props.competition.id) {
        try {
          isSubscribed.value = await store.dispatch('subscription/checkSubscription', props.competition.id)
        } catch (error) {
          console.error('Failed to check subscription status:', error)
        }
      }
    }
    
    onMounted(() => {
      checkSubscriptionStatus()
    })
    
    return {
      isSubscribed,
      subscribeLoading,
      isAuthenticated,
      navigateToDetail,
      toggleSubscription,
      truncateDescription,
      formatDate,
      getStatusType,
      getStatusText
    }
  }
}
</script>

<style lang="scss" scoped>
.competition-card {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 20px;
  transition: transform 0.3s, box-shadow 0.3s;
  cursor: pointer;
  
  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
  }
  
  .competition-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 15px;
    
    .competition-title {
      font-size: 1.2rem;
      margin: 0;
      flex: 1;
      margin-right: 10px;
    }
  }
  
  .competition-info {
    display: flex;
    flex-wrap: wrap;
    margin-bottom: 15px;
    gap: 10px;
    
    .info-item {
      display: flex;
      align-items: center;
      color: #606266;
      font-size: 0.9rem;
      margin-right: 15px;
      
      .el-icon {
        margin-right: 5px;
        font-size: 16px;
      }
    }
  }
  
  .competition-description {
    color: #606266;
    margin-bottom: 15px;
    font-size: 0.9rem;
    line-height: 1.5;
    height: 4.5em;
    overflow: hidden;
  }
  
  .competition-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    .tags {
      display: flex;
      flex-wrap: wrap;
      gap: 5px;
    }
  }
}
</style> 