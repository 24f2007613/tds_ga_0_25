import json
import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["POST", "OPTIONS"], allow_headers=["*"])

with open("data.json") as f:
    DATA = json.load(f)

class Req(BaseModel):
    regions: list[str]
    threshold_ms: float = 180

@app.post("/")
def metrics(req: Req):
    out = {}
    for r in req.regions:
        rows = [d for d in DATA if d["region"] == r]
        if not rows:
            continue
        lat = np.array([d["latency_ms"] for d in rows])
        up = np.array([d["uptime_pct"] for d in rows])
        out[r] = {
            "avg_latency": round(float(lat.mean()), 3),
            "p95_latency": round(float(np.percentile(lat, 95)), 3),
            "avg_uptime": round(float(up.mean()), 3),
            "breaches": int((lat > req.threshold_ms).sum()),
        }
    return {"regions": out}