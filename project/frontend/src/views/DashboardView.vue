<script setup>
import { onMounted, ref } from "vue";

import http, { extractErrorMessage } from "../api/http";
import { useI18n } from "../composables/useI18n.js";

const { t } = useI18n();
const loading = ref(false);
const errorText = ref("");
const stats = ref({
  herbCount: 0,
  formulaCount: 0,
  stockCount: 0,
  warningCount: 0,
});
const records = ref([]);

function totalFrom(payload) {
  return payload?.count ?? (Array.isArray(payload) ? payload.length : 0);
}

function listFrom(payload) {
  return Array.isArray(payload) ? payload : payload?.results || [];
}

async function fetchDashboard() {
  loading.value = true;
  errorText.value = "";
  try {
    const [herbs, formulas, stocks, warnings, recordRows] = await Promise.all([
      http.get("/api/herbs/?page=1"),
      http.get("/api/formulas/?page=1"),
      http.get("/api/inventory/stocks/?page=1"),
      http.get("/api/inventory/warnings/?warning_status=active&page=1"),
      http.get("/api/inventory/records/?page=1"),
    ]);
    stats.value.herbCount = totalFrom(herbs.data);
    stats.value.formulaCount = totalFrom(formulas.data);
    stats.value.stockCount = totalFrom(stocks.data);
    stats.value.warningCount = totalFrom(warnings.data);
    records.value = listFrom(recordRows.data).slice(0, 8);
  } catch (error) {
    errorText.value = extractErrorMessage(error, t("dashboard.loadFailed"));
  } finally {
    loading.value = false;
  }
}

onMounted(fetchDashboard);
</script>

<template>
  <div class="view-grid">
    <div class="card">
      <h2>{{ t("dashboard.overview") }}</h2>
      <p class="muted">{{ t("dashboard.overviewDesc") }}</p>
      <p v-if="errorText" class="error-text">{{ errorText }}</p>
      <div class="kpi-grid">
        <article class="kpi">
          <span>{{ t("dashboard.totalHerbs") }}</span>
          <strong>{{ stats.herbCount }}</strong>
        </article>
        <article class="kpi">
          <span>{{ t("dashboard.totalFormulas") }}</span>
          <strong>{{ stats.formulaCount }}</strong>
        </article>
        <article class="kpi">
          <span>{{ t("dashboard.stockItems") }}</span>
          <strong>{{ stats.stockCount }}</strong>
        </article>
        <article class="kpi warn">
          <span>{{ t("dashboard.activeWarnings") }}</span>
          <strong>{{ stats.warningCount }}</strong>
        </article>
      </div>
      <button class="btn btn-muted" @click="fetchDashboard" :disabled="loading">
        {{ loading ? t("common.refreshing") : t("common.refreshData") }}
      </button>
    </div>

    <div class="card">
      <h2>{{ t("dashboard.recentRecords") }}</h2>
      <table class="table">
        <thead>
          <tr>
            <th>{{ t("dashboard.time") }}</th>
            <th>{{ t("dashboard.herb") }}</th>
            <th>{{ t("dashboard.type") }}</th>
            <th>{{ t("dashboard.qty") }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in records" :key="item.id">
            <td>{{ (item.created_at || "").replace("T", " ").slice(0, 16) }}</td>
            <td>{{ item.herb_name }}</td>
            <td>{{ item.record_type }}</td>
            <td>{{ item.quantity }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.view-grid {
  background: var(--tcm-bg);
  padding: 14px;
  border-radius: 18px;
}

.view-grid .card {
  background: var(--tcm-card);
  border: 1px solid var(--tcm-line);
  border-radius: 18px;
  box-shadow: 0 16px 32px rgba(45, 42, 36, 0.08);
  padding: 24px;
}

.view-grid .card h2 {
  color: var(--tcm-ink);
}

.view-grid .card .muted {
  color: var(--tcm-subtle);
}

.kpi {
  background: var(--tcm-card);
  border: 1px solid var(--tcm-line);
  border-radius: 14px;
  padding: 16px;
  box-shadow: 0 4px 12px rgba(45, 42, 36, 0.05);
  transition: all 0.2s ease;
}

.kpi:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(45, 42, 36, 0.1);
}

.kpi span {
  color: var(--tcm-subtle);
  font-size: 14px;
  font-weight: 500;
}

.kpi strong {
  color: var(--tcm-green);
  font-size: 32px;
  font-weight: 800;
  font-family: "ZCOOL XiaoWei", "LXGW WenKai", "Noto Serif SC", serif;
}

.kpi.warn {
  background: linear-gradient(135deg, #fff8f8 0%, #fffdfd 100%);
  border-color: #e8c0c0;
}

.kpi.warn span {
  color: var(--tcm-subtle);
}

.kpi.warn strong {
  color: var(--tcm-warn);
}

.table {
  background: var(--tcm-card);
  border-radius: 12px;
  overflow: hidden;
}

.table thead {
  background: linear-gradient(135deg, var(--tcm-paper) 0%, var(--tcm-card) 100%);
}

.table th {
  color: var(--tcm-ink);
  font-weight: 600;
  border-bottom: 2px solid var(--tcm-line);
  padding: 14px 12px;
}

.table td {
  color: var(--tcm-ink);
  border-bottom: 1px solid var(--tcm-line);
  padding: 12px;
}

.table tbody tr:hover {
  background: var(--tcm-paper);
}

.btn-muted {
  color: var(--tcm-ink);
  background: var(--tcm-paper);
  border: 1px solid var(--tcm-line);
  transition: all 0.2s ease;
}

.btn-muted:hover:not(:disabled) {
  background: var(--tcm-card);
  border-color: var(--tcm-green);
  color: var(--tcm-green);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(74, 124, 89, 0.2);
}
</style>
