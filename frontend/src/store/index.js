import { createStore } from 'vuex'
import axios from 'axios'

// 导入模块
import userModule from './modules/user'
import competitionModule from './modules/competition'
import subscriptionModule from './modules/subscription'
import reportModule from './modules/report'

// 设置API基础URL
axios.defaults.baseURL = process.env.VUE_APP_API_BASE_URL || 'http://localhost:8000/api/v1';

// 创建HTTP请求拦截器，自动添加token
axios.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
}, error => {
  return Promise.reject(error)
})

// 创建HTTP响应拦截器，处理401错误
axios.interceptors.response.use(response => {
  return response
}, error => {
  if (error.response && error.response.status === 401) {
    // 清除token和用户信息
    localStorage.removeItem('token')
    // 如果需要，可以在这里重定向到登录页面
    // window.location.href = '/login'
  }
  return Promise.reject(error)
})

export default createStore({
  state: {
    notifications: [],
    loading: false,
    error: null
  },
  getters: {
    notifications: state => state.notifications,
    isLoading: state => state.loading,
    error: state => state.error
  },
  mutations: {
    SET_LOADING(state, loading) {
      state.loading = loading
    },
    SET_ERROR(state, error) {
      state.error = error
    },
    ADD_NOTIFICATION(state, notification) {
      state.notifications.push(notification)
    },
    REMOVE_NOTIFICATION(state, id) {
      state.notifications = state.notifications.filter(n => n.id !== id)
    },
    CLEAR_NOTIFICATIONS(state) {
      state.notifications = []
    }
  },
  actions: {
    // 通知相关
    addNotification({ commit }, notification) {
      const id = Date.now()
      commit('ADD_NOTIFICATION', { ...notification, id })
      
      // 自动移除通知
      setTimeout(() => {
        commit('REMOVE_NOTIFICATION', id)
      }, notification.timeout || 5000)
      
      return id
    },
    
    // 全局错误处理
    setError({ commit, dispatch }, error) {
      commit('SET_ERROR', error)
      
      // 如果提供了错误消息，显示通知
      if (error && typeof error === 'string') {
        dispatch('addNotification', {
          type: 'error',
          message: error,
          timeout: 5000
        })
      }
    },
    
    // 全局加载状态
    setLoading({ commit }, loading) {
      commit('SET_LOADING', loading)
    }
  },
  modules: {
    user: userModule,
    competition: competitionModule,
    subscription: subscriptionModule,
    report: reportModule
  }
}) 