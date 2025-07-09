<template>
  <div class="competition-detail-page">
    <div class="container">
      <!-- 加载中状态 -->
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="10" animated />
      </div>
      
      <!-- 竞赛详情 -->
      <div v-else-if="competition" class="competition-detail">
        <div class="competition-header">
          <div class="header-content">
            <h1 class="competition-title">{{ competition.title }}</h1>
            <div class="competition-meta">
              <el-tag size="small" type="success">{{ competition.category?.name }}</el-tag>
              <el-tag size="small" type="info">{{ competition.level?.name }}</el-tag>
              <el-tag 
                size="small" 
                :type="getStatusType(competition.status)"
              >
                {{ getStatusText(competition.status) }}
              </el-tag>
            </div>
          </div>
          
          <div class="header-actions">
            <el-button 
              type="primary" 
              :icon="isSubscribed ? 'Check' : 'Plus'" 
              @click="handleSubscription"
              :loading="subscribeLoading"
            >
              {{ isSubscribed ? '已订阅' : '订阅竞赛' }}
            </el-button>
            
            <el-dropdown v-if="competition.website || competition.registration_link">
              <el-button>
                相关链接 <el-icon class="el-icon--right"><arrow-down /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item v-if="competition.website">
                    <a :href="competition.website" target="_blank">官方网站</a>
                  </el-dropdown-item>
                  <el-dropdown-item v-if="competition.registration_link">
                    <a :href="competition.registration_link" target="_blank">报名链接</a>
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
        
        <el-divider />
        
        <div class="competition-info">
          <div class="info-section">
            <h2 class="section-title">基本信息</h2>
            <div class="info-grid">
              <div class="info-item">
                <div class="info-label">主办单位</div>
                <div class="info-value">{{ competition.organizer || '未提供' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">报名开始</div>
                <div class="info-value">{{ formatDate(competition.registration_start_date) }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">报名截止</div>
                <div class="info-value">{{ formatDate(competition.registration_end_date) }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">竞赛开始</div>
                <div class="info-value">{{ formatDate(competition.start_date) }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">竞赛结束</div>
                <div class="info-value">{{ formatDate(competition.end_date) }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">竞赛地点</div>
                <div class="info-value">{{ competition.location || '未提供' }}</div>
              </div>
            </div>
          </div>
          
          <div class="info-section">
            <h2 class="section-title">竞赛简介</h2>
            <div class="competition-description" v-html="competition.description"></div>
          </div>
          
          <div class="info-section" v-if="competition.requirements">
            <h2 class="section-title">参赛要求</h2>
            <div class="competition-requirements" v-html="competition.requirements"></div>
          </div>
          
          <div class="info-section" v-if="competition.rewards">
            <h2 class="section-title">奖项设置</h2>
            <div class="competition-rewards" v-html="competition.rewards"></div>
          </div>
          
          <div class="info-section" v-if="competition.schedule">
            <h2 class="section-title">赛程安排</h2>
            <div class="competition-schedule" v-html="competition.schedule"></div>
          </div>
          
          <div class="info-section" v-if="competition.contact">
            <h2 class="section-title">联系方式</h2>
            <div class="competition-contact" v-html="competition.contact"></div>
          </div>
        </div>
        
        <!-- 相关竞赛推荐 -->
        <div class="related-competitions" v-if="relatedCompetitions.length > 0">
          <h2 class="section-title">相关竞赛</h2>
          <div class="related-grid">
            <competition-card 
              v-for="item in relatedCompetitions" 
              :key="item.id" 
              :competition="item"
              @click="viewCompetitionDetail(item.id)"
            />
          </div>
        </div>
      </div>
      
      <!-- 未找到竞赛 -->
      <el-empty v-else description="未找到竞赛信息" />
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter, useRoute } from 'vue-router'
import { ElMessageBox } from 'element-plus'
// eslint-disable-next-line no-unused-vars
import { ArrowDown, Check, Plus } from '@element-plus/icons-vue'
import CompetitionCard from '@/components/competition/CompetitionCard.vue'

export default {
  name: 'CompetitionDetailPage',
  components: {
    ArrowDown,
    CompetitionCard
  },
  setup() {
    const store = useStore()
    const router = useRouter()
    const route = useRoute()
    
    const competition = ref(null)
    const loading = ref(true)
    const isSubscribed = ref(false)
    const subscribeLoading = ref(false)
    const relatedCompetitions = ref([])
    
    const competitionId = computed(() => route.params.id)
    const isAuthenticated = computed(() => store.getters['user/isAuthenticated'])
    
    const loadCompetitionDetail = async () => {
      loading.value = true
      try {
        competition.value = await store.dispatch('competition/fetchCompetitionDetail', competitionId.value)
        
        // 检查是否已订阅
        if (isAuthenticated.value) {
          checkSubscriptionStatus()
        }
        
        // 加载相关竞赛
        loadRelatedCompetitions()
      } catch (error) {
        console.error('Failed to load competition details:', error)
        store.dispatch('addNotification', {
          type: 'error',
          message: '获取竞赛详情失败',
          timeout: 5000
        })
      } finally {
        loading.value = false
      }
    }
    
    const checkSubscriptionStatus = async () => {
      try {
        isSubscribed.value = await store.dispatch('subscription/checkSubscription', competitionId.value)
      } catch (error) {
        console.error('Failed to check subscription status:', error)
      }
    }
    
    const loadRelatedCompetitions = async () => {
      try {
        if (!competition.value) return
        
        const params = {
          category_id: competition.value.category?.id,
          limit: 3,
          exclude_id: competitionId.value
        }
        
        const result = await store.dispatch('competition/fetchCompetitions', params)
        relatedCompetitions.value = result.items || []
      } catch (error) {
        console.error('Failed to load related competitions:', error)
      }
    }
    
    const handleSubscription = async () => {
      if (!isAuthenticated.value) {
        ElMessageBox.confirm('需要登录才能订阅竞赛，是否前往登录页面？', '提示', {
          confirmButtonText: '前往登录',
          cancelButtonText: '取消',
          type: 'info'
        }).then(() => {
          router.push({
            path: '/login',
            query: { redirect: route.fullPath }
          })
        }).catch(() => {})
        return
      }
      
      subscribeLoading.value = true
      try {
        if (isSubscribed.value) {
          // 查找订阅ID并取消订阅
          const subscriptions = await store.dispatch('subscription/fetchUserSubscriptions')
          const numericCompetitionId = parseInt(competitionId.value, 10)
          const subscription = subscriptions.find(s => s.competition_id === numericCompetitionId)
          
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
          await store.dispatch('subscription/subscribeCompetition', competitionId.value)
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
    
    const formatDate = (dateString) => {
      if (!dateString) return '未设置'
      
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
      })
    }
    
    const getStatusType = (status) => {
      switch (status) {
        case 'upcoming': return 'warning'
        case 'ongoing': return 'success'
        case 'ended': return 'info'
        default: return 'info'
      }
    }
    
    const getStatusText = (status) => {
      switch (status) {
        case 'upcoming': return '即将开始'
        case 'ongoing': return '正在进行'
        case 'ended': return '已结束'
        default: return '未知状态'
      }
    }
    
    const viewCompetitionDetail = (id) => {
      router.push(`/competition/${id}`)
    }
    
    onMounted(() => {
      loadCompetitionDetail()
    })
    
    return {
      competition,
      loading,
      isSubscribed,
      subscribeLoading,
      relatedCompetitions,
      isAuthenticated,
      handleSubscription,
      formatDate,
      getStatusType,
      getStatusText,
      viewCompetitionDetail
    }
  }
}
</script>

<style lang="scss" scoped>
.competition-detail-page {
  padding: 20px 0;
  
  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
  }
  
  .loading-container {
    background-color: #fff;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  }
  
  .competition-detail {
    background-color: #fff;
    border-radius: 8px;
    padding: 30px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    
    .competition-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      flex-wrap: wrap;
      gap: 20px;
      
      .header-content {
        flex: 1;
        min-width: 300px;
        
        .competition-title {
          font-size: 1.8rem;
          margin: 0 0 15px;
          color: #303133;
        }
        
        .competition-meta {
          display: flex;
          flex-wrap: wrap;
          gap: 10px;
        }
      }
      
      .header-actions {
        display: flex;
        gap: 10px;
      }
    }
    
    .info-section {
      margin-bottom: 30px;
      
      .section-title {
        font-size: 1.4rem;
        margin-bottom: 20px;
        color: #303133;
        position: relative;
        padding-left: 15px;
        
        &::before {
          content: '';
          position: absolute;
          left: 0;
          top: 50%;
          transform: translateY(-50%);
          width: 5px;
          height: 20px;
          background-color: #409EFF;
          border-radius: 3px;
        }
      }
      
      .info-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 20px;
        
        .info-item {
          .info-label {
            font-size: 0.9rem;
            color: #909399;
            margin-bottom: 5px;
          }
          
          .info-value {
            font-size: 1rem;
            color: #303133;
          }
        }
      }
      
      .competition-description,
      .competition-requirements,
      .competition-rewards,
      .competition-schedule,
      .competition-contact {
        line-height: 1.8;
        color: #606266;
        
        ::v-deep(h1),
        ::v-deep(h2),
        ::v-deep(h3),
        ::v-deep(h4),
        ::v-deep(h5),
        ::v-deep(h6) {
          margin-top: 1.5em;
          margin-bottom: 0.5em;
        }
        
        ::v-deep(p) {
          margin-bottom: 1em;
        }
        
        ::v-deep(ul),
        ::v-deep(ol) {
          padding-left: 2em;
          margin-bottom: 1em;
        }
      }
    }
    
    .related-competitions {
      margin-top: 40px;
      
      .related-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 20px;
      }
    }
  }
}

@media (max-width: 768px) {
  .competition-detail-page .competition-detail {
    padding: 20px;
    
    .competition-header {
      flex-direction: column;
      
      .header-actions {
        width: 100%;
        justify-content: flex-start;
      }
    }
  }
}
</style> 