<script setup>
import { computed, onMounted, ref } from "vue";

import http, { extractErrorMessage } from "../api/http";
import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const loading = ref(false);
const errorText = ref("");
const keyword = ref("");
const rows = ref([]);

const canCreate = computed(() => auth.hasPermission("herb.create"));
const canUpdate = computed(() => auth.hasPermission("herb.update"));
const canDelete = computed(() => auth.hasPermission("herb.delete"));

function listFrom(payload) {
  return Array.isArray(payload) ? payload : payload?.results || [];
}

async function fetchHerbs() {
  loading.value = true;
  errorText.value = "";
  try {
    const params = new URLSearchParams();
    if (keyword.value) params.set("search", keyword.value);
    const query = params.toString();
    const response = await http.get(`/api/herbs/${query ? `?${query}` : ""}`);
    rows.value = listFrom(response.data);
  } catch (error) {
    errorText.value = extractErrorMessage(error, "无法加载药材列表。");
  } finally {
    loading.value = false;
  }
}

onMounted(fetchHerbs);
</script>

<template>
  <div class="card">
    <div class="toolbar">
      <div>
        <h2>药材管理</h2>
        <p class="muted">通过 REST API 展示药材资料，支持关键词搜索。</p>
      </div>
      <div class="toolbar-right">
        <input v-model.trim="keyword" placeholder="搜索药材名称/编码" @keyup.enter="fetchHerbs" />
        <button class="btn btn-muted" @click="fetchHerbs" :disabled="loading">
          {{ loading ? "查询中..." : "查询" }}
        </button>
      </div>
    </div>

    <div class="permission-line">
      <span :class="{ ok: canCreate }">新增: {{ canCreate ? "有权限" : "无权限" }}</span>
      <span :class="{ ok: canUpdate }">编辑: {{ canUpdate ? "有权限" : "无权限" }}</span>
      <span :class="{ ok: canDelete }">删除: {{ canDelete ? "有权限" : "无权限" }}</span>
    </div>
    <p v-if="errorText" class="error-text">{{ errorText }}</p>

    <table class="table">
      <thead>
        <tr>
          <th>药材编码</th>
          <th>药材名称</th>
          <th>分类</th>
          <th>性味</th>
          <th>单位</th>
          <th>参考价</th>
          <th>状态</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in rows" :key="item.id">
          <td>{{ item.herb_code }}</td>
          <td>{{ item.herb_name }}</td>
          <td>{{ item.category }}</td>
          <td>{{ item.nature_taste }}</td>
          <td>{{ item.unit }}</td>
          <td>{{ item.reference_price }}</td>
          <td>{{ item.status ? "启用" : "停用" }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
