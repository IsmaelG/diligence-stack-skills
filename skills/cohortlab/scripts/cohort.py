#!/usr/bin/env python3
"""Turn a raw customer-revenue export into product-DD evidence.

Input: one row per customer per period (CSV or XLSX), with at minimum
       a customer id, a period, and a revenue amount.

    python3 cohort.py revenue.csv \
        --customer customer_id --period month --revenue mrr \
        [--segment plan] [--out evidence.json]

Output: evidence.json — cohort matrices, retention curves, an NRR bridge and
concentration stats, already shaped as `exhibits[].chart` blocks that
build_product_doc.py renders without further editing.

Why pandas: the whole job is group-by, pivot and shift on a customer x period
grid. Doing it by hand in dicts is where cohort bugs are born — off-by-one
periods, customers silently dropped when they skip a month.
"""

import argparse
import json
import sys

import numpy as np
import pandas as pd


def load(path):
    if str(path).lower().endswith((".xlsx", ".xlsm", ".xls")):
        return pd.read_excel(path)
    return pd.read_csv(path)


def prep(df, customer, period, revenue, segment=None):
    cols = {customer: "customer", period: "period", revenue: "revenue"}
    if segment:
        cols[segment] = "segment"
    missing = [c for c in cols if c not in df.columns]
    if missing:
        sys.exit(f"Column(s) not found: {missing}. Available: {list(df.columns)}")
    df = df.rename(columns=cols)[list(cols.values())].copy()
    df["period"] = pd.PeriodIndex(pd.to_datetime(df["period"], errors="coerce"), freq="M")
    df = df.dropna(subset=["period"])
    df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce").fillna(0.0)
    # collapse duplicate rows (multi-product customers)
    keys = ["customer", "period"] + (["segment"] if segment else [])
    return df.groupby(keys, as_index=False)["revenue"].sum()


def cohort_matrices(df, max_periods=13):
    """Logo and revenue retention triangles, indexed by acquisition month."""
    active = df[df["revenue"] > 0]
    first = active.groupby("customer")["period"].min().rename("cohort")
    a = active.join(first, on="customer")
    a["age"] = (a["period"].astype("int64") - a["cohort"].astype("int64")).astype(int)
    a = a[(a["age"] >= 0) & (a["age"] < max_periods)]

    logos = a.pivot_table(index="cohort", columns="age", values="customer",
                          aggfunc="nunique")
    rev = a.pivot_table(index="cohort", columns="age", values="revenue", aggfunc="sum")
    logo_pct = logos.div(logos[0], axis=0) * 100
    rev_pct = rev.div(rev[0], axis=0) * 100

    def triangle(pct, sizes):
        rows, labels = [], []
        for idx in pct.index:
            vals = [None if pd.isna(v) else round(float(v), 1) for v in pct.loc[idx]]
            # trim the immature tail so the triangle doesn't imply 0% retention
            while vals and vals[-1] is None:
                vals.pop()
            rows.append(vals)
            labels.append(f"{idx}  (n={int(sizes.loc[idx, 0])})")
        return rows, labels

    logo_rows, labels = triangle(logo_pct, logos)
    rev_rows, _ = triangle(rev_pct, logos)
    width = max((len(r) for r in logo_rows), default=1)
    return {
        "x": [f"M{i}" for i in range(width)],
        "y": labels,
        "logo": logo_rows,
        "revenue": rev_rows,
        "avg_logo_curve": [round(float(v), 1) for v in logo_pct.mean(axis=0).tolist()],
        "avg_rev_curve": [round(float(v), 1) for v in rev_pct.mean(axis=0).tolist()],
    }


def plateau(curve, tol=2.0, window=3):
    """First period where the retention curve stops falling — the PMF test.
    Returns None if it never flattens inside the observed window."""
    for i in range(1, len(curve) - window):
        seg = curve[i:i + window + 1]
        if max(seg) - min(seg) <= tol:
            return {"period": f"M{i}", "level": round(float(np.mean(seg)), 1)}
    return None


def nrr_bridge(df, months=12):
    """Revenue retention on the cohort of customers present `months` ago,
    decomposed into expansion / contraction / churn."""
    periods = sorted(df["period"].unique())
    if len(periods) <= months:
        return None
    start, end = periods[-1 - months], periods[-1]
    s = df[df["period"] == start].set_index("customer")["revenue"]
    e = df[df["period"] == end].set_index("customer")["revenue"]
    s = s[s > 0]
    e = e.reindex(s.index).fillna(0.0)
    delta = e - s
    churned = float(-s[e == 0].sum())
    expansion = float(delta[(e > 0) & (delta > 0)].sum())
    contraction = float(delta[(e > 0) & (delta < 0)].sum())
    base, ending = float(s.sum()), float(e.sum())
    return {
        "start_period": str(start), "end_period": str(end),
        "base": round(base), "expansion": round(expansion),
        "contraction": round(contraction), "churn": round(churned),
        "ending": round(ending),
        "nrr_pct": round(ending / base * 100, 1) if base else None,
        "grr_pct": round((base + contraction + churned) / base * 100, 1) if base else None,
    }


def concentration(df):
    last = df[df["period"] == df["period"].max()]
    tot = last["revenue"].sum()
    top = last.groupby("customer")["revenue"].sum().sort_values(ascending=False)
    out = {"period": str(df["period"].max()), "total_revenue": round(float(tot)),
           "customers": int((top > 0).sum())}
    for n in (1, 5, 10, 20):
        if len(top) >= n and tot:
            out[f"top{n}_pct"] = round(float(top.head(n).sum()) / tot * 100, 1)
    return out


def by_segment(df):
    if "segment" not in df.columns:
        return None
    rows = []
    for seg, g in df.groupby("segment"):
        b = nrr_bridge(g)
        c = cohort_matrices(g)
        rows.append({
            "segment": str(seg),
            "customers": int(g[g["period"] == g["period"].max()]["customer"].nunique()),
            "revenue_latest": round(float(g[g["period"] == g["period"].max()]["revenue"].sum())),
            "nrr_pct": b["nrr_pct"] if b else None,
            "m6_logo_retention": (c["avg_logo_curve"][6]
                                  if len(c["avg_logo_curve"]) > 6 else None),
            "plateau": plateau(c["avg_logo_curve"]),
        })
    return sorted(rows, key=lambda r: -(r["revenue_latest"] or 0))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--customer", required=True)
    ap.add_argument("--period", required=True)
    ap.add_argument("--revenue", required=True)
    ap.add_argument("--segment")
    ap.add_argument("--max-periods", type=int, default=13)
    ap.add_argument("--out", default="evidence.json")
    a = ap.parse_args()

    df = prep(load(a.path), a.customer, a.period, a.revenue, a.segment)
    coh = cohort_matrices(df, a.max_periods)
    nrr = nrr_bridge(df)
    ev = {
        "source_file": a.path,
        "periods": [str(df["period"].min()), str(df["period"].max())],
        "cohorts": coh,
        "plateau_logo": plateau(coh["avg_logo_curve"]),
        "plateau_revenue": plateau(coh["avg_rev_curve"]),
        "nrr": nrr,
        "concentration": concentration(df),
        "segments": by_segment(df),
        # ready-to-embed chart specs
        "charts": {
            "logo_heatmap": {
                "type": "heatmap", "title": "Logo retention by cohort (%)",
                "x": coh["x"], "y": coh["y"], "matrix": coh["logo"], "vmax": 100,
                "source": f"Source: {a.path}, computed. [A]"},
            "revenue_heatmap": {
                "type": "heatmap", "title": "Net revenue retention by cohort (%)",
                "x": coh["x"], "y": coh["y"], "matrix": coh["revenue"],
                "vmax": max(120, int(max((max([v for v in r if v is not None] or [0])
                                          for r in coh["revenue"]), default=120))),
                "source": f"Source: {a.path}, computed. [A]"},
            "retention_curve": {
                "type": "line", "title": "Average retention curve \u2014 does it flatten?",
                "x": coh["x"][:len(coh["avg_logo_curve"])],
                "series": [{"name": "Logo", "values": coh["avg_logo_curve"]},
                           {"name": "Revenue", "values": coh["avg_rev_curve"]}],
                "ylabel": "% of cohort", "source": "Computed from data room export. [A]"},
        },
    }
    if nrr:
        ev["charts"]["nrr_bridge"] = {
            "type": "waterfall", "title": f"NRR bridge {nrr['start_period']} \u2192 {nrr['end_period']}",
            "x": ["Base", "Expansion", "Contraction", "Churn", "Ending"],
            "series": [{"values": [nrr["base"], nrr["expansion"], nrr["contraction"],
                                   nrr["churn"], nrr["ending"]]}],
            "source": "Computed from data room export. [A]"}

    with open(a.out, "w") as f:
        json.dump(ev, f, indent=2, default=str)

    print(f"Wrote {a.out}")
    print(f"  window        : {ev['periods'][0]} \u2192 {ev['periods'][1]}")
    print(f"  logo plateau  : {ev['plateau_logo'] or 'NONE — curve still falling'}")
    print(f"  NRR / GRR     : {nrr['nrr_pct'] if nrr else 'n/a'}% / {nrr['grr_pct'] if nrr else 'n/a'}%")
    print(f"  top-10 concn  : {ev['concentration'].get('top10_pct', 'n/a')}%")


if __name__ == "__main__":
    main()
