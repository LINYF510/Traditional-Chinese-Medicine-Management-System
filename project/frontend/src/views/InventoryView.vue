<script setup>
import { onMounted, reactive, ref } from "vue";

import http, { extractErrorMessage } from "../api/http";

const loading = ref(false);
const submitting = ref(false);
const errorText = ref("");
const stocks = ref([]);
const warnings = ref([]);

const actionForm = reactive({
  herb_id: "",
  quantity: "",
  type: "inbound",
  remark: "",
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
  } catch (error) {
    errorText.value = extractErrorMessage(error, "无法加载库存数据。");
  } finally {
    loading.value = false;
  }
}

async function submitAction() {
  submitting.value = true;
  errorText.value = "";
  try {
    const endpoint =
      actionForm.type === "inbound" ? "/api/inventory/inbound/" : "/api/inventory/outbound/";
    await http.post(endpoint, {
      herb_id: actionForm.herb_id,
      quantity: actionForm.quantity,
      remark: actionForm.remark,
    });
    actionForm.quantity = "";
    actionForm.remark = "";
    await fetchInventory();
  } catch (error) {
    errorText.value = extractErrorMessage(error, "库存操作失败。");
  } finally {
    submitting.value = false;
  }
}

onMounted(fetchInventory);
</script>

<template>
  <div class="view-grid">
    <div class="card">
      <div class="toolbar">
        <div>
          <h2>库存管理</h2>
          <p class="muted">维护当前库存、低库存预警与流水操作。</p>
        </div>
        <button class="btn btn-muted" @click="fetchInventory" :disabled="loading">
          {{ loading ? "刷新中..." : "刷新" }}
        </button>
      </div>
      <p v-if="errorText" class="error-text">{{ errorText }}</p>
      <table class="table">
        <thead>
          <tr>
            <th>药材</th>
            <th>当前库存</th>
            <th>安全库存</th>
            <th>仓位</th>
            <th>状态</th>
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
      <h2>快捷入库/出库</h2>
      <form class="inventory-form" @submit.prevent="submitAction">
        <label>
          <span>类型</span>
          <select v-model="actionForm.type">
            <option value="inbound">入库</option>
            <option value="outbound">出库</option>
          </select>
        </label>
        <label>
          <span>药材</span>
          <select v-model="actionForm.herb_id">
            <option v-for="item in stocks" :key="item.herb" :value="String(item.herb)">
              {{ item.herb_name }} ({{ item.herb_code }})
            </option>
          </select>
        </label>
        <label>
          <span>数量</span>
          <input v-model.trim="actionForm.quantity" type="number" min="0.01" step="0.01" required />
        </label>
        <label>
          <span>备注</span>
          <input v-model.trim="actionForm.remark" />
        </label>
        <button class="btn btn-primary" type="submit" :disabled="submitting || !actionForm.herb_id">
          {{ submitting ? "提交中..." : "提交操作" }}
        </button>
      </form>

      <h3>低库存预警</h3>
      <ul class="warning-list">
        <li v-for="item in warnings" :key="item.id">
          {{ item.herb_name }}: 当前 {{ item.current_quantity }} / 安全 {{ item.safe_quantity }}
        </li>
        <li v-if="warnings.length === 0">暂无低库存预警</li>
      </ul>
    </div>
  </div>
</template>
