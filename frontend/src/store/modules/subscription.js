import axios from 'axios'

// 设置API基础URL
const apiBaseUrl = process.env.VUE_APP_API_BASE_URL || 'http://localhost:8000/api/v1'

export default {
  namespaced: true,
  
  state: {
    subscriptions: [],
    loading: false,
    error: null
  },
  
  getters: {
    subscriptions: state => state.subscriptions,
    isLoading: state => state.loading,
    error: state => state.error
  },
  
  mutations: {
    SET_SUBSCRIPTIONS(state, subscriptions) {
      state.subscriptions = subscriptions
    },
    ADD_SUBSCRIPTION(state, subscription) {
      state.subscriptions.push(subscription)
    },
    REMOVE_SUBSCRIPTION(state, subscriptionId) {
      state.subscriptions = state.subscriptions.filter(s => s.id !== subscriptionId)
    },
    SET_LOADING(state, loading) {
      state.loading = loading
    },
    SET_ERROR(state, error) {
      state.error = error
    }
  },
  
  actions: {
    // 获取用户的所有订阅
    async fetchUserSubscriptions({ commit, rootState }, params = {}) {
      if (!rootState.user.token) {
        throw new Error('用户未登录')
      }
      
      commit('SET_LOADING', true)
      try {
        const response = await axios.get(`${apiBaseUrl}/subscriptions`, {
          headers: { Authorization: `Bearer ${rootState.user.token}` },
          params
        })
        commit('SET_SUBSCRIPTIONS', response.data.items || [])
        commit('SET_LOADING', false)
        return response.data
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.detail || '获取订阅列表失败')
        commit('SET_LOADING', false)
        throw error
      }
    },
    
    // 订阅竞赛
    async subscribeCompetition({ commit, rootState }, competitionId) {
      if (!rootState.user.token || !rootState.user.user) {
        throw new Error('用户未登录或用户信息不可用')
      }
      
      commit('SET_LOADING', true)
      try {
        const response = await axios.post(`${apiBaseUrl}/subscriptions`, 
          { 
            competition_id: competitionId,
            user_id: rootState.user.user.id
          },
          { headers: { Authorization: `Bearer ${rootState.user.token}` } }
        )
        commit('ADD_SUBSCRIPTION', response.data)
        commit('SET_LOADING', false)
        return response.data
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.detail || '订阅失败')
        commit('SET_LOADING', false)
        throw error
      }
    },
    
    // 取消订阅
    async unsubscribeCompetition({ commit, rootState }, subscriptionId) {
      if (!rootState.user.token) {
        throw new Error('用户未登录')
      }
      
      commit('SET_LOADING', true)
      try {
        await axios.delete(`${apiBaseUrl}/subscriptions/${subscriptionId}`, {
          headers: { Authorization: `Bearer ${rootState.user.token}` }
        })
        commit('REMOVE_SUBSCRIPTION', subscriptionId)
        commit('SET_LOADING', false)
        return true
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.detail || '取消订阅失败')
        commit('SET_LOADING', false)
        throw error
      }
    },
    
    // 检查用户是否已订阅某竞赛
    async checkSubscription({ rootState }, competitionId) {
      if (!rootState.user.token) {
        return false
      }
      
      try {
        const response = await axios.get(`${apiBaseUrl}/subscriptions/check/${competitionId}`, {
          headers: { Authorization: `Bearer ${rootState.user.token}` }
        })
        return response.data.is_subscribed
      } catch (error) {
        console.error('检查订阅状态失败:', error)
        return false
      }
    }
  }
} 