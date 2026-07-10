<!-- src/views/UploadCases.vue -->
<script setup>
import api from "../services/api";
const upload = async (e) => {
  const form = new FormData();
  form.append("file", e.target.files[0]);
  await api.post("/cases/upload", form);
  alert("Uploaded");
};
</script>

<template>
  <input type="file" @change="upload" />
</template>
