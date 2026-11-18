"""eBay search results -> CSV + price research, using the rel8ble/ebay-search-scraper actor on Apify.

Usage:
    export APIFY_TOKEN=<YOUR_APIFY_TOKEN>
    python example.py "wireless earbuds" "mechanical keyboard"
    python example.py "iphone 15" --site ebay.co.uk --conditions new refurbished --max 240
    python example.py --from-json sample.json          # offline, no token needed
"""
import argparse
import csv
import json
import os
import statistics
from collections import Counter, defaultdict

FIELDS = ["rank", "title", "condition", "price", "currency", "shippingCost", "landedPrice",
          "freeShipping", "buyingFormat", "soldCount", "sellerName", "sellerFeedbackPercent",
          "sellerFeedbackCount", "itemLocation", "isSponsored", "itemUrl"]


def fetch(queries, site, conditions, max_items):
    from apify_client import ApifyClient

    client = ApifyClient(os.environ.get("APIFY_TOKEN", "<YOUR_APIFY_TOKEN>"))
    run_input = {"queries": queries, "site": site, "maxItemsPerSearch": max_items}
    if conditions:
        run_input["conditions"] = conditions
    run = client.actor("rel8ble/ebay-search-scraper").call(run_input=run_input)
    return list(client.dataset(run["defaultDatasetId"]).iterate_items())


def landed(r):
    """Item price + shipping, or None when eBay showed no shipping price."""
    if r.get("price") is None:
        return None
    if r.get("freeShipping"):
        return round(r["price"], 2)
    if r.get("shippingCost") is None:
        return None
    return round(r["price"] + r["shippingCost"], 2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("queries", nargs="*", default=["wireless earbuds"])
    ap.add_argument("--site", default="ebay.com")
    ap.add_argument("--conditions", nargs="*", default=[])
    ap.add_argument("--max", type=int, default=120)
    ap.add_argument("--from-json", help="read rows from a saved dataset instead of calling Apify")
    ap.add_argument("--out", default="ebay_listings.csv")
    args = ap.parse_args()

    if args.from_json:
        with open(args.from_json, encoding="utf-8") as f:
            rows = json.load(f)
    else:
        rows = fetch(args.queries, args.site, args.conditions, args.max)

    for r in rows:
        r["landedPrice"] = landed(r)

    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} listings -> {args.out}")

    cur = rows[0]["currency"] if rows else ""

    print("\nItem price by condition (median / count):")
    by_cond = defaultdict(list)
    for r in rows:
        if r.get("price") is not None:
            by_cond[r.get("condition") or "?"].append(r["price"])
    for cond, prices in sorted(by_cond.items(), key=lambda kv: -len(kv[1])):
        print(f"  {cond:<26} {statistics.median(prices):>8.2f} {cur}  ({len(prices)})")

    sponsored = sum(1 for r in rows if r.get("isSponsored"))
    print(f"\nSponsored listings: {sponsored} of {len(rows)}")

    print("\nBest sellers by units sold (soldCount shown on the card):")
    sold = sorted((r for r in rows if r.get("soldCount")), key=lambda r: -r["soldCount"])[:5]
    for r in sold:
        print(f"  {r['soldCount']:>6} sold  {r['price']:>8.2f} {cur}  {r['title'][:60]}")

    print("\nCheapest landed price from well-rated sellers (>= 98% positive, >= 1,000 ratings):")
    good = [r for r in rows if r["landedPrice"] is not None
            and (r.get("sellerFeedbackPercent") or 0) >= 98
            and (r.get("sellerFeedbackCount") or 0) >= 1000]
    for r in sorted(good, key=lambda r: r["landedPrice"])[:5]:
        print(f"  {r['landedPrice']:>8.2f} {cur}  {r.get('condition', ''):<24} {r['title'][:50]}")

    print("\nSellers with the most listings in these results:")
    for name, n in Counter(r.get("sellerName") for r in rows if r.get("sellerName")).most_common(5):
        print(f"  {n:>3}  {name}")


if __name__ == "__main__":
    main()
