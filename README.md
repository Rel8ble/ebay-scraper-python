# eBay Scraper in Python: search listings, prices, shipping and sellers as JSON / CSV

eBay scraper Python example: get eBay search results (price, condition, shipping, units sold, seller rating, sponsored flag) as JSON or CSV for any keyword on ebay.com, ebay.co.uk, ebay.de and other eBay sites, with no eBay API key and no browser. It calls the [eBay Search Scraper](https://apify.com/rel8ble/ebay-search-scraper) actor on Apify through `apify-client`.

> I built this actor; it's a paid tool on Apify ($0.60 per 1,000 listings, no start fee). This repo is a free example of how to use it.

## Quick start (Python)

```bash
pip install apify-client
```

```python
from apify_client import ApifyClient

client = ApifyClient("<YOUR_APIFY_TOKEN>")

run = client.actor("rel8ble/ebay-search-scraper").call(run_input={
    "queries": ["wireless earbuds"],
    "site": "ebay.com",
    "conditions": ["new", "refurbished"],
    "maxItemsPerSearch": 240,
})

for item in client.dataset(run["defaultDatasetId"]).iterate_items():
    print(item["price"], item["currency"], item["condition"], item["soldCount"], item["title"][:60])
```

## Node

```js
import { ApifyClient } from 'apify-client';

const client = new ApifyClient({ token: '<YOUR_APIFY_TOKEN>' });
const run = await client.actor('rel8ble/ebay-search-scraper').call({ queries: ['mechanical keyboard'], site: 'ebay.co.uk' });
const { items } = await client.dataset(run.defaultDatasetId).listItems();
console.log(items.length, items[0]);
```

## Input

| field | what it does |
|---|---|
| `queries` | search phrases, one search each, as typed into the eBay search box |
| `startUrls` | eBay search result URLs copied from the browser (optional) |
| `site` | `ebay.com` (default), `ebay.co.uk`, `ebay.de`, ... prices come in that site's currency |
| `listingType` | `active` (default) |
| `categoryId` | numeric eBay category, e.g. `9355` cell phones |
| `priceMin` / `priceMax` | price band in the site's currency |
| `conditions` | any of `new`, `open-box`, `refurbished`, `used`, ... |
| `buyingFormat` | `all`, `buy-it-now`, `auction` |
| `freeShippingOnly`, `itemLocation`, `sort` | eBay's own filters and sort orders |
| `includeSponsored` | keep promoted listings (default true, flagged with `isSponsored`) |
| `maxItemsPerSearch` / `maxItems` | caps per search (default 240 = one eBay page) and per run (default 1,000) |

## What a row looks like

Real row from a 20 Oct 2026 cloud run (`wireless earbuds`, ebay.com), trimmed:

```json
{
  "itemId": "325792996056",
  "title": "Soundcore P20i True Wireless Earbuds Big Bass Bluetooth Headphones 30H Playtime",
  "condition": "Brand New",
  "price": 22.99,
  "currency": "USD",
  "buyingFormat": "Buy It Now",
  "shippingText": "+$30.75 delivery",
  "shippingCost": 30.75,
  "freeShipping": false,
  "itemLocation": "United States",
  "soldCount": 1362,
  "sellerName": "ankerdirect",
  "sellerFeedbackPercent": 99.8,
  "sellerFeedbackCount": 283800,
  "isSponsored": false,
  "rank": 12
}
```

`sample.json` holds the 20 real rows from that run (seller names of small private-looking accounts removed).

## example.py: quick price research

```bash
export APIFY_TOKEN=<YOUR_APIFY_TOKEN>
python example.py "wireless earbuds" --conditions new refurbished --max 240
python example.py --from-json sample.json      # offline, no token
```

It writes `ebay_listings.csv` (with a computed `landedPrice` = price + shipping) and prints the median price by condition, how many results are sponsored, the best sellers by units sold, the cheapest landed price from well-rated sellers, and the sellers with the most listings. Real output on `sample.json`:

```
Item price by condition (median / count):
  Brand New                     28.95 USD  (13)
  Open Box                      47.99 USD  (3)
  Certified - Refurbished       47.49 USD  (3)
  Pre-Owned                     29.99 USD  (1)

Sponsored listings: 7 of 20

Best sellers by units sold (soldCount shown on the card):
    3521 sold     65.99 USD  Soundcore Space One Wireless Headphones 40H ANC Playtime 2XS
    1362 sold     22.99 USD  Soundcore P20i True Wireless Earbuds Big Bass Bluetooth Head
     967 sold     65.95 USD  Bose SoundSport Wireless In Ear Bluetooth Headphones NFC Ear
```

## Ideas

- Resellers: the going price of an item by condition before you list or buy.
- Brands: who else sells your product, at what price, and how often it shows up as sponsored.
- Price trackers: run the same search daily (Apify schedules) and diff `price` per `itemId`.

## Price and limits

- $0.60 per 1,000 listings saved, no start fee. Failed requests are never charged.
- One eBay page holds up to 240 listings; split wide searches by price band or category to go deeper.
- `soldCount` and `watchers` only exist when eBay prints them on the card.
- `shippingCost` is what eBay quoted to the run's proxy location, which can differ from your own address. Treat it as a guide and compare item prices first.
- Uses residential proxy by default; that is what keeps eBay from blocking the requests.

Store page: https://apify.com/rel8ble/ebay-search-scraper
Tutorial on dev.to: https://dev.to/rel8ble/getting-ebay-search-results-and-prices-as-json-with-python-no-api-key-no-browser-5h0k

Related: [amazon-search-scraper-python](https://github.com/Rel8ble/amazon-search-scraper-python), [aliexpress-scraper-python](https://github.com/Rel8ble/aliexpress-scraper-python), [vinted-scraper-python](https://github.com/Rel8ble/vinted-scraper-python)

Need a custom scraper or a ready dataset? Hire me on Fiverr: https://www.fiverr.com/rel8ble

MIT licensed.
