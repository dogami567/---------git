<template>
  <div class="home-page">
    <!-- 英雄区域 -->
    <section class="hero-section">
      <div class="container">
        <div class="hero-content">
          <h1 class="hero-title">大学生竞赛信息聚合与订阅平台</h1>
          <p class="hero-subtitle">发现最新竞赛，追踪重要信息，提升你的竞争力</p>
          <div class="hero-actions">
            <el-button type="primary" size="large" @click="router.push('/competitions')">
              浏览竞赛
            </el-button>
            <el-button size="large" @click="router.push('/register')" v-if="!isAuthenticated">
              立即注册
            </el-button>
          </div>
        </div>
      </div>
    </section>

    <!-- 平台特点 -->
    <section class="features-section">
      <div class="container">
        <h2 class="section-title text-center">平台特点</h2>
        <div class="features-grid">
          <div class="feature-card">
            <el-icon class="feature-icon"><Search /></el-icon>
            <h3>竞赛聚合</h3>
            <p>汇集各类大学生竞赛信息，分类整理，方便查找</p>
          </div>
          <div class="feature-card">
            <el-icon class="feature-icon"><Bell /></el-icon>
            <h3>订阅提醒</h3>
            <p>关注感兴趣的竞赛，获取实时更新和重要提醒</p>
          </div>
          <div class="feature-card">
            <el-icon class="feature-icon"><Document /></el-icon>
            <h3>报告生成</h3>
            <p>自动生成竞赛报告，支持多种格式导出</p>
          </div>
          <div class="feature-card">
            <el-icon class="feature-icon"><ChatDotRound /></el-icon>
            <h3>智能助手</h3>
            <p>AI驱动的竞赛助手，提供个性化推荐和建议</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 热门竞赛 -->
    <section class="popular-competitions">
      <div class="container">
        <div class="section-header">
          <h2 class="section-title">热门竞赛</h2>
          <router-link to="/competitions" class="view-all">查看全部</router-link>
        </div>
        
        <el-skeleton :rows="3" animated v-if="loading" />
        
        <div v-else class="competitions-grid">
          <competition-card 
            v-for="competition in popularCompetitions" 
            :key="competition.id" 
            :competition="competition" 
          />
          
          <div class="no-competitions" v-if="popularCompetitions.length === 0">
            <p>暂无热门竞赛信息</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 平台统计 -->
    <section class="stats-section">
      <div class="container">
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-number">{{ stats.competitions || '1000+' }}</div>
            <div class="stat-label">竞赛总数</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ stats.users || '5000+' }}</div>
            <div class="stat-label">注册用户</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ stats.subscriptions || '8000+' }}</div>
            <div class="stat-label">订阅数量</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ stats.reports || '3000+' }}</div>
            <div class="stat-label">生成报告</div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { Search, Bell, Document, ChatDotRound } from '@element-plus/icons-vue'
import CompetitionCard from '@/components/competition/CompetitionCard.vue'

export default {
  name: 'HomePage',
  components: {
    Search,
    Bell,
    Document,
    ChatDotRound,
    CompetitionCard
  },
  setup() {
    const store = useStore()
    const router = useRouter()
    
    const popularCompetitions = ref([])
    const stats = ref({
      competitions: null,
      users: null,
      subscriptions: null,
      reports: null
    })
    const loading = ref(true)
    
    const isAuthenticated = computed(() => store.getters['user/isAuthenticated'])
    
    const loadPopularCompetitions = async () => {
      loading.value = true
      try {
        // 获取热门竞赛（按订阅量排序）
        const result = await store.dispatch('competition/fetchHotCompetitions', 6)
        popularCompetitions.value = result || []
      } catch (error) {
        console.error('Failed to load popular competitions:', error)
        popularCompetitions.value = []
      } finally {
        loading.value = false
      }
    }
    
    const loadStats = async () => {
      try {
        // 这里应该调用获取平台统计数据的API
        // 暂时使用模拟数据
        stats.value = {
          competitions: '1000+',
          users: '5000+',
          subscriptions: '8000+',
          reports: '3000+'
        }
      } catch (error) {
        console.error('Failed to load platform stats:', error)
      }
    }
    
    onMounted(() => {
      loadPopularCompetitions()
      loadStats()
    })
    
    return {
      popularCompetitions,
      stats,
      loading,
      isAuthenticated,
      router
    }
  }
}
</script>

<style lang="scss" scoped>
.home-page {
  .hero-section {
    background: linear-gradient(135deg, #409EFF 0%, #66b1ff 100%);
    color: white;
    padding: 80px 0;
    text-align: center;
    
    .hero-content {
      max-width: 800px;
      margin: 0 auto;
    }
    
    .hero-title {
      font-size: 2.5rem;
      margin-bottom: 20px;
    }
    
    .hero-subtitle {
      font-size: 1.2rem;
      margin-bottom: 30px;
      opacity: 0.9;
    }
    
    .hero-actions {
      display: flex;
      justify-content: center;
      gap: 15px;
    }
  }
  
  .features-section {
    padding: 60px 0;
    background-color: white;
    
    .section-title {
      margin-bottom: 40px;
    }
    
    .features-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 30px;
    }
    
    .feature-card {
      text-align: center;
      padding: 30px 20px;
      border-radius: 8px;
      transition: transform 0.3s, box-shadow 0.3s;
      
      &:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
      }
      
      .feature-icon {
        font-size: 40px;
        color: #409EFF;
        margin-bottom: 20px;
      }
      
      h3 {
        font-size: 1.3rem;
        margin-bottom: 15px;
      }
      
      p {
        color: #606266;
        line-height: 1.6;
      }
    }
  }
  
  .popular-competitions {
    padding: 60px 0;
    
    .section-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 30px;
      
      .view-all {
        font-size: 1rem;
        color: #409EFF;
        text-decoration: none;
        
        &:hover {
          text-decoration: underline;
        }
      }
    }
    
    .competitions-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 20px;
    }
    
    .no-competitions {
      grid-column: 1 / -1;
      text-align: center;
      padding: 40px;
      color: #909399;
    }
  }
  
  .stats-section {
    background-color: #f5f7fa;
    padding: 60px 0;
    
    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 30px;
    }
    
    .stat-item {
      text-align: center;
      
      .stat-number {
        font-size: 2.5rem;
        font-weight: bold;
        color: #409EFF;
        margin-bottom: 10px;
      }
      
      .stat-label {
        font-size: 1.1rem;
        color: #606266;
      }
    }
  }
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.section-title {
  font-size: 2rem;
  color: #303133;
  margin-bottom: 20px;
  
  &.text-center {
    text-align: center;
  }
}
</style> 