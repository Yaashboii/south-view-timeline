"""One-off: download specific image URLs into images/_incoming/<id>.jpg for review."""
import io, json, os, urllib.request
from PIL import Image
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"}
URLS = {
 "borders": "https://wearewheatstreet.org/wp-content/uploads/2023/04/cp6-1920w.webp",
 "bryant": "https://wearewheatstreet.org/wp-content/uploads/2023/04/cp4-1920w.webp",
 "neal": "https://img1.wsimg.com/isteam/ip/ab5099b1-8745-4c32-90a5-5264368b96c0/X.L.%20Neal.PNG/:/rs=w:400,cg:true,m",
 "lillian-lewis": "https://images.ajc.com/resizer/v2/YIMOIRCN52ARA3Z7MIOFRY4E3Q.jpg",
 "cunningham": "https://www.atlantahistorycenter.com/app/uploads/2022/06/02_PlanATL_4572-760x947.jpg",
 "washington-king": "https://stonemountainguide.com/images/Washington-W-King.jpg",
 "willis": "https://vocalgroupharmony.com/5ROWNEW/ChuckWillis.jpg",
 "duke-pearson": "https://www.bluenote.com/wp-content/uploads/sites/956/2019/03/DukePearson_color_byFrancisWolff.jpg",
 "donald-reeves": "https://www.seamheads.com/NegroLgs/pics/1/donald_reeves.jpg",
 "dave-harper": "https://www.seamheads.com/NegroLgs/pics/1/dave_harper.jpg",
 "agnes-jones": "https://static.fox5atlanta.com/www.fox5atlanta.com/content/uploads/2019/09/F9501EC7FB7E4DD9B46EB51613921B4F.jpg",
 "william-guest": "https://cdn.tukioswebsites.com/7d84e8e4-c470-4d13-b674-2978433ed6ef/lg",
 "john-harden": "https://readtheplaque.com/uploads/19/1973585b7b42439db684dd658980c7c1.jpg",
}
os.makedirs("images/_incoming", exist_ok=True)
report = {}
for pid, url in URLS.items():
    try:
        data = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40).read()
        im = Image.open(io.BytesIO(data)).convert("RGB")
        if im.height > 1200: im = im.resize((round(im.width * 1200 / im.height), 1200), Image.LANCZOS)
        im.save(f"images/_incoming/{pid}.jpg", "JPEG", quality=90)
        report[pid] = {"status": "saved", "size": im.size}
    except Exception as e:
        report[pid] = {"status": "error", "error": str(e)[:200]}
json.dump(report, open("images/_incoming/report.json", "w"), indent=1)
print(json.dumps(report, indent=1))
