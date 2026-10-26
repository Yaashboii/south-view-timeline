"""Download freely licensed portraits from Wikipedia/Wikimedia Commons into images/.
Only images whose license is public domain or Creative Commons are saved; everything else is
listed in images/photo-report.json so a person can decide. Run by .github/workflows/fetch-photos.yml."""
import io, json, os, re, urllib.parse, urllib.request
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

report = {}
for pid, title in PEOPLE.items():
    out = f"images/{pid}.jpg"
    if os.path.exists(out):
        report[pid] = {"status": "already present"}; continue
    try:
        r = api("https://en.wikipedia.org/w/api.php", action="query", titles=title, redirects=1, prop="pageimages", piprop="name")
        page = r["query"]["pages"][0]
        if page.get("missing") or not page.get("pageimage"):
            report[pid] = {"status": "no article image", "title": title}; continue
        fname = page["pageimage"]
        if re.search(r"signature|\.svg$", fname, re.I):
            report[pid] = {"status": "skipped (not a portrait)", "file": fname}; continue
        info = api("https://commons.wikimedia.org/w/api.php", action="query", titles="File:" + fname,
                   prop="imageinfo", iiprop="url|extmetadata", iiurlheight=900)
        ii = info["query"]["pages"][0].get("imageinfo")
        if not ii:  # not on Commons -> local (usually non-free) file
            report[pid] = {"status": "not free (hosted on Wikipedia only)", "file": fname, "page": "https://en.wikipedia.org/wiki/File:" + urllib.parse.quote(fname)}; continue
        ii = ii[0]; meta = ii.get("extmetadata", {})
        lic = strip(meta.get("LicenseShortName", {}).get("value"))
        if not FREE.search(lic):
            report[pid] = {"status": "not free", "license": lic, "page": ii["descriptionurl"]}; continue
        img = Image.open(io.BytesIO(get(ii.get("thumburl") or ii["url"]))).convert("RGB")
        if img.height > 900:
            img = img.resize((round(img.width * 900 / img.height), 900), Image.LANCZOS)
        img.save(out, "JPEG", quality=86)
        report[pid] = {"status": "saved", "file": fname, "license": lic,
                       "author": strip(meta.get("Artist", {}).get("value"))[:120], "page": ii["descriptionurl"]}
    except Exception as e:
        report[pid] = {"status": "error", "error": str(e)[:200]}
json.dump(report, open("images/photo-report.json", "w"), indent=1)
print(json.dumps(report, indent=1))
