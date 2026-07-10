<script setup>
import { ref } from "vue";
import api from "../../services/api";

/* Props */
const props = defineProps({
  caseId: {
    type: Number,
    required: true
  }
});

const emit = defineEmits(["close"]);

/* State */
const reason = ref("");
const loading = ref(false);

/* Submit escalation request */
async function submitEscalation() {
  if (!reason.value.trim()) {
    alert("Please provide a reason for escalation");
    return;
  }

  loading.value = true;

  await api.post(
    `/api/dca/cases/${props.caseId}/request-escalation`,
    {
      reason: reason.value
    }
  );

  loading.value = false;
  emit("close");
}
</script>

<template>
  <div class="update-panel-wrapper">
    <div class="update-panel">
      <!-- Header -->
      <div class="panel-header">
        <h2>Request Escalation</h2>
      </div>

      <!-- Body -->
      <div class="panel-body">
        <div class="field">
          <label>Reason for Escalation</label>
          <textarea
            v-model="reason"
            rows="4"
            placeholder="Explain why this case needs escalation..."
          ></textarea>
        </div>

        <div class="actions">
          <button class="cancel" @click="emit('close')">
            Cancel
          </button>
          <button
            class="submit"
            :disabled="loading"
            @click="submitEscalation"
          >
            Request Escalation
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.update-panel-wrapper {
  margin-top: 16px;
  display: flex;
  justify-content: center;
  margin-bottom: 32px;
}

.update-panel {
  width: 100%;
  max-width: 480px;
  background: #ffffff;
  border: 1px solid #d1d5db;
  border-radius: 8px;
}

.panel-header {
  padding: 16px 20px;
  border-bottom: 1px solid #e5e7eb;
  font-size: 18px;
  font-weight: 600;
}

.panel-body {
  padding: 20px;
}

.field {
  margin-bottom: 16px;
}

.field label {
  font-weight: 600;
  margin-bottom: 6px;
  display: block;
}

textarea {
  width: 100%;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  padding: 8px 10px;
}

.actions {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
}

button.cancel {
  background: #e5e7eb;
  border: 1px solid #9ca3af;
  padding: 8px 20px;
}

button.submit {
  background: #475569;
  color: white;
  border: none;
}

button.submit:hover {
  background: #334155;
}

button.submit:disabled {
  opacity: 0.6;
}
</style>

