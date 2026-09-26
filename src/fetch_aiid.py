"""Step 0a - Download the AI Incident Database export of 21 Sept 2026 from AIID's own file
host and check its SHA-256. AIID incident data is licensed CC BY-SA 4.0; the export also
contains report text that is not under that licence, so the raw file is fetched rather than
redistributed. Derived tables in output/ are shared under CC BY-SA 4.0 with attribution to
the AI Incident Database (incidentdatabase.ai)."""
import hashlib
import pathlib
import urllib.request

# Some file hosts reject Python's default user agent (HTTP 403).
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; portfolio-analysis-fetch/1.0)"}

RAW = pathlib.Path(__file__).resolve().parents[1] / "data" / "raw"
NAME = "AIID_Excel_Export-20260921.xlsx"
URL = "https://pub-72b2b2fc36ec423189843747af98f80e.r2.dev/" + NAME
SHA = "d8c26069f47363eb4adad00c381f8f80877f06e784050cd4bff900ee2159413c"

RAW.mkdir(parents=True, exist_ok=True)
dest = RAW / NAME
if not dest.exists():
    with urllib.request.urlopen(urllib.request.Request(URL, headers=HEADERS), timeout=120) as r:
        dest.write_bytes(r.read())
actual = hashlib.sha256(dest.read_bytes()).hexdigest()
print("  {}  {}".format(NAME, "ok" if actual == SHA else "CHANGED"))
if actual != SHA:
    raise SystemExit("AIID export differs from the one this analysis was built on.")
