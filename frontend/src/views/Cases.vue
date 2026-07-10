<!-- src/views/Cases.vue -->
<script setup>
import { ref, onMounted } from "vue";
import api from "../services/api";
const cases = ref([]);

onMounted(async () => {
  cases.value = (await api.get("/cases")).data;
});
</script>

<template>
  <table>
    <tr v-for="c in cases" :key="c.id">
      <td>{{ c.tracking_number }}</td>
      <td>{{ c.customer_name }}</td>
      <td>{{ c.amount_due }}</td>
      <td>{{ c.aging_bucket }}</td>
      <td>{{ c.priority_score }}</td>
    </tr>
  </table>
</template>
