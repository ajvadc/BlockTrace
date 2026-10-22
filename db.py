"""
BlockTrace Database Layer.

Provides a unified graph storage interface with dual backend support:
1. Neo4j graph database (production / full Cypher support)
2. SQLite embedded graph engine (zero-dependency, robust local fallback)

Automatic detection:
If DB_BACKEND is 'auto' (default), it checks if Neo4j is reachable.
If Neo4j is available, it uses Neo4j.
If Neo4j is unavailable or not configured, it seamlessly falls back to the
embedded SQLite graph engine without crashing.
"""

import os
import sys
import time
import sqlite3
import hashlib
import logging
from typing import List, Tuple, Dict, Any, Optional
from collections import defaultdict, deque

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("blocktrace.db")

ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")
DB_BACKEND = os.getenv("DB_BACKEND", "auto").lower()
SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", "blocktrace.db")


# ==================== SQLite Backend ====================

class SQLiteBackend:
    """Embedded SQLite implementation of BlockTrace graph operations."""

    def __init__(self, db_path: str = SQLITE_DB_PATH):
        self.db_path = db_path
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        if self.db_path != ":memory:":
            self._conn.execute("PRAGMA journal_mode=WAL;")
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        return self._conn

    def _init_db(self):
        with self._get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS wallets (
                    address TEXT PRIMARY KEY COLLATE NOCASE,
                    label TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS transactions (
                    tx_hash TEXT PRIMARY KEY,
                    from_addr TEXT NOT NULL COLLATE NOCASE,
                    to_addr TEXT NOT NULL COLLATE NOCASE,
                    value REAL NOT NULL,
                    timestamp INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX IF NOT EXISTS idx_tx_from ON transactions(from_addr);
                CREATE INDEX IF NOT EXISTS idx_tx_to ON transactions(to_addr);
                CREATE INDEX IF NOT EXISTS idx_tx_value ON transactions(value);

                CREATE TABLE IF NOT EXISTS certificates (
                    hash TEXT PRIMARY KEY,
                    prev_hash TEXT,
                    wallet TEXT COLLATE NOCASE,
                    created_at TEXT
                );
            """)

    def load_transactions(self, transactions: List[Dict[str, Any]]) -> set:
        new_wallets = set()
        with self._get_connection() as conn:
            for tx in transactions:
                from_addr = tx.get("from")
                to_addr = tx.get("to")
                tx_hash = tx.get("hash")
                if not from_addr or not to_addr or not tx_hash:
                    continue

                try:
                    raw_val = tx.get("value", 0)
                    val_float = float(raw_val)
                    if val_float > 1_000_000:
                        value_eth = val_float / 1e18
                    else:
                        value_eth = val_float
                except (ValueError, TypeError):
                    continue

                if value_eth < 0 or value_eth > 1_000_000:
                    continue

                timestamp = int(tx.get("timeStamp", 0) or 0)

                conn.execute(
                    "INSERT OR IGNORE INTO wallets (address) VALUES (?)",
                    (from_addr,)
                )
                conn.execute(
                    "INSERT OR IGNORE INTO wallets (address) VALUES (?)",
                    (to_addr,)
                )
                conn.execute(
                    """
                    INSERT INTO transactions (tx_hash, from_addr, to_addr, value, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(tx_hash) DO UPDATE SET
                        value = excluded.value,
                        timestamp = excluded.timestamp
                    """,
                    (tx_hash, from_addr, to_addr, value_eth, timestamp)
                )
                new_wallets.add(from_addr)
                new_wallets.add(to_addr)
        return new_wallets

    def get_graph_data(self, limit: int = 300) -> List[Tuple[str, str, float]]:
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT from_addr, to_addr, value FROM transactions ORDER BY rowid DESC LIMIT ?",
                (limit,)
            ).fetchall()
            return [(r["from_addr"], r["to_addr"], float(r["value"])) for r in rows]

    def get_summary_stats(self) -> Tuple[int, int]:
        with self._get_connection() as conn:
            wallet_row = conn.execute("""
                SELECT COUNT(DISTINCT address) AS total_wallets FROM (
                    SELECT from_addr AS address FROM transactions
                    UNION
                    SELECT to_addr AS address FROM transactions
                )
            """).fetchone()
            wallets = wallet_row["total_wallets"] if wallet_row else 0

            tx_row = conn.execute("SELECT COUNT(*) AS total_txs FROM transactions").fetchone()
            txs = tx_row["total_txs"] if tx_row else 0
            return wallets, txs

    def get_hub_wallets(self, limit: int = 1000) -> List[Tuple[str, int]]:
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT wallet, COUNT(*) AS total_txs FROM (
                    SELECT from_addr AS wallet FROM transactions
                    UNION ALL
                    SELECT to_addr AS wallet FROM transactions
                )
                GROUP BY wallet
                ORDER BY total_txs DESC
                LIMIT ?
            """, (limit,)).fetchall()
            return [(r["wallet"], r["total_txs"]) for r in rows]

    def get_fanout_wallets(self, min_recipients: int = 4, limit: int = 1000) -> List[Tuple[str, int]]:
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT from_addr AS wallet, COUNT(DISTINCT to_addr) AS distinct_recipients
                FROM transactions
                GROUP BY from_addr
                HAVING distinct_recipients >= ?
                ORDER BY distinct_recipients DESC
                LIMIT ?
            """, (min_recipients, limit)).fetchall()
            return [(r["wallet"], r["distinct_recipients"]) for r in rows]

    def get_peel_chains(self, limit: int = 1000) -> List[Tuple[str, float, float]]:
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT from_addr, to_addr, value
                FROM transactions
                WHERE value > 0.001
            """).fetchall()

        outgoing = defaultdict(list)
        for r in rows:
            outgoing[r["from_addr"]].append((r["to_addr"], float(r["value"])))

        peel_matches = []
        for mid, recs in outgoing.items():
            best_pair = None
            max_bigger = -1.0
            best_peel = 0.0

            for i in range(len(recs)):
                for j in range(i + 1, len(recs)):
                    to1, val1 = recs[i]
                    to2, val2 = recs[j]
                    if to1.lower() == to2.lower():
                        continue
                    bigger = max(val1, val2)
                    smaller = min(val1, val2)
                    if bigger > 0 and (smaller / bigger) < 0.15:
                        if bigger > max_bigger:
                            max_bigger = bigger
                            best_peel = smaller
                            best_pair = (mid, bigger, smaller)

            if best_pair:
                peel_matches.append(best_pair)

        peel_matches.sort(key=lambda x: x[1], reverse=True)
        return peel_matches[:limit]

    def get_round_number_transactions(self, min_value: float = 1.0, limit: int = 1000) -> List[Tuple[str, str, float]]:
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT from_addr, to_addr, value
                FROM transactions
                WHERE value >= ?
                ORDER BY value DESC
            """, (min_value,)).fetchall()

            results = []
            for r in rows:
                v = float(r["value"])
                if v == int(v):
                    results.append((r["from_addr"], r["to_addr"], v))
                    if len(results) >= limit:
                        break
            return results

    def get_circular_flows(self, max_hops: int = 4, limit: int = 1000) -> List[Tuple[str, int]]:
        with self._get_connection() as conn:
            rows = conn.execute("SELECT from_addr, to_addr FROM transactions").fetchall()

        adj = defaultdict(set)
        for r in rows:
            adj[r["from_addr"]].add(r["to_addr"])

        cycles = []
        all_nodes = list(adj.keys())

        for start_node in all_nodes:
            queue = deque([(start_node, 0)])
            visited_in_path = {start_node}
            shortest_cycle = None

            # BFS from start_node to find shortest path back to start_node with 2 <= hops <= max_hops
            bfs_q = deque([(start_node, 0, [start_node])])
            while bfs_q:
                curr, depth, path = bfs_q.popleft()
                if depth >= max_hops:
                    continue
                for nxt in adj.get(curr, set()):
                    if nxt.lower() == start_node.lower() and depth + 1 >= 2:
                        shortest_cycle = depth + 1
                        break
                    if nxt not in path and depth + 1 < max_hops:
                        bfs_q.append((nxt, depth + 1, path + [nxt]))
                if shortest_cycle:
                    break

            if shortest_cycle:
                cycles.append((start_node, shortest_cycle))

        cycles.sort(key=lambda x: (x[1], x[0]))
        return cycles[:limit]

    def get_all_wallet_addresses(self) -> List[str]:
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT DISTINCT address FROM (
                    SELECT from_addr AS address FROM transactions
                    UNION
                    SELECT to_addr AS address FROM transactions
                )
            """).fetchall()
            return [r["address"] for r in rows]

    def clear_graph(self):
        with self._get_connection() as conn:
            conn.execute("DELETE FROM transactions")
            conn.execute("DELETE FROM wallets")

    def load_case_edges(self, edges: List[Dict[str, Any]]):
        with self._get_connection() as conn:
            for i, e in enumerate(edges):
                synthetic_hash = hashlib.sha256(
                    f"{e['from']}-{e['to']}-{e['value']}-{i}".encode()
                ).hexdigest()
                conn.execute(
                    "INSERT OR IGNORE INTO wallets (address) VALUES (?)",
                    (e["from"],)
                )
                conn.execute(
                    "INSERT OR IGNORE INTO wallets (address) VALUES (?)",
                    (e["to"],)
                )
                conn.execute(
                    """
                    INSERT INTO transactions (tx_hash, from_addr, to_addr, value, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(tx_hash) DO UPDATE SET value = excluded.value
                    """,
                    (synthetic_hash, e["from"], e["to"], float(e["value"]), int(time.time()))
                )

    def get_paths_between(self, source: str, destination: str, max_hops: int = 6, limit: int = 10) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            rows = conn.execute("SELECT from_addr, to_addr, value FROM transactions").fetchall()

        adj = defaultdict(list)
        for r in rows:
            adj[r["from_addr"].lower()].append({
                "from": r["from_addr"],
                "to": r["to_addr"],
                "value": float(r["value"])
            })

        source_lower = source.lower()
        dest_lower = destination.lower()

        # BFS for paths
        queue = deque([([source], [], source_lower)])
        found_paths = []

        while queue and len(found_paths) < limit:
            wallets, rels, curr_lower = queue.popleft()
            if len(rels) >= max_hops:
                continue

            for edge in adj.get(curr_lower, []):
                next_addr = edge["to"]
                next_lower = next_addr.lower()
                if next_lower in [w.lower() for w in wallets]:
                    continue  # avoid cycles

                new_wallets = wallets + [next_addr]
                new_rels = rels + [edge]

                if next_lower == dest_lower:
                    found_paths.append({
                        "wallets": new_wallets,
                        "rels": new_rels,
                        "hops": len(new_rels)
                    })
                    if len(found_paths) >= limit:
                        break
                else:
                    if len(new_rels) < max_hops:
                        queue.append((new_wallets, new_rels, next_lower))

        found_paths.sort(key=lambda p: p["hops"])
        return found_paths

    def get_last_certificate(self) -> Tuple[Optional[str], Optional[str]]:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT hash, created_at FROM certificates ORDER BY created_at DESC LIMIT 1"
            ).fetchone()
            if row:
                return row["hash"], row["created_at"]
            return None, None

    def store_certificate(self, cert_hash: str, prev_hash: str, wallet: str, created_at: str):
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO certificates (hash, prev_hash, wallet, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (cert_hash, prev_hash, wallet, created_at)
            )


# ==================== Neo4j Backend ====================

class Neo4jBackend:
    """Production Neo4j implementation of BlockTrace graph operations."""

    def __init__(self, uri=NEO4J_URI, user=NEO4J_USER, password=NEO4J_PASSWORD, database=NEO4J_DATABASE):
        from neo4j import GraphDatabase
        self.database = database or "neo4j"
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def verify_connectivity(self) -> bool:
        try:
            self.driver.verify_connectivity()
            return True
        except Exception:
            return False

    def load_transactions(self, transactions: List[Dict[str, Any]]) -> set:
        new_wallets = set()
        with self.driver.session(database=self.database) as session:
            for tx in transactions:
                from_addr, to_addr = tx.get("from"), tx.get("to")
                if not to_addr or not from_addr:
                    continue
                try:
                    raw_val = tx.get("value", 0)
                    val_float = float(raw_val)
                    if val_float > 1_000_000:
                        value_eth = val_float / 1e18
                    else:
                        value_eth = val_float
                except (ValueError, TypeError):
                    continue

                if value_eth < 0 or value_eth > 1_000_000:
                    continue

                session.run(
                    """
                    MERGE (a:Wallet {address: $from_addr})
                    MERGE (b:Wallet {address: $to_addr})
                    MERGE (a)-[t:SENT {hash: $tx_hash}]->(b)
                    SET t.value = $value_eth, t.timestamp = $timestamp
                    """,
                    from_addr=from_addr, to_addr=to_addr, tx_hash=tx["hash"],
                    value_eth=value_eth, timestamp=tx.get("timeStamp", "")
                )
                new_wallets.add(from_addr)
                new_wallets.add(to_addr)
        return new_wallets

    def get_graph_data(self, limit: int = 300) -> List[Tuple[str, str, float]]:
        with self.driver.session(database=self.database) as session:
            result = session.run(
                "MATCH (a:Wallet)-[r:SENT]->(b:Wallet) RETURN a.address AS from_addr, b.address AS to_addr, r.value AS value LIMIT $limit",
                limit=limit
            )
            return [(r["from_addr"], r["to_addr"], float(r["value"])) for r in result]

    def get_summary_stats(self) -> Tuple[int, int]:
        with self.driver.session(database=self.database) as session:
            result = session.run(
                "MATCH (w:Wallet) OPTIONAL MATCH (w)-[r:SENT]->() RETURN count(DISTINCT w) AS wallets, count(r) AS txs"
            )
            record = result.single()
            return record["wallets"], record["txs"]

    def get_hub_wallets(self, limit: int = 1000) -> List[Tuple[str, int]]:
        with self.driver.session(database=self.database) as session:
            result = session.run(
                """
                MATCH (w:Wallet)-[r:SENT]-()
                RETURN w.address AS wallet, count(r) AS total_txs
                ORDER BY total_txs DESC LIMIT $limit
                """, limit=limit
            )
            return [(r["wallet"], r["total_txs"]) for r in result]

    def get_fanout_wallets(self, min_recipients: int = 4, limit: int = 1000) -> List[Tuple[str, int]]:
        with self.driver.session(database=self.database) as session:
            result = session.run(
                """
                MATCH (a:Wallet)-[:SENT]->(b:Wallet)
                WITH a, count(DISTINCT b) AS distinct_recipients
                WHERE distinct_recipients >= $min_recipients
                RETURN a.address AS wallet, distinct_recipients
                ORDER BY distinct_recipients DESC LIMIT $limit
                """, min_recipients=min_recipients, limit=limit
            )
            return [(r["wallet"], r["distinct_recipients"]) for r in result]

    def get_peel_chains(self, limit: int = 1000) -> List[Tuple[str, float, float]]:
        with self.driver.session(database=self.database) as session:
            result = session.run(
                """
                MATCH (mid:Wallet)-[r2:SENT]->(next1:Wallet)
                MATCH (mid)-[r3:SENT]->(next2:Wallet)
                WHERE elementId(next1) < elementId(next2) AND r2.value > 0.001 AND r3.value > 0.001
                WITH mid,
                     CASE WHEN r2.value > r3.value THEN r2.value ELSE r3.value END AS bigger,
                     CASE WHEN r2.value > r3.value THEN r3.value ELSE r2.value END AS smaller
                WHERE (smaller / bigger) < 0.15
                WITH mid, bigger, smaller
                ORDER BY bigger DESC
                WITH mid, collect({main: bigger, peel: smaller})[0] AS top_match
                RETURN mid.address AS wallet, top_match.main AS main_amount, top_match.peel AS peel_amount
                ORDER BY main_amount DESC
                LIMIT $limit
                """, limit=limit
            )
            return [(r["wallet"], r["main_amount"], r["peel_amount"]) for r in result]

    def get_round_number_transactions(self, min_value: float = 1.0, limit: int = 1000) -> List[Tuple[str, str, float]]:
        with self.driver.session(database=self.database) as session:
            result = session.run(
                """
                MATCH (a:Wallet)-[r:SENT]->(b:Wallet)
                WHERE r.value >= $min_value AND r.value = toInteger(r.value)
                RETURN a.address AS from_addr, b.address AS to_addr, r.value AS value
                ORDER BY r.value DESC
                LIMIT $limit
                """, min_value=min_value, limit=limit
            )
            return [(r["from_addr"], r["to_addr"], r["value"]) for r in result]

    def get_circular_flows(self, max_hops: int = 4, limit: int = 1000) -> List[Tuple[str, int]]:
        with self.driver.session(database=self.database) as session:
            result = session.run(
                """
                MATCH path = (a:Wallet)-[:SENT*2..%d]->(a)
                RETURN DISTINCT a.address AS wallet, length(path) AS hops
                ORDER BY hops ASC
                LIMIT $limit
                """ % max_hops, limit=limit
            )
            return [(r["wallet"], r["hops"]) for r in result]

    def get_all_wallet_addresses(self) -> List[str]:
        with self.driver.session(database=self.database) as session:
            result = session.run("MATCH (w:Wallet) RETURN w.address AS address")
            return [r["address"] for r in result]

    def clear_graph(self):
        with self.driver.session(database=self.database) as session:
            session.run("MATCH (n:Wallet) DETACH DELETE n")

    def load_case_edges(self, edges: List[Dict[str, Any]]):
        with self.driver.session(database=self.database) as session:
            for i, e in enumerate(edges):
                synthetic_hash = hashlib.sha256(
                    f"{e['from']}-{e['to']}-{e['value']}-{i}".encode()
                ).hexdigest()
                session.run(
                    """
                    MERGE (a:Wallet {address: $from_addr})
                    MERGE (b:Wallet {address: $to_addr})
                    MERGE (a)-[t:SENT {hash: $tx_hash}]->(b)
                    SET t.value = $value_eth
                    """,
                    from_addr=e["from"], to_addr=e["to"], tx_hash=synthetic_hash, value_eth=e["value"]
                )

    def get_paths_between(self, source: str, destination: str, max_hops: int = 6, limit: int = 10) -> List[Dict[str, Any]]:
        with self.driver.session(database=self.database) as session:
            result = session.run(
                """
                MATCH (a:Wallet), (b:Wallet)
                WHERE toLower(a.address) = toLower($source) AND toLower(b.address) = toLower($destination)
                MATCH p = (a)-[:SENT*1..%d]->(b)
                RETURN [n IN nodes(p) | n.address] AS wallets,
                       [r IN relationships(p) | {from: startNode(r).address, to: endNode(r).address, value: r.value}] AS rels,
                       length(p) AS hops
                ORDER BY hops ASC
                LIMIT $limit
                """ % max_hops,
                source=source, destination=destination, limit=limit
            )
            return [{"wallets": r["wallets"], "rels": r["rels"], "hops": r["hops"]} for r in result]

    def get_last_certificate(self) -> Tuple[Optional[str], Optional[str]]:
        with self.driver.session(database=self.database) as session:
            result = session.run(
                """
                MATCH (c:Certificate)
                RETURN c.hash AS hash, c.created_at AS created_at
                ORDER BY c.created_at DESC LIMIT 1
                """
            )
            record = result.single()
            if record:
                return record["hash"], record["created_at"]
            return None, None

    def store_certificate(self, cert_hash: str, prev_hash: str, wallet: str, created_at: str):
        with self.driver.session(database=self.database) as session:
            session.run(
                """
                CREATE (c:Certificate {hash: $hash, prev_hash: $prev_hash, wallet: $wallet, created_at: $created_at})
                """,
                hash=cert_hash, prev_hash=prev_hash, wallet=wallet, created_at=created_at
            )


# ==================== Backend Selection & Initialization ====================

_active_backend = None
_active_backend_name = "unknown"

def _initialize_backend():
    global _active_backend, _active_backend_name

    if DB_BACKEND == "neo4j":
        try:
            backend = Neo4jBackend()
            if backend.verify_connectivity():
                _active_backend = backend
                _active_backend_name = "neo4j"
                print("[BlockTrace DB] Connected to Neo4j graph database.")
                return
            else:
                raise ConnectionError(f"Could not connect to Neo4j at {NEO4J_URI}")
        except Exception as e:
            print(f"[BlockTrace DB ERROR] Neo4j specified but unavailable: {e}")
            raise

    elif DB_BACKEND == "sqlite":
        _active_backend = SQLiteBackend()
        _active_backend_name = "sqlite"
        print(f"[BlockTrace DB] Using SQLite embedded engine ({SQLITE_DB_PATH}).")
        return

    # Default 'auto': try Neo4j first, gracefully fallback to SQLite
    if NEO4J_URI:
        try:
            backend = Neo4jBackend()
            if backend.verify_connectivity():
                _active_backend = backend
                _active_backend_name = "neo4j"
                print("[BlockTrace DB] Connected to Neo4j graph database.")
                return
        except Exception:
            pass

    _active_backend = SQLiteBackend()
    _active_backend_name = "sqlite"
    print(f"[BlockTrace DB] Neo4j not reachable. Gracefully using SQLite engine ({SQLITE_DB_PATH}).")


def get_backend():
    global _active_backend
    if _active_backend is None:
        _initialize_backend()
    return _active_backend


def get_active_backend_name() -> str:
    get_backend()
    return _active_backend_name


# ==================== Global Helper Functions ====================

def load_transactions(transactions: List[Dict[str, Any]]) -> set:
    return get_backend().load_transactions(transactions)

def get_graph_data(limit: int = 300) -> List[Tuple[str, str, float]]:
    return get_backend().get_graph_data(limit=limit)

def get_summary_stats() -> Tuple[int, int]:
    return get_backend().get_summary_stats()

def get_hub_wallets(limit: int = 1000) -> List[Tuple[str, int]]:
    return get_backend().get_hub_wallets(limit=limit)

def get_fanout_wallets(min_recipients: int = 4, limit: int = 1000) -> List[Tuple[str, int]]:
    return get_backend().get_fanout_wallets(min_recipients=min_recipients, limit=limit)

def get_peel_chains(limit: int = 1000) -> List[Tuple[str, float, float]]:
    return get_backend().get_peel_chains(limit=limit)

def get_round_number_transactions(min_value: float = 1.0, limit: int = 1000) -> List[Tuple[str, str, float]]:
    return get_backend().get_round_number_transactions(min_value=min_value, limit=limit)

def get_circular_flows(max_hops: int = 4, limit: int = 1000) -> List[Tuple[str, int]]:
    return get_backend().get_circular_flows(max_hops=max_hops, limit=limit)

def get_all_wallet_addresses() -> List[str]:
    return get_backend().get_all_wallet_addresses()

def clear_graph():
    return get_backend().clear_graph()

def load_case_edges(edges: List[Dict[str, Any]]):
    return get_backend().load_case_edges(edges)

def get_paths_between(source: str, destination: str, max_hops: int = 6, limit: int = 10) -> List[Dict[str, Any]]:
    return get_backend().get_paths_between(source=source, destination=destination, max_hops=max_hops, limit=limit)

def get_last_certificate() -> Tuple[Optional[str], Optional[str]]:
    return get_backend().get_last_certificate()

def store_certificate(cert_hash: str, prev_hash: str, wallet: str, created_at: str):
    return get_backend().store_certificate(cert_hash=cert_hash, prev_hash=prev_hash, wallet=wallet, created_at=created_at)
