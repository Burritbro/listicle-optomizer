#!/usr/bin/env python3
"""Rank /lm offers by payout-per-sale (AOV) and earnings, and propose a new page order.

Usage:
    python3 analysis/aov_rank.py <funnelflux_export.csv> [--min-clicks 50] [--out analysis/report.md]

Input: a FunnelFlux report export grouped by Offer (or by action), last ~30 days.
Column names are matched loosely; the script needs, per row:
    - an offer name or action ID          ("Offer", "Name", "Action", ...)
    - clicks / visits to the offer        ("Offer clicks", "Clicks", "Visits", ...)
    - conversions                         ("Conversions", "Conv.", ...)
    - revenue                             ("Revenue", ...)
Rows are joined to analysis/current_page_inventory.csv by action ID, or by product name
when no ID column exists.

Definitions (AOV = what we get paid per sale):
    AOV  = revenue / conversions
    CR   = conversions / offer clicks
    EPC  = revenue / offer clicks = AOV x CR   <- what a slot is worth per click

Why EPC, not AOV alone, decides the order: moving a high-payout offer up only raises
revenue if enough of the clicks it gains still convert. EPC captures both.
Clicks per offer depend heavily on position (top slots get far more), so EPC per click
is the fairest comparison between offers in different slots.

Low-volume offers are shrunk toward the page average (Bayesian smoothing), so a
1-for-3 fluke doesn't jump to slot #1.
"""
import argparse
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
INVENTORY = os.path.join(HERE, "current_page_inventory.csv")

ALIASES = {
    "name": ["offer", "offer name", "name", "product", "element", "node"],
    "action": ["action", "action id", "action number", "ff_action", "offer id", "id"],
    "clicks": ["offer clicks", "offer visits", "clicks", "outclicks", "visits", "lp clicks"],
    "conv": ["conversions", "conv", "conv.", "sales", "orders"],
    "rev": ["revenue", "rev", "payout", "income"],
    "cost": ["cost", "spend"],
}


def norm(s):
    return re.sub(r"[^a-z0-9 .]", "", (s or "").strip().lower())


def num(v):
    v = re.sub(r"[^0-9.\-]", "", str(v or ""))
    try:
        return float(v) if v not in ("", "-", ".") else 0.0
    except ValueError:
        return 0.0


def pick(header, key):
    h = {norm(c): c for c in header}
    for alias in ALIASES[key]:
        if alias in h:
            return h[alias]
    for alias in ALIASES[key]:  # partial match as a fallback
        for n, c in h.items():
            if alias in n:
                return c
    return None


def key_name(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def load_inventory():
    with open(INVENTORY, newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["action_key"] = r["ff_action"].split()[0]
        r["name_key"] = key_name(re.sub(r"^VERIFY:\s*", "", r["product"]))
    return rows


def match(inv, action, name):
    if action:
        for r in inv:
            if r["action_key"] == action:
                return r
    nk = key_name(name)
    if nk:
        for r in inv:
            if r["name_key"] and (r["name_key"] in nk or nk in r["name_key"]):
                return r
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("export")
    ap.add_argument("--min-clicks", type=int, default=50,
                    help="clicks needed before an offer's own EPC is trusted (smoothing weight)")
    ap.add_argument("--out", default=os.path.join(HERE, "report.md"))
    a = ap.parse_args()

    with open(a.export, newline="", encoding="utf-8-sig") as f:
        data = list(csv.DictReader(f))
    if not data:
        sys.exit("export is empty")
    header = list(data[0].keys())
    cols = {k: pick(header, k) for k in ALIASES}
    missing = [k for k in ("clicks", "conv", "rev") if not cols[k]]
    if missing or not (cols["name"] or cols["action"]):
        sys.exit(f"could not find columns {missing or ['name/action']} in header: {header}")

    inv = load_inventory()
    agg, unmatched = {}, []
    for row in data:
        name = row.get(cols["name"], "") if cols["name"] else ""
        action = ""
        if cols["action"]:
            m = re.search(r"\d+", str(row.get(cols["action"], "")))
            action = m.group(0) if m else ""
        if not action:
            m = re.search(r"action/(\d+)", name)
            action = m.group(1) if m else ""
        if norm(name) in ("total", "totals", "grand total"):
            continue
        inv_row = match(inv, action, name)
        k = inv_row["action_key"] if inv_row else f"?{name or action}"
        if not inv_row:
            unmatched.append(name or action)
        g = agg.setdefault(k, {"inv": inv_row, "label": inv_row["product"] if inv_row else (name or action),
                               "clicks": 0.0, "conv": 0.0, "rev": 0.0})
        g["clicks"] += num(row.get(cols["clicks"]))
        g["conv"] += num(row.get(cols["conv"]))
        g["rev"] += num(row.get(cols["rev"]))

    tot_c = sum(g["clicks"] for g in agg.values())
    tot_v = sum(g["conv"] for g in agg.values())
    tot_r = sum(g["rev"] for g in agg.values())
    page_epc = tot_r / tot_c if tot_c else 0
    page_aov = tot_r / tot_v if tot_v else 0
    k = a.min_clicks

    for g in agg.values():
        g["aov"] = g["rev"] / g["conv"] if g["conv"] else None
        g["cr"] = g["conv"] / g["clicks"] if g["clicks"] else None
        g["epc"] = g["rev"] / g["clicks"] if g["clicks"] else None
        # smoothed EPC: shrink toward page average until the offer has ~k clicks
        g["epc_s"] = (g["rev"] + k * page_epc) / (g["clicks"] + k)
        g["pos"] = int(g["inv"]["page_position"]) if g["inv"] else None

    on_page = [g for g in agg.values() if g["pos"]]
    ranked = sorted(on_page, key=lambda g: -g["epc_s"])
    # offers on the page with no FunnelFlux row at all
    seen = {g["inv"]["action_key"] for g in on_page}
    no_data = [r for r in inv if r["action_key"] not in seen]

    def f(v, fmt):
        return "—" if v is None else fmt.format(v)

    L = []
    L.append("# /lm offer ranking: payout per sale (AOV) and EPC\n")
    L.append(f"Page totals: {tot_c:,.0f} offer clicks · {tot_v:,.0f} sales · ${tot_r:,.2f} revenue · "
             f"**AOV ${page_aov:,.2f}** · EPC ${page_epc:,.3f}\n")
    L.append(f"Smoothing: offers are shrunk toward the page EPC until they have ~{k} clicks.\n")
    L.append("## Proposed order (by smoothed EPC)\n")
    L.append("| New # | Now # | Move | Product | Action | Clicks | Sales | Revenue | AOV | CR | EPC | Smoothed EPC |")
    L.append("|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for i, g in enumerate(ranked, 1):
        mv = g["pos"] - i
        L.append(f"| {i} | {g['pos']} | {'+' if mv > 0 else ''}{mv if mv else '·'} | {g['label']} | "
                 f"{g['inv']['ff_action']} | {g['clicks']:,.0f} | {g['conv']:,.0f} | ${g['rev']:,.2f} | "
                 f"{f(g['aov'], '${:,.2f}')} | {f(g['cr'] and g['cr'] * 100, '{:.2f}%')} | "
                 f"{f(g['epc'], '${:,.3f}')} | ${g['epc_s']:,.3f} |")
    L.append("\n## Highest payout per sale (AOV), min 3 sales\n")
    L.append("| Product | Now # | Sales | AOV | CR | EPC |")
    L.append("|---|---:|---:|---:|---:|---:|")
    for g in sorted([g for g in on_page if g["conv"] >= 3], key=lambda g: -g["aov"]):
        L.append(f"| {g['label']} | {g['pos']} | {g['conv']:,.0f} | ${g['aov']:,.2f} | "
                 f"{g['cr'] * 100:.2f}% | ${g['epc']:,.3f} |")
    if no_data:
        L.append("\n## On the page but no FunnelFlux data\n")
        L.append(", ".join(f"#{r['page_position']} {r['product']} (action {r['ff_action']})" for r in no_data))
    if unmatched:
        L.append("\n## Export rows not matched to a page item\n")
        L.append(", ".join(sorted(set(unmatched))))
    open(a.out, "w").write("\n".join(L) + "\n")
    print("\n".join(L))
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
