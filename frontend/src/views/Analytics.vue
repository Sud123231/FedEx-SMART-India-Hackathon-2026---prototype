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
  <div class="dashboard-container">
    <h2>Analytics</h2>

    <p class="hint">
      AI insights are derived from historical recovery patterns and model predictions
      to help enterprise teams prioritize and assign cases efficiently.
    </p>

    <!-- KPI Cards -->
    <div class="cards">
      <div class="card">
        <h3>Total Cases</h3>
        <p>{{ metrics.total }}</p>
      </div>

      <div class="card">
        <h3>Closed Cases</h3>
        <p>{{ metrics.closed }}</p>
      </div>

      <div class="card">
        <h3>Escalated Cases</h3>
        <p>{{ metrics.escalated }}</p>
      </div>

      <div class="card">
        <h3>Average Recovery</h3>
        <p>{{ metrics.avg_recovery }}</p>
      </div>
    </div>

    <!-- Charts + AI Insights -->
    <div class="analytics-grid">
      <div class="section">
        <h3>Aging Distribution</h3>
        <img
          v-if="charts.aging"
          :src="'data:image/png;base64,' + charts.aging"
          alt="Aging Distribution Chart"
        />
      </div>

      <div class="section">
        <h3>AI Insights</h3>
        <ul class="ai-insights">
          <li><strong>High Recovery Probability Cases:</strong> {{ metrics.high_recovery }}</li>
          <li><strong>Low Recovery Probability Cases:</strong> {{ metrics.low_recovery }}</li>
          <li><strong>Avg Predicted Recovery:</strong> {{ metrics.avg_predicted_recovery }}%</li>
        </ul>
      </div>
    </div>

    <div class="section">
      <h3>AI Priority Distribution</h3>
      <img
        v-if="charts.priority"
        :src="'data:image/png;base64,' + charts.priority"
        alt="Priority Distribution Chart"
      />
      <p v-else class="hint">
        AI priority scores will appear once prediction models are applied.
      </p>
    </div>
  </div>
</div>  
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "../services/api";

const charts = ref({
  aging: null,
  priority: null,
});

const metrics = ref({
  total: 0,
  closed: 0,
  escalated: 0,
  avg_recovery: 0,
  high_recovery: 0,
  low_recovery: 0,
  avg_predicted_recovery: 0,
  priority: { high: 0, medium: 0, low: 0 },
});

onMounted(async () => {
  // ENTERPRISE CASES
  const casesRes = await api.get("/api/enterprise/cases");
  const cases = casesRes.data;

  // CHARTS
  const chartRes = await api.get("/api/enterprise/analytics/charts");
  charts.value.aging = chartRes.data.aging_chart;
  charts.value.priority = chartRes.data.priority_chart;

  // OVERVIEW METRICS
  const overviewRes = await api.get("/api/enterprise/overview");
  metrics.value.escalated = overviewRes.data.escalated;

  metrics.value.total = cases.length;
  metrics.value.closed = cases.filter(c => c.status === "CLOSED").length;

  // AVERAGE RECOVERY
  const closedCases = cases.filter(
    c => c.status === "CLOSED" && c.recovered_amount !== null
  );

  metrics.value.avg_recovery =
    closedCases.length > 0
      ? Math.round(
          closedCases.reduce((s, c) => s + c.recovered_amount, 0) /
            closedCases.length
        )
      : 0;

  // AI METRICS
  const predictions = cases.filter(c => c.recovery_probability !== null);

  metrics.value.high_recovery =
    predictions.filter(c => c.recovery_probability >= 0.7).length;

  metrics.value.low_recovery =
    predictions.filter(c => c.recovery_probability < 0.3).length;

  metrics.value.avg_predicted_recovery =
    predictions.length > 0
      ? Math.round(
          (predictions.reduce((s, c) => s + c.recovery_probability, 0) /
            predictions.length) * 100
        )
      : 0;

  predictions.forEach(c => {
    if (c.priority_score >= 0.7) metrics.value.priority.high++;
    else if (c.priority_score >= 0.4) metrics.value.priority.medium++;
    else metrics.value.priority.low++;
  });
});
</script>

<style scoped>
/* Page container */
.dashboard-container {
  padding: 24px 32px;
  max-width: 1200px;
  margin: 0 auto;
}

/* Page intro */
.hint {
  color: #555;
  font-size: 16px;
  margin-bottom: 24px;
  max-width: 800px;
}

/* KPI cards */
.cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 32px;
}

.card {
  border: 1px solid #ddd;
  background: #fafafa;
  padding: 16px;
}

.card h3 {
  font-size: 13px;
  color: #666;
  margin-bottom: 6px;
}

.card p {
  font-size: 22px;
  font-weight: bold;
}

/* Sections */
.section {
  margin-top: 32px;
  padding-top: 16px;
  border-top: 1px solid #e0e0e0;
}

.section h3 {
  margin-bottom: 12px;
  font-size: 16px;
}

/* Two-column analytics layout */
.analytics-grid {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 32px;
  margin-top: 16px;
}

/* Images (charts) */
.section img {
  max-width: 100%;
  border: 1px solid #ddd;
  background: #fff;
  padding: 8px;
}

/* AI Insights list */
.section ul {
  padding-left: 18px;
}

.ai-insights li {
  margin-bottom: 8px;
  font-size: 14px;
}
.ai-insights strong {
  color: #333;
}

.section li {
  margin-bottom: 6px;
  font-size: 14px;
}

/* Mobile fallback */
@media (max-width: 900px) {
  .cards {
    grid-template-columns: repeat(2, 1fr);
  }

  .analytics-grid {
    grid-template-columns: 1fr;
  }
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
</style>
