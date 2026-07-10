<template>
  <div>
    <!-- Top Navigation -->
    <div class="top-nav">
      <span class="brand">FedEx DCA Management Platform</span>

      <router-link to="/enterprise" class="nav-link" exact-active-class="active">
        Dashboard
      </router-link>

      <router-link to="/enterprise/analytics" class="nav-link" exact-active-class="active">
        Analytics
      </router-link>
    </div>

    <!-- Main Dashboard -->
    <div class="dashboard-container">
      <div class="section-header">
        <h2>Enterprise Dashboard (For Internal Teams)</h2>

        <button class="upload-btn" @click="goToUpload">
          Upload Cases
        </button>

        <input
          type="file"
          ref="fileInput"
          style="display: none"
          accept=".csv,.xlsx"
          @change="uploadFile"
        />
      </div>

      <!-- KPI Cards -->
      <div class="cards">
        <div class="card">
          <h3>Total Overdue Cases</h3>
          <p>{{ stats.total_overdue }}</p>
        </div>

        <div class="card">
          <h3>In Progress</h3>
          <p>{{ stats.in_progress }}</p>
        </div>

        <div class="card">
          <h3>Escalated Cases</h3>
          <p>{{ stats.escalated }}</p>
        </div>

        <div class="card">
          <h3>Closed Cases</h3>
          <p>{{ stats.closed }}</p>
        </div>
      </div>

      <!-- Case List -->
      <div v-if="cases.length" class="case-list">
        <h3>Case List</h3>

        <table class="case-table">
          <thead>
            <tr>
              <th>Select</th>
              <th>Case ID</th>
              <th>Customer</th>
              <th>Amount</th>
              <th>Aging</th>
              <th>AI Recovery Outlook</th>
              <th>Status</th>
              <th>Escalation</th>
              <th>SLA</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="c in cases" :key="c.id">
              <td>
                <input type="checkbox" :value="c.id" v-model="selectedCases" />
              </td>
              <td>{{ c.tracking_number }}</td>
              <td>{{ c.customer_name }}</td>
              <td>{{ c.amount_due }}</td>
              <td>{{ c.aging_bucket ?? "—" }}</td>
              <td>
                <span v-if="c.recovery_probability >= 0.65">High Opportunity</span>
                <span v-else-if="c.recovery_probability < 0.3">Low Recovery</span>
                <span v-else>Medium</span>
              </td>
              <td>{{ c.status }}</td>

              <!-- Escalation status -->
              <td>
                <span
                  v-if="c.escalation_status === 'PENDING'"
                  class="badge escalation-pending"
                >
                  Requested
                </span>
                <span
                  v-else-if="c.escalation_status === 'APPROVED'"
                  class="badge escalation-approved"
                >
                  Approved
                </span>
                <span
                  v-else-if="c.escalation_status === 'REJECTED'"
                  class="badge escalation-rejected"
                >
                  Rejected
                </span>
                <span v-else>—</span>
              </td>

              <!-- SLA -->
              <td>
                <span
                  v-if="slaMap[c.id]"
                  class="sla-badge"
                  :class="slaBadgeClass(slaMap[c.id].status)"
                >
                  {{ slaLabel(slaMap[c.id].status) }}
                </span>
                <span v-else class="sla-badge sla-na">
                  N/A
                </span>
              </td>
            </tr>
          </tbody>
        </table>

        <div class="actions">
          <button @click="openAssignPanel">Assign Cases</button>

          <button
            @click="openEscalationReviewPanel"
            :disabled="!hasPendingEscalation"
          >
            Review Escalation
          </button>

          <button @click="openClosePanel">Close Cases</button>
        </div>
      </div>

      <!-- Escalation Review Panel -->
      <div v-if="activeAction === 'review-escalation'" class="action-panel">
        <h3>Review Escalation Request</h3>

        <p><strong>Reason from DCA:</strong></p>
        <p class="escalation-reason">
          {{ selectedEscalationReason }}
        </p>

        <div class="panel-actions">
          <button @click="rejectEscalation">
            Reject & Send Back
          </button>
          <button @click="approveEscalation">
            Approve Escalation
          </button>
        </div>
      </div>

      <!-- Assign Panel -->
      <div v-if="activeAction === 'assign'" class="action-panel">
        <h3>Assign Selected Cases</h3>

        <label>Assign to DCA</label>
        <select v-model="selectedDca">
          <option disabled value="">Select a DCA</option>
          <option v-for="dca in dcas" :key="dca.id" :value="dca.id">
            {{ dca.name }}
          </option>
        </select>

        <div class="panel-actions">
          <button @click="activeAction = null">Cancel</button>
          <button @click="confirmAssign">Confirm Assign</button>
        </div>
      </div>

      <!-- Close Panel (unchanged) -->
      <div v-if="activeAction === 'close'" class="action-panel">
        <h3>Close Selected Cases</h3>
        <label>Closure Type</label> <select v-model="closureReason"> <option disabled value="">Select closure type</option> <option value="PAID">PAID</option> <option value="WRITE_OFF">WRITE-OFF</option> <option value="DISPUTE">DISPUTE</option> </select> <label v-if="closureReason === 'PAID'"> Recovered Amount </label> <input v-if="closureReason === 'PAID'" type="number" v-model="recoveryAmount" /> <label>Internal Note (optional)</label> <textarea v-model="closureNote"></textarea> <div class="panel-actions"> <button @click="activeAction = null">Cancel</button> <button @click="confirmClose">Confirm Closure</button>
        </div>
      </div>
    </div>
  </div>
</template>



<script setup>
import { ref, onMounted, computed } from "vue";
import api from "../services/api";

/* ---------------- EXISTING STATE ---------------- */
const stats = ref({
  total_overdue: 0,
  in_progress: 0,
  escalated: 0,
  closed: 0,
});

const cases = ref([]);
const selectedCases = ref([]);
const dcas = ref([]);

const activeAction = ref(null);
const selectedDca = ref("");
const closureReason = ref("");
const recoveryAmount = ref("");
const closureNote = ref("");

const fileInput = ref(null);

/* ---------------- SLA STATE ---------------- */
const slaMap = ref({});

/* ---------------- ESCALATION STATE (NEW) ---------------- */
const escalations = ref([]);
const selectedEscalationReason = ref("");

/* ---------------- FETCHERS ---------------- */
const fetchOverview = async () => {
  const res = await api.get("/api/enterprise/overview");
  stats.value = res.data;
};

const refreshCases = async () => {
  const res = await api.get("/api/enterprise/cases");
  cases.value = res.data;
  selectedCases.value = [];
};

const fetchDcas = async () => {
  const res = await api.get("/api/enterprise/dcas");
  dcas.value = res.data;
};

/* SLA */
const fetchSlaStatus = async () => {
  const res = await api.get("/api/enterprise/sla/status");
  slaMap.value = Object.fromEntries(
    res.data.map(sla => [sla.case_id, sla])
  );
};

/* Escalations requested by DCA */
const fetchEscalations = async () => {
  const res = await api.get("/api/enterprise/escalations/pending");
  escalations.value = res.data;

  cases.value = cases.value.map(c => {
    const esc = escalations.value.find(e => e.case_id === c.id);
    return {
      ...c,
      escalation_status: esc?.status || null,
      escalation_reason: esc?.reason || null
    };
  });
};

/* ---------------- COMPUTED ---------------- */
const hasPendingEscalation = computed(() =>
  selectedCases.value.some(id =>
    cases.value.find(
      c => c.id === id && c.escalation_status === "PENDING"
    )
  )
);

/* ---------------- LIFECYCLE ---------------- */
onMounted(async () => {
  await fetchOverview();
  await refreshCases();
  await fetchDcas();
  await fetchSlaStatus();
  await fetchEscalations();
});

/* ---------------- ACTIONS ---------------- */
const confirmAssign = async () => {
  await api.post("/api/enterprise/assign", {
    dca_id: selectedDca.value,
    case_ids: selectedCases.value,
  });

  activeAction.value = null;
  await refreshCases();
  await fetchSlaStatus();
  await fetchEscalations();
};

const confirmClose = async () => {
  if (!selectedCases.value.length) {
    alert("Please select at least one case");
    return;
  }

  if (!closureReason.value) {
    alert("Please select a closure type");
    return;
  }

  for (const id of selectedCases.value) {
  try {
    await api.post(`/api/enterprise/cases/${id}/close`, {
      reason: closureReason.value,
      amount:
        closureReason.value === "PAID"
          ? Number(recoveryAmount.value) || 0
          : 0,
      note: closureNote.value || null
    });
  } catch (err) {
    const message =
      err.response?.data?.error ||
      `Failed to close case ${id}`;

    // Show error but DO NOT crash the loop
    alert(message);
  }
}

  activeAction.value = null;
  closureReason.value = "";
  recoveryAmount.value = "";
  closureNote.value = "";
  selectedCases.value = [];

  await refreshCases();
  await fetchSlaStatus();
  await fetchEscalations();
};

/* ---------------- ESCALATION REVIEW ---------------- */
const openEscalationReviewPanel = () => {
  const c = cases.value.find(
    c => selectedCases.value.includes(c.id) &&
         c.escalation_status === "PENDING"
  );

  if (!c) {
    alert("Select a case with pending escalation");
    return;
  }

  selectedEscalationReason.value = c.escalation_reason;
  activeAction.value = "review-escalation";
};

/* ---------------- UI HANDLERS ---------------- */
const openAssignPanel = () => {
  if (!selectedCases.value.length) return alert("Select cases first");
  activeAction.value = "assign";
};

const openClosePanel = () => {
  if (!selectedCases.value.length) return alert("Select cases first");
  activeAction.value = "close";
};

const goToUpload = () => fileInput.value?.click();

const uploadFile = async (e) => {
  const file = e.target.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append("file", file);

  await api.post("/api/enterprise/cases/upload", formData);
  await fetchOverview();
  await refreshCases();
  await fetchSlaStatus();
  await fetchEscalations();

  e.target.value = "";
};

/* ---------------- SLA UI HELPERS ---------------- */
const slaBadgeClass = (status) => {
  if (status === "COMPLETED") return "sla-completed";
  if (status === "BREACHED") return "sla-breached";
  return "sla-pending";
};

const slaLabel = (status) => {
  if (status === "RUNNING") return "IN PROGRESS";
  return status;
};

/* ---------------- ESCALATION DECISION ---------------- */
const approveEscalation = async () => {
  const caseId = selectedCases.value.find(id =>
    cases.value.find(c => c.id === id && c.escalation_status === "PENDING")
  );

  if (!caseId) {
    alert("No pending escalation selected");
    return;
  }

  await api.post("/api/enterprise/escalations/approve", {
    case_id: caseId
  });

  activeAction.value = null;
  selectedCases.value = [];

  await refreshCases();
  await fetchSlaStatus();
  await fetchEscalations();
};

const rejectEscalation = async () => {
  const caseId = selectedCases.value.find(id =>
    cases.value.find(c => c.id === id && c.escalation_status === "PENDING")
  );

  if (!caseId) {
    alert("No pending escalation selected");
    return;
  }

  await api.post("/api/enterprise/escalations/reject", {
    case_id: caseId
  });

  activeAction.value = null;
  selectedCases.value = [];

  await refreshCases();
  await fetchSlaStatus();
  await fetchEscalations();
};

</script>


<style scoped>
.case-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 12px;
}

.case-table th,
.case-table td {
  border: 1px solid #ccc;
  padding: 8px;
  text-align: left;
}

.case-table th {
  background: #f2f2f2;
}

h1 {
  margin-bottom: 16px;
}

/* Top Nav */
.top-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 24px;
  border-bottom: 1px solid #ccc;
  background: #f2f2f2;
}

.brand {
  font-weight: bold;
}

.nav-links span {
  margin-left: 20px;
  cursor: pointer;
}

.nav-link {
  margin-left: 20px;
  cursor: pointer;
  text-decoration: none;
  color: black;
}

.nav-link.active {
  font-weight: bold;
  border-bottom: 2px solid black;
}

/* Main container */
.dashboard-container {
  padding: 24px;
}

/* Section header */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

/* Upload button */
.upload-btn {
  padding: 8px 16px;
  border: 1px solid #333;
  background: #f5f5f5;
  cursor: pointer;
}

/* KPI cards */
.cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 32px;
}

.card {
  border: 1px solid #ccc;
  padding: 16px;
  background: #fafafa;
}

/* Case list */
.case-list {
  border-top: 1px solid #ccc;
  padding-top: 16px;
}

.filters {
  font-size: 14px;
  color: #555;
  margin-bottom: 8px;
}

.empty-table {
  border: 1px solid #ddd;
  padding: 24px;
  color: #777;
  background: #fff;
}

.action-panel {
  border: 1px solid #ccc;
  padding: 16px;
  margin-top: 20px;
  background: #fafafa;
}

.panel-actions {
  margin-top: 12px;
  display: flex;
  gap: 8px;
}

/* ================= SLA BADGES (ADDED) ================= */

.sla-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
}

/* SLA running */
.sla-pending {
  background-color: #fef3c7;
  color: #92400e;
}

/* SLA completed */
.sla-completed {
  background-color: #dcfce7;
  color: #166534;
}

/* SLA breached */
.sla-breached {
  background-color: #fee2e2;
  color: #b91c1c;
}

/* SLA not applicable */
.sla-na {
  background-color: #f3f4f6;
  color: #6b7280;
}
</style>
