<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";

import { extractErrorMessage } from "../api/http";
import { useAuthStore } from "../stores/auth";
import { useI18n } from "../composables/useI18n.js";

const router = useRouter();
const auth = useAuthStore();
const { t, changeLocale, locale } = useI18n();
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
    errorText.value = extractErrorMessage(error, t("login.loginFailed"));
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-card card">
      <div class="login-header">
        <h1>{{ t("login.title") }}</h1>
      </div>
      <form @submit.prevent="onSubmit" class="login-form">
        <label>
          <span>{{ t("login.username") }}</span>
          <input v-model.trim="form.username" autocomplete="username" />
        </label>
        <label>
          <span>{{ t("login.password") }}</span>
          <input v-model="form.password" type="password" autocomplete="current-password" />
        </label>
        <p v-if="errorText" class="error-text">{{ errorText }}</p>
        <button class="btn btn-primary" type="submit" :disabled="loading">
          {{ loading ? t("common.signingIn") : t("common.signIn") }}
        </button>
      </form>
      <div class="login-lang-switcher-mini">
        <select :value="locale" @change="changeLocale($event.target.value)">
          <option value="zh-CN">中文</option>
          <option value="en-US">EN</option>
        </select>
      </div>
    </div>
  </div>
</template>
