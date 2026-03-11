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
const rows = ref([]);
const herbs = ref([]);
const editingId = ref(null);

const canCreate = computed(() => auth.hasPermission("formula.create"));
const canUpdate = computed(() => auth.hasPermission("formula.update"));
const canDelete = computed(() => auth.hasPermission("formula.delete"));

const form = reactive({
  formula_code: "",
  formula_name: "",
  source: "",
  efficacy: "",
  indication: "",
  usage_method: "",
  contraindication: "",
  status: "enabled",
  items: [],
});

function listFrom(payload) {
  return Array.isArray(payload) ? payload : payload?.results || [];
}

function emptyItem() {
  return {
    herb: "",
    dosage: "1.00",
    dosage_unit: "g",
    role_in_formula: "",
    sort_no: form.items.length + 1,
    remark: "",
  };
}

async function fetchFormulas() {
  loading.value = true;
  errorText.value = "";
  try {
    const response = await http.get("/api/formulas/?ordering=-id");
    rows.value = listFrom(response.data);
  } catch (error) {
    errorText.value = extractErrorMessage(error, t("formulas.loadFailed"));
  } finally {
    loading.value = false;
  }
}

async function fetchHerbs() {
  try {
    const response = await http.get("/api/herbs/?page_size=200");
    herbs.value = listFrom(response.data);
  } catch (error) {
    errorText.value = extractErrorMessage(error, t("formulas.loadHerbListFailed"));
  }
}

function resetForm() {
  editingId.value = null;
  form.formula_code = "";
  form.formula_name = "";
  form.source = "";
  form.efficacy = "";
  form.indication = "";
  form.usage_method = "";
  form.contraindication = "";
  form.status = "enabled";
  form.items = [emptyItem()];
}

function startEdit(row) {
  editingId.value = row.id;
  form.formula_code = row.formula_code || "";
  form.formula_name = row.formula_name || "";
  form.source = row.source || "";
  form.efficacy = row.efficacy || "";
  form.indication = row.indication || "";
  form.usage_method = row.usage_method || "";
  form.contraindication = row.contraindication || "";
  form.status = row.status || "enabled";
  form.items = (row.items_detail || []).map((item, index) => ({
    herb: String(item.herb),
    dosage: String(item.dosage),
    dosage_unit: item.dosage_unit || "g",
    role_in_formula: item.role_in_formula || "",
    sort_no: item.sort_no || index + 1,
    remark: item.remark || "",
  }));
  if (form.items.length === 0) form.items = [emptyItem()];
}

function addItem() {
  form.items.push(emptyItem());
}

function removeItem(index) {
  form.items.splice(index, 1);
  if (form.items.length === 0) form.items.push(emptyItem());
}

async function submitForm() {
  submitting.value = true;
  errorText.value = "";
  try {
    const payload = {
      formula_code: form.formula_code,
      formula_name: form.formula_name,
      source: form.source,
      efficacy: form.efficacy,
      indication: form.indication,
      usage_method: form.usage_method,
      contraindication: form.contraindication,
      status: form.status,
      items: form.items
        .filter((item) => item.herb && item.dosage)
        .map((item, index) => ({
          herb: Number(item.herb),
          dosage: item.dosage,
          dosage_unit: item.dosage_unit || "g",
          role_in_formula: item.role_in_formula || "",
          sort_no: Number(item.sort_no || index + 1),
          remark: item.remark || "",
        })),
    };
    if (editingId.value) {
      if (!canUpdate.value) throw new Error(t("formulas.noPermissionUpdate"));
      await http.put(`/api/formulas/${editingId.value}/`, payload);
    } else {
      if (!canCreate.value) throw new Error(t("formulas.noPermissionCreate"));
      await http.post("/api/formulas/", payload);
    }
    resetForm();
    await fetchFormulas();
  } catch (error) {
    errorText.value = extractErrorMessage(error, t("formulas.operationFailed"));
  } finally {
    submitting.value = false;
  }
}

async function removeFormula(row) {
  if (!canDelete.value) return;
  if (!window.confirm(t("formulas.deleteConfirm", { name: row.formula_name }))) return;
  try {
    await http.delete(`/api/formulas/${row.id}/`);
    await fetchFormulas();
  } catch (error) {
    errorText.value = extractErrorMessage(error, t("formulas.deleteFailed"));
  }
}

onMounted(async () => {
  await Promise.all([fetchHerbs(), fetchFormulas()]);
  resetForm();
});
</script>

<template>
  <div class="view-grid">
    <div class="card tcm-card">
      <div class="toolbar">
        <div>
          <h2>{{ t("formulas.title") }}</h2>
          <p class="tcm-muted">{{ t("formulas.desc") }}</p>
        </div>
        <button class="btn tcm-btn-muted" @click="fetchFormulas" :disabled="loading">
          {{ loading ? t("common.refreshing") : t("common.refresh") }}
        </button>
      </div>
      <p v-if="errorText" class="tcm-error-text">{{ errorText }}</p>

      <div class="formula-list">
        <article v-for="item in rows" :key="item.id" class="formula-card tcm-formula-card">
          <h3>{{ item.formula_name }} <small>{{ item.formula_code }}</small></h3>
          <p><strong>{{ t("formulas.source") }}:</strong> {{ item.source || "-" }}</p>
          <p><strong>{{ t("formulas.efficacy") }}:</strong> {{ item.efficacy || "-" }}</p>
          <p><strong>{{ t("formulas.indication") }}:</strong> {{ item.indication || "-" }}</p>
          <p>
            <strong>{{ t("formulas.items") }}:</strong>
            {{
              (item.items_detail || [])
                .map((x) => `${x.herb_name} ${x.dosage}${x.dosage_unit}`)
                .join(", ") || "-"
            }}
          </p>
          <div class="row-actions">
            <button class="btn tcm-btn-muted" @click="startEdit(item)" :disabled="!canUpdate">{{ t("common.edit") }}</button>
            <button class="btn tcm-btn-danger" @click="removeFormula(item)" :disabled="!canDelete">{{ t("common.delete") }}</button>
          </div>
        </article>
      </div>
    </div>

    <div class="card tcm-card">
      <h2>{{ editingId ? t("formulas.editFormula") : t("formulas.createFormula") }}</h2>
      <form class="inventory-form tcm-form" @submit.prevent="submitForm">
        <label class="tcm-label">
          <span>{{ t("formulas.formulaCode") }}</span>
          <input v-model.trim="form.formula_code" :disabled="Boolean(editingId)" required />
        </label>
        <label class="tcm-label">
          <span>{{ t("formulas.formulaName") }}</span>
          <input v-model.trim="form.formula_name" required />
        </label>
        <label class="tcm-label">
          <span>{{ t("formulas.source") }}</span>
          <input v-model.trim="form.source" />
        </label>
        <label class="tcm-label">
          <span>{{ t("formulas.efficacy") }}</span>
          <textarea v-model.trim="form.efficacy"></textarea>
        </label>
        <label class="tcm-label">
          <span>{{ t("formulas.indication") }}</span>
          <textarea v-model.trim="form.indication"></textarea>
        </label>
        <label class="tcm-label">
          <span>{{ t("formulas.usage") }}</span>
          <textarea v-model.trim="form.usage_method"></textarea>
        </label>
        <label class="tcm-label">
          <span>{{ t("formulas.contraindication") }}</span>
          <textarea v-model.trim="form.contraindication"></textarea>
        </label>
        <label class="tcm-label">
          <span>{{ t("formulas.status") }}</span>
          <select v-model="form.status">
            <option value="enabled">{{ t("formulas.enabled") }}</option>
            <option value="disabled">{{ t("formulas.disabled") }}</option>
          </select>
        </label>

        <h3 class="tcm-section-title">{{ t("formulas.composition") }}</h3>
        <div v-for="(item, index) in form.items" :key="index" class="compose-row tcm-compose-row">
          <select v-model="item.herb">
            <option value="">{{ t("common.selectHerb") }}</option>
            <option v-for="herb in herbs" :key="herb.id" :value="String(herb.id)">
              {{ herb.herb_name }} ({{ herb.herb_code }})
            </option>
          </select>
          <input v-model.trim="item.dosage" type="number" min="0.01" step="0.01" :placeholder="t('formulas.dosage')" />
          <input v-model.trim="item.dosage_unit" :placeholder="t('formulas.dosageUnit')" />
          <input v-model.trim="item.role_in_formula" :placeholder="t('formulas.roleInFormula')" />
          <button class="btn tcm-btn-danger" type="button" @click="removeItem(index)">{{ t("common.remove") }}</button>
        </div>
        <button class="btn tcm-btn-muted" type="button" @click="addItem">{{ t("common.addHerbItem") }}</button>

        <div class="row-actions">
          <button class="btn tcm-btn-primary" :disabled="submitting">
            {{ submitting ? t("common.submitting") : editingId ? t("common.saveChanges") : t("formulas.createFormula") }}
          </button>
          <button class="btn tcm-btn-muted" type="button" @click="resetForm">{{ t("common.reset") }}</button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.tcm-card {
  background: var(--tcm-card);
  border: 1px solid var(--tcm-line);
  border-radius: 18px;
  box-shadow: 0 16px 32px rgba(45, 42, 36, 0.08);
}

.tcm-muted {
  color: var(--tcm-subtle);
}

.tcm-error-text {
  color: var(--tcm-warn);
  font-size: 14px;
}

.tcm-btn-primary {
  color: #ffffff;
  background: linear-gradient(90deg, var(--tcm-green), #3a6e4a);
  transition: all 0.2s ease;
  border: 0;
  border-radius: 10px;
  padding: 10px 16px;
  font-weight: 700;
  cursor: pointer;
}

.tcm-btn-primary:hover:not(:disabled) {
  background: linear-gradient(90deg, #3a6e4a, var(--tcm-green));
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(74, 124, 89, 0.3);
}

.tcm-btn-muted {
  color: var(--tcm-ink);
  background: var(--tcm-paper);
  border: 1px solid var(--tcm-line);
  border-radius: 10px;
  padding: 10px 16px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tcm-btn-muted:hover:not(:disabled) {
  background: var(--tcm-bg);
  border-color: var(--tcm-wood);
}

.tcm-btn-danger {
  color: #fff;
  background: var(--tcm-cinnabar);
  border: 0;
  border-radius: 10px;
  padding: 10px 16px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tcm-btn-danger:hover:not(:disabled) {
  background: #a73737;
  transform: translateY(-1px);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.tcm-formula-card {
  border: 1px solid var(--tcm-line);
  border-radius: 14px;
  padding: 14px;
  background: var(--tcm-paper);
  transition: all 0.2s ease;
}

.tcm-formula-card:hover {
  box-shadow: 0 4px 16px rgba(45, 42, 36, 0.1);
  border-color: var(--tcm-wood);
}

.tcm-formula-card small {
  color: var(--tcm-subtle);
  font-size: 12px;
}

.tcm-form {
  display: grid;
  gap: 10px;
  margin-bottom: 14px;
}

.tcm-label {
  display: grid;
  gap: 8px;
  color: var(--tcm-ink);
}

.tcm-label input,
.tcm-label select {
  width: 100%;
  border: 1px solid var(--tcm-line);
  background: var(--tcm-paper);
  border-radius: 10px;
  padding: 10px 12px;
  font-size: 14px;
  color: var(--tcm-ink);
  transition: all 0.2s ease;
}

.tcm-label input:focus,
.tcm-label select:focus {
  outline: none;
  border-color: var(--tcm-green);
  box-shadow: 0 0 0 2px rgba(74, 124, 89, 0.15);
}

.tcm-label textarea {
  width: 100%;
  border: 1px solid var(--tcm-line);
  background: var(--tcm-paper);
  border-radius: 10px;
  padding: 10px 12px;
  font-size: 14px;
  color: var(--tcm-ink);
  min-height: 84px;
  resize: vertical;
  transition: all 0.2s ease;
}

.tcm-label textarea:focus {
  outline: none;
  border-color: var(--tcm-green);
  box-shadow: 0 0 0 2px rgba(74, 124, 89, 0.15);
}

.tcm-section-title {
  margin-top: 16px;
  margin-bottom: 12px;
  color: var(--tcm-ink-stone);
  font-family: "ZCOOL XiaoWei", "LXGW WenKai", "Noto Serif SC", serif;
  border-bottom: 2px solid var(--tcm-line);
  padding-bottom: 8px;
}

.tcm-compose-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr auto;
  gap: 8px;
  align-items: center;
  padding: 8px;
  background: var(--tcm-paper);
  border-radius: 10px;
  border: 1px solid var(--tcm-line);
}

.tcm-compose-row select,
.tcm-compose-row input {
  width: 100%;
  border: 1px solid var(--tcm-line);
  background: var(--tcm-card);
  border-radius: 8px;
  padding: 8px 10px;
  font-size: 14px;
  color: var(--tcm-ink);
  transition: all 0.2s ease;
}

.tcm-compose-row select:focus,
.tcm-compose-row input:focus {
  outline: none;
  border-color: var(--tcm-wood);
  box-shadow: 0 0 0 2px rgba(139, 105, 20, 0.15);
}

@media (max-width: 960px) {
  .tcm-compose-row {
    grid-template-columns: 1fr;
  }
}
</style>
