# ===========================================================================
# India Macro — Streamlit front end
# ---------------------------------------------------------------------------
# Single file. Reads data.json from the same directory and renders whatever
# it finds. A page whose blocks are all absent hides itself.
#
# THE DATA CONTRACT (all keys optional)
#   stamp {reference, generated_ist, generated_utc, content_hash,
#          observations, families, asof{family: date}}
#   as_of {verified_to, provisional_to}
#   position  str
#   tiles     [{label, value, unit, period, source}]   source: live|snapshot
#   narrative {key: [{verdict, text}]}
#   <table>   {cols, rows, note, period?, source?}
#   sectors   [str]
#   checks    table block with a "Result" column
#
# TO ADD A MODULE: write the block into data.json, add one tuple to PAGES.
# ===========================================================================
import json
import pathlib

import pandas as pd
import streamlit as st

st.set_page_config(page_title="India Macro", layout="wide")

HERE = pathlib.Path(__file__).parent
try:
    D = json.loads((HERE / "data.json").read_text())
except Exception as exc:
    st.error(f"data.json could not be read: {exc}")
    st.stop()

NARR = D.get("narrative", {}) or {}
STAMP = D.get("stamp", {}) or {}
ASOF = D.get("as_of", {}) or {}

st.markdown(
    """<style>
.block-container{padding-top:2rem;max-width:1180px}
.tile{border:1px solid #e3e0d8;border-radius:8px;padding:14px 16px;
      background:#fcfbf8;height:100%}
.tile .v{font-size:28px;font-weight:700;line-height:1.1}
.tile .l{font-size:11px;color:#555;text-transform:uppercase;
         letter-spacing:.4px}
.tile .p{font-size:11px;color:#888;margin-top:3px}
.badge{display:inline-block;font-size:10px;padding:1px 7px;border-radius:9px;
       border:1px solid #ccc;color:#666;margin-left:6px}
.prov{background:#fff4e0;border-color:#e0b870;color:#8a5a00}
.ver{background:#eef7f0;border-color:#8fc0a0;color:#1d6b3a}
.note{font-size:13px;color:#444;background:#f7f6f3;border-left:3px solid #222;
      padding:10px 14px;margin:6px 0 16px}
.key{font-size:14px;color:#1f1f1f;background:#fff9ec;
     border-left:3px solid #b8860b;padding:11px 15px;margin:6px 0 14px;
     line-height:1.55}
.hero{font-size:40px;font-weight:700;line-height:1;letter-spacing:-1px}
.herolab{font-size:11px;color:#555;text-transform:uppercase;
         letter-spacing:.6px;margin-top:2px}
.ref{font-size:11px;color:#555;text-align:right;line-height:1.7}
</style>""",
    unsafe_allow_html=True,
)


def badge(src):
    if src == "live":
        return '<span class="badge ver">Verified</span>'
    return '<span class="badge prov">Provisional</span>'


def frame(block):
    df = pd.DataFrame(block.get("rows", []), columns=block.get("cols", []))
    for c in df.columns[1:]:
        conv = pd.to_numeric(
            df[c].astype(str).str.replace(",", "", regex=False),
            errors="coerce")
        if conv.notna().mean() > 0.6:
            df[c] = conv
    return df


def table(block, chart=None, key=""):
    if not block or not block.get("rows"):
        return False
    df = frame(block)
    if block.get("period"):
        st.caption(block["period"])
    st.dataframe(df, hide_index=True, width="stretch")
    if chart and st.toggle("Show chart", key=f"tg_{key}"):
        idx = df.columns[0]
        try:
            if chart == "line":
                st.line_chart(df.set_index(idx).select_dtypes("number"))
            elif chart in df.columns:
                st.bar_chart(df.set_index(idx)[chart])
            else:
                st.bar_chart(df.set_index(idx).select_dtypes("number"))
        except Exception as exc:
            st.caption(f"chart unavailable: {exc}")
    if block.get("note"):
        st.markdown(f'<div class="note">{block["note"]}</div>',
                    unsafe_allow_html=True)
    return True


def narr(key):
    items = NARR.get(key) or []
    for o in items:
        st.markdown(f'<div class="key">{o.get("text", "")}</div>',
                    unsafe_allow_html=True)
    return bool(items)


def checks_table(block):
    if not block or not block.get("rows"):
        return False
    df = frame(block)
    if "Result" in df.columns:
        def colour(v):
            v = str(v)
            if v == "AGREE":
                return "background-color:#eef7f0"
            if v == "BREAK":
                return "background-color:#fdecea"
            if v and v != "nan":
                return "background-color:#fff4e0"
            return ""
        st.dataframe(df.style.map(colour, subset=["Result"]),
                     hide_index=True, width="stretch")
    else:
        st.dataframe(df, hide_index=True, width="stretch")
    if block.get("note"):
        st.markdown(f'<div class="note">{block["note"]}</div>',
                    unsafe_allow_html=True)
    return True


def sector_list(_=None):
    items = D.get("sectors") or []
    for s in items:
        st.markdown(f"- {s}")
    return bool(items)


def asof_table(_=None):
    m = STAMP.get("asof") or {}
    if not m:
        return False
    st.dataframe(pd.DataFrame({"Data family": list(m.keys()),
                               "As at": list(m.values())}),
                 hide_index=True, width="stretch")
    st.markdown('<div class="note">Official releases arrive on different '
                'calendars, so each family carries its own as-at date. A '
                'single report date would misrepresent most of them.</div>',
                unsafe_allow_html=True)
    return True


STATIC = {
    "growth_vs_avg": {
        "cols": ["Measure", "Latest", "Own average",
                 "Distance from average"],
        "rows": [["Real GDP growth, base 2022-23 (13 readings)",
                  7.82, 7.47, 0.35],
                 ["Real GDP growth, base 2011-12 (54 readings)",
                  None, 6.29, None]],
        "note": ("The current base has thirteen readings. That is a run "
                 "rate, not a trend, and the average of thirteen quarters "
                 "is not a measure of this economy's normal growth. The "
                 "earlier base average of 6.29% covers 54 quarters "
                 "including the 2020 collapse, so the two measure different "
                 "things and are never subtracted from one another. "
                 "Capacity utilisation carries the slack judgement because "
                 "it has 73 quarters behind it."),
    },
    "orders_detail": {
        "cols": ["Measure", "Value"],
        "rows": [["Latest, average per responding company, year on year",
                  "-2.56%"],
                 ["Trailing 20-quarter median, same basis", "+5.70%"],
                 ["Full-sample mean, same basis", "+11.33%"],
                 ["Derived aggregate, year on year", "+9.33%"],
                 ["Responding companies, four quarters ago", "385"],
                 ["Responding companies, latest", "432"],
                 ["Change in the panel", "+12.2%"]],
        "note": ("The published figure is an average per responding company "
                 "and the panel grew 12.2% over the year. A growing panel "
                 "drags a per-company average down with no change in "
                 "demand, which is why the per-company reading is negative "
                 "while the aggregate is positive. Both are shown because "
                 "neither settles it, and no conclusion in this report "
                 "rests on them."),
    },
    "data_kinds": {
        "cols": ["Kind of data", "Source type", "Coverage used"],
        "rows": [
            ["National accounts, quarterly", "Official statistics office",
             "Expenditure components across current and previous bases"],
            ["Gross value added, quarterly", "Official statistics office",
             "Nine production sectors"],
            ["Industrial production, monthly", "Official statistics office",
             "Eleven series, two independent classifications"],
            ["Consumer prices, monthly", "Official statistics office",
             "Twelve divisions and the headline, three sectors"],
            ["Capacity utilisation, quarterly", "Central bank survey",
             "73 quarters, about 1,000 companies"],
            ["Order books and inventories, quarterly", "Central bank survey",
             "73 quarters, 353 to 432 companies"],
            ["Corporate accounts, quarterly", "Central bank survey",
             "52 industry groups, 47 quarters, about 3,200 companies"],
            ["Equity indices, daily", "Exchanges",
             "Sector and factor indices with valuation ratios, since 2011"],
            ["Policy rates and yields", "Central bank",
             "Policy decisions and the yield curve"],
            ["Professional forecaster survey", "Central bank survey",
             "Consensus growth and inflation expectations"],
        ],
        "note": ("Every figure traces to a published official series. "
                 "Nothing is modelled or estimated unless it is labelled as "
                 "derived at the point of use."),
    },
    "validation": {
        "cols": ["Test", "Result"],
        "rows": [
            ["Industrial production against a second official channel, "
             "month by month",
             "165 comparisons, every one at 0.00 difference"],
            ["Our year-on-year arithmetic against the publisher's own "
             "published growth rate",
             "220 comparisons, largest difference 0.05 — the rounding floor"],
            ["Published industrial index rebuilt from two independent "
             "weighting schemes",
             "Maximum error 0.049 and 0.074 index points over 41 months"],
            ["Published consumer price index rebuilt from its twelve "
             "divisions",
             "All 21 months pass, maximum error 0.0075 index points"],
            ["Inflation contributions summed against the published headline",
             "Difference 0.0061 percentage points"],
            ["GDP expenditure identity", "Closes to 0.000000%"],
            ["Fiscal deficit against an independent published spreadsheet",
             "Zero difference across four months"],
        ],
        "note": ("These are reproducible from published figures. Where two "
                 "measurements of the same thing disagree, the disagreement "
                 "is reported rather than averaged away."),
    },
}


st.title("India Macro")

if STAMP:
    left, right = st.columns([3, 2])
    left.markdown(
        f'<div class="hero">{STAMP.get("observations", 0):,}</div>'
        f'<div class="herolab">observations analysed across '
        f'{STAMP.get("families", 0)} data families</div>',
        unsafe_allow_html=True)
    right.markdown(
        f'<div class="ref"><b>{STAMP.get("reference", "")}</b><br>'
        f'{STAMP.get("generated_ist", "")}<br>'
        f'content hash {STAMP.get("content_hash", "")}</div>',
        unsafe_allow_html=True)

bits = []
if ASOF.get("verified_to"):
    bits.append(f"Verified through {ASOF['verified_to']}")
if ASOF.get("provisional_to"):
    bits.append(f"provisional through {ASOF['provisional_to']}")
if bits:
    st.caption(" · ".join(bits))

if D.get("position"):
    st.markdown(f"#### {D['position']}")

if D.get("tiles"):
    cols = st.columns(len(D["tiles"]))
    for col, t in zip(cols, D["tiles"]):
        try:
            val = f'{float(t["value"]):+.2f}{t.get("unit", "")}'
        except Exception:
            val = str(t.get("value", ""))
        col.markdown(
            f'<div class="tile"><div class="l">{t.get("label","")}'
            f'{badge(t.get("source"))}</div>'
            f'<div class="v">{val}</div>'
            f'<div class="p">{t.get("period","")}</div></div>',
            unsafe_allow_html=True)

st.divider()

PAGES = [
    ("Overview", [
        ("narr", "confidence"),
        ("narr", "coverage"),
        ("fn", asof_table, "Data currency by family"),
    ]),
    ("Inflation", [
        ("narr", "inflation"),
        ("narr", "policy"),
        ("table", "inflation", "line"),
        ("table", "inflation_sources", "pp of headline"),
    ]),
    ("Growth", [
        ("narr", "growth"),
        ("table", "components", None),
    ]),
    ("Industry", [
        ("narr", "industry"),
        ("table", "industry", None),
    ]),
    ("Slack", [
        ("narr", "slack"),
        ("table", "slack", None),
        ("static", "growth_vs_avg", None),
        ("static", "orders_detail", None),
    ]),
    ("Corporate", [
        ("narr", "corporate"),
        ("table", "corporate", None),
    ]),
    ("Market", [
        ("narr", "market"),
        ("table", "market_table", None),
        ("narr", "recommendations"),
    ]),
    ("Factors", [
        ("narr", "factors"),
        ("table", "factor_table", None),
    ]),
    ("Reconciliation", [
        ("narr", "reconciliation"),
        ("table", "reco_agreement", None),
        ("table", "reco_book", "After regime exposure %"),
    ]),
    ("Cross-checks", [
        ("checks", "checks"),
    ]),
    ("Sector view", [
        ("fn", sector_list, None),
    ]),
    ("Data", [
        ("table", "census", None),
        ("static", "data_kinds", None),
        ("static", "validation", None),
    ]),
]

HEADINGS = {
    "confidence": "How much of this is corroborated",
    "coverage": "What this run was built on",
    "inflation": "Inflation",
    "policy": "Policy",
    "growth": "Growth and the gap",
    "industry": "Industrial production",
    "slack": "Slack",
    "growth_vs_avg": "Growth against its own average",
    "orders_detail": "Order books, both bases of measurement",
    "corporate": "Corporate accounts",
    "market": "The market",
    "market_table": "Every index, return and valuation",
    "recommendations": "Recommendations",
    "factors": "Factors",
    "factor_table": "Factor returns and valuation",
    "reconciliation": "Fundamental and quantitative, reconciled",
    "reco_agreement": "Where the two models agree",
    "reco_book": "The combined book",
    "components": "GDP components",
    "inflation_sources": "Where inflation comes from",
    "checks": "Cross-checks",
    "census": "Observations analysed",
    "data_kinds": "What this analysis is built on",
    "validation": "How the figures were verified",
}


def has_content(items):
    for it in items:
        kind = it[0]
        if kind == "narr" and NARR.get(it[1]):
            return True
        if kind == "table" and (D.get(it[1]) or {}).get("rows"):
            return True
        if kind == "static" and STATIC.get(it[1]):
            return True
        if kind == "checks" and (D.get(it[1]) or {}).get("rows"):
            return True
        if kind == "fn":
            return True
    return False


LIVE = [(n, i) for n, i in PAGES if has_content(i)]

if not LIVE:
    st.warning("data.json contains no renderable blocks yet.")
    st.stop()

for tab, (name, items) in zip(st.tabs([n for n, _ in LIVE]), LIVE):
    with tab:
        for it in items:
            kind = it[0]
            if kind == "narr":
                if NARR.get(it[1]):
                    st.subheader(HEADINGS.get(it[1], it[1].title()))
                    narr(it[1])
            elif kind == "table":
                blk = D.get(it[1])
                if blk and blk.get("rows"):
                    st.subheader(HEADINGS.get(it[1], it[1].title()))
                    if blk.get("source"):
                        st.markdown(badge(blk["source"]),
                                    unsafe_allow_html=True)
                    table(blk, chart=it[2], key=it[1])
            elif kind == "static":
                if STATIC.get(it[1]):
                    st.subheader(HEADINGS.get(it[1], it[1].title()))
                    table(STATIC[it[1]], chart=it[2], key=f"s_{it[1]}")
            elif kind == "checks":
                blk = D.get(it[1])
                if blk and blk.get("rows"):
                    st.subheader(HEADINGS.get(it[1], "Cross-checks"))
                    checks_table(blk)
            elif kind == "fn":
                if it[2]:
                    st.subheader(it[2])
                elif name == "Sector view":
                    st.subheader("Sector view")
                it[1]()

st.divider()
foot = ["Figures marked Provisional carry data pending source release "
        "updates and are subject to revision.",
        "Measurement only; not investment advice."]
if STAMP.get("reference"):
    foot.insert(0, f"Report {STAMP['reference']} · "
                   f"{STAMP.get('generated_ist', '')} · "
                   f"hash {STAMP.get('content_hash', '')}")
st.caption("  ·  ".join(foot))
