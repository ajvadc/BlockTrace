"""
End-to-end integration tests for FastAPI backend (api.py).
Tests every endpoint mapped in INTEGRATION_BRIEF.md.
"""

import os
import json
import pytest
from fastapi.testclient import TestClient

from api import app
from db import clear_graph, get_active_backend_name

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_database():
    clear_graph()
    yield
    clear_graph()


def test_health_and_db_status():
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert "database_backend" in data

    res_db = client.get("/db/status")
    assert res_db.status_code == 200
    assert res_db.json()["status"] == "healthy"


def test_chains_list():
    res = client.get("/chains")
    assert res.status_code == 200
    chains = res.json()["chains"]
    assert "Ethereum" in chains
    assert "BNB Smart Chain" in chains
    assert "Polygon" in chains


def test_curated_cases_list():
    res = client.get("/curated-cases")
    assert res.status_code == 200
    cases = res.json()["cases"]
    assert len(cases) >= 6
    case_names = [c["name"] for c in cases]
    assert "Ronin Bridge Hack ($600M, 2022)" in case_names
    assert "Euler Finance Exploit ($197M, 2023)" in case_names


def test_load_curated_case_ronin():
    res = client.post("/curated-cases/Ronin%20Bridge%20Hack%20%28%24600M%2C%202022%29/load")
    assert res.status_code == 200
    data = res.json()
    assert data["wallets_visited"] > 0
    assert data["start_wallet"].lower() == "0x098b716b8aaf21512996dc57eb0615e2383e2f96"

    # Verify graph has edges
    res_graph = client.get("/graph")
    assert res_graph.status_code == 200
    edges = res_graph.json()["edges"]
    assert len(edges) > 0

    # Verify summary
    res_summary = client.get("/summary")
    assert res_summary.status_code == 200
    assert res_summary.json()["wallets_traced"] > 0
    assert res_summary.json()["transactions_mapped"] > 0


def test_findings_endpoints():
    # Load Ronin case to have rich detection data
    client.post("/curated-cases/Ronin%20Bridge%20Hack%20%28%24600M%2C%202022%29/load")

    # Detections
    res_hub = client.get("/detections/hub")
    assert res_hub.status_code == 200
    assert "results" in res_hub.json()

    res_fanout = client.get("/detections/fanout")
    assert res_fanout.status_code == 200
    assert "results" in res_fanout.json()

    res_peel = client.get("/detections/peel-chains")
    assert res_peel.status_code == 200
    assert "results" in res_peel.json()

    res_round = client.get("/detections/round-number")
    assert res_round.status_code == 200
    assert "results" in res_round.json()

    res_circular = client.get("/detections/circular")
    assert res_circular.status_code == 200
    assert "results" in res_circular.json()

    res_sanctions = client.get("/sanctions")
    assert res_sanctions.status_code == 200
    assert "matches" in res_sanctions.json()

    res_risk = client.get("/risk")
    assert res_risk.status_code == 200
    assert "results" in res_risk.json()

    res_narrative = client.get("/narrative")
    assert res_narrative.status_code == 200
    assert len(res_narrative.json()["paragraphs"]) > 0


def test_certificates_flow():
    # Load case first
    client.post("/curated-cases/Ronin%20Bridge%20Hack%20%28%24600M%2C%202022%29/load")

    # Generate certificate
    res_cert = client.post("/certificate", json={"start_wallet": "0x098B716B8Aaf21512996dC57EB0615e2383E2f96"})
    assert res_cert.status_code == 200
    cert_data = res_cert.json()
    assert "certificate_hash" in cert_data
    assert "payload" in cert_data

    # Verify valid certificate
    res_verify = client.post("/certificate/verify", json={
        "certificate_hash": cert_data["certificate_hash"],
        "previous_hash": cert_data["previous_hash"],
        "payload": cert_data["payload"]
    })
    assert res_verify.status_code == 200
    assert res_verify.json()["valid"] is True

    # Verify tampered certificate fails
    tampered_payload = dict(cert_data["payload"])
    tampered_payload["wallets_traced"] = 999999
    res_tampered = client.post("/certificate/verify", json={
        "certificate_hash": cert_data["certificate_hash"],
        "previous_hash": cert_data["previous_hash"],
        "payload": tampered_payload
    })
    assert res_tampered.status_code == 200
    assert res_tampered.json()["valid"] is False


def test_cases_save_load_delete():
    # Load Ronin case
    client.post("/curated-cases/Ronin%20Bridge%20Hack%20%28%24600M%2C%202022%29/load")

    # Save case
    case_name = "Automated_Test_Case"
    res_save = client.post("/cases", json={"name": case_name})
    assert res_save.status_code == 200
    assert res_save.json()["status"] == "saved"

    # List cases
    res_list = client.get("/cases")
    assert res_list.status_code == 200
    names = [c["name"] for c in res_list.json()["cases"]]
    assert case_name in names

    # Clear graph and load saved case
    client.post("/clear")
    assert client.get("/summary").json()["wallets_traced"] == 0

    res_load = client.post(f"/cases/{case_name}/load")
    assert res_load.status_code == 200
    assert res_load.json()["status"] == "loaded"
    assert client.get("/summary").json()["wallets_traced"] > 0

    # Delete case
    res_del = client.delete(f"/cases/{case_name}")
    assert res_del.status_code == 200
    assert res_del.json()["status"] == "deleted"


def test_pdf_report_generation():
    # Load case
    client.post("/curated-cases/Ronin%20Bridge%20Hack%20%28%24600M%2C%202022%29/load")

    res = client.get("/report?start_wallet=0x098B716B8Aaf21512996dC57EB0615e2383E2f96")
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert len(res.content) > 1000  # PDF generated
