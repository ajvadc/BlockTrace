"""
Unit tests for db.py — tests the SQLite backend and ensures all database queries work cleanly.
"""

import pytest
from db import SQLiteBackend


@pytest.fixture
def test_db():
    backend = SQLiteBackend(db_path=":memory:")
    yield backend


def test_sqlite_load_transactions_and_summary(test_db):
    txs = [
        {"from": "0xAAA", "to": "0xBBB", "hash": "0x1", "value": 10**18, "timeStamp": 1600000000},
        {"from": "0xAAA", "to": "0xCCC", "hash": "0x2", "value": 2 * 10**18, "timeStamp": 1600000001},
        {"from": "0xBBB", "to": "0xDDD", "hash": "0x3", "value": 5 * 10**17, "timeStamp": 1600000002},
    ]
    wallets = test_db.load_transactions(txs)
    assert len(wallets) == 4

    w_count, tx_count = test_db.get_summary_stats()
    assert w_count == 4
    assert tx_count == 3

    graph = test_db.get_graph_data()
    assert len(graph) == 3


def test_sqlite_hub_wallets(test_db):
    txs = [
        {"from": "0xHUB", "to": "0x1", "hash": "0x1", "value": 10**18},
        {"from": "0xHUB", "to": "0x2", "hash": "0x2", "value": 10**18},
        {"from": "0x3", "to": "0xHUB", "hash": "0x3", "value": 10**18},
        {"from": "0xA", "to": "0xB", "hash": "0x4", "value": 10**18},
    ]
    test_db.load_transactions(txs)
    hubs = test_db.get_hub_wallets()
    assert hubs[0][0] == "0xHUB"
    assert hubs[0][1] == 3


def test_sqlite_fanout_wallets(test_db):
    txs = [
        {"from": "0xFAN", "to": f"0xREC_{i}", "hash": f"0x{i}", "value": 10**18}
        for i in range(5)
    ]
    test_db.load_transactions(txs)
    fanout = test_db.get_fanout_wallets(min_recipients=4)
    assert len(fanout) == 1
    assert fanout[0][0] == "0xFAN"
    assert fanout[0][1] == 5


def test_sqlite_peel_chains(test_db):
    # Wallet sends 10.0 ETH to main recipient and 0.5 ETH to peel recipient (0.5 / 10.0 = 0.05 < 0.15)
    txs = [
        {"from": "0xPEELER", "to": "0xMAIN", "hash": "0x10", "value": 10 * 10**18},
        {"from": "0xPEELER", "to": "0xPEEL", "hash": "0x11", "value": 5 * 10**17},
    ]
    test_db.load_transactions(txs)
    peels = test_db.get_peel_chains()
    assert len(peels) == 1
    mid, bigger, smaller = peels[0]
    assert mid == "0xPEELER"
    assert bigger == 10.0
    assert smaller == 0.5


def test_sqlite_round_number_txs(test_db):
    txs = [
        {"from": "0xA", "to": "0xB", "hash": "0x1", "value": 5 * 10**18},       # 5.0 (round)
        {"from": "0xA", "to": "0xC", "hash": "0x2", "value": 12345678901234},    # fractional
    ]
    test_db.load_transactions(txs)
    rounds = test_db.get_round_number_transactions(min_value=1.0)
    assert len(rounds) == 1
    assert rounds[0][2] == 5.0


def test_sqlite_circular_flows(test_db):
    # A -> B -> C -> A (cycle of length 3)
    txs = [
        {"from": "0xA", "to": "0xB", "hash": "0x1", "value": 10**18},
        {"from": "0xB", "to": "0xC", "hash": "0x2", "value": 10**18},
        {"from": "0xC", "to": "0xA", "hash": "0x3", "value": 10**18},
    ]
    test_db.load_transactions(txs)
    cycles = test_db.get_circular_flows(max_hops=4)
    assert len(cycles) >= 1
    wallets_in_cycle = {c[0] for c in cycles}
    assert "0xA" in wallets_in_cycle
    assert cycles[0][1] == 3


def test_sqlite_paths_between(test_db):
    # A -> B -> C
    txs = [
        {"from": "0xSRC", "to": "0xMID", "hash": "0x1", "value": 1.5 * 10**18},
        {"from": "0xMID", "to": "0xDST", "hash": "0x2", "value": 1.2 * 10**18},
    ]
    test_db.load_transactions(txs)
    paths = test_db.get_paths_between("0xSRC", "0xDST", max_hops=4)
    assert len(paths) == 1
    assert paths[0]["hops"] == 2
    assert paths[0]["wallets"] == ["0xSRC", "0xMID", "0xDST"]


def test_sqlite_certificates(test_db):
    assert test_db.get_last_certificate() == (None, None)
    test_db.store_certificate("HASH1", "GENESIS", "0xWALLET", "2026-10-22T10:00:00")
    h, created = test_db.get_last_certificate()
    assert h == "HASH1"
    assert created == "2026-10-22T10:00:00"
