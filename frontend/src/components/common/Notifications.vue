<template>
  <div class="notifications-container">
    <transition-group name="notification">
      <div 
        v-for="notification in notifications" 
        :key="notification.id"
        :class="['notification', `notification--${notification.type}`]"
      >
        <div class="notification__content">
          <el-icon class="notification__icon">
            <component :is="iconComponent(notification.type)"></component>
          </el-icon>
          <span class="notification__message">{{ notification.message }}</span>
        </div>
        <button class="notification__close" @click="removeNotification(notification.id)">
          <el-icon><Close /></el-icon>
        </button>
      </div>
    </transition-group>
  </div>
</template>

<script>
import { computed } from 'vue'
import { useStore } from 'vuex'
import { Check, Warning, CircleClose, InfoFilled, Close } from '@element-plus/icons-vue'

export default {
  name: 'Notifications',
  
  components: {
    Check,
    Warning,
    CircleClose,
    InfoFilled,
    Close
  },
  
  setup() {
    const store = useStore()
    
    const notifications = computed(() => store.getters.notifications)
    
    const iconComponent = (type) => {
      switch (type) {
        case 'success':
          return 'Check'
        case 'warning':
          return 'Warning'
        case 'error':
          return 'CircleClose'
        case 'info':
        default:
          return 'InfoFilled'
      }
    }
    
    const removeNotification = (id) => {
      store.commit('REMOVE_NOTIFICATION', id)
    }
    
    return {
      notifications,
      iconComponent,
      removeNotification
    }
  }
}
</script>

<style scoped>
.notifications-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  max-width: 350px;
}

.notification {
  margin-bottom: 10px;
  padding: 15px;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  background-color: #fff;
  border-left: 4px solid #909399;
}

.notification--success {
  border-left-color: #67c23a;
}

.notification--warning {
  border-left-color: #e6a23c;
}

.notification--error {
  border-left-color: #f56c6c;
}

.notification--info {
  border-left-color: #409eff;
}

.notification__content {
  display: flex;
  align-items: center;
}

.notification__icon {
  margin-right: 10px;
  font-size: 18px;
}

.notification--success .notification__icon {
  color: #67c23a;
}

.notification--warning .notification__icon {
  color: #e6a23c;
}

.notification--error .notification__icon {
  color: #f56c6c;
}

.notification--info .notification__icon {
  color: #409eff;
}

.notification__message {
  font-size: 14px;
  color: #333;
}

.notification__close {
  background: transparent;
  border: none;
  cursor: pointer;
  font-size: 16px;
  color: #909399;
  padding: 0;
  margin-left: 10px;
  display: flex;
  align-items: center;
}

.notification__close:hover {
  color: #333;
}

/* 过渡动画 */
.notification-enter-active,
.notification-leave-active {
  transition: all 0.3s ease;
}

.notification-enter-from {
  transform: translateX(30px);
  opacity: 0;
}

.notification-leave-to {
  transform: translateX(30px);
  opacity: 0;
}
</style> 