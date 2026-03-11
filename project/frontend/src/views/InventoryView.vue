<script setup>
import { onMounted, reactive, ref } from "vue";

import http, { extractErrorMessage } from "../api/http";
import { useI18n } from "../composables/useI18n.js";

const { t } = useI18n();
const loading = ref(false);
const submitting = ref(false);
const errorText = ref("");
const stocks = ref([]);
const warnings = ref([]);
const records = ref([]);

const actionForm = reactive({
  herb_id: "",
  quantity: "",
  type: "inbound",
  remark: "",
});

const recordFilters = reactive({
  record_type: "",
  herb: "",
});

function listFrom(payload) {
  return Array.isArray(payload) ? payload : payload?.results || [];
}

async function fetchInventory() {
  loading.value = true;
  errorText.value = "";
  try {
    const [stockRes, warningRes] = await Promise.all([
      http.get("/api/inventory/stocks/"),
      http.get("/api/inventory/warnings/?warning_status=active"),
    ]);
    stocks.value = listFrom(stockRes.data);
    warnings.value = listFrom(warningRes.data);
    if (!actionForm.herb_id && stocks.value.length > 0) {
      actionForm.herb_id = String(stocks.value[0].herb);
    }
    if (!recordFilters.herb && stocks.value.length > 0) {
      recordFilters.herb = String(stocks.value[0].herb);
    }
  } catch (error) {
    errorText.value = extractErrorMessage(error, t("inventory.loadFailed"));
  } finally {
    loading.value = false;
  }
}

async function fetchRecords() {
  try {
    const params = new URLSearchParams();
    if (recordFilters.record_type) params.set("record_type", recordFilters.record_type);
    if (recordFilters.herb) params.set("herb", recordFilters.herb);
    const query = params.toString();
    const response = await http.get(`/api/inventory/records/${query ? `?${query}` : ""}`);
    records.value = listFrom(response.data);
  } catch (error) {
    errorText.value = extractErrorMessage(error, t("inventory.loadRecordsFailed"));
  }
}

async function submitAction() {
  submitting.value = true;
  errorText.value = "";
  try {
    let endpoint = "/api/inventory/inbound/";
    let payload = {
      herb_id: actionForm.herb_id,
      quantity: actionForm.quantity,
      remark: actionForm.remark,
    };
    if (actionForm.type === "outbound") {
      endpoint = "/api/inventory/outbound/";
    } else if (actionForm.type === "check") {
      endpoint = "/api/inventory/check/";
      payload = {
        herb_id: actionForm.herb_id,
        checked_quantity: actionForm.quantity,
        remark: actionForm.remark,
      };
    }
    await http.post(endpoint, payload);
    actionForm.quantity = "";
    actionForm.remark = "";
    await Promise.all([fetchInventory(), fetchRecords()]);
  } catch (error) {
    errorText.value = extractErrorMessage(error, t("inventory.actionFailed"));
  } finally {
    submitting.value = false;
  }
}

onMounted(async () => {
  await fetchInventory();
  await fetchRecords();
});
</script>

<template>
  <div class="view-grid">
    <div class="card">
      <div class="toolbar">
        <div>
          <h2>{{ t("inventory.title") }}</h2>
          <p class="muted">{{ t("inventory.desc") }}</p>
        </div>
        <button class="btn btn-muted" @click="fetchInventory" :disabled="loading">
          {{ loading ? t("common.refreshing") : t("common.refresh") }}
        </button>
      </div>
      <p v-if="errorText" class="error-text">{{ errorText }}</p>
      <table class="table">
        <thead>
          <tr>
            <th>{{ t("inventory.herb") }}</th>
            <th>{{ t("inventory.current") }}</th>
            <th>{{ t("inventory.safe") }}</th>
            <th>{{ t("inventory.location") }}</th>
            <th>{{ t("inventory.status") }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in stocks" :key="item.id">
            <td>{{ item.herb_name }} ({{ item.herb_code }})</td>
            <td>{{ item.current_quantity }} {{ item.unit }}</td>
            <td>{{ item.safe_quantity }} {{ item.unit }}</td>
            <td>{{ item.warehouse_location || "-" }}</td>
            <td>{{ item.stock_status }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="card">
      <h2>{{ t("inventory.stockAction") }}</h2>
      <form class="inventory-form" @submit.prevent="submitAction">
        <label>
          <span>{{ t("inventory.actionType") }}</span>
          <select v-model="actionForm.type">
            <option value="inbound">{{ t("inventory.inbound") }}</option>
            <option value="outbound">{{ t("inventory.outbound") }}</option>
            <option value="check">{{ t("inventory.stockCheck") }}</option>
          </select>
        </label>
        <label>
          <span>{{ t("inventory.herb") }}</span>
          <select v-model="actionForm.herb_id">
            <option v-for="item in stocks" :key="item.herb" :value="String(item.herb)">
              {{ item.herb_name }} ({{ item.herb_code }})
            </option>
          </select>
        </label>
        <label>
          <span>{{ actionForm.type === "check" ? t("inventory.checkedQuantity") : t("inventory.quantity") }}</span>
          <input v-model.trim="actionForm.quantity" type="number" min="0.01" step="0.01" required />
        </label>
        <label>
          <span>{{ t("inventory.remark") }}</span>
          <input v-model.trim="actionForm.remark" />
        </label>
        <button class="btn btn-primary" type="submit" :disabled="submitting || !actionForm.herb_id">
          {{ submitting ? t("common.submitting") : t("inventory.submit") }}
        </button>
      </form>

      <h3>{{ t("inventory.activeLowStockWarnings") }}</h3>
      <ul class="warning-list">
        <li v-for="item in warnings" :key="item.id">
          {{ item.herb_name }}: {{ t("inventory.current") }} {{ item.current_quantity }} / {{ t("inventory.safe") }} {{ item.safe_quantity }}
        </li>
        <li v-if="warnings.length === 0" class="no-warning">{{ t("common.noActiveWarnings") }}</li>
      </ul>
    </div>

    <div class="card">
      <div class="toolbar">
        <h2>{{ t("inventory.inventoryRecords") }}</h2>
        <div class="toolbar-right">
          <select v-model="recordFilters.record_type">
            <option value="">{{ t("inventory.allTypes") }}</option>
            <option value="inbound">{{ t("inventory.inbound") }}</option>
            <option value="outbound">{{ t("inventory.outbound") }}</option>
            <option value="check">{{ t("inventory.stockCheck") }}</option>
          </select>
          <select v-model="recordFilters.herb">
            <option value="">{{ t("inventory.allHerbs") }}</option>
            <option v-for="item in stocks" :key="item.herb" :value="String(item.herb)">
              {{ item.herb_name }}
            </option>
          </select>
          <button class="btn btn-muted" @click="fetchRecords">{{ t("inventory.filter") }}</button>
        </div>
      </div>

      <table class="table">
        <thead>
          <tr>
            <th>{{ t("inventory.time") }}</th>
            <th>{{ t("inventory.herb") }}</th>
            <th>{{ t("inventory.type") }}</th>
            <th>{{ t("inventory.before") }}</th>
            <th>{{ t("inventory.after") }}</th>
            <th>{{ t("inventory.operator") }}</th>
            <th>{{ t("inventory.remark") }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in records" :key="item.id">
            <td>{{ (item.created_at || "").replace("T", " ").slice(0, 19) }}</td>
            <td>{{ item.herb_name }}</td>
            <td>{{ item.record_type }}</td>
            <td>{{ item.before_quantity }}</td>
            <td>{{ item.after_quantity }}</td>
            <td>{{ item.operator_name || "-" }}</td>
            <td>{{ item.remark || "-" }}</td>
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

.view-grid .card h3 {
  color: var(--tcm-ink);
  margin-top: 20px;
  margin-bottom: 10px;
}

.view-grid .card .muted {
  color: var(--tcm-subtle);
}

.toolbar {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: end;
  margin-bottom: 12px;
}

.toolbar-right {
  display: flex;
  gap: 8px;
  align-items: center;
}

.table {
  width: 100%;
  border-collapse: collapse;
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
  text-align: left;
}

.table td {
  color: var(--tcm-ink);
  border-bottom: 1px solid var(--tcm-line);
  padding: 12px;
  text-align: left;
}

.table tbody tr:hover {
  background: var(--tcm-paper);
}

.inventory-form {
  display: grid;
  gap: 10px;
  margin-bottom: 14px;
}

.inventory-form label {
  display: grid;
  gap: 8px;
  color: var(--tcm-ink);
}

.inventory-form input,
.inventory-form select {
  width: 100%;
  border: 1px solid var(--tcm-line);
  background: var(--tcm-paper);
  border-radius: 10px;
  padding: 10px 12px;
  font-size: 14px;
  color: var(--tcm-ink);
  transition: all 0.2s ease;
}

.inventory-form input:focus,
.inventory-form select:focus {
  outline: none;
  border-color: var(--tcm-green);
  box-shadow: 0 0 0 2px rgba(74, 124, 89, 0.15);
}

.btn-muted {
  color: var(--tcm-ink);
  background: var(--tcm-paper);
  border: 1px solid var(--tcm-line);
  transition: all 0.2s ease;
  border-radius: 10px;
  padding: 10px 16px;
  font-weight: 700;
  cursor: pointer;
}

.btn-muted:hover:not(:disabled) {
  background: var(--tcm-card);
  border-color: var(--tcm-green);
  color: var(--tcm-green);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(74, 124, 89, 0.2);
}

.btn-muted:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  color: #ffffff;
  background: linear-gradient(90deg, var(--tcm-green), #3a6e4a);
  transition: all 0.2s ease;
  border: 0;
  border-radius: 10px;
  padding: 10px 16px;
  font-weight: 700;
  cursor: pointer;
}

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(90deg, #3a6e4a, var(--tcm-green));
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(74, 124, 89, 0.3);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.warning-list {
  margin: 8px 0 0;
  padding-left: 18px;
  color: var(--tcm-warn);
}

.warning-list li {
  padding: 4px 0;
}

.warning-list .no-warning {
  color: var(--tcm-green);
  font-weight: 600;
  list-style: none;
  padding-left: 0;
  margin-left: -18px;
}

.error-text {
  color: var(--tcm-warn);
  font-size: 14px;
}
</style>
