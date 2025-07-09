<template>
  <div class="reports-container">
    <h1 class="page-title">生成竞赛报告</h1>
    
    <el-card class="report-card">
      <template #header>
        <h2>报告生成器</h2>
      </template>
      
      <el-form :model="form" :rules="rules" label-position="top">
        <!-- 报告标题 -->
        <el-form-item label="报告标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入报告标题"></el-input>
        </el-form-item>

        <!-- 选择竞赛 -->
        <el-form-item label="选择竞赛" prop="competition_ids">
          <el-select v-model="form.competition_ids" multiple filterable placeholder="请选择竞赛" style="width: 100%;">
            <el-option v-for="comp in competitions" :key="comp.id" :label="comp.title" :value="comp.id"></el-option>
          </el-select>
        </el-form-item>

        <!-- 报告格式 -->
        <el-form-item label="报告格式" prop="format">
          <el-radio-group v-model="form.format">
            <el-radio label="PDF">PDF</el-radio>
            <el-radio label="DOCX">Word文档</el-radio>
            <el-radio label="MARKDOWN">Markdown</el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 报告模板 -->
        <el-form-item label="报告模板" prop="template_id">
          <el-select v-model="form.template_id" placeholder="请选择报告模板" style="width: 100%;" :loading="templatesLoading">
            <el-option
              v-for="item in templates"
              :key="item.id"
              :label="item.title"
              :value="item.id"
            />
          </el-select>
        </el-form-item>

        <!-- 包含内容 -->
        <el-form-item label="包含内容" prop="included_sections">
           <el-checkbox-group v-model="form.included_sections">
              <el-checkbox label="basic_info">基本信息</el-checkbox>
              <el-checkbox label="summary">竞赛简介</el-checkbox>
              <el-checkbox label="requirements">参赛要求</el-checkbox>
              <el-checkbox label="schedule">赛程安排</el-checkbox>
              <el-checkbox label="awards">奖项设置</el-checkbox>
            </el-checkbox-group>
        </el-form-item>

        <!-- 操作按钮 -->
        <el-form-item>
          <el-button type="primary" @click="generateReport" :loading="generating">生成报告</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 最近报告列表 -->
    <el-card class="report-card recent-reports">
      <template #header>
        <h2>最近生成的报告</h2>
      </template>
      <el-table :data="reports" v-loading="loading" style="width: 100%">
        <el-table-column prop="title" label="报告标题"></el-table-column>
        <el-table-column prop="created_at" label="生成时间">
          <template #default="scope">
            {{ new Date(scope.row.created_at).toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态"></el-table-column>
        <el-table-column label="操作">
          <template #default="scope">
            <el-button size="small" type="primary" @click="handleDownload(scope.row)">下载</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { ElMessage, ElMessageBox } from 'element-plus'

const store = useStore()

// --- 响应式状态 ---

// 表单数据
const form = reactive({
  title: '',
  competition_ids: [],
  format: 'PDF',
  template_id: '',
  included_sections: ['basic_info', 'summary', 'requirements', 'schedule', 'awards']
})

// 从 Store 获取的数据
const reports = computed(() => store.state.report.reports)
const loading = computed(() => store.state.report.loading)
const competitions = computed(() => store.state.competition.competitions)
const templates = computed(() => store.state.report.templates)

// 本地加载状态
const templatesLoading = ref(false)
const generating = ref(false)

// 表单验证规则
const rules = reactive({
  title: [{ required: true, message: '请输入报告标题', trigger: 'blur' }],
  competition_ids: [{ required: true, message: '请选择至少一个竞赛', trigger: 'change' }],
  template_id: [{ required: true, message: '请选择报告模板', trigger: 'change' }]
})

// --- 函数 ---

/**
 * @todo: 建议将此函数移至Vuex Store或API服务层
 * 这是一个临时的下载文件辅助函数。
 * 它使用fetch API来处理带有认证头的文件下载。
 * @param {string} url - 要下载的文件的URL
 * @param {string} filename - 下载后保存的文件名
 */
const downloadFile = async (url, filename) => {
  try {
    const token = store.state.user.token; // 从store获取认证token
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      // 尝试解析错误信息
      const errorData = await response.json().catch(() => ({ detail: '无法解析错误信息' }));
      throw new Error(`下载失败: ${response.status} ${response.statusText}. ${errorData.detail}`);
    }

    const blob = await response.blob();
    const link = document.createElement('a');
    link.href = window.URL.createObjectURL(blob);
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(link.href);
    ElMessage.success('下载任务已开始！');

  } catch (error) {
    console.error('下载文件时出错:', error);
    ElMessage.error(error.message || '下载文件时出错，请检查控制台。');
  }
};


// 处理下载报告
const handleDownload = async (report) => {
  const downloadUrl = `/api/v1/reports/download/${report.id}`;
  const filename = `report_${report.id}.pdf`; // 您可以根据报告标题生成更友好的文件名
  await downloadFile(downloadUrl, filename);
}

// 初始化数据加载
const loadInitialData = async () => {
  templatesLoading.value = true
  try {
    // 并行加载，提高效率
    await Promise.all([
        store.dispatch('report/fetchTemplates'),
        store.dispatch('report/fetchUserReports', { page: 1, pageSize: 5 }),
        // 确保竞赛列表也被加载
        store.dispatch('competition/fetchCompetitions')
    ]);
  } catch (error) {
    console.error('加载初始数据失败:', error)
    ElMessage.error('加载页面数据失败，请稍后重试。')
  } finally {
    templatesLoading.value = false
  }
}

// 加载模板列表的函数不再需要，已合并到 loadInitialData
// const loadTemplates = async () => { ... }

// 生成报告
const generateReport = async () => {
  generating.value = true
  try {
    const reportData = {
      ...form,
      format: form.format.toLowerCase()
    };
    await store.dispatch('report/generateReport', reportData)
    ElMessage.success('报告已提交生成队列！')
    
    // 成功后可以考虑重置表单
    form.title = ''
    form.competition_ids = []
    form.template_id = ''

  } catch (error) {
    // store的action中已经有通知了，这里可以只log
    console.error('报告生成请求失败:', error)
    ElMessage.error('报告生成请求失败，请查看控制台获取详情。')
  } finally {
    generating.value = false
  }
}

// 删除报告
const handleDelete = async (report) => {
  try {
    // 可以加入一个确认对话框，防止误删
    await ElMessageBox.confirm(
      `确定要删除报告 "${report.title}" 吗？此操作无法撤销。`,
      '警告',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    await store.dispatch('report/deleteReport', report.id)
  } catch (error) {
    if (error !== 'cancel') {
      // 如果不是用户取消操作，则显示错误
      console.error('删除操作失败:', error)
    }
  }
}

// --- 生命周期钩子 ---

onMounted(() => {
  loadInitialData()
})
</script>

<style lang="scss" scoped>
.reports-container {
  padding: 2rem;
  max-width: 900px;
  margin: auto;
}
.page-title {
  font-size: 2rem;
  margin-bottom: 2rem;
}
.report-card {
  margin-top: 2rem;
}
.recent-reports {
  margin-top: 2rem;
}
</style> 