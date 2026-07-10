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
const note = ref("");
const loading = ref(false);

/* Submit note */
async function submitNote() {
  if (!note.value.trim()) {
    alert("Please enter a note");
    return;
  }

  loading.value = true;

  // 🔹 Backend endpoint can be finalized later
  await api.post(`/api/dca/cases/${props.caseId}/notes`, {
    note: note.value
  });

  loading.value = false;
  emit("close");
}
</script>

<template>
  <div class="update-panel-wrapper">
    <div class="update-panel">
      <!-- Header -->
      <div class="panel-header">
        <h2>Add Notes</h2>
      </div>

      <!-- Body -->
      <div class="panel-body">
        <div class="field">
          <label>Internal Note</label>
          <textarea
            v-model="note"
            rows="4"
            placeholder="Add internal notes here..."
          ></textarea>
        </div>

        <div class="actions">
          <button class="cancel" @click="emit('close')">
            Cancel
          </button>
          <button
            class="submit"
            :disabled="loading"
            @click="submitNote"
          >
            Save Note
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
  padding: 8px 20px;
  border: none;
}

button.submit:disabled {
  opacity: 0.6;
}
</style>

