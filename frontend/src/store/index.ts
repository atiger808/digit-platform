import { defineStore } from 'pinia'

interface Tab {
  name: string;
  path: string;
  title: string;
}

export const useTabStore = defineStore('tabs', {
  state: () => ({
    tabs: [] as Tab[],
    activeTab: '' as string,
  }),
  actions: {
    addTab(tab: Tab) {
      if (!this.tabs.some((t) => t.path === tab.path)) {
        this.tabs.push(tab);
      }
      this.activeTab = tab.path;
    },
    removeTab(path: string) {
      const index = this.tabs.findIndex((tab) => tab.path === path);
      if (index !== -1) {
        this.tabs.splice(index, 1);
        if (this.activeTab === path) {
          this.activeTab = this.tabs.length > 0 ? this.tabs[this.tabs.length - 1].path : '';
        }
      }
    },
  },
});

