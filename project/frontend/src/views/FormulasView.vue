<script setup>
import { onMounted, ref } from "vue";

import http, { extractErrorMessage } from "../api/http";

const loading = ref(false);
const errorText = ref("");
const rows = ref([]);

function listFrom(payload) {
  return Array.isArray(payload) ? payload : payload?.results || [];
}

async function fetchFormulas() {
  loading.value = true;
  errorText.value = "";
  try {
    const response = await http.get("/api/formulas/");
    rows.value = listFrom(response.data);
  } catch (error) {
    errorText.value = extractErrorMessage(error, "无法加载方剂列表。");
  } finally {
    loading.value = false;
  }
}

onMounted(fetchFormulas);
</script>

<template>
  <div class="card">
    <div class="toolbar">
      <div>
        <h2>方剂数据库</h2>
        <p class="muted">方剂基础信息与组成药材明细。</p>
      </div>
      <button class="btn btn-muted" @click="fetchFormulas" :disabled="loading">
        {{ loading ? "刷新中..." : "刷新" }}
      </button>
    </div>
    <p v-if="errorText" class="error-text">{{ errorText }}</p>

    <div class="formula-list">
      <article v-for="item in rows" :key="item.id" class="formula-card">
        <h3>{{ item.formula_name }} <small>{{ item.formula_code }}</small></h3>
        <p><strong>来源:</strong> {{ item.source || "-" }}</p>
        <p><strong>功效:</strong> {{ item.efficacy || "-" }}</p>
        <p><strong>主治:</strong> {{ item.indication || "-" }}</p>
        <p><strong>组成:</strong> {{ (item.items_detail || []).map((x) => `${x.herb_name} ${x.dosage}${x.dosage_unit}`).join("、") || "-" }}</p>
      </article>
    </div>
  </div>
</template>
