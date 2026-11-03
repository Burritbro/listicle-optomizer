#!/usr/bin/env python3
"""Pull per-offer performance for the /lm listicle straight from the FunnelFlux Pro API.

Usage:
    python3 analysis/ff_pull.py [--days 30] [--funnel 3vkva49LIKjr] [--out analysis/ff_offers.csv]
    python3 analysis/aov_rank.py analysis/ff_offers.csv

Auth: FunnelFlux only accepts a short-lived access token (Authorization: Bearer, 72h).
  - In a Claude cloud session, a network secret on api.funnelflux.pro injects it; no token
    is needed here.
  - Anywhere else, set FUNNELFLUX_ACCESS_TOKEN. Never commit tokens: this repo is public.

Report: POST /v1/reporting/drilldown/, filtered to the /lm funnel, grouped by
"Insight: Action Number" then "Element: Offer". The action number is the N in
path.consumergrabs.com/action/N on the page, so rows join to current_page_inventory.csv.
"""
import argparse
import csv
import datetime as dt
import json
import os
import ssl
import sys
import urllib.error
import urllib.request

API = "https://api.funnelflux.pro/v1/reporting/drilldown/"
LM_FUNNEL = "3vkva49LIKjr"  # fluxDefaults.f on consumergrabs.com/lm
HERE = os.path.dirname(os.path.abspath(__file__))


def ssl_ctx():
    ca = "/root/.ccr/ca-bundle.crt"  # agent proxy CA in Claude cloud sessions
    return ssl.create_default_context(cafile=ca) if os.path.exists(ca) else ssl.create_default_context()


def post(body):
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    tok = os.environ.get("FUNNELFLUX_ACCESS_TOKEN")
    if tok:
        headers["Authorization"] = "Bearer " + tok
    req = urllib.request.Request(API, data=json.dumps(body).encode(), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, context=ssl_ctx(), timeout=180) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"FunnelFlux API error {e.code}: {e.read().decode(errors='replace')[:500]}")


def flatten(rows, parents=()):
    """Drilldown rows may be nested (one level per grouping); yield leaf rows with all attrs."""
    for r in rows or []:
        attrs = list(parents) + list(r.get("attributes") or [])
        kids = r.get("rows") or r.get("children")
        if kids:
            yield from flatten(kids, attrs)
        else:
            yield attrs, r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--funnel", default=LM_FUNNEL)
    ap.add_argument("--out", default=os.path.join(HERE, "ff_offers.csv"))
    ap.add_argument("--raw", help="also save the raw JSON response here")
    a = ap.parse_args()

    end = dt.datetime.now(dt.timezone.utc).replace(minute=0, second=0, microsecond=0)
    start = end - dt.timedelta(days=a.days)
    body = {
        "timeStart": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "timeEnd": end.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "attributes": [{"attribute": "Insight: Action Number"}, {"attribute": "Element: Offer"}],
        "filters": [{"attribute": "Element: Funnel", "whitelistFilters": [a.funnel]}],
        "restrictToMetrics": ["Visits", "Cost", "OfferClicks", "OfferClicksUnique",
                              "Conversions", "Revenue", "TotalRevenue"],
    }
    rep = post(body)
    if a.raw:
        json.dump(rep, open(a.raw, "w"), indent=1)

    out = []
    for attrs, r in flatten(rep.get("rows")):
        by = {x.get("attribute"): x for x in attrs}
        act = by.get("Insight: Action Number", {})
        off = by.get("Element: Offer", {})
        out.append({
            "Action": act.get("value") or act.get("id") or "",
            "Offer": off.get("value") or "",
            "Offer ID": off.get("id") or "",
            "Visits": r.get("visits", 0),
            "Offer Clicks": r.get("offerClicks", 0),
            "Offer Clicks Unique": r.get("offerClicksUnique", 0),
            "Conversions": r.get("conversions", 0),
            "Revenue": r.get("revenue", "0"),
            "Total Revenue": r.get("totalRevenue", "0"),
            "Cost": r.get("cost", "0"),
        })
    if not out:
        sys.exit("report returned no rows: check the funnel ID and date range")
    with open(a.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    print(f"{len(out)} rows, {start:%Y-%m-%d} to {end:%Y-%m-%d} UTC -> {a.out}")


if __name__ == "__main__":
    main()
