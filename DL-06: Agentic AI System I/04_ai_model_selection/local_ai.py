### local_ai.py - local PyTorch models (student data never leaves the server)
### 1) TextClassifier : embedding -> MLP (router intent and request type)
### 2) RiskModel      : MLP for academic risk from 4 features, explained with gradients

import json
import re
import torch
import torch.nn as nn

import config
import embedder

RISK_FEATURES = ["gpa", "credits", "failed_courses", "absence_rate"]
### scale features to roughly 0-1
RISK_SCALE = torch.tensor([4.0, 22.0, 5.0, 1.0])
RISK_BASELINE = {"gpa": 2.8, "credits": 18.0, "failed_courses": 0.0, "absence_rate": 0.1}


class TextClassifier(nn.Module):
    def __init__(self, dim, n_classes):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(dim, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, n_classes),
        )

    def forward(self, x):
        return self.net(x)


class RiskModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(len(RISK_FEATURES), 16),
            nn.ReLU(),
            nn.Linear(16, 1),
        )

    def forward(self, x):
        return self.net(x).squeeze(-1)


### ---------- load models from file (cached) ----------
_cache = {}


def load(name):
    if name not in _cache:
        saved = torch.load(config.MODEL_DIR / f"{name}.pt", weights_only=False)
        if name == "risk":
            model = RiskModel()
        else:
            model = TextClassifier(saved["dim"], len(saved["labels"]))
        model.load_state_dict(saved["state_dict"])
        model.eval()
        _cache[name] = (model, saved)
    return _cache[name]


def predict_text(name, text):
    ### returns (label, probability, model version)
    model, saved = load(name)
    x = embedder.encode([text])
    with torch.no_grad():
        probs = torch.softmax(model(x), dim=-1)[0]
    best = int(torch.argmax(probs))
    return saved["labels"][best], float(probs[best]), saved["version"]


def extract_risk_features(text):
    ### read numbers from text, e.g. "เกรด 1.8 ติด F 2 วิชา ขาดเรียน 30%"
    low = text.lower()
    gpa = re.search(r"(?:gpa|เกรดเฉลี่ย|เกรด)\s*(?:สะสม)?\s*([0-4](?:\.\d+)?)", low)
    ### GPA must be 0.00-4.00 (e.g. 4.5 is invalid, ask again)
    if not gpa or float(gpa.group(1)) > 4.0:
        return None
    failed = re.search(r"(?:ติด\s*f|failed)\s*(\d+)", low)
    absence = re.search(r"(?:ขาดเรียน|absence|absent)\s*(\d+)\s*%", low)
    credits = re.search(r"(\d+)\s*(?:หน่วยกิต|credits)", low)
    return {
        "gpa": float(gpa.group(1)),
        "credits": float(credits.group(1)) if credits else 15.0,
        "failed_courses": float(failed.group(1)) if failed else 0.0,
        "absence_rate": float(absence.group(1)) / 100 if absence else 0.1,
    }


def predict_risk(features):
    ### predict + find the strongest features with gradient x (input - baseline)
    ### baseline = typical student; positive = more risk, negative = less risk
    model, saved = load("risk")
    x = torch.tensor([[features[f] for f in RISK_FEATURES]]) / RISK_SCALE
    baseline = torch.tensor([[RISK_BASELINE[f] for f in RISK_FEATURES]]) / RISK_SCALE
    x.requires_grad_(True)
    logit = model(x)
    prob = torch.sigmoid(logit)
    prob.sum().backward()
    impact = (x.grad * (x - baseline)).detach()[0]
    factors = sorted(zip(RISK_FEATURES, impact.tolist()), key=lambda t: abs(t[1]), reverse=True)
    return float(prob.item()), factors, saved["version"]


def registry():
    path = config.MODEL_DIR / "registry.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
