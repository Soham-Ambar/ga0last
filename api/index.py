from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import numpy as np
import json

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=["Access-Control-Allow-Origin"],
)

# Force headers on every response
@app.middleware("http")
async def cors_all(request, call_next):
    response = await call_next(request)

    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Expose-Headers"] = "Access-Control-Allow-Origin"

    return response


with open("q-vercel-latency.json", "r") as f:
    DATA = json.load(f)


@app.options("/api/latency")
async def options_latency():
    response = Response()

    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Expose-Headers"] = "Access-Control-Allow-Origin"

    return response


@app.get("/api/latency")
async def latency_get():
    return {"status": "ok"}


@app.post("/api/latency")
async def latency(req: dict):
    regions = req["regions"]
    threshold = req["threshold_ms"]

    result = {}

    for region in regions:
        rows = [r for r in DATA if r["region"] == region]

        if not rows:
            continue

        latencies = [r["latency_ms"] for r in rows]
        uptimes = [r["uptime_pct"] for r in rows]

        result[region] = {
            "avg_latency": round(sum(latencies) / len(latencies), 2),
            "p95_latency": round(float(np.percentile(latencies, 95)), 2),
            "avg_uptime": round(sum(uptimes) / len(uptimes), 3),
            "breaches": sum(1 for x in latencies if x > threshold)
        }

    return JSONResponse(content=result)