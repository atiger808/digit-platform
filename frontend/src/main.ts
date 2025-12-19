import { createApp } from 'vue'
import Antd, { message } from 'ant-design-vue';
// import * as antIcons from '@ant-design/icons-vue';
// import './style.css'
import App from './App.vue'

import router from './router'
import { createPinia } from "pinia";
import { useTabsStore } from './store/main/tabs/tabs.ts'
import {useLoginStore} from './store/login/login.ts'

// 图标样式（如果使用图标）
import 'element-plus/theme-chalk/dark/css-vars.css' // 可选暗黑主题
import * as ElementPlusIconsVue from '@element-plus/icons-vue'


// 全局配置国际化
import ElementPlus from 'element-plus'
import zhCn from "element-plus/dist/locale/zh-cn.mjs"
// app.use(ElementPlus, {locale: zhCn})

const app =createApp(App)
// 创建Pinia实例
const pinia = createPinia()

// 0.针对ElMessage, ElLoading, ElMessageBox等组件引入样式
// 1.全局引入（所有样式全部引入）
// import 'element-plus/dist/index.css'
//
// 2.ElMessage组件样式引入
import 'element-plus/theme-chalk/el-message.css'
import 'element-plus/theme-chalk/el-loading.css'
//
// 3.ElMessageBox组件样式引入
import 'element-plus/theme-chalk/base.css'; // 基础样式
import 'element-plus/theme-chalk/el-message-box.css'; // MessageBox 样式
import 'element-plus/theme-chalk/el-overlay.css'; // 遮罩层样式

// 3.使用vite-plugin-style-import插件


// 1.全局注册element-plus：方便简洁
// import ElementPlus from 'element-plus'
// import 'element-plus/dist/index.css'
// app.use(ElementPlus)

// 2.按需引入：用到哪一个组件再引入
// import { ElButton  } from "element-plus";
// app.component(ElButton.name, ElButton)



// 3.注册Element Plus图标（可选）
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}
app.use(Antd)
app.use(pinia)
const loginStore = useLoginStore()
loginStore.loadLocalCacheAction()
app.use(router)
app.mount('#app')


router.beforeEach((to) => {
  const tabsStore = useTabsStore()
  tabsStore.addTab(to)
})
