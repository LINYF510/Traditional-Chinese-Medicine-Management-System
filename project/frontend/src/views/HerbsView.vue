<script setup>
import { computed, onMounted, reactive, ref } from "vue";

import http, { extractErrorMessage } from "../api/http";
import { useAuthStore } from "../stores/auth";
import { useI18n } from "../composables/useI18n.js";

const auth = useAuthStore();
const { t } = useI18n();
const loading = ref(false);
const submitting = ref(false);
const errorText = ref("");
const keyword = ref("");
const rows = ref([]);
const editingId = ref(null);

const canCreate = computed(() => auth.hasPermission("herb.create"));
const canUpdate = computed(() => auth.hasPermission("herb.update"));
const canDelete = computed(() => auth.hasPermission("herb.delete"));

const form = reactive({
  herb_code: "",
  herb_name: "",
  category: "",
  nature_taste: "",
  meridian_tropism: "",
  efficacy: "",
  indication: "",
  unit: "g",
  reference_price: "0.00",
  status: "enabled",
});

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
    errorText.value = extractErrorMessage(error, t("herbs.loadFailed"));
  } finally {
    loading.value = false;
  }
}

function resetForm() {
  editingId.value = null;
  form.herb_code = "";
  form.herb_name = "";
  form.category = "";
  form.nature_taste = "";
  form.meridian_tropism = "";
  form.efficacy = "";
  form.indication = "";
  form.unit = "g";
  form.reference_price = "0.00";
  form.status = "enabled";
}

function startEdit(row) {
  editingId.value = row.id;
  form.herb_code = row.herb_code;
  form.herb_name = row.herb_name;
  form.category = row.category || "";
  form.nature_taste = row.nature_taste || "";
  form.meridian_tropism = row.meridian_tropism || "";
  form.efficacy = row.efficacy || "";
  form.indication = row.indication || "";
  form.unit = row.unit || "g";
  form.reference_price = String(row.reference_price ?? "0.00");
  form.status = row.status || "enabled";
}

async function submitForm() {
  submitting.value = true;
  errorText.value = "";
  try {
    const payload = {
      herb_code: form.herb_code,
      herb_name: form.herb_name,
      category: form.category,
      nature_taste: form.nature_taste,
      meridian_tropism: form.meridian_tropism,
      efficacy: form.efficacy,
      indication: form.indication,
      unit: form.unit,
      reference_price: form.reference_price,
      status: form.status,
    };
    if (editingId.value) {
      if (!canUpdate.value) throw new Error(t("herbs.noPermissionUpdate"));
      await http.put(`/api/herbs/${editingId.value}/`, payload);
    } else {
      if (!canCreate.value) throw new Error(t("herbs.noPermissionCreate"));
      await http.post("/api/herbs/", payload);
    }
    resetForm();
    await fetchHerbs();
  } catch (error) {
    errorText.value = extractErrorMessage(error, t("herbs.operationFailed"));
  } finally {
    submitting.value = false;
  }
}

async function removeHerb(row) {
  if (!canDelete.value) return;
  if (!window.confirm(t("herbs.deleteConfirm", { name: row.herb_name }))) return;
  try {
    await http.delete(`/api/herbs/${row.id}/`);
    await fetchHerbs();
  } catch (error) {
    errorText.value = extractErrorMessage(error, t("herbs.deleteFailed"));
  }
}

onMounted(fetchHerbs);
</script>

<template>
  <div class="view-grid">
    <div class="tcm-card">
      <div class="toolbar">
        <div>
          <h2 class="tcm-title">{{ t("herbs.title") }}</h2>
          <p class="tcm-subtitle">{{ t("herbs.desc") }}</p>
        </div>
        <div class="toolbar-right">
          <input class="tcm-input" v-model.trim="keyword" :placeholder="t('herbs.searchPlaceholder')" @keyup.enter="fetchHerbs" />
          <button class="tcm-btn tcm-btn-secondary" @click="fetchHerbs" :disabled="loading">
            {{ loading ? t("common.searching") : t("common.search") }}
          </button>
        </div>
      </div>

      <p v-if="errorText" class="tcm-error">{{ errorText }}</p>
      <div class="tcm-table-wrapper">
        <table class="tcm-table">
          <thead>
            <tr>
              <th>{{ t("herbs.code") }}</th>
              <th>{{ t("herbs.name") }}</th>
              <th>{{ t("herbs.category") }}</th>
              <th>{{ t("herbs.natureTaste") }}</th>
              <th>{{ t("herbs.unit") }}</th>
              <th>{{ t("herbs.refPrice") }}</th>
              <th>{{ t("herbs.status") }}</th>
              <th>{{ t("common.actions") }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in rows" :key="item.id">
              <td>{{ item.herb_code }}</td>
              <td>{{ item.herb_name }}</td>
              <td>{{ item.category }}</td>
              <td>{{ item.nature_taste || "-" }}</td>
              <td>{{ item.unit }}</td>
              <td>{{ item.reference_price }}</td>
              <td>
                <span :class="item.status === 'enabled' ? 'tcm-status-enabled' : 'tcm-status-disabled'">
                  {{ item.status }}
                </span>
              </td>
              <td class="row-actions">
                <button class="tcm-btn tcm-btn-secondary" @click="startEdit(item)" :disabled="!canUpdate">{{ t("common.edit") }}</button>
                <button class="tcm-btn tcm-btn-danger" @click="removeHerb(item)" :disabled="!canDelete">{{ t("common.delete") }}</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="tcm-card">
      <h2 class="tcm-title">{{ editingId ? t("herbs.editHerb") : t("herbs.createHerb") }}</h2>
      <form class="tcm-form" @submit.prevent="submitForm">
        <label class="tcm-label">
          <span class="tcm-label-text">{{ t("herbs.herbCode") }}</span>
          <input class="tcm-input" v-model.trim="form.herb_code" :disabled="Boolean(editingId)" required />
        </label>
        <label class="tcm-label">
          <span class="tcm-label-text">{{ t("herbs.herbName") }}</span>
          <input class="tcm-input" v-model.trim="form.herb_name" required />
        </label>
        <label class="tcm-label">
          <span class="tcm-label-text">{{ t("herbs.category") }}</span>
          <input class="tcm-input" v-model.trim="form.category" required />
        </label>
        <label class="tcm-label">
          <span class="tcm-label-text">{{ t("herbs.natureTaste") }}</span>
          <input class="tcm-input" v-model.trim="form.nature_taste" />
        </label>
        <label class="tcm-label">
          <span class="tcm-label-text">{{ t("herbs.meridian") }}</span>
          <input class="tcm-input" v-model.trim="form.meridian_tropism" />
        </label>
        <label class="tcm-label">
          <span class="tcm-label-text">{{ t("herbs.efficacy") }}</span>
          <textarea class="tcm-textarea" v-model.trim="form.efficacy"></textarea>
        </label>
        <label class="tcm-label">
          <span class="tcm-label-text">{{ t("herbs.indication") }}</span>
          <textarea class="tcm-textarea" v-model.trim="form.indication"></textarea>
        </label>
        <label class="tcm-label">
          <span class="tcm-label-text">{{ t("herbs.unit") }}</span>
          <input class="tcm-input" v-model.trim="form.unit" />
        </label>
        <label class="tcm-label">
          <span class="tcm-label-text">{{ t("herbs.referencePrice") }}</span>
          <input class="tcm-input" v-model.trim="form.reference_price" type="number" min="0" step="0.01" />
        </label>
        <label class="tcm-label">
          <span class="tcm-label-text">{{ t("herbs.status") }}</span>
          <select class="tcm-select" v-model="form.status">
            <option value="enabled">{{ t("herbs.enabled") }}</option>
            <option value="disabled">{{ t("herbs.disabled") }}</option>
          </select>
        </label>
        <div class="row-actions">
          <button class="tcm-btn tcm-btn-primary" :disabled="submitting">
            {{ submitting ? t("common.submitting") : editingId ? t("common.saveChanges") : t("herbs.createHerb") }}
          </button>
          <button class="tcm-btn tcm-btn-secondary" type="button" @click="resetForm">{{ t("common.reset") }}</button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.tcm-card {
  background: var(--tcm-card);
  border: 1px solid var(--tcm-line);
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 12px 40px rgba(45, 42, 36, 0.06);
  position: relative;
  overflow: hidden;
}

.tcm-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, var(--tcm-wood), var(--tcm-brand), var(--tcm-green));
}

.tcm-title {
  color: var(--tcm-ink);
  font-family: "ZCOOL XiaoWei", "LXGW WenKai", "Noto Serif SC", serif;
  font-size: 24px;
  font-weight: 600;
  letter-spacing: 1px;
}

.tcm-subtitle {
  color: var(--tcm-subtle);
  font-size: 14px;
  margin-top: 4px;
}

.tcm-input,
.tcm-select {
  width: 100%;
  border: 1px solid var(--tcm-line);
  background: var(--tcm-paper);
  border-radius: 10px;
  padding: 12px 14px;
  font-size: 14px;
  color: var(--tcm-ink);
  transition: all 0.3s ease;
  font-family: "Noto Sans SC", "Source Han Sans SC", "PingFang SC", sans-serif;
}

.tcm-input:focus,
.tcm-select:focus {
  outline: none;
  border-color: var(--tcm-wood);
  box-shadow: 0 0 0 3px rgba(139, 105, 20, 0.1);
  background: #fff;
}

.tcm-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.tcm-textarea {
  width: 100%;
  border: 1px solid var(--tcm-line);
  background: var(--tcm-paper);
  border-radius: 10px;
  padding: 12px 14px;
  font-size: 14px;
  color: var(--tcm-ink);
  min-height: 90px;
  resize: vertical;
  transition: all 0.3s ease;
  font-family: "Noto Sans SC", "Source Han Sans SC", "PingFang SC", sans-serif;
}

.tcm-textarea:focus {
  outline: none;
  border-color: var(--tcm-wood);
  box-shadow: 0 0 0 3px rgba(139, 105, 20, 0.1);
  background: #fff;
}

.tcm-label {
  display: grid;
  gap: 8px;
}

.tcm-label-text {
  color: var(--tcm-ink);
  font-weight: 500;
  font-size: 14px;
}

.tcm-form {
  display: grid;
  gap: 14px;
  margin-top: 20px;
}

.tcm-btn {
  border: 0;
  border-radius: 10px;
  padding: 12px 20px;
  font-weight: 600;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
  font-family: "Noto Sans SC", "Source Han Sans SC", "PingFang SC", sans-serif;
  letter-spacing: 0.5px;
}

.tcm-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: none !important;
}

.tcm-btn-primary {
  color: #ffffff;
  background: linear-gradient(135deg, var(--tcm-green), #3a6e4a);
  box-shadow: 0 4px 14px rgba(74, 124, 89, 0.3);
}

.tcm-btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #3a6e4a, var(--tcm-green));
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(74, 124, 89, 0.4);
}

.tcm-btn-secondary {
  color: var(--tcm-ink);
  background: var(--tcm-paper);
  border: 1px solid var(--tcm-line);
}

.tcm-btn-secondary:hover:not(:disabled) {
  background: #fff;
  border-color: var(--tcm-wood);
  transform: translateY(-1px);
}

.tcm-btn-danger {
  color: #fff;
  background: linear-gradient(135deg, var(--tcm-cinnabar), #a73737);
  box-shadow: 0 4px 14px rgba(167, 55, 55, 0.3);
}

.tcm-btn-danger:hover:not(:disabled) {
  background: linear-gradient(135deg, #a73737, var(--tcm-cinnabar));
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(167, 55, 55, 0.4);
}

.tcm-table-wrapper {
  overflow-x: auto;
  border-radius: 12px;
  border: 1px solid var(--tcm-line);
  margin-top: 16px;
}

.tcm-table {
  width: 100%;
  border-collapse: collapse;
  background: var(--tcm-paper);
}

.tcm-table th {
  background: linear-gradient(180deg, var(--tcm-card), var(--tcm-paper));
  color: var(--tcm-ink);
  font-weight: 600;
  text-align: left;
  padding: 14px 16px;
  border-bottom: 2px solid var(--tcm-line);
  font-family: "ZCOOL XiaoWei", "LXGW WenKai", "Noto Serif SC", serif;
  font-size: 15px;
}

.tcm-table td {
  padding: 14px 16px;
  border-bottom: 1px solid var(--tcm-line);
  color: var(--tcm-ink);
  font-size: 14px;
}

.tcm-table tbody tr {
  transition: background 0.2s ease;
}

.tcm-table tbody tr:hover {
  background: rgba(139, 105, 20, 0.05);
}

.tcm-error {
  color: var(--tcm-warn);
  font-size: 14px;
  margin: 12px 0;
  padding: 10px 14px;
  background: rgba(167, 55, 55, 0.08);
  border-radius: 8px;
  border-left: 3px solid var(--tcm-warn);
}

.tcm-status-enabled {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 20px;
  background: rgba(74, 124, 89, 0.15);
  color: var(--tcm-green);
  font-size: 13px;
  font-weight: 600;
}

.tcm-status-disabled {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 20px;
  background: rgba(167, 55, 55, 0.15);
  color: var(--tcm-warn);
  font-size: 13px;
  font-weight: 600;
}
</style>
