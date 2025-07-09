<template>
  <div class="competition-list-page">
    <div class="container">
      <h1 class="page-title">竞赛列表</h1>
      
      <!-- 搜索和筛选区域 -->
      <div class="search-filter-container">
        <el-form :model="filterForm" class="filter-form">
          <el-row :gutter="20">
            <el-col :xs="24" :sm="8">
              <el-form-item>
                <el-input
                  v-model="filterForm.keyword"
                  placeholder="搜索竞赛名称、组织者..."
                  clearable
                  @keyup.enter="handleSearch"
                >
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                </el-input>
              </el-form-item>
            </el-col>
            
            <el-col :xs="24" :sm="8" :md="6">
              <el-form-item>
                <el-select
                  v-model="filterForm.category"
                  placeholder="竞赛类别"
                  clearable
                  style="width: 100%"
                >
                  <el-option
                    v-for="item in categories"
                    :key="item.id"
                    :label="item.name"
                    :value="item.id"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            
            <el-col :xs="24" :sm="8" :md="6">
              <el-form-item>
                <el-select
                  v-model="filterForm.level"
                  placeholder="竞赛级别"
                  clearable
                  style="width: 100%"
                >
                  <el-option
                    v-for="item in levels"
                    :key="item.id"
                    :label="item.name"
                    :value="item.id"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            
            <el-col :xs="24" :sm="8" :md="6">
              <el-form-item>
                <el-select
                  v-model="filterForm.status"
                  placeholder="竞赛状态"
                  clearable
                  style="width: 100%"
                >
                  <el-option label="即将开始" value="upcoming" />
                  <el-option label="正在进行" value="ongoing" />
                  <el-option label="已结束" value="ended" />
                </el-select>
              </el-form-item>
            </el-col>
            
            <el-col :xs="24" :sm="24" :md="6">
              <div class="filter-buttons">
                <el-button type="primary" @click="handleSearch">
                  <el-icon><Search /></el-icon> 搜索
                </el-button>
                <el-button @click="resetFilters">
                  <el-icon><RefreshRight /></el-icon> 重置
                </el-button>
              </div>
            </el-col>
          </el-row>
        </el-form>
      </div>
      
      <!-- 竞赛列表 -->
      <div class="competition-list-container">
        <el-skeleton :rows="10" animated v-if="loading" />
        
        <el-alert
          v-else-if="error"
          :title="'获取数据失败: ' + error"
          type="error"
          show-icon
          :closable="false"
        />
        
        <el-empty v-else-if="!competitions.length" description="暂无竞赛数据" />

        <div v-else class="competition-grid">
          <competition-card 
            v-for="competition in competitions" 
            :key="competition.id" 
            :competition="competition"
            @click="viewCompetitionDetail(competition.id)"
          />
        </div>
        
        <!-- 分页 -->
        <div class="pagination-container" v-if="totalItems > 0 && !loading && !error">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[12, 24, 36, 48]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="totalItems"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, watch, computed } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { Search, RefreshRight } from '@element-plus/icons-vue'
import CompetitionCard from '@/components/competition/CompetitionCard.vue'

export default {
  name: 'CompetitionListPage',
  components: {
    Search,
    RefreshRight,
    CompetitionCard
  },
  setup() {
    const store = useStore()
    const router = useRouter()
    
    const totalItems = ref(0)
    const currentPage = ref(1)
    const pageSize = ref(12)

    // 从 Vuex Store 获取核心状态
    const loading = computed(() => store.getters['competition/isLoading'])
    const error = computed(() => store.getters['competition/error'])
    const competitions = computed(() => store.getters['competition/competitions'])
    const categories = computed(() => store.getters['competition/categories'])
    const levels = computed(() => store.getters['competition/levels'])
    
    const filterForm = reactive({
      keyword: '',
      category: '',
      level: '',
      status: ''
    })
    
    const loadCategories = () => {
      store.dispatch('competition/fetchCategories').catch(error => {
        console.error('Failed to load categories:', error)
      })
    }
    
    const loadLevels = () => {
      store.dispatch('competition/fetchLevels').catch(error => {
        console.error('Failed to load levels:', error)
      })
    }
    
    const loadCompetitions = async () => {
      // 不再需要本地loading和try/catch
      // Vuex action会处理这些
      const params = {
        page: currentPage.value,
        page_size: pageSize.value,
        keyword: filterForm.keyword,
        category_id: filterForm.category,
        level_id: filterForm.level,
        status: filterForm.status
      }
      
      try {
        const result = await store.dispatch('competition/fetchCompetitions', params)
        // totalItems 仍然可以从返回结果中获取
        totalItems.value = result.total || 0
      } catch(e) {
        // action中已处理错误状态，这里可以只log
        console.error("Vue component caught error:", e)
        totalItems.value = 0 // 出错时清空
      }
    }
    
    const handleSearch = () => {
      currentPage.value = 1
      loadCompetitions()
    }
    
    const resetFilters = () => {
      Object.keys(filterForm).forEach(key => {
        filterForm[key] = ''
      })
      currentPage.value = 1
      loadCompetitions()
    }
    
    const handleSizeChange = (size) => {
      pageSize.value = size
      loadCompetitions()
    }
    
    const handleCurrentChange = (page) => {
      currentPage.value = page
      loadCompetitions()
    }
    
    const viewCompetitionDetail = (id) => {
      router.push(`/competition/${id}`)
    }
    
    // 监听筛选条件变化
    watch([() => filterForm.category, () => filterForm.level, () => filterForm.status], () => {
      currentPage.value = 1
      loadCompetitions()
    })
    
    onMounted(() => {
      loadCategories()
      loadLevels()
      loadCompetitions()
    })
    
    return {
      competitions,
      categories,
      levels,
      loading, // 使用computed属性
      error,   // 新增error属性
      totalItems,
      currentPage,
      pageSize,
      filterForm,
      handleSearch,
      resetFilters,
      handleSizeChange,
      handleCurrentChange,
      viewCompetitionDetail
    }
  }
}
</script>

<style lang="scss" scoped>
.competition-list-page {
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
  
  .search-filter-container {
    background-color: #fff;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 30px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    
    .filter-buttons {
      display: flex;
      justify-content: flex-start;
      gap: 10px;
      
      @media (min-width: 768px) {
        justify-content: flex-end;
      }
    }
  }
  
  .competition-list-container {
    background-color: #fff;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    
    .competition-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 20px;
      margin-bottom: 30px;
    }
    
    .pagination-container {
      display: flex;
      justify-content: center;
      margin-top: 30px;
    }
  }
}
</style> 