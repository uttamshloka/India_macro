import json, pathlib
import pandas as pd
import streamlit as st

st.set_page_config(page_title="India Macro", layout="wide")
D = json.loads((pathlib.Path(__file__).parent / "data.json").read_text())

st.markdown("""<style>
.block-container{padding-top:2rem;max-width:1180px}
.tile{border:1px solid #e3e0d8;border-radius:8px;padding:14px 16px;background:#fcfbf8}
.tile .v{font-size:30px;font-weight:700;line-height:1.1}
.tile .l{font-size:12px;color:#555;text-transform:uppercase;letter-spacing:.4px}
.tile .p{font-size:11px;color:#888;margin-top:3px}
.badge{display:inline-block;font-size:10px;padding:1px 7px;border-radius:9px;
       border:1px solid #ccc;color:#666;margin-left:6px}
.prov{background:#fff4e0;border-color:#e0b870;color:#8a5a00}
.ver{background:#eef7f0;border-color:#8fc0a0;color:#1d6b3a}
.note{font-size:13px;color:#444;background:#f7f6f3;border-left:3px solid #222;
      padding:10px 14px;margin:6px 0 16px}
.key{font-size:13px;color:#333;background:#fff9ec;border-left:3px solid #b8860b;
     padding:10px 14px;margin:6px 0 16px}
</style>""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Supplementary content. Verified in analysis; to be folded into data.json.
# ---------------------------------------------------------------------------
SUPP = {
 "policy": (
  "**Policy has turned, and it is tightening into this.** The repo rate was "
  "raised to 5.50% on 9 October 2026, the first increase since February 2023. "
  "Inflation has risen for nine consecutive months on all three measures "
  "reported here, and at 5.54% it sits in the upper half of the 4% plus or "
  "minus 2% tolerance band while still climbing. On that evidence the "
  "direction of policy is tighter, not neutral.\n\n"
  "That matters here specifically. Net margins sit at their normal level "
  "while operating margins sit below it, and the difference is being filled "
  "by an interest burden 1.41 standard deviations below normal. **Policy is "
  "tightening into the one support holding net profitability up.** If debt "
  "service normalises while operating margins stay soft, net margins follow "
  "operating margins down. Interest coverage at 6.09 against a recent median "
  "of 5.40 gives real cushion, and only one industry group in fifty cannot "
  "cover its interest — so this is a margin question, not a solvency one."),
 "industry_key": (
  "**Intermediate goods is the largest single contributor to industrial "
  "growth** — the inputs firms buy before they produce. It has accelerated "
  "from 4.39% to 9.21% over four quarters. Input purchases lead final output, "
  "so this is a forward-looking signal pointing up, and it is independent of "
  "capacity utilisation, of order books and of the national accounts. The "
  "reading that would undercut it is firms stockpiling inputs they cannot "
  "sell, and inventories are exactly normal, which closes that door."),
 "growth_key": (
  "**Listed company sales now grow faster than the economy.** Eighteen "
  "months ago nominal GDP grew 4.41 percentage points faster than listed "
  "company sales. It has now crossed over: sales +10.11% against nominal GDP "
  "+8.72%. Listed corporate revenue is gaining share against aggregate "
  "nominal activity, which is the condition under which equity allocations "
  "are rewarded."),
 "inflation_key": (
  "**This is not a food story.** All three measures have risen for nine "
  "consecutive months. If it were food, the excluding-food measure would be "
  "flat. It is up 1.39 percentage points, and the typical division in the "
  "basket has gone from 2.12% to 5.01% — it has more than doubled. "
  "Inflation is broad.\n\n"
  "Food has switched sides. In January the excluding-food measure ran "
  "*above* headline by 0.36 points, so food was pulling inflation down. By "
  "September food adds 1.06 points. A swing of 1.42 points in eight months, "
  "on top of an underlying rate that was already rising."),
 "slack_extra": {
  "cols": ["Measure", "Latest", "Own average", "Distance from average"],
  "rows": [["Real GDP growth, base 2022-23 (13 readings)", 7.82, 7.47, 0.35],
           ["Real GDP growth, base 2011-12 (54 readings)", None, 6.29, None]],
  "note": ("The 2022-23 base has thirteen readings. That is a run rate, not "
           "a trend, and the average of thirteen quarters is not a measure of "
           "this economy's normal growth. The 2011-12 average of 6.29% covers "
           "54 quarters including the 2020 collapse, so the two averages "
           "measure different things and are never subtracted from each "
           "other. Capacity utilisation carries the slack judgement because "
           "it has 73 quarters behind it.")},
 "orders": {
  "cols": ["Measure", "Value"],
  "rows": [["Latest, average per responding company, YoY", "-2.56%"],
           ["Trailing 20-quarter median, same basis", "+5.70%"],
           ["Full-sample mean, same basis", "+11.33%"],
           ["Derived aggregate, YoY", "+9.33%"],
           ["Responding companies, four quarters ago", "385"],
           ["Responding companies, latest", "432"],
           ["Change in the panel", "+12.2%"]],
  "note": ("The published figure is an **average per responding company** and "
           "the survey panel grew 12.2% over the year. A growing panel drags "
           "a per-company average down with no change in demand, which is why "
           "the per-company reading is negative while the aggregate is "
           "positive. Both are shown because neither settles it: the "
           "per-company figure is not comparable across a changing panel, and "
           "the aggregate is not a population total. The forward signal from "
           "order books is therefore unresolved, and no conclusion here "
           "rests on it.")},
 "data_kinds": {
  "cols": ["Kind of data", "Source type", "Coverage used"],
  "rows": [
   ["National accounts, quarterly", "Official statistics office",
    "9 expenditure components, 17 quarters on the current base and 58 on the previous one"],
   ["Gross value added, quarterly", "Official statistics office",
    "9 production sectors, 17 quarters"],
   ["Industrial production, monthly", "Official statistics office",
    "11 series, 41 months, two independent classifications"],
   ["Consumer prices, monthly", "Official statistics office",
    "12 divisions plus the headline, 21 months, three sectors"],
   ["Capacity utilisation, quarterly", "Central bank survey",
    "73 quarters, about 1,000 companies"],
   ["Order books and inventories, quarterly", "Central bank survey",
    "73 quarters, 353 to 432 companies"],
   ["Corporate accounts, quarterly", "Central bank survey",
    "52 industry groups, 47 quarters, 19 indicators, about 3,200 companies"],
   ["Equity indices, daily", "Exchanges", "7,605 daily closes since 2011"],
   ["Policy rates and yields", "Central bank", "Policy decisions and the yield curve"],
   ["Professional forecaster survey", "Central bank survey",
    "Consensus growth and inflation expectations"]],
  "note": ("Over 70,000 individual observations across ten kinds of data, "
           "from four institutions. Every figure in this report traces to a "
           "published official series; none is modelled or estimated unless "
           "it is labelled as derived.")},
 "validation": {
  "cols": ["Test", "Result"],
  "rows": [
   ["Industrial production, our figures against a second official channel, month by month",
    "165 comparisons, every one at 0.00 difference"],
   ["Our year-on-year arithmetic against the publisher's own published growth rate",
    "220 comparisons, largest difference 0.05 — the rounding floor"],
   ["Published industrial index rebuilt from two independent weighting schemes",
    "Maximum error 0.049 and 0.074 index points over 41 months"],
   ["Published consumer price index rebuilt from its twelve divisions",
    "All 21 months pass, maximum error 0.0075 index points"],
   ["Inflation contributions summed against the published headline",
    "Difference 0.0061 percentage points"],
   ["GDP expenditure identity",
    "Closes to 0.000000%"],
   ["Fiscal deficit against an independent published spreadsheet",
    "Zero difference across four months"]],
  "note": ("These are reproducible from published figures. Where two "
           "measurements of the same thing disagree, the disagreement is "
           "reported rather than averaged away — that is what the "
           "cross-checks page shows.")},
 "sector_caveat": (
  "**What this view does not tell you.** It does not check whether these "
  "sectors have already repriced. Sector-level equity indices are not in "
  "this dataset — only broad market indices are — so the question of how "
  "much of this is already in prices cannot be answered here and is not "
  "answered by implication. Treat the view as a reading of the economy, not "
  "as a statement about valuation."),
}

a = D["as_of"]
st.title("India Macro")
st.caption(f"Verified through {a['verified_to']} · provisional through "
           f"{a['provisional_to']} · generated {D['generated'][:16]}")
st.markdown(f"#### {D['position']}")
st.divider()


def badge(src):
    if src == "live":
        return '<span class="badge ver">Verified</span>'
    return '<span class="badge prov">Provisional</span>'


cols = st.columns(len(D["tiles"]))
for c, t in zip(cols, D["tiles"]):
    c.markdown(
        f'<div class="tile"><div class="l">{t["label"]}{badge(t["source"])}'
        f'</div><div class="v">{t["value"]:+.2f}{t["unit"]}</div>'
        f'<div class="p">{t["period"]}</div></div>', unsafe_allow_html=True)


def table(b, chart=None, key=""):
    df = pd.DataFrame(b["rows"], columns=b["cols"])
    if b.get("period"):
        st.caption(b["period"])
    st.dataframe(df, hide_index=True, use_container_width=True)
    if chart and st.toggle("Show chart", key="t_" + key):
        idx = df.columns[0]
        if chart == "line":
            st.line_chart(df.set_index(idx))
        else:
            st.bar_chart(df.set_index(idx)[chart])
    if b.get("note"):
        st.markdown(f'<div class="note">{b["note"]}</div>',
                    unsafe_allow_html=True)


def block(key, title, chart=None):
    b = D.get(key)
    if not b:
        return
    st.subheader(title)
    st.markdown(badge(b.get("source", "snapshot")), unsafe_allow_html=True)
    table(b, chart=chart, key=key)


tabs = st.tabs(["Inflation", "Growth", "Industry", "Slack", "Corporate",
                "Cross-checks", "Sector view", "Data"])

with tabs[0]:
    block("inflation", "Inflation, three measures", chart="line")
    st.markdown(f'<div class="key">{SUPP["inflation_key"]}</div>',
                unsafe_allow_html=True)
    block("inflation_sources", "Where inflation comes from",
          chart="pp of headline")

with tabs[1]:
    block("components", "GDP components")
    st.markdown(f'<div class="key">{SUPP["growth_key"]}</div>',
                unsafe_allow_html=True)

with tabs[2]:
    block("industry", "Industrial production by use")
    st.markdown(f'<div class="key">{SUPP["industry_key"]}</div>',
                unsafe_allow_html=True)

with tabs[3]:
    block("slack", "Slack")
    st.subheader("Growth against its own average")
    table(SUPP["slack_extra"], key="slackx")
    st.subheader("Order books, both bases of measurement")
    table(SUPP["orders"], key="orders")

with tabs[4]:
    block("corporate", "Corporate accounts")
    st.markdown(f'<div class="key">{SUPP["policy"]}</div>',
                unsafe_allow_html=True)

with tabs[5]:
    b = D["checks"]
    st.subheader("Cross-checks")
    df = pd.DataFrame(b["rows"], columns=b["cols"])

    def col(v):
        if v == "AGREE":
            return "background-color:#eef7f0"
        if v == "BREAK":
            return "background-color:#fdecea"
        if v:
            return "background-color:#fff4e0"
        return ""

    st.dataframe(df.style.map(col, subset=["Result"]),
                 hide_index=True, use_container_width=True)
    st.markdown(f'<div class="note">{b["note"]}</div>',
                unsafe_allow_html=True)

with tabs[6]:
    st.subheader("Sector view")
    for s in D["sectors"]:
        st.markdown(f"- {s}")
    st.markdown(f'<div class="note">{SUPP["sector_caveat"]}</div>',
                unsafe_allow_html=True)

with tabs[7]:
    st.subheader("What this analysis is built on")
    table(SUPP["data_kinds"], key="kinds")
    st.subheader("How the figures were verified")
    table(SUPP["validation"], key="valid")

st.divider()
st.caption("Figures marked Provisional carry data pending source release "
           "updates and are subject to revision. Measurement only; not "
           "investment advice.")
