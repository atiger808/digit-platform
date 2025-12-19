# Vue 3 + TypeScript + Vite

This template should help get you started developing with Vue 3 and TypeScript in Vite. The template uses Vue 3 `<script setup>` SFCs, check out the [script setup docs](https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup) to learn more.

Learn more about the recommended Project Setup and IDE Support in the [Vue Docs TypeScript Guide](https://vuejs.org/guide/typescript/overview.html#project-setup).





要实现一个基于 Vue3、Element Plus 和 TypeScript 的企业级管理后台，我们可以按照以下步骤进行。这个项目将包含通用的后台管理页面布局（左侧树形菜单 + 多页签导航），并提供项目的启动命令。

------

### 项目创建

```
npm init vite
Project name (输入项目名称):
vue3-company
Select a framework (选择框架):
Vue
Select a variant （选择语言）:
TypeScript
```



### 安装依赖并启动项目

```
cd vue3-warehouse
npm install
npm run dev
```







### **1. 项目初始化**

首先，使用 `Vite` 创建一个 Vue3 + TypeScript 项目：



```
npm create vite@latest vue3-element-plus-admin --template vue-ts

cd vue3-element-plus-admin
```



安装依赖：



```
npm install
```

安装 `Element Plus` 和其他必要的依赖：



```
npm install element-plus axios vue-router@4 pinia

npm install -D unplugin-vue-components unplugin-auto-import
```



------

### **2. 配置 Element Plus**

在 `vite.config.ts` 中配置 `unplugin-vue-components` 和 `unplugin-auto-import` 自动导入 Element Plus 组件和 API：

typescript

```
import { defineConfig } from 'vite';

import vue from '@vitejs/plugin-vue';

import AutoImport from 'unplugin-auto-import/vite';

import Components from 'unplugin-vue-components/vite';

import { ElementPlusResolver } from 'unplugin-vue-components/resolvers';

export default defineConfig({

  plugins: [

​    vue(),

​    AutoImport({

​      resolvers: [ElementPlusResolver()],

​    }),

​    Components({

​      resolvers: [ElementPlusResolver()],

​    }),

  ],

});
```



在 `main.ts` 中引入 Element Plus 和样式：

typescript



```
import { createApp } from 'vue';

import App from './App.vue';

import ElementPlus from 'element-plus';

import 'element-plus/dist/index.css';

import router from './router';

import pinia from './store';

const app = createApp(App);

app.use(ElementPlus);

app.use(router);

app.use(pinia);

app.mount('#app');
```



------

### **3. 路由配置**

创建 `src/router/index.ts` 文件，定义路由：

typescript

```
import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router';

const routes: Array<RouteRecordRaw> = [

  {

​    path: '/',

​    redirect: '/dashboard',

  },

  {

​    path: '/dashboard',

​    name: 'Dashboard',

​    component: () => import('@/views/Dashboard.vue'),

​    meta: { title: '仪表盘' },

  },

  {

​    path: '/about',

​    name: 'About',

​    component: () => import('@/views/About.vue'),

​    meta: { title: '关于' },

  },

];

const router = createRouter({

  history: createWebHistory(),

  routes,

});

export default router;
```



------

### **4. 状态管理 (Pinia)**

创建 `src/store/index.ts` 文件，用于管理多页签状态：

typescript

```
import { defineStore } from 'pinia';

interface Tab {

  name: string;

  path: string;

  title: string;

}

export const useTabStore = defineStore('tabs', {

  state: () => ({

​    tabs: [] as Tab[],

​    activeTab: '' as string,

  }),

  actions: {

​    addTab(tab: Tab) {

​      if (!this.tabs.some((t) => t.path === tab.path)) {

​        this.tabs.push(tab);

​      }

​      this.activeTab = tab.path;

​    },

​    removeTab(path: string) {

​      const index = this.tabs.findIndex((tab) => tab.path === path);

​      if (index !== -1) {

​        this.tabs.splice(index, 1);

​        if (this.activeTab === path) {

​          this.activeTab = this.tabs.length > 0 ? this.tabs[this.tabs.length - 1].path : '';

​        }

​      }

​    },

  },

});
```



------

### **5. 页面布局**

创建 `src/layout/index.vue` 文件，定义通用布局：

vue

```


<template>


  <el-container style="height: 100vh;">

​    <el-aside width="200px">

​      <el-menu

​        :default-active="activeMenu"

​        router

​        @select="handleMenuSelect"

​      \>

​        <el-submenu index="1">

​          <template #title>导航一</template>

​          <el-menu-item index="/dashboard">仪表盘</el-menu-item>

​          <el-menu-item index="/about">关于</el-menu-item>

​        </el-submenu>

​      </el-menu>

​    </el-aside>

​    <el-container>

​      <el-header>

​        <el-tabs v-model="activeTab" type="card" closable @tab-remove="removeTab">

​          <el-tab-pane

​            v-for="tab in tabs"

​            :key="tab.path"

​            :label="tab.title"

​            :name="tab.path"

​          />

​        </el-tabs>

​      </el-header>

​      <el-main>

​        <router-view />

​      </el-main>

​    </el-container>

  </el-container>

</template>

<script setup lang="ts">


import { ref, watch } from 'vue';

import { useRoute, useRouter } from 'vue-router';

import { useTabStore } from '@/store';

const route = useRoute();

const router = useRouter();

const tabStore = useTabStore();

const activeTab = ref(tabStore.activeTab);

const tabs = ref(tabStore.tabs);

// 监听路由变化

watch(

  () => route.path,

  (newPath) => {

​    const matched = route.matched[0];

​    if (matched) {

​      const tab = {

​        name: matched.name as string,

​        path: newPath,

​        title: matched.meta.title as string,

​      };

​      tabStore.addTab(tab);

​      activeTab.value = newPath;

​    }

  },

  { immediate: true }

);

// 移除页签

const removeTab = (path: string) => {

  tabStore.removeTab(path);

  if (path === activeTab.value && tabs.value.length > 0) {

​    router.push(tabs.value[tabs.value.length - 1].path);

  }

};

// 菜单选中事件

const handleMenuSelect = (path: string) => {

  router.push(path);

};

</script>
```



------

### **6. 示例页面**

创建 `src/views/Dashboard.vue` 和 `src/views/About.vue`：

**Dashboard.vue**

vue

```


<template>


  <div>这是仪表盘页面</div>

</template>
```

**About.vue**

vue

```


<template>


  <div>这是关于页面</div>

</template>
```



------

### **7. 启动命令**

确保所有依赖已安装后，运行以下命令启动项目：

bash

```
npm run dev
```



------

### **8. 总结**

以上代码实现了一个基本的企业级管理后台，包含以下功能：

1. 左侧树形菜单。
2. 多页签导航。
3. 基于 Vue3、Element Plus 和 TypeScript 的开发环境。

你可以根据实际需求扩展功能，例如添加权限控制、动态路由加载等。





### 9.国际化

```
<script setup lang="ts">
// 国际化配置
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
</script>

<template>
  <div class="app">
    <el-config-provider :locale="zhCn">
      <router-view />
    </el-config-provider>
  </div>
</template>
```

##### 针对ElMessage, ElLoading, ElMessageBox等组件引入样式

```
// 0.针对ElMessage, ElLoading, ElMessageBox等组件引入样式
// 1.全局引入（所有样式全部引入）
// import 'element-plus/dist/index.css'

// 2.ElMessage组件样式引入
import 'element-plus/theme-chalk/el-message.css'
import 'element-plus/theme-chalk/el-loading.css'

// 3.ElMessageBox组件样式引入
import 'element-plus/theme-chalk/base.css'; // 基础样式
import 'element-plus/theme-chalk/el-message-box.css'; // MessageBox 样式
import 'element-plus/theme-chalk/el-overlay.css'; // 遮罩层样式
```



##### nextTick 更新dom

```
const treeRef = ref<InstanceType<typeof ElTree>>()
function editCallback(itemData: any) {
  console.log('点击了编辑：', itemData)
  nextTick(() => {
    const menuIds = mapMenuListToIds(itemData.menus)
    console.log('menuIds: ', menuIds)
    treeRef.value?.setCheckedKeys(menuIds)
  })
}
```

