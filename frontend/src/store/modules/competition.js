import axios from 'axios'

// 设置API基础URL
const apiBaseUrl = process.env.VUE_APP_API_BASE_URL || 'http://localhost:8000/api'

export default {
  namespaced: true,
  
  state: {
    competitions: [],
    currentCompetition: null,
    categories: [],
    levels: [],
    loading: false,
    error: null
  },
  
  getters: {
    competitions: state => state.competitions,
    currentCompetition: state => state.currentCompetition,
    categories: state => state.categories,
    levels: state => state.levels,
    isLoading: state => state.loading,
    error: state => state.error
  },
  
  mutations: {
    SET_COMPETITIONS(state, competitions) {
      state.competitions = competitions
    },
    SET_CURRENT_COMPETITION(state, competition) {
      state.currentCompetition = competition
    },
    SET_CATEGORIES(state, categories) {
      state.categories = categories
    },
    SET_LEVELS(state, levels) {
      state.levels = levels
    },
    SET_LOADING(state, loading) {
      state.loading = loading
    },
    SET_ERROR(state, error) {
      state.error = error
    }
  },
  
  actions: {
    // 获取竞赛列表
    async fetchCompetitions({ commit }, params = {}) {
      commit('SET_LOADING', true)
      try {
        const response = await axios.get(`${apiBaseUrl}/competitions`, { params })
        
        const data = response.data

        // 检查后端返回的是否是数组
        if (Array.isArray(data)) {
          // 如果是数组，直接提交
          commit('SET_COMPETITIONS', data)
          commit('SET_LOADING', false)
          // 并返回组件期望的 { items, total } 结构
          return { items: data, total: data.length }
        } else {
          // 兼容未来可能返回对象格式的情况
          commit('SET_COMPETITIONS', data.items || [])
          commit('SET_LOADING', false)
          return data
        }
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.detail || '获取竞赛列表失败')
        commit('SET_LOADING', false)
        throw error
      }
    },
    
    // 获取竞赛详情
    async fetchCompetitionDetail({ commit }, competitionId) {
      commit('SET_LOADING', true)
      try {
        const response = await axios.get(`${apiBaseUrl}/competitions/${competitionId}`)
        commit('SET_CURRENT_COMPETITION', response.data)
        commit('SET_LOADING', false)
        return response.data
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.detail || '获取竞赛详情失败')
        commit('SET_LOADING', false)
        throw error
      }
    },
    
    // 获取热门竞赛（用于首页展示）
    async fetchHotCompetitions({ commit }, limit = 6) {
      commit('SET_LOADING', true)
      try {
        const response = await axios.get(`${apiBaseUrl}/competitions/hot`, {
          params: { limit }
        })
        commit('SET_LOADING', false)
        return response.data
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.detail || '获取热门竞赛失败')
        commit('SET_LOADING', false)
        throw error
      }
    },
    
    // 获取即将开始的竞赛
    async fetchUpcomingCompetitions({ commit }, limit = 6) {
      commit('SET_LOADING', true)
      try {
        const response = await axios.get(`${apiBaseUrl}/competitions/upcoming`, {
          params: { limit }
        })
        commit('SET_LOADING', false)
        return response.data
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.detail || '获取即将开始的竞赛失败')
        commit('SET_LOADING', false)
        throw error
      }
    },
    
    // 获取竞赛类别
    async fetchCategories({ commit, state }) {
      if (state.categories.length > 0) {
        return state.categories
      }
      
      try {
        const response = await axios.get(`${apiBaseUrl}/competitions/categories`)
        commit('SET_CATEGORIES', response.data)
        return response.data
      } catch (error) {
        console.error('获取竞赛类别失败:', error)
        return []
      }
    },
    
    // 获取竞赛级别
    async fetchLevels({ commit, state }) {
      if (state.levels.length > 0) {
        return state.levels
      }
      
      try {
        const response = await axios.get(`${apiBaseUrl}/competitions/levels`)
        commit('SET_LEVELS', response.data)
        return response.data
      } catch (error) {
        console.error('获取竞赛级别失败:', error)
        return []
      }
    },
    
    // 搜索竞赛
    async searchCompetitions({ commit }, searchParams) {
      commit('SET_LOADING', true)
      try {
        const response = await axios.get(`${apiBaseUrl}/competitions/search`, {
          params: searchParams
        })
        commit('SET_COMPETITIONS', response.data.items || [])
        commit('SET_LOADING', false)
        return response.data
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.detail || '搜索竞赛失败')
        commit('SET_LOADING', false)
        throw error
      }
    }
  }
} 