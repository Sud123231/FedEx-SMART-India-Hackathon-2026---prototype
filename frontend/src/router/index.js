import { createRouter, createWebHistory } from "vue-router";
import api from "../services/api";

/* Enterprise views */
import Overview from "../views/Overview.vue";
import UploadCases from "../views/UploadCases.vue";
import Cases from "../views/Cases.vue";
import Analytics from "../views/Analytics.vue";

/* Auth */
import Login from "../views/Login.vue";

const routes = [
  /* -------- PUBLIC -------- */
  {
    path: "/login",
    component: Login
  },

  /* -------- ENTERPRISE -------- */
  {
    path: "/enterprise",
    component: Overview,
    meta: { role: "ENTERPRISE" }
  },
  {
    path: "/enterprise/upload",
    component: UploadCases,
    meta: { role: "ENTERPRISE" }
  },
  {
    path: "/enterprise/cases",
    component: Cases,
    meta: { role: "ENTERPRISE" }
  },
  {
    path: "/enterprise/analytics",
    component: Analytics,
    meta: { role: "ENTERPRISE" }
  },

  /* -------- DCA -------- */
  {
    path: "/dca",
    component: () => import("../views/dca/Dashboard.vue"),
    meta: { role: "DCA" }
  },

  /* -------- DEFAULT -------- */
  {
    path: "/",
    redirect: "/login"
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

/* -------- GLOBAL ROUTE GUARD -------- */
router.beforeEach(async (to) => {
  // Allow login page
  if (to.path === "/login") {
    return true;
  }

  // Public routes without role metadata
  if (!to.meta.role) {
    return true;
  }

  try {
    const res = await api.get("/api/auth/me");

    if (res.data.role !== to.meta.role) {
      return "/login";
    }

    return true;
  } catch {
    return "/login";
  }
});

export default router;
