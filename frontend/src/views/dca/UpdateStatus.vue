<script setup>
import { ref, onMounted, watch } from "vue";
import api from "../../services/api";

/* Props — NOT required */
const props = defineProps({
  caseId: {
    type: Number,
    required: false
  }
});

const emit = defineEmits(["close"]);

/* State */
const caseData = ref(null);
const newStatus = ref("");
const internalNote = ref("");
const loading = ref(false);
const errorMessage = ref("");

/* Load case */
async function loadCase() {
  if (!props.caseId) {
    errorMessage.value = "Please select a case first";
    caseData.value = null;
    return;
  }

  errorMessage.value = "";
  const res = await api.get(`/api/dca/cases/${props.caseId}`);
  caseData.value = res.data;
  newStatus.value = caseData.value.status;
}

/* Initial + reactive load */
onMounted(loadCase);
watch(() => props.caseId, loadCase);

/* Submit */
async function submitUpdate() {
  if (!props.caseId) {
    errorMessage.value = "Please select a case first";
    return;
  }

  loading.value = true;

  await api.post(`/api/dca/cases/${props.caseId}/update-status`, {
    status: newStatus.value,
    note: internalNote.value
  });

  loading.value = false;
  emit("close");
}

/* Cancel */
function cancel() {
  emit("close");
}
</script>

<template>
  <div class="update-panel-wrapper">
    <div class="update-panel">

      <!-- 🔴 ALERT -->
      <div v-if="errorMessage" class="alert">
        {{ errorMessage }}
      </div>

      <!-- Header -->
      <div class="panel-header">
        <h2>Update Status</h2>
      </div>

      <!-- Body -->
      <div v-if="caseData" class="panel-body">
        <p><strong>Case ID:</strong> {{ caseData.case_id }}</p>
        <p><strong>Customer:</strong> {{ caseData.customer }}</p>

        <label>New Status: </label>
        <select v-model="newStatus">
          <option value="Paid">Paid</option>
          <option value="Escalate">Escalate</option>
        </select>
        <div class="intNote">
        <label>Internal Note:</label> 
        <br>
        <textarea v-model="internalNote" rows="3"></textarea>
        </div>

        <div class="actions">
          <button @click="cancel">Cancel</button>
          <button
            :disabled="loading"
            @click="submitUpdate"
          >
            Update Status
          </button>
        </div>
      </div>

      <!-- Empty -->
      <div v-else class="empty">
        Select a case to update its status.
      </div>

    </div>
  </div>
</template>

<style scoped>
.update-panel-wrapper {
  margin-top: 24px;
  display: flex;
  justify-content: center;
  margin-bottom:50px;
}

.update-panel {
  width: 420px;
  border: 2px solid #d1d5db;
  background: #fff;
  border-radius: 8px;
  height:350px;
}

/* ALERT */
.alert {
  background: #fee2e2;
  color: #991b1b;
  padding: 12px;
  font-weight: 600;
}

/* Header */
.panel-header {
  padding: 16px;
  border-bottom: 1px solid #e5e7eb;
}

/* Body */
.panel-body {
  padding: 16px;
}

.actions {
  display: flex;
  justify-content: space-between;
  margin-top: 16px;
}
.intNote{
margin-top:15px;
}
</style>
