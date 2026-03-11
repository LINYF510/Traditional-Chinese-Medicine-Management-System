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
const roles = ref([]);
const editingId = ref(null);

const canCreate = computed(() => auth.hasPermission("user.create"));
const canUpdate = computed(() => auth.hasPermission("user.update"));
const canDelete = computed(() => auth.hasPermission("user.delete"));

const form = reactive({
  username: "",
  password: "",
  real_name: "",
  email: "",
  role: "",
  is_active: true,
});

function listFrom(payload) {
  return Array.isArray(payload) ? payload : payload?.results || [];
}

async function fetchUsers() {
  loading.value = true;
  errorText.value = "";
  try {
    const response = await http.get("/api/users/?ordering=-id");
    rows.value = listFrom(response.data);
  } catch (error) {
    errorText.value = extractErrorMessage(error, t("users.loadUsersFailed"));
  } finally {
    loading.value = false;
  }
}

async function fetchRoles() {
  try {
    const response = await http.get("/api/roles/");
    roles.value = listFrom(response.data);
  } catch (error) {
    errorText.value = extractErrorMessage(error, t("users.loadRolesFailed"));
  }
}

function resetForm() {
  editingId.value = null;
  form.username = "";
  form.password = "";
  form.real_name = "";
  form.email = "";
  form.role = "";
  form.is_active = true;
}

function startEdit(row) {
  editingId.value = row.id;
  form.username = row.username;
  form.password = "";
  form.real_name = row.real_name || "";
  form.email = row.email || "";
  form.role = row.role || "";
  form.is_active = row.is_active;
}

async function submitForm() {
  submitting.value = true;
  errorText.value = "";
  try {
    if (editingId.value) {
      if (!canUpdate.value) throw new Error(t("users.noPermissionUpdate"));
      const payload = {
        real_name: form.real_name,
        email: form.email,
        role: form.role || null,
        is_active: form.is_active,
      };
      if (form.password) payload.password = form.password;
      await http.patch(`/api/users/${editingId.value}/`, payload);
    } else {
      if (!canCreate.value) throw new Error(t("users.noPermissionCreate"));
      await http.post("/api/users/", {
        username: form.username,
        password: form.password,
        real_name: form.real_name,
        email: form.email,
        role: form.role || null,
        is_active: form.is_active,
      });
    }
    resetForm();
    await fetchUsers();
  } catch (error) {
    errorText.value = extractErrorMessage(error, t("users.userOperationFailed"));
  } finally {
    submitting.value = false;
  }
}

async function toggleActive(row) {
  if (!canUpdate.value) return;
  try {
    await http.patch(`/api/users/${row.id}/`, { is_active: !row.is_active });
    await fetchUsers();
  } catch (error) {
    errorText.value = extractErrorMessage(error, t("users.updateUserStatusFailed"));
  }
}

async function removeUser(row) {
  if (!canDelete.value) return;
  if (!window.confirm(t("users.deleteUserConfirm", { username: row.username }))) return;
  try {
    await http.delete(`/api/users/${row.id}/`);
    await fetchUsers();
  } catch (error) {
    errorText.value = extractErrorMessage(error, t("users.deleteUserFailed"));
  }
}

onMounted(async () => {
  await Promise.all([fetchRoles(), fetchUsers()]);
});
</script>

<template>
  <div class="view-grid">
    <div class="tcm-card">
      <div class="tcm-toolbar">
        <div>
          <h2 class="tcm-title">{{ t("users.title") }}</h2>
          <p class="tcm-subtitle">{{ t("users.desc") }}</p>
        </div>
        <button class="tcm-btn tcm-btn-muted" @click="fetchUsers" :disabled="loading">
          {{ loading ? t("common.refreshing") : t("common.refresh") }}
        </button>
      </div>

      <p v-if="errorText" class="tcm-error-text">{{ errorText }}</p>

      <div class="tcm-table-container">
        <table class="tcm-table">
          <thead>
            <tr>
              <th>{{ t("users.id") }}</th>
              <th>{{ t("users.username") }}</th>
              <th>{{ t("users.realName") }}</th>
              <th>{{ t("users.role") }}</th>
              <th>{{ t("users.email") }}</th>
              <th>{{ t("users.status") }}</th>
              <th>{{ t("common.actions") }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in rows" :key="row.id">
              <td>{{ row.id }}</td>
              <td>{{ row.username }}</td>
              <td>{{ row.real_name || "-" }}</td>
              <td>{{ row.role_name || "-" }}</td>
              <td>{{ row.email || "-" }}</td>
              <td>{{ row.is_active ? t("common.active") : t("common.disabled") }}</td>
              <td class="tcm-row-actions">
                <button class="tcm-btn tcm-btn-muted" @click="startEdit(row)" :disabled="!canUpdate">{{ t("common.edit") }}</button>
                <button class="tcm-btn tcm-btn-muted" @click="toggleActive(row)" :disabled="!canUpdate">
                  {{ row.is_active ? t("common.disable") : t("common.enable") }}
                </button>
                <button class="tcm-btn tcm-btn-danger" @click="removeUser(row)" :disabled="!canDelete">{{ t("common.delete") }}</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="tcm-card">
      <h2 class="tcm-title">{{ editingId ? t("users.editUser") : t("users.createUser") }}</h2>
      <form class="tcm-form" @submit.prevent="submitForm">
        <label class="tcm-label">
          <span>{{ t("users.username") }}</span>
          <input class="tcm-input" v-model.trim="form.username" :disabled="Boolean(editingId)" required />
        </label>
        <label class="tcm-label">
          <span>{{ t("login.password") }} {{ editingId ? `(${t("common.optional")})` : "" }}</span>
          <input class="tcm-input" v-model="form.password" type="password" :required="!editingId" />
        </label>
        <label class="tcm-label">
          <span>{{ t("users.realName") }}</span>
          <input class="tcm-input" v-model.trim="form.real_name" />
        </label>
        <label class="tcm-label">
          <span>{{ t("users.email") }}</span>
          <input class="tcm-input" v-model.trim="form.email" type="email" />
        </label>
        <label class="tcm-label">
          <span>{{ t("users.role") }}</span>
          <select class="tcm-select" v-model="form.role">
            <option value="">{{ t("common.noRole") }}</option>
            <option v-for="role in roles" :key="role.id" :value="role.id">
              {{ role.role_name }} ({{ role.role_code }})
            </option>
          </select>
        </label>
        <label class="tcm-label">
          <span>{{ t("users.status") }}</span>
          <select class="tcm-select" v-model="form.is_active">
            <option :value="true">{{ t("common.active") }}</option>
            <option :value="false">{{ t("common.disabled") }}</option>
          </select>
        </label>
        <div class="tcm-row-actions">
          <button class="tcm-btn tcm-btn-primary" type="submit" :disabled="submitting">
            {{ submitting ? t("common.submitting") : editingId ? t("common.saveChanges") : t("common.createUser") }}
          </button>
          <button class="tcm-btn tcm-btn-muted" type="button" @click="resetForm">{{ t("common.reset") }}</button>
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
  padding: 24px;
}

.tcm-toolbar {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: end;
  margin-bottom: 20px;
}

.tcm-title {
  font-family: "ZCOOL XiaoWei", "LXGW WenKai", "Noto Serif SC", serif;
  color: var(--tcm-ink);
  font-size: 24px;
  margin: 0 0 4px 0;
}

.tcm-subtitle {
  color: var(--tcm-subtle);
  font-size: 14px;
  margin: 0;
}

.tcm-error-text {
  color: var(--tcm-warn);
  font-size: 14px;
  margin-bottom: 16px;
}

.tcm-table-container {
  overflow-x: auto;
  border-radius: 12px;
  border: 1px solid var(--tcm-line);
}

.tcm-table {
  width: 100%;
  border-collapse: collapse;
  background: var(--tcm-paper);
}

.tcm-table th {
  background: linear-gradient(180deg, var(--tcm-paper) 0%, #f0ebe0 100%);
  color: var(--tcm-ink);
  text-align: left;
  padding: 14px 12px;
  font-weight: 600;
  font-family: "ZCOOL XiaoWei", "LXGW WenKai", "Noto Serif SC", serif;
  border-bottom: 2px solid var(--tcm-line);
}

.tcm-table td {
  border-bottom: 1px solid var(--tcm-line);
  text-align: left;
  padding: 12px;
  color: var(--tcm-ink);
}

.tcm-table tbody tr:hover {
  background: rgba(74, 124, 89, 0.05);
}

.tcm-row-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.tcm-btn {
  border: 0;
  border-radius: 10px;
  padding: 10px 18px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: "Noto Sans SC", "Source Han Sans SC", "PingFang SC", sans-serif;
}

.tcm-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: none !important;
}

.tcm-btn-primary {
  color: #ffffff;
  background: linear-gradient(135deg, var(--tcm-green) 0%, #3a6e4a 100%);
  box-shadow: 0 4px 12px rgba(74, 124, 89, 0.3);
}

.tcm-btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #3a6e4a 0%, var(--tcm-green) 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(74, 124, 89, 0.4);
}

.tcm-btn-muted {
  color: var(--tcm-ink);
  background: var(--tcm-paper);
  border: 1px solid var(--tcm-line);
}

.tcm-btn-muted:hover:not(:disabled) {
  background: #f0ebe0;
  border-color: var(--tcm-wood);
  transform: translateY(-1px);
}

.tcm-btn-danger {
  color: #fff;
  background: linear-gradient(135deg, var(--tcm-cinnabar) 0%, #a73737 100%);
  box-shadow: 0 4px 12px rgba(167, 55, 55, 0.3);
}

.tcm-btn-danger:hover:not(:disabled) {
  background: linear-gradient(135deg, #a73737 0%, var(--tcm-cinnabar) 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(167, 55, 55, 0.4);
}

.tcm-form {
  display: grid;
  gap: 16px;
}

.tcm-label {
  display: grid;
  gap: 8px;
  color: var(--tcm-ink);
  font-weight: 500;
}

.tcm-input,
.tcm-select {
  width: 100%;
  border: 1px solid var(--tcm-line);
  background: var(--tcm-paper);
  border-radius: 10px;
  padding: 12px 14px;
  font-size: 15px;
  color: var(--tcm-ink);
  transition: all 0.2s ease;
  font-family: "Noto Sans SC", "Source Han Sans SC", "PingFang SC", sans-serif;
}

.tcm-input:focus,
.tcm-select:focus {
  outline: none;
  border-color: var(--tcm-green);
  box-shadow: 0 0 0 3px rgba(74, 124, 89, 0.15);
}

.tcm-input:disabled,
.tcm-select:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background: #f0ebe0;
}
</style>
