<script setup>
import { computed, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import { useAuthStore } from "../stores/auth";
import { useI18n } from "../composables/useI18n.js";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();
const { t, changeLocale, locale } = useI18n();

const sidebarCollapsed = ref(false);
const menuItems = computed(() => auth.menu);

function isActive(path) {
  return route.path.startsWith(path);
}

function go(path) {
  router.push(path);
}

async function logout() {
  await auth.logoutRemote();
  router.push({ name: "login" });
}

function getMenuIcon(label) {
  const iconMap = {
    "dashboard": "📊",
    "users": "👥",
    "herbs": "🌿",
    "formulas": "📜",
    "inventory": "📦",
    "settings": "⚙️"
  };
  return iconMap[label] || "📋";
}
</script>

<template>
  <div class="shell">
    <aside class="sidebar card" :class="{ collapsed: sidebarCollapsed }">
      <div class="brand">
        <div class="brand-mark">TCM</div>
        <div v-if="!sidebarCollapsed">
          <div class="brand-title">{{ t("app.brandTitle") }}</div>
          <div class="brand-sub">{{ t("app.brandSub") }}</div>
        </div>
      </div>

      <nav class="menu">
        <button
          v-for="item in menuItems"
          :key="item.permission_code"
          class="menu-item"
          :class="{ active: isActive(item.path) }"
          @click="go(item.path)"
        >
          <span class="menu-icon">{{ getMenuIcon(item.label) }}</span>
          <span v-if="!sidebarCollapsed">{{ t(`menu.${item.label}`) }}</span>
        </button>
      </nav>

      <div class="user-box" v-if="!sidebarCollapsed">
        <div class="user-name">{{ auth.user?.real_name || auth.user?.username }}</div>
        <div class="user-role">{{ auth.user?.role_name || t("common.noRole") }}</div>
        <button class="btn btn-muted" @click="logout">{{ t("common.logout") }}</button>
      </div>
      <div class="user-box-mini" v-else>
        <div class="user-avatar">{{ auth.user?.real_name?.[0] || auth.user?.username?.[0] || '管' }}</div>
      </div>
    </aside>

    <main class="main">
      <header class="topbar">
        <div class="topbar-left">
          <button class="toggle-sidebar-btn" @click="sidebarCollapsed = !sidebarCollapsed">
            <span class="toggle-icon">{{ sidebarCollapsed ? '☰' : '✕' }}</span>
          </button>
          <div>
            <div class="topbar-title">{{ t(`route.${route.name}`) }}</div>
            <div class="topbar-tip">{{ t("common.permissions") }}: {{ auth.permissions.length }}</div>
          </div>
        </div>
        <div class="topbar-right">
          <div class="lang-switcher-mini">
            <select :value="locale" @change="changeLocale($event.target.value)">
              <option value="zh-CN">中文</option>
              <option value="en-US">EN</option>
            </select>
          </div>
        </div>
      </header>
      <section class="content">
        <RouterView />
      </section>
    </main>
  </div>
</template>
