### train_local_ai.py - train the 3 PyTorch models, save to models/ + registry.json
### Run: python train_local_ai.py

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "09_backend"))
import setup_path  ### add folders 02-09 to sys.path (must come first)
import json
import random
from datetime import date

import numpy as np
import torch
import torch.nn as nn

import config
import embedder
from local_ai import TextClassifier, RiskModel, RISK_SCALE

torch.manual_seed(42)
random.seed(42)
np.random.seed(42)
VERSION = date.today().strftime("%Y.%m.%d")


def split(n, val_ratio=0.2):
    idx = list(range(n))
    random.shuffle(idx)
    cut = int(n * val_ratio)
    return idx[cut:], idx[:cut]


def train_text_model(name, data):
    ### text -> embedding (same sentence-transformers model as retrieval)
    labels = sorted(data.keys())
    texts, y = [], []
    for i, label in enumerate(labels):
        texts += data[label]
        y += [i] * len(data[label])
    X = embedder.encode(texts)
    y = torch.tensor(y)
    tr, va = split(len(y))

    model = TextClassifier(X.shape[1], len(labels))
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-4)
    loss_fn = nn.CrossEntropyLoss()

    ### basic training loop (full batch, small data)
    for epoch in range(300):
        model.train()
        optimizer.zero_grad()
        loss = loss_fn(model(X[tr]), y[tr])
        loss.backward()
        optimizer.step()

    model.eval()
    with torch.no_grad():
        val_acc = (model(X[va]).argmax(-1) == y[va]).float().mean().item()
    print(f"[{name}] loss={loss.item():.4f} val_acc={val_acc:.2f} ({len(va)} samples)")

    torch.save({"state_dict": model.state_dict(), "labels": labels, "dim": X.shape[1],
                "version": f"{name}-{VERSION}", "embedding_model": config.EMBEDDING_MODEL},
               config.MODEL_DIR / f"{name}.pt")
    return {"version": f"{name}-{VERSION}", "val_accuracy": round(val_acc, 3),
            "train_size": len(tr), "labels": labels}


def make_risk_data(n=2000):
    ### synthetic data; real data needs PDPA approval
    gpa = np.random.uniform(0.8, 4.0, n)
    credits = np.random.randint(6, 23, n).astype(float)
    failed = np.random.poisson(0.7, n).clip(0, 5).astype(float)
    absence = np.random.beta(2, 8, n)
    score = -2.2 * (gpa - 2.0) + 0.8 * failed + 4.0 * (absence - 0.2) - 0.05 * (credits - 15)
    prob = 1 / (1 + np.exp(-score))
    y = (np.random.rand(n) < prob).astype(float)
    X = np.stack([gpa, credits, failed, absence], axis=1)
    return torch.tensor(X, dtype=torch.float32) / RISK_SCALE, torch.tensor(y, dtype=torch.float32)


def train_risk_model():
    X, y = make_risk_data()
    tr, va = split(len(y))
    model = RiskModel()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-2)
    loss_fn = nn.BCEWithLogitsLoss()

    ### mini-batch training
    for epoch in range(60):
        model.train()
        perm = torch.tensor(tr)[torch.randperm(len(tr))]
        for i in range(0, len(perm), 64):
            batch = perm[i:i + 64]
            optimizer.zero_grad()
            loss = loss_fn(model(X[batch]), y[batch])
            loss.backward()
            optimizer.step()

    ### accuracy and F1 on the validation set
    model.eval()
    with torch.no_grad():
        pred = (torch.sigmoid(model(X[va])) > 0.5).float()
    yv = y[va]
    acc = (pred == yv).float().mean().item()
    tp = ((pred == 1) & (yv == 1)).sum().item()
    precision = tp / max(pred.sum().item(), 1)
    recall = tp / max(yv.sum().item(), 1)
    f1 = 2 * precision * recall / max(precision + recall, 1e-9)
    print(f"[risk] val_acc={acc:.2f} f1={f1:.2f}")

    torch.save({"state_dict": model.state_dict(), "version": f"risk-{VERSION}"},
               config.MODEL_DIR / "risk.pt")
    return {"version": f"risk-{VERSION}", "val_accuracy": round(acc, 3), "f1": round(f1, 3),
            "train_size": len(tr), "data": "synthetic", "snapshot_date": str(date.today())}


if __name__ == "__main__":
    config.MODEL_DIR.mkdir(exist_ok=True)
    data = json.loads(config.TRAIN_DATA.read_text(encoding="utf-8"))

    ### model registry: keep old versions for rollback
    path = config.MODEL_DIR / "registry.json"
    reg = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    new = {
        "router": train_text_model("router", data["router"]),
        "request_type": train_text_model("request_type", data["request_type"]),
        "risk": train_risk_model(),
    }
    for name, info in new.items():
        old = reg.get(name)
        history = old.get("history", []) if old else []
        if old:
            history.append({k: v for k, v in old.items() if k != "history"})
        info["history"] = history[-5:]
        reg[name] = info
    path.write_text(json.dumps(reg, ensure_ascii=False, indent=2), encoding="utf-8")
    print("saved models to", config.MODEL_DIR)
