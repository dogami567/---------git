import axios from 'axios'
import api from '@/utils/api' // 确保api实例被导入
import { ElMessage } from 'element-plus'

// 设置API基础URL
const apiBaseUrl = process.env.VUE_APP_API_BASE_URL || 'http://localhost:8000/api/v1'

export default {
  namespaced: true,
  
  state: {
    reports: [],
    templates: [],
    currentReport: null,
    loading: false,
    error: null,
    pagination: {
      total: 0
    }
  },
  
  getters: {
    reports: state => state.reports,
    currentReport: state => state.currentReport,
    isLoading: state => state.loading,
    error: state => state.error
  },
  
  mutations: {
    SET_REPORTS(state, reports) {
      state.reports = reports
    },
    SET_CURRENT_REPORT(state, report) {
      state.currentReport = report
    },
    ADD_REPORT(state, report) {
      state.reports.unshift(report) // 将新报告添加到列表顶部
    },
    REMOVE_REPORT(state, reportId) {
      state.reports = state.reports.filter(r => r.id !== reportId)
    },
    SET_TEMPLATES(state, templates) {
      state.templates = templates
    },
    SET_LOADING(state, loading) {
      state.loading = loading
    },
    SET_ERROR(state, error) {
      state.error = error
    },
    SET_PAGINATION(state, pagination) {
      state.pagination = pagination
    }
  },
  
  actions: {
    // 获取用户的所有报告
    async fetchReports({ commit, rootState }, params = {}) {
      if (!rootState.user.token) {
        throw new Error('用户未登录')
      }
      
      commit('SET_LOADING', true)
      try {
        const response = await axios.get(`${apiBaseUrl}/reports`, {
          headers: { Authorization: `Bearer ${rootState.user.token}` },
          params
        })
        commit('SET_REPORTS', response.data.items || [])
        commit('SET_LOADING', false)
        return response.data
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.detail || '获取报告列表失败')
        commit('SET_LOADING', false)
        throw error
      }
    },
    
    // 获取用户的报告（用于用户中心页面）
    async fetchUserReports({ commit, dispatch }, { page = 1, pageSize = 10 }) {
      commit('SET_LOADING', true)
      try {
        const response = await api.get(`/users/me/reports?page=${page}&page_size=${pageSize}`)
        commit('SET_REPORTS', response.data.items || [])
        commit('SET_PAGINATION', {
          page: response.data.page,
          pageSize: response.data.page_size,
          total: response.data.total
        })
      } catch (error) {
        console.error('Failed to fetch user reports:', error)
        dispatch('addNotification', {
          type: 'error',
          message: '获取我的报告列表失败',
          timeout: 5000
        }, { root: true })
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    // 获取报告详情
    async fetchReportById({ commit, rootState }, reportId) {
      if (!rootState.user.token) {
        throw new Error('用户未登录')
      }
      
      commit('SET_LOADING', true)
      try {
        const response = await axios.get(`${apiBaseUrl}/reports/${reportId}`, {
          headers: { Authorization: `Bearer ${rootState.user.token}` }
        })
        commit('SET_CURRENT_REPORT', response.data)
        commit('SET_LOADING', false)
        return response.data
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.detail || '获取报告详情失败')
        commit('SET_LOADING', false)
        throw error
      }
    },
    
    // 获取报告内容（用于预览）
    async fetchReportContent({ rootState }, reportId) {
      if (!rootState.user.token) {
        throw new Error('用户未登录')
      }
      
      try {
        const response = await axios.get(`${apiBaseUrl}/reports/${reportId}/content`, {
          headers: { Authorization: `Bearer ${rootState.user.token}` }
        })
        return response.data.content
      } catch (error) {
        console.error('获取报告内容失败:', error)
        throw error
      }
    },
    
    // 生成报告
    async generateReport({ commit, dispatch }, reportData) {
      commit('SET_LOADING', true) // 开始时设置加载状态
      try {
        const response = await api.post('/reports/', reportData)
        commit('ADD_REPORT', response.data)
        dispatch('fetchUserReports', { page: 1, pageSize: 5 }) // 重新获取列表
        dispatch('addNotification', {
          type: 'success',
          message: '报告已成功创建并开始生成！',
          timeout: 5000
        }, { root: true })
        return response.data
      } catch (error) {
        console.error('Failed to generate report:', error)
        dispatch('addNotification', {
          type: 'error',
          message: error.response?.data?.detail || '报告创建失败，请稍后重试。',
          timeout: 5000
        }, { root: true })
        throw error
      } finally {
        commit('SET_LOADING', false) // 结束时取消加载状态
      }
    },
    
    // 删除报告
    async deleteReport({ commit }, reportId) {
      try {
        await api.delete(`/reports/${reportId}`)
        commit('REMOVE_REPORT', reportId)
        ElMessage.success('报告删除成功！')
      } catch (error) {
        console.error('删除报告失败:', error)
        ElMessage.error('删除报告失败，请稍后重试。')
        throw error
      }
    },
    
    // 获取报告模板列表
    async fetchTemplates({ commit }) {
      commit('SET_LOADING', true)
      try {
        const response = await api.get('/reports/templates')
        commit('SET_TEMPLATES', response.data)
      } catch (error) {
        console.error('Failed to fetch templates:', error)
        ElMessage.error('获取报告模板失败，请检查网络或联系管理员。');
      } finally {
        commit('SET_LOADING', false)
      }
    }
  }
} 