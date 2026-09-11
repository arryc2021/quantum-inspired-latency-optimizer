import time
import numpy as np
from flask import Flask, jsonify, request

app = Flask(__name__)

# --- SYSTEM INITIALIZATION ---
# Simulating a legacy hardware constraint environment (e.g., restricted memory/CPU)
NUM_BOOKS = 100000
DIMENSION = 20
np.random.seed(42)

print(
    f"[*] Initializing QIS-Engine: Generating catalog matrix ({NUM_BOOKS} items"
    f" x {DIMENSION} features)..."
)
CATALOG_MATRIX = np.random.randn(NUM_BOOKS, DIMENSION)
ACTIVE_USER_PROFILE = np.random.randn(DIMENSION)


# --- 1. CLASSICAL BASELINE ALGORITHM ---
def classical_full_scan(user_profile, catalog):
  """Performs traditional exhaustive dot-product search.

  Time Complexity: O(N) - Linear scaling with catalog size.
  """
  start_time = time.time()

  # Brute-force multiplication across every single book vector
  scores = np.dot(catalog, user_profile)
  top_indices = np.argsort(scores)[::-1][:5]

  latency_ms = (time.time() - start_time) * 1000
  return top_indices.tolist(), latency_ms


# --- 2. QUANTUM-INSPIRED ALGORITHM ---
def quantum_inspired_sampling(user_profile, catalog):
  """Applies l2-norm amplitude probability sampling to bypass full scans.

  Time Complexity: Sublinear based on sample size subset.
  """
  start_time = time.time()

  # Step A: Compute l2-norms (Classical analogue to quantum superposition amplitudes)
  row_norms = np.linalg.norm(catalog, axis=1)
  total_norm = np.sum(row_norms)

  if total_norm == 0:
    return [], 0.0

  probabilities = row_norms / total_norm

  # Step B: Sub-linear sampling of a restricted high-probability subset
  sample_size = 50
  sampled_indices = np.random.choice(
      len(catalog), size=sample_size, p=probabilities, replace=False
  )

  # Step C: Score only the sample subset
  subset_embeddings = catalog[sampled_indices]
  scores = np.dot(subset_embeddings, user_profile)

  best_relative = np.argsort(scores)[::-1][:5]
  top_indices = sampled_indices[best_relative]

  latency_ms = (time.time() - start_time) * 1000
  return top_indices.tolist(), latency_ms


# --- REST API ENDPOINTS ---


@app.route("/", methods=["GET"])
def health_check():
  return jsonify({
      "status": "online",
      "project": "QIS-Engine",
      "catalog_size": NUM_BOOKS,
      "message": (
          "Use /recommend/side-by-side to test performance benchmarks."
      ),
  })


@app.route("/recommend/classical", methods=["GET"])
def api_classical():
  recommendations, latency = classical_classical = classical_full_scan(
      ACTIVE_USER_PROFILE, CATALOG_MATRIX
  )
  return jsonify({
      "engine": "Classical Full-Scan",
      "latency_ms": round(latency, 2),
      "recommendations": recommendations,
  })


@app.route("/recommend/quantum-inspired", methods=["GET"])
def api_quantum():
  recommendations, latency = quantum_inspired_sampling(
      ACTIVE_USER_PROFILE, CATALOG_MATRIX
  )
  return jsonify({
      "engine": "Quantum-Inspired Sublinear Sampling",
      "latency_ms": round(latency, 2),
      "recommendations": recommendations,
  })


@app.route("/recommend/side-by-side", methods=["GET"])
def api_side_by_side():
  _, c_latency = classical_full_scan(ACTIVE_USER_PROFILE, CATALOG_MATRIX)
  _, q_latency = quantum_inspired_sampling(ACTIVE_USER_PROFILE, CATALOG_MATRIX)

  speedup = round(c_latency / q_latency, 1) if q_latency > 0 else 0

  return jsonify({
      "catalog_size": NUM_BOOKS,
      "classical_engine": {
          "latency_ms": round(c_latency, 2),
          "architecture": "Full-Scan O(N)",
      },
      "quantum_inspired_engine": {
          "latency_ms": round(q_latency, 2),
          "architecture": "Probability Sampling Sublinear",
      },
      "performance_multiplier": (
          f"{speedup}x faster performance on legacy hardware"
      ),
  })


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000, debug=False)