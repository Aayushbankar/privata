import pathlib, json, re, html, uuid
from unstructured.partition.md import partition_md
from unstructured.staging.base import convert_to_dict
from pydantic import BaseModel
from typing import List, Optional

# ---------- 1. Output schema: one row per atomic fact ----------
class Fact(BaseModel):
    id: str
    url: str
    page_title: str
    section_path: str          # h1>h2>h3>...
    fact_type: str             # 'table_row' | 'list_item' | 'paragraph' | 'faq' | 'metadata'
    mission: Optional[str]     # extracted satellite name
    product: Optional[str]     # extracted product name
    key: Optional[str]         # e.g. 'spatial_resolution'
    value: Optional[str]       # e.g. '1 km'
    raw_text: str              # full sentence / row / cell
    table_md: Optional[str]    # markdown table source (if any)
    bbox: Optional[str]        # future: xpath or css path

# ---------- 2. Regex arsenal ----------
MISS_RE = re.compile(r'\b(INSAT-3DR|INSAT-3D|KALPANA-1|INSAT-3A|INSAT-3DS|OCEANSAT-2|OCEANSAT-3|SCATSAT-1|MeghaTropiques|SARAL-AltiKa)\b', re.I)
PROD_RE = re.compile(r'\b(rainfall|sea surface temperature|soil moisture|wind|salinity|current|cloud|water vapour|discharge|height|ice|eddy|wave|saphir|gsmap|dwr|terls)\b', re.I)
KV_RE   = re.compile(r'(?P<key>spatial|temporal|resolution|swath|band|wavelength|frequency|accuracy|repeat|launch|longitude|latitude|altitude|data format|file format|API|contact|email|phone)\s*[:—-]\s*(?P<value>[^\n,.]+)', re.I)
NUM_RE  = re.compile(r'\b\d+(?:\.\d+)?\s*(km|m|hour|min|day|MHz|GHz|°[EC]|[Nn]m|mb|hPa|km²|m²)\b')

# ---------- 3. Helpers ----------
def build_section_path(elements, idx):
    """Return h1>h2>h3... up to element idx."""
    path = []
    for i in range(idx):
        if elements[i].category == "Title":
            path.append(elements[i].text.strip())
    return " > ".join(path[-4:])          # keep last 4 levels

def extract_kv(text):
    """Return list of (key,value) tuples."""
    return [(m.group("key").strip(), m.group("value").strip()) for m in KV_RE.finditer(text)]

def mission_from_text(text):
    m = MISS_RE.search(text)
    return m.group(0) if m else None

def product_from_text(text):
    m = PROD_RE.search(text)
    return m.group(0) if m else None

# ---------- 4. Explode one markdown file ----------
def explode(md_file: pathlib.Path, base_url: str) -> List[Fact]:
    elements = partition_md(filename=str(md_file))
    url  = base_url + md_file.stem.replace("crw4ai_", "")
    facts: List[Fact] = []
    page_title = md_file.stem.replace("crw4ai_", "").replace("-", " ").title()

    for i, el in enumerate(elements):
        section = build_section_path(elements, i)
        mission = mission_from_text(el.text)
        product = product_from_text(el.text)

        # ---- 4.1  TABLE → one row per fact ----
        if el.category == "Table":
            table_md = el.metadata.text_as_html or el.text
            for line in el.text.splitlines():
                if "|" in line and not line.startswith("|---"):
                    facts.append(Fact(
                        id=str(uuid.uuid4()),
                        url=url,
                        page_title=page_title,
                        section_path=section,
                        fact_type="table_row",
                        mission=mission,
                        product=product,
                        key=None,
                        value=None,
                        raw_text=line.strip(),
                        table_md=table_md,
                        bbox=None
                    ))

        # ---- 4.2  LIST ITEM ----
        elif el.category == "ListItem":
            facts.append(Fact(
                id=str(uuid.uuid4()),
                url=url,
                page_title=page_title,
                section_path=section,
                fact_type="list_item",
                mission=mission,
                product=product,
                key=None,
                value=None,
                raw_text=el.text.strip(),
                table_md=None,
                bbox=None
            ))

        # ---- 4.3  PARAGRAPH → explode key:value sentences ----
        elif el.category == "NarrativeText":
            kvs = extract_kv(el.text)
            if kvs:
                for k, v in kvs:
                    facts.append(Fact(
                        id=str(uuid.uuid4()),
                        url=url,
                        page_title=page_title,
                        section_path=section,
                        fact_type="metadata",
                        mission=mission,
                        product=product,
                        key=k,
                        value=v,
                        raw_text=f"{k}: {v}",
                        table_md=None,
                        bbox=None
                    ))
            else:
                # fallback: whole paragraph
                facts.append(Fact(
                    id=str(uuid.uuid4()),
                    url=url,
                    page_title=page_title,
                    section_path=section,
                    fact_type="paragraph",
                    mission=mission,
                    product=product,
                    key=None,
                    value=None,
                    raw_text=el.text.strip(),
                    table_md=None,
                    bbox=None
                ))

        # ---- 4.4  TITLE → treat as section anchor ----
        elif el.category == "Title":
            facts.append(Fact(
                id=str(uuid.uuid4()),
                url=url,
                page_title=page_title,
                section_path=section,
                fact_type="heading",
                mission=mission,
                product=product,
                key="heading",
                value=el.text.strip(),
                raw_text=el.text.strip(),
                table_md=None,
                bbox=None
            ))

    return facts

# ---------- 5. Batch process ----------
def main():
    md_dir   = pathlib.Path("crw4ai_output/mosdac.gov.in")
    out_file = pathlib.Path("mosdac_facts.jsonl")
    base_url = "https://mosdac.gov.in/"

    with out_file.open("w", encoding="utf-8") as f_out:
        for md in md_dir.glob("*.md"):
            for r in explode(md, base_url):
                f_out.write(json.dumps(r.model_dump(), ensure_ascii=False) + "\n")
    print("✅  →", out_file, "(rows:", sum(1 for _ in out_file.open()), ")")

if __name__ == "__main__":
    main()
    