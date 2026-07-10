<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import api from "../services/api";

const email = ref("");
const error = ref("");
const router = useRouter();

async function login() {
  if (!email.value) {
    error.value = "Email is required";
    return;
  }

  try {
    const res = await api.post("/api/auth/login", {
      email: email.value
    });

    if (res.data.role === "ENTERPRISE") {
      router.push("/enterprise");
    } else if (res.data.role === "DCA") {
      router.push("/dca");
    }
  } catch {
    error.value = "Invalid email";
  }
}
</script>

<template>
  <div>
    <h2>Login</h2>

    <input
      v-model="email"
      placeholder="Enter your official email"
    />

    <button @click="login">Login</button>

    <p v-if="error" style="color:red">{{ error }}</p>
  </div>
</template>
