import axios from 'axios';
import store from '../store';

// 创建axios实例
const api = axios.create({
  baseURL: process.env.VUE_APP_API_BASE_URL || 'http://localhost:8000/api/v1',
  timeout: 10000, // 请求超时时间
});

// 请求拦截器
api.interceptors.request.use(
  config => {
    const token = store.state.user.token; // 从Vuex store中获取token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  response => {
    // 对响应数据做点什么
    return response;
  },
  error => {
    // 对响应错误做点什么
    if (error.response && error.response.status === 401) {
        // 例如，如果未授权，可以重定向到登录页
        store.dispatch('user/logout'); // 假设有logout的action
    }
    return Promise.reject(error);
  }
);

export default api; 