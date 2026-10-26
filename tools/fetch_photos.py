"""Download freely licensed portraits from Wikipedia/Wikimedia Commons into images/.
Only images whose license is public domain or Creative Commons are saved; everything else is
listed in images/photo-report.json so a person can decide. Run by .github/workflows/fetch-photos.yml."""
import io, json, os, re, time, urllib.error, urllib.parse, urllib.request
from PIL import Image

UA = {"User-Agent": "SouthViewTimeline/1.0 (Georgia Tech class project; github.com/Yaashboii/south-view-timeline)"}
PEOPLE = {
 "king-sr": "Martin Luther King Sr.", "ad-king": "A. D. King", "robinson": "Ruby Doris Smith-Robinson",
 "ad-williams": "Adam Daniel Williams", "sw-williams": "Samuel Woodrow Williams", "bearden": "Harold I. Bearden",
 "archer": "Samuel Archer", "bowen": "John W. E. Bowen Sr.", "brawley": "James P. Brawley",
 "cary": "Alice Dugged Cary", "usher": "Bazoline Estelle Usher", "pace": "Dinah Watts Pace", "towns": "George A. Towns",
 "fountain": "William A. Fountain", "turner": "Henry McNeal Turner", "williamson": "Q. V. Williamson",
 "calhoun": "John H. Calhoun", "proctor": "Henry H. Proctor", "price": "Luther Judson Price",
 "irene-jackson": "Irene Dobbs Jackson", "golightly": "Cornelius Golightly", "alexander": "T. M. Alexander",
 "jesse-hill": "Jesse Hill", "russell": "Herman J. Russell", "norris-herndon": "Norris B. Herndon",
 "haugabrooks": "Geneva Haugabrooks", "henderson": "Freddye Scarborough Henderson", "blayton": "Jesse B. Blayton",
 "penn": "William F. Penn", "moses-amos": "Moses Amos", "miles-amos": "Miles Amos", "nash": "Homer E. Nash",
 "bennette": "Fred C. Bennette",
}
FREE = re.compile(r"^(public domain|pd|cc0|cc[- ]by)", re.I)

def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read()

def api(base, **q):
    q.update(format="json", formatversion="2")
    return json.loads(get(base + "?" + urllib.parse.urlencode(q)))

def strip(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html or "")).strip()

def get_retry(url):
    for wait in (0, 5, 15, 40, 90):
        time.sleep(wait)
        try:
            return get(url)
        except urllib.error.HTTPError as e:
            if e.code != 429: raise
    raise RuntimeError("still rate limited")

def api(base, **q):
    q.update(format="json", formatversion="2")
    return json.loads(get_retry(base + "?" + urllib.parse.urlencode(q)))

report = json.load(open("images/photo-report.json")) if os.path.exists("images/photo-report.json") else {}
todo = {pid: t for pid, t in PEOPLE.items() if not os.path.exists(f"images/{pid}.jpg")}
# one request for all article images
r = api("https://en.wikipedia.org/w/api.php", action="query", titles="|".join(todo.values()), redirects=1, prop="pageimages", piprop="name")
alias = {}
for x in r["query"].get("normalized", []) + r["query"].get("redirects", []):
    alias[x["to"]] = alias.get(x["from"], x["from"])
pages = {}
for pg in r["query"]["pages"]:
    t = pg["title"]
    while t in alias: t = alias[t]
    pages[t] = pg
files = {}
for pid, title in todo.items():
    pg = pages.get(title) or pages.get(title.replace("_", " "))
    if not pg or pg.get("missing") or not pg.get("pageimage"):
        report[pid] = {"status": "no article image", "title": title}; continue
    fname = pg["pageimage"]; surname = re.sub(r"[^a-z]", "", title.split()[-1].lower().replace("sr.", "").replace("jr.", "")) or title.split()[-2].lower()
    if title.split()[-1] in ("Sr.", "Jr."): surname = title.split()[-2].lower()
    if re.search(r"signature|\.svg$", fname, re.I) or surname not in fname.lower().replace("_", " "):
        report[pid] = {"status": "skipped (image may not show this person)", "file": fname}; continue
    files[pid] = fname
info = api("https://commons.wikimedia.org/w/api.php", action="query", titles="|".join("File:" + f for f in files.values()),
           prop="imageinfo", iiprop="url|extmetadata", iiurlheight=900) if files else {"query": {"pages": []}}
byname = {}
for pg in info["query"]["pages"]:
    byname[pg["title"].replace("File:", "", 1).replace(" ", "_")] = pg
for x in info["query"].get("normalized", []):
    byname[x["from"].replace("File:", "", 1).replace(" ", "_")] = byname.get(x["to"].replace("File:", "", 1).replace(" ", "_"))
for pid, fname in files.items():
    try:
        pg = byname.get(fname.replace(" ", "_")) or {}
        ii = pg.get("imageinfo")
        if not ii:
            report[pid] = {"status": "not free (hosted on Wikipedia only)", "file": fname}; continue
        ii = ii[0]; meta = ii.get("extmetadata", {})
        lic = strip(meta.get("LicenseShortName", {}).get("value"))
        if not FREE.search(lic):
            report[pid] = {"status": "not free", "license": lic, "page": ii["descriptionurl"]}; continue
        time.sleep(3)
        img = Image.open(io.BytesIO(get_retry(ii.get("thumburl") or ii["url"]))).convert("RGB")
        if img.height > 900:
            img = img.resize((round(img.width * 900 / img.height), 900), Image.LANCZOS)
        img.save(f"images/{pid}.jpg", "JPEG", quality=86)
        report[pid] = {"status": "saved", "file": fname, "license": lic,
                       "author": strip(meta.get("Artist", {}).get("value"))[:120], "page": ii["descriptionurl"]}
    except Exception as e:
        report[pid] = {"status": "error", "error": str(e)[:200]}
report["ad-williams"] = {"status": "removed (article image showed the church, not him)"}
json.dump(report, open("images/photo-report.json", "w"), indent=1)
print(json.dumps(report, indent=1))
