<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";

import { extractErrorMessage } from "../api/http";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const auth = useAuthStore();
const loading = ref(false);
const errorText = ref("");

const form = reactive({
  username: "admin",
  password: "admin123456",
});

async function onSubmit() {
  loading.value = true;
  errorText.value = "";
  try {
    await auth.login(form.username, form.password);
    router.push({ name: "dashboard" });
  } catch (error) {
    errorText.value = extractErrorMessage(error, "登录失败，请检查账号密码。");
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-card card">
      <div class="login-header">
        <h1>中医药管理系统</h1>
        <p>使用 JWT 登录，按角色加载菜单与权限。</p>
      </div>
      <form @submit.prevent="onSubmit" class="login-form">
        <label>
          <span>用户名</span>
          <input v-model.trim="form.username" autocomplete="username" />
        </label>
        <label>
          <span>密码</span>
          <input v-model="form.password" type="password" autocomplete="current-password" />
        </label>
        <p v-if="errorText" class="error-text">{{ errorText }}</p>
        <button class="btn btn-primary" type="submit" :disabled="loading">
          {{ loading ? "登录中..." : "登录系统" }}
        </button>
      </form>
    </div>
  </div>
</template>
