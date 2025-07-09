<template>
  <div v-if="isLoading" class="loading-overlay">
    <div class="loading-spinner">
      <el-icon class="is-loading"><loading /></el-icon>
      <span class="loading-text">{{ message }}</span>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'
import { useStore } from 'vuex'
import { Loading } from '@element-plus/icons-vue'

export default {
  name: 'LoadingIndicator',
  components: {
    Loading
  },
  props: {
    message: {
      type: String,
      default: '加载中...'
    }
  },
  setup() {
    const store = useStore()
    const isLoading = computed(() => store.getters.isLoading)
    
    return {
      isLoading
    }
  }
}
</script>

<style scoped>
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.7);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  background-color: white;
  padding: 20px;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.loading-spinner .el-icon {
  font-size: 30px;
  color: #409eff;
  margin-bottom: 10px;
}

.loading-text {
  font-size: 14px;
  color: #606266;
}
</style> 