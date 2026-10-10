from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)

# (region, latency_ms, uptime_pct)
DATA = [
    ("apac", 222.48, 98.056), ("apac", 142.27, 98.209), ("apac", 138.77, 97.109),
    ("apac", 200.24, 98.563), ("apac", 103.71, 97.732), ("apac", 194.84, 97.546),
    ("apac", 200.9, 98.179), ("apac", 157.37, 99.3), ("apac", 164.23, 98.321),
    ("apac", 117.57, 98.549), ("apac", 155.47, 99.247), ("apac", 194.34, 98.686),
    ("emea", 234.75, 97.184), ("emea", 174.54, 98.545), ("emea", 155.8, 97.994),
    ("emea", 160.65, 99.186), ("emea", 178.86, 98.813), ("emea", 119.65, 98.334),
    ("emea", 140.52, 97.664), ("emea", 131.95, 97.599), ("emea", 193.67, 99.013),
    ("emea", 122.46, 99.161), ("emea", 179.1, 97.223), ("emea", 108.85, 97.975),
    ("amer", 125.96, 97.197), ("amer", 168.63, 97.941), ("amer", 151.44, 98.721),
    ("amer", 188.98, 98.373), ("amer", 148.47, 98.862), ("amer", 113.85, 99.275),
    ("amer", 138.81, 98.021), ("amer", 186.16, 98.543), ("amer", 140.04, 97.314),
    ("amer", 146.76, 97.48), ("amer", 181.23, 97.501), ("amer", 123.98, 97.519),
]


class Req(BaseModel):
    regions: list[str]
    threshold_ms: float = 180


@app.get("/")
def health():
    return {"status": "ok"}


@app.post("/")
def metrics(req: Req):
    out = {}
    for r in req.regions:
        rows = [d for d in DATA if d[0] == r]
        if not rows:
            continue
        lat = np.array([d[1] for d in rows])
        up = np.array([d[2] for d in rows])
        out[r] = {
            "avg_latency": round(float(lat.mean()), 3),
            "p95_latency": round(float(np.percentile(lat, 95)), 3),
            "avg_uptime": round(float(up.mean()), 3),
            "breaches": int((lat > req.threshold_ms).sum()),
        }
    return {"regions": out}