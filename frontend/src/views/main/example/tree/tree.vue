<template>
  <div class="tree-container">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>树形控件示例</span>
          <div>
            <el-button type="primary" size="small" @click="handleAdd">
              <el-icon><Plus /></el-icon>
              新增
            </el-button>
          </div>
        </div>
      </template>

      <el-row :gutter="20">
        <el-col :span="8">
          <el-tree
            :data="treeData"
            node-key="id"
            default-expand-all
            :expand-on-click-node="false"
            @node-click="handleNodeClick"
          >
            <template #default="{ node, data }">
              <span class="custom-tree-node">
                <span>{{ node.label }}</span>
                <span>
                  <el-button
                    type="text"
                    size="small"
                    @click.stop="handleAppend(data)"
                  >
                    添加
                  </el-button>
                  <el-button
                    type="text"
                    size="small"
                    @click.stop="handleRemove(node, data)"
                  >
                    删除
                  </el-button>
                </span>
              </span>
            </template>
          </el-tree>
        </el-col>
        <el-col :span="16">
          <el-card shadow="never">
            <template #header>
              <span>节点详情</span>
            </template>
            <div v-if="currentNode">
              <el-form label-width="80px">
                <el-form-item label="节点ID">
                  <el-input v-model="currentNode.id" disabled />
                </el-form-item>
                <el-form-item label="节点名称">
                  <el-input v-model="currentNode.label" />
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="handleSave">保存</el-button>
                </el-form-item>
              </el-form>
            </div>
            <div v-else class="empty-tip">
              请点击左侧树节点
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script lang="ts" setup>
import { ref } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import type Node from 'element-plus/es/components/tree/src/model/node'

interface TreeNode {
  id: number
  label: string
  children?: TreeNode[]
}

const treeData = ref<TreeNode[]>([
  {
    id: 1,
    label: '一级 1',
    children: [
      {
        id: 4,
        label: '二级 1-1',
        children: [
          {
            id: 9,
            label: '三级 1-1-1'
          },
          {
            id: 10,
            label: '三级 1-1-2'
          }
        ]
      }
    ]
  },
  {
    id: 2,
    label: '一级 2',
    children: [
      {
        id: 5,
        label: '二级 2-1'
      },
      {
        id: 6,
        label: '二级 2-2'
      }
    ]
  },
  {
    id: 3,
    label: '一级 3',
    children: [
      {
        id: 7,
        label: '二级 3-1'
      },
      {
        id: 8,
        label: '二级 3-2'
      }
    ]
  }
])

const currentNode = ref<TreeNode | null>(null)
let id = 100

const handleNodeClick = (data: TreeNode) => {
  currentNode.value = data
}

const handleAdd = () => {
  const newChild = { id: id++, label: '新节点' }
  treeData.value.push(newChild)
}

const handleAppend = (data: TreeNode) => {
  const newChild = { id: id++, label: '新子节点' }
  if (!data.children) {
    data.children = []
  }
  data.children.push(newChild)
  treeData.value = [...treeData.value]
}

const handleRemove = (node: Node, data: TreeNode) => {
  const parent = node.parent
  const children = parent?.data?.children || treeData.value
  const index = children.findIndex((d: TreeNode) => d.id === data.id)
  children.splice(index, 1)
}

const handleSave = () => {
  console.log('保存节点:', currentNode.value)
}
</script>

<style lang="scss" scoped>
.tree-container {
  padding: 20px;

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .custom-tree-node {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 14px;
    padding-right: 8px;
  }

  .empty-tip {
    text-align: center;
    color: #909399;
    padding: 20px 0;
  }
}
</style>