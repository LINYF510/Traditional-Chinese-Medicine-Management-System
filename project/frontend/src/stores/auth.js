import { computed, ref } from "vue";
import { defineStore } from "pinia";

import http, { ACCESS_TOKEN_KEY, REFRESH_TOKEN_KEY, extractErrorMessage } from "../api/http";

export const useAuthStore = defineStore("auth", () => {
  const accessToken = ref(localStorage.getItem(ACCESS_TOKEN_KEY) || "");
  const refreshToken = ref(localStorage.getItem(REFRESH_TOKEN_KEY) || "");
  const user = ref(null);
  const permissions = ref([]);
  const menu = ref([]);

  const isAuthenticated = computed(() => Boolean(accessToken.value));

  function setTokens(access, refresh) {
    accessToken.value = access || "";
    refreshToken.value = refresh || "";
    if (access) {
      localStorage.setItem(ACCESS_TOKEN_KEY, access);
    } else {
      localStorage.removeItem(ACCESS_TOKEN_KEY);
    }
    if (refresh) {
      localStorage.setItem(REFRESH_TOKEN_KEY, refresh);
    } else {
      localStorage.removeItem(REFRESH_TOKEN_KEY);
    }
  }

  async function login(username, password) {
    const response = await http.post("/api/auth/login/", { username, password });
    setTokens(response.data.access, response.data.refresh);
    await fetchAccess();
  }

  async function fetchAccess() {
    if (!isAuthenticated.value) return;
    const response = await http.get("/api/auth/access/");
    user.value = response.data.user;
    permissions.value = response.data.permissions || [];
    menu.value = response.data.menu || [];
  }

  function hasPermission(permissionCode) {
    if (!permissionCode) return true;
    return permissions.value.includes(permissionCode);
  }

  function logout() {
    setTokens("", "");
    user.value = null;
    permissions.value = [];
    menu.value = [];
  }

  async function safeBootstrap() {
    if (!isAuthenticated.value) return;
    try {
      await fetchAccess();
    } catch (error) {
      const message = extractErrorMessage(error, "登录信息已过期，请重新登录。");
      logout();
      throw new Error(message);
    }
  }

  return {
    accessToken,
    refreshToken,
    user,
    permissions,
    menu,
    isAuthenticated,
    login,
    logout,
    hasPermission,
    safeBootstrap,
  };
});
