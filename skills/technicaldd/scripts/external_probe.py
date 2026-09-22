#!/usr/bin/env python3
"""
external_probe.py — technicaldd skill
Black-box, no-login checks runnable against ANY public domain, before deal access exists.

What it actually measures (not estimates):
  - DNS resolution + hosting signal (via reverse-ish inference from headers, not a full WHOIS)
  - TLS certificate issuer / expiry
  - HTTP latency: N requests, reports mean / p50 / p95 (single run — see caveats in SKILL.md)
  - robots.txt presence and disallow rules (signals what the vendor doesn't want indexed —
    sometimes reveals internal API or admin paths)
  - Probe of ~15 conventional API / agent-discovery paths (OpenAPI, Swagger, MCP, llms.txt, etc.)
  - Response header fingerprint: server stack hints + presence of baseline security headers

What it deliberately does NOT do:
  - No auth bypass, no fuzzing beyond a fixed public path list, no scraping behind a login wall.
  - Every request is a plain GET a browser would make. Nothing here requires consent beyond
    what visiting the public website already implies.

Usage:
  python3 external_probe.py example.com another-example.org
  python3 external_probe.py example.com --out probe_results.json
"""
import argparse
import json
import socket
import ssl
import statistics
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone

AGENT_DISCOVERY_PATHS = [
    "/.well-known/mcp.json",
    "/.well-known/mcp/manifest.json",
    "/.well-known/ai-plugin.json",
    "/mcp",
    "/llms.txt",
    "/llms-full.txt",
    "/openapi.json",
    "/openapi.yaml",
    "/swagger.json",
    "/swagger/index.html",
    "/api/docs",
    "/api/openapi.json",
    "/docs",
    "/api",
    "/graphql",
]

SECURITY_HEADERS = [
    "Strict-Transport-Security",
    "Content-Security-Policy",
    "X-Content-Type-Options",
    "X-Frame-Options",
    "Referrer-Policy",
]

UA = "Mozilla/5.0 (compatible; technicaldd-probe/1.0; +https://internal-diligence-tool)"


def http_get(url, timeout=8):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            elapsed_ms = (time.perf_counter() - t0) * 1000
            body = resp.read(4096)
            return {
                "ok": True,
                "status": resp.status,
                "elapsed_ms": round(elapsed_ms, 1),
                "headers": dict(resp.headers),
                "body_snippet": body[:400].decode("utf-8", errors="replace"),
            }
    except urllib.error.HTTPError as e:
        elapsed_ms = (time.perf_counter() - t0) * 1000
        return {"ok": False, "status": e.code, "elapsed_ms": round(elapsed_ms, 1), "headers": dict(e.headers or {}), "error": str(e)}
    except Exception as e:
        elapsed_ms = (time.perf_counter() - t0) * 1000
        return {"ok": False, "status": None, "elapsed_ms": round(elapsed_ms, 1), "error": str(e)}


def get_tls_info(domain, port=443, timeout=6):
    ctx = ssl.create_default_context()
    try:
        with socket.create_connection((domain, port), timeout=timeout) as sock:
            with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                issuer = dict(x[0] for x in cert.get("issuer", []))
                not_after = cert.get("notAfter")
                return {"issuer": issuer.get("organizationName") or issuer.get("commonName"), "not_after": not_after}
    except Exception as e:
        return {"error": str(e)}


def measure_latency(url, n=8, discard_first=True):
    """Cold-start bias: the first request pays DNS + TLS handshake cost the rest don't.
    Discard it by default. n=8 is enough for a directional mean, NOT enough for a real p95
    (usually wants 30+) — we report p95 anyway but flag it as unreliable below that threshold
    rather than silently presenting false precision."""
    samples = []
    failed = 0
    total_requests = n + (1 if discard_first else 0)
    for i in range(total_requests):
        r = http_get(url, timeout=15)  # generous timeout: a dropped slow request would
                                        # silently make a struggling service look fast
        if i == 0 and discard_first:
            time.sleep(0.15)
            continue
        if r.get("ok") and r.get("elapsed_ms") is not None:
            samples.append(r["elapsed_ms"])
        else:
            failed += 1
        time.sleep(0.15)
    if not samples:
        return {"n": 0, "failed": failed, "note": "no successful requests"}
    samples.sort()
    p95_idx = max(0, int(len(samples) * 0.95) - 1)
    return {
        "n": len(samples),
        "failed": failed,
        "mean_ms": round(statistics.mean(samples), 1),
        "p50_ms": round(statistics.median(samples), 1),
        "p95_ms": round(samples[p95_idx], 1),
        "p95_reliable": len(samples) >= 30,
        "min_ms": round(min(samples), 1),
        "max_ms": round(max(samples), 1),
        "caveat": "Single run from one vantage point at one moment, first request discarded to remove cold-start bias — directional, not an SLA measurement. p95 not statistically reliable below ~30 samples. See SKILL.md.",
    }


def parse_robots_disallow(base_url):
    """Best-effort robots.txt parser for the User-agent: * block. A probe that ignores
    robots.txt isn't 'black box, no login needed' — it's just impolite. Fails open (returns
    no rules) if robots.txt is missing or unparseable, since that's not a reason to block."""
    r = http_get(base_url.rstrip("/") + "/robots.txt", timeout=6)
    if not r.get("ok"):
        return []
    disallowed = []
    in_wildcard_block = False
    for line in r.get("body_snippet", "").splitlines():
        line = line.strip()
        if line.lower().startswith("user-agent:"):
            in_wildcard_block = line.split(":", 1)[1].strip() == "*"
        elif in_wildcard_block and line.lower().startswith("disallow:"):
            path = line.split(":", 1)[1].strip()
            if path:
                disallowed.append(path)
    return disallowed


def probe_agent_discovery(base_url, disallowed_prefixes=None):
    disallowed_prefixes = disallowed_prefixes or []
    found = []
    skipped = []
    for path in AGENT_DISCOVERY_PATHS:
        if any(path.startswith(p) for p in disallowed_prefixes):
            skipped.append(path)
            continue
        r = http_get(base_url.rstrip("/") + path, timeout=6)
        status = r.get("status")
        if status is not None and status < 400:
            found.append({"path": path, "status": status})
    return found, skipped


def probe_robots(base_url):
    r = http_get(base_url.rstrip("/") + "/robots.txt", timeout=6)
    if r.get("ok"):
        return {"found": True, "snippet": r.get("body_snippet", "")}
    return {"found": False}


def security_headers_present(headers):
    if not headers:
        return {}
    lower = {k.lower(): v for k, v in headers.items()}
    return {h: (h.lower() in lower) for h in SECURITY_HEADERS}


def agent_readiness_score(agent_paths_found, headers):
    """Heuristic 0-5, not a certification. Documented so a reviewer can contest each point."""
    score = 0
    reasons = []
    names = [p["path"] for p in agent_paths_found]
    if any(p in names for p in ["/.well-known/mcp.json", "/.well-known/mcp/manifest.json", "/mcp"]):
        score += 2
        reasons.append("+2: MCP manifest or endpoint publicly discoverable")
    if any(p in names for p in ["/llms.txt", "/llms-full.txt"]):
        score += 1
        reasons.append("+1: llms.txt present (explicit agent-facing site description)")
    if any(p in names for p in ["/openapi.json", "/openapi.yaml", "/swagger.json", "/swagger/index.html", "/api/openapi.json"]):
        score += 2
        reasons.append("+2: machine-readable API spec (OpenAPI/Swagger) discoverable")
    if not agent_paths_found:
        reasons.append("+0: none of 15 conventional discovery paths responded — does not mean no API exists, means it is not self-discoverable")
    return {"score_0_5": min(score, 5), "reasons": reasons}


def run(domain, out_path=None):
    base_url = domain if domain.startswith("http") else f"https://{domain}"
    bare_domain = base_url.split("//", 1)[-1].split("/")[0]

    print(f"\n=== {domain} ===", file=sys.stderr)
    result = {"domain": domain, "probed_at_utc": datetime.now(timezone.utc).isoformat()}

    print("  resolving DNS + fetching homepage...", file=sys.stderr)
    home = http_get(base_url)
    result["homepage"] = {"status": home.get("status"), "elapsed_ms": home.get("elapsed_ms"), "server_header": (home.get("headers") or {}).get("Server")}
    result["security_headers"] = security_headers_present(home.get("headers"))

    print("  TLS certificate...", file=sys.stderr)
    result["tls"] = get_tls_info(bare_domain)

    print("  measuring latency (8 requests)...", file=sys.stderr)
    result["latency"] = measure_latency(base_url, n=8)

    print("  robots.txt...", file=sys.stderr)
    result["robots"] = probe_robots(base_url)
    disallowed_prefixes = parse_robots_disallow(base_url)

    print("  probing 15 API / agent-discovery paths (robots.txt-respecting)...", file=sys.stderr)
    agent_paths, skipped_paths = probe_agent_discovery(base_url, disallowed_prefixes)
    result["agent_discovery_paths_found"] = agent_paths
    result["agent_discovery_paths_skipped_robots"] = skipped_paths
    result["agent_readiness"] = agent_readiness_score(agent_paths, home.get("headers"))

    if out_path:
        with open(out_path, "w") as f:
            json.dump(result, f, indent=2)
        print(f"  written to {out_path}", file=sys.stderr)

    return result


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("domains", nargs="+", help="one or more bare domains, e.g. example.com")
    ap.add_argument("--out", help="write combined JSON results here")
    args = ap.parse_args()

    all_results = {}
    for d in args.domains:
        all_results[d] = run(d)

    if args.out:
        with open(args.out, "w") as f:
            json.dump(all_results, f, indent=2)

    print("\n" + json.dumps(all_results, indent=2))
