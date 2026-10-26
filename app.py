
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
</style>""", unsafe_allow_html=True)

a = D["as_of"]
st.title("India Macro")
st.caption(f"Verified through {a['verified_to']} · provisional through "
           f"{a['provisional_to']} · generated {D['generated'][:16]}")
st.markdown(f"#### {D['position']}")
st.divider()

def badge(src):
    return ('<span class="badge ver">Verified</span>' if src == "live"
            else '<span class="badge prov">Provisional</span>')

cols = st.columns(len(D["tiles"]))
for c, t in zip(cols, D["tiles"]):
    c.markdown(
        f'<div class="tile"><div class="l">{t["label"]}{badge(t["source"])}'
        f'</div><div class="v">{t["value"]:+.2f}{t["unit"]}</div>'
        f'<div class="p">{t["period"]}</div></div>', unsafe_allow_html=True)

def block(key, title, chart=None, pct=None):
    b = D.get(key)
    if not b:
        return
    st.subheader(title)
    st.markdown(badge(b.get("source", "snapshot")), unsafe_allow_html=True)
    df = pd.DataFrame(b["rows"], columns=b["cols"])
    if b.get("period"):
        st.caption(b["period"])
    st.dataframe(df, hide_index=True, use_container_width=True)
    if chart and st.toggle("Show chart", key="t_" + key):
        st.line_chart(df.set_index(df.columns[0])) if chart == "line" \
            else st.bar_chart(df.set_index(df.columns[0])[chart])
    if b.get("note"):
        st.markdown(f'<div class="note">{b["note"]}</div>',
                    unsafe_allow_html=True)

tabs = st.tabs(["Inflation", "Growth", "Industry", "Slack",
                "Corporate", "Cross-checks", "Sector view"])
with tabs[0]:
    block("inflation", "Inflation, three measures", chart="line")
    block("inflation_sources", "Where inflation comes from",
          chart="pp of headline")
with tabs[1]:
    block("components", "GDP components")
with tabs[2]:
    block("industry", "Industrial production by use")
with tabs[3]:
    block("slack", "Slack")
with tabs[4]:
    block("corporate", "Corporate accounts")
with tabs[5]:
    b = D["checks"]
    st.subheader("Cross-checks")
    df = pd.DataFrame(b["rows"], columns=b["cols"])
    def col(v):
        return ("background-color:#eef7f0" if v == "AGREE" else
                "background-color:#fdecea" if v == "BREAK" else
                "background-color:#fff4e0" if v else "")
    st.dataframe(df.style.map(col, subset=["Result"]),
                 hide_index=True, use_container_width=True)
    st.markdown(f'<div class="note">{b["note"]}</div>',
                unsafe_allow_html=True)
with tabs[6]:
    st.subheader("Sector view")
    for s in D["sectors"]:
        st.markdown(f"- {s}")

st.divider()
st.caption("Figures marked Provisional carry data pending source release "
           "updates and are subject to revision. Measurement only; not "
           "investment advice.")
