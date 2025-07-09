<template>
  <footer class="app-footer">
    <div class="container">
      <div class="footer-content">
        <div class="footer-section">
          <h3>大学生竞赛平台</h3>
          <p>为大学生提供全面的竞赛信息聚合与订阅服务</p>
        </div>
        
        <div class="footer-section">
          <h3>快速链接</h3>
          <ul>
            <li><router-link to="/">首页</router-link></li>
            <li><router-link to="/competitions">竞赛信息</router-link></li>
            <li><router-link to="/about">关于我们</router-link></li>
          </ul>
        </div>
        
        <div class="footer-section">
          <h3>联系我们</h3>
          <p>邮箱: contact@competition-platform.com</p>
          <p>电话: 123-456-7890</p>
        </div>
      </div>
      
      <div class="footer-bottom">
        <p>&copy; {{ currentYear }} 大学生竞赛信息聚合与订阅平台 版权所有</p>
      </div>
    </div>
  </footer>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'AppFooter',
  setup() {
    const currentYear = computed(() => new Date().getFullYear())
    
    return {
      currentYear
    }
  }
}
</script>

<style lang="scss" scoped>
.app-footer {
  background-color: #f5f7fa;
  padding: 40px 0 20px;
  margin-top: 40px;
  
  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
  }
  
  .footer-content {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    margin-bottom: 30px;
    
    @media (max-width: 768px) {
      flex-direction: column;
    }
  }
  
  .footer-section {
    flex: 1;
    min-width: 200px;
    margin-bottom: 20px;
    
    h3 {
      font-size: 1.2rem;
      margin-bottom: 15px;
      color: #303133;
    }
    
    ul {
      list-style: none;
      padding: 0;
      margin: 0;
      
      li {
        margin-bottom: 8px;
        
        a {
          color: #606266;
          text-decoration: none;
          
          &:hover {
            color: #409EFF;
          }
        }
      }
    }
    
    p {
      color: #606266;
      margin: 8px 0;
    }
  }
  
  .footer-bottom {
    border-top: 1px solid #dcdfe6;
    padding-top: 20px;
    text-align: center;
    
    p {
      color: #909399;
      font-size: 0.9rem;
      margin: 0;
    }
  }
}
</style> 