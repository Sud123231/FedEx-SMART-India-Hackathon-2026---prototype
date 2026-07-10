<script setup>
import { ref, onMounted, computed } from "vue";
import api from "../../services/api";

import UpdateStatus from "./UpdateStatus.vue";
import AddNote from "./AddNote.vue"; 
import RequestEscalation from "./RequestEscalation.vue"; 


const selectedCase = computed(() =>
  cases.value.find(c => c.id === selectedCaseId.value)
);

const isCaseClosed = computed(() =>
  selectedCase.value?.status === "CLOSED"
);

/* State */
const cases = ref([]);
const selectedCaseId = ref(null);
const activeAction = ref(null);

/* Filters */
const priorityFilter = ref("");
const statusFilter = ref("");

/* Priority mapping: SCORE (0–1) → LABEL */
function normalizePriority(score) {
  if (score === null || score === undefined) return "";

  const s = Number(score);
  if (Number.isNaN(s)) return "";

  if (s >= 0.65) return "High";
  if (s >= 0.30) return "Medium";
  return "Low";
}

/* Load assigned cases */
onMounted(async () => {
  const res = await api.get("/api/dca/cases");

  cases.value = res.data.map(c => ({
    ...c,
    priorityScore: c.priority,
    priority: normalizePriority(c.priority)
  }));
});

/* Filter logic */
const filteredCases = computed(() => {
  return cases.value.filter(c => {
    return (
      (!priorityFilter.value ||
        c.priority?.toLowerCase() === priorityFilter.value.toLowerCase()) &&
      (!statusFilter.value ||
        c.status?.toLowerCase() === statusFilter.value.toLowerCase())
    );
  });
});

/* Action handlers */
function openUpdateStatus() {
  if (!selectedCaseId.value) {
    alert("Please select a case first");
    return;
  }
  if (isCaseClosed.value) {
    alert("This case is already closed");
    return;
  }
  activeAction.value = "update-status";
}

function openAddNote() {
  if (!selectedCaseId.value) {
    alert("Please select a case first");
    return;
  }
  if (isCaseClosed.value) {
    alert("Cannot add notes to a closed case");
    return;
  }
  activeAction.value = "add-note";
}

function openRequestEscalation() {
  if (!selectedCaseId.value) {
    alert("Please select a case first");
    return;
  }
  if (isCaseClosed.value) {
    alert("Closed cases cannot be escalated");
    return;
  }
  activeAction.value = "request-escalation";
}

</script>

<template>
  <div class="dca-portal p-6">
    <h1 class="page-title">DCA Portal</h1>

    <div class="card">
      <div class="card-header">
        My Assigned Cases
      </div>

      <!-- Filters -->
      <div class="filters">
        <label>Filter:</label>

        <select v-model="priorityFilter">
          <option value="">Priority</option>
          <option>High</option>
          <option>Medium</option>
          <option>Low</option>
        </select>

        <select v-model="statusFilter">
          <option value="">Status</option>
          <option>PENDING</option>
          <option>ESCALATED</option>
          <option>CLOSED</option>
        </select>
      </div>

      <!-- Table -->
      <div class="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Select</th>
              <th>Case ID</th>
              <th>Customer</th>
              <th>Amount</th>
              <th>Aging</th>
              <th>Priority</th>
              <th>Status</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="c in filteredCases" :key="c.id">
              <td class="center">
                <input
                  type="radio"
                  :value="c.id"
                  v-model="selectedCaseId"
                />
              </td>
              <td>{{ c.case_id }}</td>
              <td>{{ c.customer }}</td>
              <td>₹{{ c.amount }}</td>
              <td>{{ c.aging }} Days</td>
              <td>
                <span
                  class="badge"
                  :class="c.priority.toLowerCase()"
                  :title="`Score: ${c.priorityScore}`"
                >
                  {{ c.priority }}
                </span>
              </td>
              <td>{{ c.status }}</td>
            </tr>

            <tr v-if="filteredCases.length === 0">
              <td colspan="7" class="empty">
                No cases found
              </td>
            </tr>
          </tbody>
        </table>
      </div>

    <div class="actions">
        <button @click="openUpdateStatus" :disabled="isCaseClosed">
          Update Status
        </button>
        <button @click="openAddNote" :disabled="isCaseClosed">
          Add Notes
        </button>
        <button @click="openRequestEscalation" :disabled="isCaseClosed">
          Request Escalation
        </button>
    </div>

    <div class="action-panels">
      <UpdateStatus v-if="activeAction === 'update-status'" :case-id="selectedCaseId" @close="activeAction = null"/>
      <AddNote v-if="activeAction === 'add-note'" :case-id="selectedCaseId" @close="activeAction = null"/>
      <RequestEscalation v-if="activeAction === 'request-escalation'" :case-id="selectedCaseId" @close="activeAction = null"/>
    </div>
   </div> 
  </div>
</template>

<style scoped>
.actions button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.dca-portal {
  background: #f5f6f8;
  min-height: 100vh;
}

/* Title */
.page-title {
  font-size: 22px;
  font-weight: 600;
  margin-bottom: 20px;
}

/* Card */
.card {
  background: #ffffff;
  border: 1px solid #d1d5db;
  border-radius: 4px;
}

/* Card Header */
.card-header {
  background: #e5e7eb;
  padding: 12px 16px;
  font-weight: 600;
  border-bottom: 1px solid #d1d5db;
}

/* Filters */
.filters {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-bottom: 1px solid #e5e7eb;
}

.filters label {
  font-weight: 500;
}

.filters select {
  padding: 6px 10px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  background: #ffffff;
}

/* Table */
.table-wrapper {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background: #f3f4f6;
}

th {
  text-align: left;
  font-size: 13px;
  font-weight: 600;
  padding: 10px;
  border-bottom: 1px solid #d1d5db;
}

td {
  padding: 12px 10px;
  border-bottom: 1px solid #e5e7eb;
  font-size: 14px;
}

.center {
  text-align: center;
}

tbody tr:hover {
  background: #f9fafb;
}

/* Badges */
.badge {
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
}

.badge.high {
  background: #fee2e2;
  color: #b91c1c;
}

.badge.medium {
  background: #fef3c7;
  color: #92400e;
}

.badge.low {
  background: #dcfce7;
  color: #166534;
}

/* Empty */
.empty {
  text-align: center;
  padding: 16px;
  color: #6b7280;
}

/* Actions */
.actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  padding: 20px;
}

.actions button {
  padding: 8px 20px;
  border: 1px solid #9ca3af;
  background: #e5e7eb;
  border-radius: 4px;
  font-weight: 500;
}

.actions button:hover {
  background: #d1d5db;
  cursor: pointer;
}
</style>
