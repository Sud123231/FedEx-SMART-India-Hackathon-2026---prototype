import io
import base64
import matplotlib
matplotlib.use("Agg")  # ✅ NON-GUI backend
import matplotlib.pyplot as plt
from collections import Counter

def generate_aging_chart(cases):
    buckets = [c.aging_bucket or "Unknown" for c in cases]
    counts = Counter(buckets)

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(counts.keys(), counts.values(), color="#4c72b0")

    ax.set_title("Aging Distribution")
    ax.set_xlabel("Aging Bucket (days)")
    ax.set_ylabel("Number of Cases")

    return _fig_to_base64(fig)


def generate_priority_chart(cases):
    priority = {"High": 0, "Medium": 0, "Low": 0}

    for c in cases:
        if c.prediction.priority_score is None:
            continue
        if c.prediction.priority_score >= 0.7:
            priority["High"] += 1
        elif c.prediction.priority_score >= 0.4:
            priority["Medium"] += 1
        else:
            priority["Low"] += 1
    if all(v == 0 for v in priority.values()):
          return None      

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(priority.keys(), priority.values(), color="#dd8452")

    ax.set_title("AI Priority Distribution")
    ax.set_xlabel("Priority")
    ax.set_ylabel("Number of Cases")

    return _fig_to_base64(fig)


def _fig_to_base64(fig):
    buf = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")
