<script setup>
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";

import { useAuthStore } from "../stores/auth";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();

const menuItems = computed(() => auth.menu);

function isActive(path) {
  return route.path.startsWith(path);
}

function go(path) {
  router.push(path);
}

function logout() {
  auth.logout();
  router.push({ name: "login" });
}
</script>

<template>
  <div class="shell">
    <aside class="sidebar card">
      <div class="brand">
        <div class="brand-mark">TCM</div>
        <div>
          <div class="brand-title">中医药管理系统</div>
          <div class="brand-sub">Vue3 + Django</div>
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
          {{ item.label }}
        </button>
      </nav>
      <div class="user-box">
        <div class="user-name">{{ auth.user?.real_name || auth.user?.username }}</div>
        <div class="user-role">{{ auth.user?.role_name || "未分配角色" }}</div>
        <button class="btn btn-muted" @click="logout">退出登录</button>
      </div>
    </aside>

    <main class="main">
      <header class="topbar card">
        <div class="topbar-title">{{ route.name }}</div>
        <div class="topbar-tip">当前账号权限数量：{{ auth.permissions.length }}</div>
      </header>
      <section class="content">
        <RouterView />
      </section>
    </main>
  </div>
</template>
