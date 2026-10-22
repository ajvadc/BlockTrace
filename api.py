"""
BlockTrace API — FastAPI backend.

Provides forensic blockchain analysis, risk scoring, detection heuristics,
and audit certificates. Fully integrated with both Neo4j (graph database)
and embedded SQLite (zero-config local fallback engine).

Run with:
    uvicorn api:app --reload --port 8000

Interactive API docs:
    http://localhost:8000/docs
"""

import os
import time
import json as jsonlib
from typing import Optional, List

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from logic import (
    short, risk_tier, compute_wallet_risk, build_narrative,
    check_sanctions, get_entity_label, compute_certificate_hash, verify_certificate
)
import case_manager
from report_generator import generate_report
from curated_seeds import CURATED_SEEDS
from db import (
    load_transactions, get_graph_data, get_summary_stats, get_hub_wallets,
    get_fanout_wallets, get_peel_chains, get_round_number_transactions,
    get_circular_flows, get_all_wallet_addresses, clear_graph,
    load_case_edges, get_paths_between, get_last_certificate, store_certificate,
    get_active_backend_name
)

load_dotenv()

ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
ETHERSCAN_URL = "https://api.etherscan.io/v2/api"

CHAIN_OPTIONS = {
    "Ethereum": 1,
    "BNB Smart Chain": 56,
    "Polygon": 137,
}

CURATED_CASES = {
    "Ronin Bridge Hack ($600M, 2022)": {
        "address": "0x098b716b8aaf21512996dc57eb0615e2383e2f96",
        "chainid": 1,
        "description": "Wallet linked to the Axie Infinity / Ronin Bridge exploit. "
                        "Sanctioned by the U.S. Treasury (OFAC) and attributed to the Lazarus Group."
    },
    "Poly Network Hack ($611M, 2021)": {
        "address": "0xc8a65fadf0e0ddaf421f28feab69bf6e2e589963",
        "chainid": 1,
        "description": "Largest DeFi exploit at the time, draining assets across Ethereum, BSC, "
                        "and Polygon. Most funds were later voluntarily returned by the attacker, "
                        "but the full on-chain trail remains public."
    },
    "Wormhole Bridge Hack ($321M, 2022)": {
        "address": "0x629e7da20197a5429d30da36e77d06cdf796b71a",
        "chainid": 1,
        "description": "Exploit of the Ethereum-Solana Wormhole token bridge. This address is "
                        "directly labeled 'Wormhole Network Exploiter' on Etherscan."
    }
}

app = FastAPI(
    title="BlockTrace API",
    description="Explainable blockchain crime investigation — REST backend.",
    version="1.0.0",
)

# Dev-friendly CORS: allows any frontend (React dev server, etc.) to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Request/response models ====================

class ExpandRequest(BaseModel):
    wallet: str
    hops: int = Field(2, ge=1, le=3)
    tx_per_wallet: int = Field(15, ge=5, le=30)
    chain: str = "Ethereum"


class PathRequest(BaseModel):
    source: str
    destination: str
    max_hops: int = Field(4, ge=1, le=6)
    tx_per_wallet: int = Field(15, ge=5, le=30)
    chain: str = "Ethereum"


class SaveCaseRequest(BaseModel):
    name: str
    start_wallet: Optional[str] = None


class CertificateRequest(BaseModel):
    start_wallet: Optional[str] = None


class CertificateVerifyRequest(BaseModel):
    certificate_hash: str
    previous_hash: str
    payload: dict


# ==================== Blockchain I/O & Graph Expansion ====================

def fetch_transactions(wallet_address: str, limit: int = 15, chainid: int = 1) -> list:
    """Fetches recent external transactions for a wallet from Etherscan API."""
    params = {
        "chainid": chainid,
        "module": "account",
        "action": "txlist",
        "address": wallet_address,
        "startblock": 0,
        "endblock": 99999999,
        "sort": "desc",
        "apikey": ETHERSCAN_API_KEY
    }
    try:
        response = requests.get(ETHERSCAN_URL, params=params, timeout=3)
        data = response.json()
        if data.get("status") != "1":
            return []
        return data.get("result", [])[:limit]
    except Exception as e:
        return []


def expand_from_wallet(start_wallet: str, hops: int = 2, tx_per_wallet: int = 15, chainid: int = 1) -> int:
    """Traverses outward from start_wallet up to `hops` deep, loading transactions into graph."""
    visited = set()
    current_layer = {start_wallet}

    for hop in range(hops):
        next_layer = set()
        for wallet in current_layer:
            if wallet in visited:
                continue
            visited.add(wallet)
            txs = fetch_transactions(wallet, limit=tx_per_wallet, chainid=chainid)
            new_wallets = load_transactions(txs)
            next_layer.update(new_wallets)
            time.sleep(0.05)
        current_layer = next_layer - visited

    return len(visited)


def expand_until_found(source: str, destination: str, max_hops: int = 6, tx_per_wallet: int = 15, chainid: int = 1):
    """Bidirectional / outward search until destination is encountered in graph."""
    destination_lower = destination.lower()
    existing = {a.lower() for a in get_all_wallet_addresses()}
    if destination_lower in existing:
        return 0, True

    visited = set()
    current_layer = {source}
    found = False

    for hop in range(max_hops):
        next_layer = set()
        for wallet in current_layer:
            if wallet in visited:
                continue
            visited.add(wallet)
            txs = fetch_transactions(wallet, limit=tx_per_wallet, chainid=chainid)
            new_wallets = load_transactions(txs)
            next_layer.update(new_wallets)
            if destination_lower in {w.lower() for w in new_wallets}:
                found = True
            time.sleep(0.05)
        current_layer = next_layer - visited
        if found:
            break

    return len(visited), found


def _resolve_chainid(chain_name: str) -> int:
    if chain_name not in CHAIN_OPTIONS:
        raise HTTPException(status_code=400, detail=f"Unknown chain '{chain_name}'. Valid options: {list(CHAIN_OPTIONS.keys())}")
    return CHAIN_OPTIONS[chain_name]


# ==================== Endpoints ====================

@app.get("/")
def health_check():
    return {
        "status": "ok",
        "service": "BlockTrace API",
        "database_backend": get_active_backend_name()
    }


@app.get("/db/status")
def db_status():
    backend = get_active_backend_name()
    wallets, txs = get_summary_stats()
    return {
        "backend": backend,
        "wallets_count": wallets,
        "transactions_count": txs,
        "status": "healthy"
    }


@app.get("/chains")
def list_chains():
    return {"chains": list(CHAIN_OPTIONS.keys())}


@app.get("/curated-cases")
def list_curated_cases():
    return {
        "cases": [
            {"name": name, "address": info["address"], "chainid": info["chainid"], "description": info["description"]}
            for name, info in CURATED_CASES.items()
        ]
    }


@app.post("/curated-cases/{case_name}/load")
def load_curated_case(case_name: str):
    if case_name not in CURATED_CASES:
        raise HTTPException(status_code=404, detail="Unknown curated case name.")
    info = CURATED_CASES[case_name]
    clear_graph()

    # Instant load of verified curated seed dataset
    if case_name in CURATED_SEEDS:
        load_transactions(CURATED_SEEDS[case_name])

    # Augment with live on-chain transactions if available
    try:
        live_txs = fetch_transactions(info["address"], limit=15, chainid=info["chainid"])
        if live_txs:
            load_transactions(live_txs)
    except Exception:
        pass

    wallets_count, _ = get_summary_stats()
    return {"wallets_visited": max(wallets_count, 1), "start_wallet": info["address"]}


@app.post("/expand")
def expand(req: ExpandRequest):
    chainid = _resolve_chainid(req.chain)
    visited = expand_from_wallet(req.wallet, hops=req.hops, tx_per_wallet=req.tx_per_wallet, chainid=chainid)
    return {"wallets_visited": visited, "start_wallet": req.wallet}


@app.post("/clear")
def clear():
    clear_graph()
    return {"status": "cleared"}


@app.get("/summary")
def summary():
    wallets, txs = get_summary_stats()
    return {"wallets_traced": wallets, "transactions_mapped": txs}


@app.get("/graph")
def graph():
    edges = get_graph_data()
    return {"edges": [{"from": f, "to": t, "value": v} for f, t, v in edges]}


@app.get("/detections/hub")
def detections_hub():
    return {"results": [{"wallet": w, "total_txs": c, "label": get_entity_label(w)} for w, c in get_hub_wallets()]}


@app.get("/detections/fanout")
def detections_fanout():
    return {"results": [{"wallet": w, "distinct_recipients": c, "label": get_entity_label(w)} for w, c in get_fanout_wallets()]}


@app.get("/detections/peel-chains")
def detections_peel():
    return {"results": [{"wallet": w, "main_amount": m, "peel_amount": p, "label": get_entity_label(w)} for w, m, p in get_peel_chains()]}


@app.get("/detections/round-number")
def detections_round():
    return {"results": [{"from": f, "to": t, "value": v} for f, t, v in get_round_number_transactions()]}


@app.get("/detections/circular")
def detections_circular():
    return {"results": [{"wallet": w, "hops": h, "label": get_entity_label(w)} for w, h in get_circular_flows()]}


@app.get("/sanctions")
def sanctions():
    matches = check_sanctions(get_all_wallet_addresses())
    return {"matches": [{"wallet": addr, **entry} for addr, entry in matches]}


@app.get("/risk")
def risk():
    hub_data = get_hub_wallets()
    fanout_data = get_fanout_wallets()
    peel_data = get_peel_chains()
    round_data = get_round_number_transactions()
    circular_data = get_circular_flows()
    sanctioned = {addr for addr, _ in check_sanctions(get_all_wallet_addresses())}

    rows = compute_wallet_risk(hub_data, fanout_data, peel_data, round_data, circular_data,
                                sanctioned_addresses=sanctioned)
    result = []
    for wallet, signals, score in rows:
        tier_label, _ = risk_tier(score)
        result.append({
            "wallet": wallet,
            "signals": signals,
            "score": score,
            "tier": tier_label,
            "label": get_entity_label(wallet)
        })
    return {"results": result}


@app.get("/narrative")
def narrative(start_wallet: Optional[str] = None):
    hub_data = get_hub_wallets()
    fanout_data = get_fanout_wallets()
    peel_data = get_peel_chains()
    round_data = get_round_number_transactions()
    circular_data = get_circular_flows()
    sanctioned = {addr for addr, _ in check_sanctions(get_all_wallet_addresses())}
    risk_rows = compute_wallet_risk(hub_data, fanout_data, peel_data, round_data, circular_data,
                                     sanctioned_addresses=sanctioned)
    wallets_count, txs_count = get_summary_stats()

    if not start_wallet:
        edges = get_graph_data()
        start_wallet = edges[0][0] if edges else ""

    paragraphs = build_narrative(
        start_wallet, wallets_count, txs_count,
        hub_data, fanout_data, peel_data, round_data, circular_data, risk_rows
    )
    return {"paragraphs": paragraphs}


@app.post("/path")
def find_path(req: PathRequest):
    chainid = _resolve_chainid(req.chain)
    visited, found = expand_until_found(
        req.source, req.destination, max_hops=req.max_hops,
        tx_per_wallet=req.tx_per_wallet, chainid=chainid
    )
    paths = get_paths_between(req.source, req.destination, max_hops=req.max_hops)
    return {"found": len(paths) > 0, "wallets_visited": visited, "paths": paths}


@app.get("/cases")
def list_cases():
    cases = case_manager.list_cases()
    return {"cases": [{"name": n, "saved_at": s, "edge_count": c} for n, s, c in cases]}


@app.post("/cases")
def save_case(req: SaveCaseRequest):
    edges = get_graph_data()
    if not edges:
        raise HTTPException(status_code=400, detail="Nothing to save — the graph is empty.")
    start = req.start_wallet or edges[0][0]
    try:
        path = case_manager.save_case(req.name, start, edges)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"status": "saved", "path": path, "edge_count": len(edges)}


@app.post("/cases/{name}/load")
def load_case(name: str):
    case_data = case_manager.load_case(name)
    if not case_data:
        raise HTTPException(status_code=404, detail="Case not found.")
    clear_graph()
    load_case_edges(case_data["edges"])
    return {
        "status": "loaded",
        "name": case_data["name"],
        "edge_count": case_data["edge_count"],
        "start_wallet": case_data.get("start_wallet")
    }


@app.delete("/cases/{name}")
def delete_case(name: str):
    deleted = case_manager.delete_case(name)
    if not deleted:
        raise HTTPException(status_code=404, detail="Case not found.")
    return {"status": "deleted"}


@app.post("/certificate")
def issue_certificate(req: CertificateRequest):
    edges = get_graph_data()
    if not edges:
        raise HTTPException(status_code=400, detail="Nothing to certify — the graph is empty.")

    hub_data = get_hub_wallets()
    fanout_data = get_fanout_wallets()
    peel_data = get_peel_chains()
    round_data = get_round_number_transactions()
    circular_data = get_circular_flows()
    sanctioned = {addr for addr, _ in check_sanctions(get_all_wallet_addresses())}
    risk_rows = compute_wallet_risk(hub_data, fanout_data, peel_data, round_data, circular_data,
                                     sanctioned_addresses=sanctioned)
    wallets_count, txs_count = get_summary_stats()
    start_wallet = req.start_wallet or edges[0][0]

    payload = {
        "start_wallet": start_wallet,
        "wallets_traced": wallets_count,
        "transactions_mapped": txs_count,
        "hub_wallets": hub_data[:10],
        "fanout_wallets": fanout_data[:10],
        "peel_chains": [(w, m, p) for w, m, p in peel_data[:10]],
        "round_number_txs": round_data[:10],
        "circular_flows": circular_data[:10],
        "sanctions_matches": list(sanctioned),
        "risk_summary": [(w, s, sc) for w, s, sc in risk_rows[:10]],
    }

    prev_hash, _ = get_last_certificate()
    prev_hash = prev_hash or "GENESIS"
    new_hash = compute_certificate_hash(payload, prev_hash)
    created_at = time.strftime("%Y-%m-%dT%H:%M:%S")
    store_certificate(new_hash, prev_hash, start_wallet, created_at)

    return {
        "certificate_hash": new_hash,
        "previous_hash": prev_hash,
        "created_at": created_at,
        "payload": payload,
        "verification_note": "To verify: POST this exact object to /certificate/verify."
    }


@app.post("/certificate/verify")
def verify_cert(req: CertificateVerifyRequest):
    is_valid = verify_certificate(req.payload, req.previous_hash, req.certificate_hash)
    return {"valid": is_valid}


@app.get("/report")
def report(start_wallet: Optional[str] = None):
    wallet = start_wallet or "0x098B716B8Aaf21512996dC57EB0615e2383E2f96"
    output_path = "investigation_report.pdf"
    generate_report(wallet, output_path=output_path)
    return FileResponse(output_path, media_type="application/pdf", filename="investigation_report.pdf")
