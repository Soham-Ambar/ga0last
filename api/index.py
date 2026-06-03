from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

with open("q-vercel-latency.json") as f:
    DATA = json.load(f)

@app.post("/")
async def latency(req: dict):
    regions = req["regions"]
    threshold = req["threshold_ms"]

    result = {}

    for region in regions:
        rows = [r for r in DATA if r["region"] == region]

        latencies = [r["latency_ms"] for r in rows]
        uptimes = [r["uptime_pct"] for r in rows]

        result[region] = {
            "avg_latency": round(sum(latencies)/len(latencies), 2),
            "p95_latency": round(float(np.percentile(latencies, 95)), 2),
            "avg_uptime": round(sum(uptimes)/len(uptimes), 3),
            "breaches": sum(1 for x in latencies if x > threshold)
        }

    return result