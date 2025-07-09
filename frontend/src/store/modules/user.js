import axios from 'axios'

// 设置API基础URL
const apiBaseUrl = process.env.VUE_APP_API_BASE_URL || 'http://localhost:8000/api/v1'

export default {
  namespaced: true,
  
  state: {
    user: null,
    token: localStorage.getItem('token') || null,
    loading: false,
    error: null
  },
  
  getters: {
    currentUser: state => state.user,
    token: state => state.token,
    isAuthenticated: state => !!state.token,
    isLoading: state => state.loading,
    error: state => state.error
  },
  
  mutations: {
    SET_USER(state, user) {
      state.user = user
    },
    SET_TOKEN(state, token) {
      state.token = token
      if (token) {
        localStorage.setItem('token', token)
      } else {
        localStorage.removeItem('token')
      }
    },
    SET_LOADING(state, loading) {
      state.loading = loading
    },
    SET_ERROR(state, error) {
      state.error = error
    }
  },
  
  actions: {
    // 用户登录
    async login({ commit }, credentials) {
      commit('SET_LOADING', true)
      try {
        const response = await axios.post(`${apiBaseUrl}/users/login`, {
          login_identifier: credentials.username,
          password: credentials.password,
        })
        const { access_token, user } = response.data
        commit('SET_TOKEN', access_token)
        commit('SET_USER', user)
        commit('SET_LOADING', false)
        return user
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.detail || '登录失败')
        commit('SET_LOADING', false)
        throw error
      }
    },
    
    // 用户注册
    async register({ commit }, userData) {
      commit('SET_LOADING', true)
      try {
        // 修复：将API端点从 /auth/register 修改为 /users
        const response = await axios.post(`${apiBaseUrl}/users`, userData)
        commit('SET_LOADING', false)
        return response.data
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.detail || '注册失败')
        commit('SET_LOADING', false)
        throw error
      }
    },
    
    // 用户退出登录
    logout({ commit }) {
      commit('SET_USER', null)
      commit('SET_TOKEN', null)
    },
    
    // 获取当前用户信息
    async fetchUserInfo({ commit, state }) {
      if (!state.token) return null
      
      commit('SET_LOADING', true)
      try {
        const response = await axios.get(`${apiBaseUrl}/users/me`, {
          headers: { Authorization: `Bearer ${state.token}` }
        })
        commit('SET_USER', response.data)
        commit('SET_LOADING', false)
        return response.data
      } catch (error) {
        if (error.response?.status === 401) {
          commit('SET_TOKEN', null)
          commit('SET_USER', null)
        }
        commit('SET_ERROR', error.response?.data?.detail || '获取用户信息失败')
        commit('SET_LOADING', false)
        throw error
      }
    },
    
    // 更新用户个人信息
    async updateProfile({ commit, state }, userData) {
      if (!state.token) {
        throw new Error('用户未登录')
      }
      
      commit('SET_LOADING', true)
      try {
        const response = await axios.put(`${apiBaseUrl}/users/me`, userData, {
          headers: { Authorization: `Bearer ${state.token}` }
        })
        commit('SET_USER', response.data)
        commit('SET_LOADING', false)
        return response.data
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.detail || '更新个人信息失败')
        commit('SET_LOADING', false)
        throw error
      }
    },
    
    // 更改密码
    async changePassword({ commit, state }, passwordData) {
      if (!state.token) {
        throw new Error('用户未登录')
      }
      
      commit('SET_LOADING', true)
      try {
        const response = await axios.post(`${apiBaseUrl}/users/me/change-password`, passwordData, {
          headers: { Authorization: `Bearer ${state.token}` }
        })
        commit('SET_LOADING', false)
        return response.data
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.detail || '密码修改失败')
        commit('SET_LOADING', false)
        throw error
      }
    },
    
    // 重置密码请求
    async requestPasswordReset({ commit }, email) {
      commit('SET_LOADING', true)
      try {
        const response = await axios.post(`${apiBaseUrl}/auth/password-reset/request`, { email })
        commit('SET_LOADING', false)
        return response.data
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.detail || '密码重置请求失败')
        commit('SET_LOADING', false)
        throw error
      }
    },
    
    // 重置密码确认
    async confirmPasswordReset({ commit }, resetData) {
      commit('SET_LOADING', true)
      try {
        const response = await axios.post(`${apiBaseUrl}/auth/password-reset/confirm`, resetData)
        commit('SET_LOADING', false)
        return response.data
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.detail || '密码重置失败')
        commit('SET_LOADING', false)
        throw error
      }
    }
  }
} 