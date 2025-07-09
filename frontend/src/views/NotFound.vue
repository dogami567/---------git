<template>
  <div class="not-found">
    <div class="container">
      <div class="not-found-content">
        <h1>404</h1>
        <h2>页面未找到</h2>
        <p>抱歉，您访问的页面不存在或已被移除。</p>
        <el-button type="primary" @click="$router.push('/')">返回首页</el-button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NotFound'
}
</script>

<style lang="scss" scoped>
.not-found {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  text-align: center;
  
  .not-found-content {
    h1 {
      font-size: 8rem;
      font-weight: bold;
      color: #409EFF;
      margin: 0;
      line-height: 1;
    }
    
    h2 {
      font-size: 2rem;
      margin: 20px 0;
    }
    
    p {
      font-size: 1.2rem;
      color: #606266;
      margin-bottom: 30px;
    }
  }
}
</style> 