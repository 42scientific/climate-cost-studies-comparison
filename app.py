import io
import math
from textwrap import dedent

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Climate Damages vs. Climate Action Costs",
    page_icon="📉",
    layout="wide",
)

DATA_URL_NOTE = "The data is embedded directly in the app and can be exported as CSV below."


@st.cache_data
def load_ranges() -> pd.DataFrame:
    ranges = [
        {
            "year_min": 2006,
            "year_max": 2006,
            "title": '"Stern Review"',
            "typical_mitigation_cost": "~1% global GDP",
            "typical_damage_cost": "≥5%, expanded to ~20% consumption equivalent",
            "knowledge_change": "Early explicit global cost-benefit comparison."
        },
        {
            "year_min": 2007,
            "year_max": 2014,
            "title": '"IPCC Era"',
            "typical_mitigation_cost": "often a few % of GDP/consumption for ambitious stabilization",
            "typical_damage_cost": "often a few % in traditional IAMs, higher values under catastrophe risk",
            "knowledge_change": "Technology and policy assumptions dominate mitigation costs; damage functions remain conservative."
        },
        {
            "year_min": 2015,
            "year_max": 2021,
            "title": '"Empirical Shift"',
            "typical_mitigation_cost": "still in the low to mid single-digit % range",
            "typical_damage_cost": "from ~1-3% up to ~23% and more",
            "knowledge_change": "Temperature-growth models open up substantially larger damage ranges. "
        },
        {
            "year_min": 2024,
            "year_max": 2026,
            "title": '"New Generation"',
            "typical_mitigation_cost": "strong climate policy sometimes with only small net GDP effects",
            "typical_damage_cost": "~3% to >50%, depending on method; meta-analyses often ~7-13% at 3 C",
            "knowledge_change": "Uncertainty is made more explicit; systemic and persistent damages move to the forefront. "
        },
    ]
    df = pd.DataFrame(ranges)
    year_cols = ["year_min", "year_max"]
    for col in year_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

@st.cache_data
def load_data() -> pd.DataFrame:
    data = [
        {
            "publication_year": 2006,
            "study": "Stern Review: The Economics of Climate Change",
            "short_name": "Stern Review",
            "scope": "Global",
            "horizon": "long term / annual equivalent",
            "metric_type": "GDP- or welfare-equivalent annual cost, % global GDP",
            "damage_low_pct": 5.0,
            "damage_mid_pct": 12.5,
            "damage_high_pct": 20.0,
            "mitigation_low_pct": 1.0,
            "mitigation_mid_pct": 1.0,
            "mitigation_high_pct": 1.0,
            "damage_text": "Unabated climate change: at least 5% of global GDP each year; with wider risks 20% or more.",
            "mitigation_text": "Strong mitigation: around 1% of global GDP per year.",
            "comparability": "High",
            "include_default": True,
            "harmonisation_note": "Both values are from the same report, but Stern's damage number is a welfare-equivalent long-run annual loss, not a point estimate for 2050/2100 GDP.",
            "source_url": "https://webarchive.nationalarchives.gov.uk/ukgwa/20100407172811/http://www.hm-treasury.gov.uk/stern_review_report.htm",
        },
        {
            "publication_year": 2014,
            "study": "IPCC AR5 WGIII: Mitigation of Climate Change",
            "short_name": "IPCC AR5 WGIII",
            "scope": "Global",
            "horizon": "2050",
            "metric_type": "Consumption loss vs baseline, %",
            "damage_low_pct": None,
            "damage_mid_pct": None,
            "damage_high_pct": None,
            "mitigation_low_pct": 2.1,
            "mitigation_mid_pct": 3.4,
            "mitigation_high_pct": 6.2,
            "damage_text": "No single directly comparable aggregate damage estimate in this row.",
            "mitigation_text": "Cost-effective 450 ppm CO2e scenarios: median global consumption loss 3.4% in 2050, range 2.1–6.2%.",
            "comparability": "Medium",
            "include_default": True,
            "harmonisation_note": "Mitigation costs only. Useful benchmark, but not a damage-vs-mitigation pair.",
            "source_url": "https://www.ipcc.ch/report/ar5/wg3/",
        },
        {
            "publication_year": 2015,
            "study": "Burke, Hsiang & Miguel: Global non-linear effect of temperature on economic production",
            "short_name": "Burke et al.",
            "scope": "Global",
            "horizon": "2100",
            "metric_type": "GDP per capita / income loss vs no climate change, %",
            "damage_low_pct": None,
            "damage_mid_pct": 23.0,
            "damage_high_pct": None,
            "mitigation_low_pct": None,
            "mitigation_mid_pct": None,
            "mitigation_high_pct": None,
            "damage_text": "Unmitigated warming expected to reduce average global incomes roughly 23% by 2100.",
            "mitigation_text": "No mitigation-cost estimate in this study row.",
            "comparability": "Medium",
            "include_default": True,
            "harmonisation_note": "Damage estimate only; macroeconometric income effect, not directly paired with a mitigation-cost estimate.",
            "source_url": "https://doi.org/10.1038/nature15725",
        },
        {
            "publication_year": 2021,
            "study": "Swiss Re Institute: The economics of climate change – no action not an option",
            "short_name": "Swiss Re",
            "scope": "Global",
            "horizon": "2050",
            "metric_type": "GDP impact vs no climate change, %",
            "damage_low_pct": 11.0,
            "damage_mid_pct": 14.5,
            "damage_high_pct": 18.0,
            "mitigation_low_pct": None,
            "mitigation_mid_pct": None,
            "mitigation_high_pct": None,
            "damage_text": "Global GDP impact by 2050: 11–14% under current trajectory; up to 18% in a severe no-action scenario.",
            "mitigation_text": "No mitigation-cost estimate in this study row.",
            "comparability": "Medium",
            "include_default": True,
            "harmonisation_note": "Damage estimate only. Midpoint combines current-trajectory range with severe scenario upper bound, so use as order-of-magnitude point.",
            "source_url": "https://www.swissre.com/institute/research/topics-and-risk-dialogues/climate-and-natural-catastrophe-risk/expertise-publication-economics-of-climate-change.html",
        },
        {
            "publication_year": 2022,
            "study": "Deloitte Center for Sustainable Progress: The Turning Point",
            "short_name": "Deloitte",
            "scope": "Global",
            "horizon": "2070",
            "metric_type": "GDP loss in 2070 and cumulative NPV, % / USD",
            "damage_low_pct": None,
            "damage_mid_pct": 7.6,
            "damage_high_pct": None,
            "mitigation_low_pct": None,
            "mitigation_mid_pct": None,
            "mitigation_high_pct": None,
            "damage_text": "Unchecked climate change: US$178 trillion cumulative cost over 2021–2070; 7.6% cut to global GDP in 2070 alone.",
            "mitigation_text": "Net-zero transition below 2°C modelled as US$43 trillion net present value gain, not a gross cost.",
            "comparability": "Low",
            "include_default": True,
            "harmonisation_note": "The 7.6% value is chartable, but the mitigation side is a net-benefit figure in USD NPV rather than a comparable % GDP cost.",
            "source_url": "https://www.deloitte.com/global/en/about/press-room/deloitte-research-reveals-inaction-on-climate-change-could-cost-the-world-economy-us-dollar-178-trillion-by-2070.html",
        },
        {
            "publication_year": 2022,
            "study": "IPCC AR6 WGIII: Mitigation pathways compatible with long-term goals",
            "short_name": "IPCC AR6 WGIII",
            "scope": "Global",
            "horizon": "2050",
            "metric_type": "GDP loss vs reference scenarios, %",
            "damage_low_pct": None,
            "damage_mid_pct": None,
            "damage_high_pct": None,
            "mitigation_low_pct": 2.6,
            "mitigation_mid_pct": 3.4,
            "mitigation_high_pct": 4.2,
            "damage_text": "No single directly comparable aggregate damage estimate in this row.",
            "mitigation_text": "1.5°C pathways with no/limited overshoot: global GDP reductions of 2.6–4.2% in 2050 vs current-policy reference pathways.",
            "comparability": "Medium",
            "include_default": True,
            "harmonisation_note": "Mitigation costs only. IPCC notes these figures exclude avoided climate damages and many co-benefits.",
            "source_url": "https://www.ipcc.ch/report/ar6/wg3/chapter/chapter-3/",
        },
        {
            "publication_year": 2023,
            "study": "BMWK/BMUV: Costs of climate change impacts in Germany",
            "short_name": "BMWK/BMUV",
            "scope": "Germany",
            "horizon": "2050",
            "metric_type": "Annual GDP loss, % German GDP",
            "damage_low_pct": None,
            "damage_mid_pct": 1.2,
            "damage_high_pct": None,
            "mitigation_low_pct": None,
            "mitigation_mid_pct": None,
            "mitigation_high_pct": None,
            "damage_text": "Germany: annual climate-damage costs in 2050 estimated at €20–70bn, or 0.6–1.8% of projected GDP.",
            "mitigation_text": "No decarbonisation-cost estimate in this study row; adaptation could reduce damages by large shares depending on scenario.",
            "comparability": "Low",
            "include_default": True,
            "harmonisation_note": "National damage estimate; not directly comparable to global mitigation-cost studies.",
            "source_url": "https://www.bmwk.de/Redaktion/DE/Artikel/Klimaschutz/kosten-klimawandelfolgen-in-deutschland.html",
        },
        {
            "publication_year": 2024,
            "study": "Kotz, Levermann & Wenz: The economic commitment of climate change",
            "short_name": "Kotz et al.",
            "scope": "Global",
            "horizon": "2050",
            "metric_type": "Income loss vs no additional climate impacts, %",
            "damage_low_pct": 11.0,
            "damage_mid_pct": 19.0,
            "damage_high_pct": 29.0,
            "mitigation_low_pct": 1.8,
            "mitigation_mid_pct": 3.2,
            "mitigation_high_pct": 4.8,
            "damage_text": "Committed climate damages: 19% global income reduction by 2050, likely range 11–29%.",
            "mitigation_text": "Implied approximate mitigation-cost equivalent: damages reported as about six times the mitigation costs required to limit warming to 2°C.",
            "comparability": "Retracted",
            "include_default": False,
            "harmonisation_note": "Retracted in 2025. Mitigation value is derived from the originally reported sixfold ratio, not quoted as a standalone %GDP estimate. Keep as historical/legacy reference only unless a corrected version is used.",
            "source_url": "https://doi.org/10.1038/s41586-024-07219-0",
        },
        {
            "publication_year": 2025,
            "study": "Institute and Faculty of Actuaries / University of Exeter: Planetary Solvency-type stress estimates",
            "short_name": "IFoA / Exeter",
            "scope": "Global",
            "horizon": "2070–2090",
            "metric_type": "Severe systemic GDP-loss stress estimate, %",
            "damage_low_pct": None,
            "damage_mid_pct": 50.0,
            "damage_high_pct": None,
            "mitigation_low_pct": None,
            "mitigation_mid_pct": None,
            "mitigation_high_pct": None,
            "damage_text": "A severe systemic-risk framing reported possible global GDP losses around 50% between 2070 and 2090 under catastrophic climate shocks.",
            "mitigation_text": "No comparable mitigation-cost estimate in this study row.",
            "comparability": "Low",
            "include_default": True,
            "harmonisation_note": "Extreme systemic risk estimate; useful as tail-risk reference, not a central comparable value.",
            "source_url": "https://actuaries.org.uk/",
        },
        {
            "publication_year": 2013,
            "study": "Institute for Policy Integrity at New York University School of Law / Department of Economics, School of Business, Economics and Law, Environmental: Economics Unit, Gothenburg: Methodology Matters: A Careful Meta-Analysis of Climate Damages",
            "short_name": "A Careful Meta-Analysis of Climate Damages",
            "scope": "Global",
            "horizon": "1990–2300",
            "metric_type": "GDP-loss and stress estimates, %",
            "damage_low_pct": 0,
            "damage_mid_pct": 9.1,
            "damage_high_pct": 30.2,
            "mitigation_low_pct": None,
            "mitigation_mid_pct": None,
            "mitigation_high_pct": None,
            "damage_text": "",
            "mitigation_text": "No comparable mitigation-cost estimate in this study.",
            "comparability": "High",
            "include_default": True,
            "harmonisation_note": "",
            "source_url": "https://link.springer.com/article/10.1007/s10640-025-01016-7",
        },
        {
            "publication_year": 2025,
            "study": "Institute for Policy Integrity at New York University School of Law / Department of Economics, School of Business, Economics and Law, Environmental: Economics Unit, Gothenburg: Methodology Matters: A Careful Meta-Analysis of Climate Damages",
            "short_name": "A Careful Meta-Analysis of Climate Damages",
            "scope": "Global",
            "horizon": "2016–2250",
            "metric_type": "GDP-loss and stress estimates, %",
            "damage_low_pct": 0,
            "damage_mid_pct": 7.7,
            "damage_high_pct": 17.6,
            "mitigation_low_pct": None,
            "mitigation_mid_pct": None,
            "mitigation_high_pct": None,
            "damage_text": "",
            "mitigation_text": "No comparable mitigation-cost estimate in this study.",
            "comparability": "High",
            "include_default": True,
            "harmonisation_note": "",
            "source_url": "https://link.springer.com/article/10.1007/s10640-025-01016-7",
        },
    ]
    df = pd.DataFrame(data)
    pct_cols = [c for c in df.columns if c.endswith("_pct")]
    for col in pct_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    year_cols = ["publication_year"]
    for col in year_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def long_format(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in df.iterrows():
        for kind, prefix in [
            ("Climate damages / inaction", "damage"),
            ("Climate action / decarbonization", "mitigation"),
        ]:
            mid = row[f"{prefix}_mid_pct"]
            if pd.notna(mid):
                low = row[f"{prefix}_low_pct"]
                high = row[f"{prefix}_high_pct"]
                publication_year = row["publication_year"]
                rows.append(
                    {
                        "publication_year": publication_year,
                        "publication_year_plot": publication_year,
                        "study": row["study"],
                        "short_name": row["short_name"],
                        "scope": row["scope"],
                        "horizon": row["horizon"],
                        "metric_type": row["metric_type"],
                        "kind": kind,
                        "mid_pct": mid,
                        "low_pct": low,
                        "high_pct": high,
                        "text": row["damage_text"] if prefix == "damage" else row["mitigation_text"],
                        "comparability": row["comparability"],
                        "harmonisation_note": row["harmonisation_note"],
                        "source_url": row["source_url"],
                        "include_default": row["include_default"],
                    }
                )
    return pd.DataFrame(rows)


def quality_badge(value: str) -> str:
    mapping = {
        "High": "high",
        "Medium": "medium",
        "Low": "low",
        "Retracted": "retracted",
    }
    return mapping.get(value, value)


def make_chart(
    points: pd.DataFrame,
    ranges_df: pd.DataFrame,
    show_labels: bool,
) -> go.Figure:
    fig = go.Figure()
    color_map = {
        "Climate damages / inaction": "#9f1239",
        "Climate action / decarbonization": "#047857",
    }
    symbol_map = {
        "High": "circle",
        "Medium": "diamond",
        "Low": "x",
        "Retracted": "cross",
    }

    range_spans = ranges_df.sort_values(["year_min", "year_max", "title"])
    shade_colors = ["rgba(148, 163, 184, 0.18)", "rgba(148, 163, 184, 0.10)"]
    for idx, (_, r) in enumerate(range_spans.iterrows()):
        span_width = float(r["year_max"] - r["year_min"])
        title = str(r["title"])
        center_x = float((r["year_min"] + r["year_max"]) / 2)
        # Heuristic: short labels and wide spans are centered, otherwise left aligned.
        fits_center = span_width >= max(0.9, len(title) * 0.18)
        label_x = center_x if fits_center else float(r["year_min"]) + 0.1
        label_anchor = "center" if fits_center else "left"

        fig.add_vrect(
            x0=r["year_min"],
            x1=r["year_max"],
            fillcolor=shade_colors[idx % len(shade_colors)],
            line_width=0,
            layer="below",
        )
        fig.add_annotation(
            x=label_x,
            y=0.985,
            xref="x",
            yref="paper",
            text=f"<b>{title}</b>",
            showarrow=False,
            xanchor=label_anchor,
            yanchor="top",
            align="center" if fits_center else "left",
            font=dict(size=14, color="#374151"),
            bgcolor="rgba(255,255,255,0.45)",
            bordercolor="rgba(148,163,184,0.5)",
            borderwidth=0,
            borderpad=2,
        )

    for kind, group in points.groupby("kind", sort=False):
        group = group.sort_values("publication_year")
        customdata = group[[
            "short_name",
            "study",
            "scope",
            "horizon",
            "metric_type",
            "text",
            "harmonisation_note",
            "source_url",
            "comparability",
            "publication_year"
        ]]
        marker_symbols = ["circle" if v == "Low" else symbol_map.get(v, "circle") for v in group["comparability"]]
        marker_colors = ["#9ca3af" if v == "Low" else color_map.get(kind) for v in group["comparability"]]
        marker_line_colors = ["#ffffff" if v != "Low" else "#d1d5db" for v in group["comparability"]]

        if kind.startswith("Climate damages"):
            band_group = group.dropna(subset=["low_pct", "high_pct"])
            if not band_group.empty:
                fig.add_trace(
                    go.Scatter(
                        x=band_group["publication_year_plot"],
                        y=band_group["low_pct"],
                        mode="lines",
                        line=dict(width=0),
                        hoverinfo="skip",
                        showlegend=False,
                        legendgroup=kind,
                    )
                )
                fig.add_trace(
                    go.Scatter(
                        x=band_group["publication_year_plot"],
                        y=band_group["high_pct"],
                        mode="lines",
                        line=dict(width=0),
                        fill="tonexty",
                        fillcolor="rgba(159, 18, 57, 0.5)",
                        hoverinfo="skip",
                        showlegend=False,
                        legendgroup=kind,
                    )
                )

        if kind.startswith("Climate action"):
            band_group = group.dropna(subset=["low_pct", "high_pct"])
            if not band_group.empty:
                fig.add_trace(
                    go.Scatter(
                        x=band_group["publication_year_plot"],
                        y=band_group["low_pct"],
                        mode="lines",
                        line=dict(width=0),
                        hoverinfo="skip",
                        showlegend=False,
                        legendgroup=kind,
                    )
                )
                fig.add_trace(
                    go.Scatter(
                        x=band_group["publication_year_plot"],
                        y=band_group["high_pct"],
                        mode="lines",
                        line=dict(width=0),
                        fill="tonexty",
                        fillcolor="rgba(4, 120, 87, 0.5)",
                        hoverinfo="skip",
                        showlegend=False,
                        legendgroup=kind,
                    )
                )

        fig.add_trace(
            go.Scatter(
                x=group["publication_year_plot"],
                y=group["mid_pct"],
                customdata=customdata,
                mode="markers" if kind.startswith("Climate damages") else "markers",
                name=kind,
                marker=dict(
                    size=12,
                    color=marker_colors,
                    line=dict(color=marker_line_colors, width=1.5),
                    symbol=marker_symbols,
                ),
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>"
                    "%{customdata[1]}<br><br>"
                    "<b>%{y:.1f}%</b><br>"
                    "Publication: %{customdata[9]}<br>"
                    "Scope: %{customdata[2]}<br>"
                    "Horizon: %{customdata[3]}<br>"
                    "Metric: %{customdata[4]}<br><br>"
                    "%{customdata[5]}<br><br>"
                    "Note: %{customdata[6]}<br>"
                    "Comparability: %{customdata[8]}"
                    "<extra></extra>"
                ),
            )
        )

    if show_labels:
        for _, r in points.iterrows():
            fig.add_annotation(
                x=r["publication_year_plot"],
                y=r["mid_pct"],
                text=r["short_name"],
                showarrow=True,
                arrowhead=2,
                ax=0,
                ay=-28 if r["kind"].startswith("Climate damages") else 28,
                font=dict(size=11),
                bgcolor="rgba(255,255,255,0.78)",
                bordercolor="rgba(0,0,0,0.12)",
                borderwidth=1,
                borderpad=3,
            )

    fig.update_layout(
        template="plotly_white",
        title=dict(
            text=(
                "Climate damages substantially exceed modeled climate action costs"
                "<br><sup>Selected, harmonized study points since the Stern Review; "
                "values as percent of GDP/income or a comparable macroeconomic "
                "loss metric.</sup>"
            ),
            x=0.02,
            xanchor="left",
            font=dict(size=23, family="Arial", color="#111827"),
        ),
        height=630,
        margin=dict(l=60, r=35, t=110, b=85),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=0.92,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255,255,255,0.0)",
        ),
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial"),
        font=dict(family="Arial", color="#111827"),
    )
    fig.update_xaxes(
        title="Publication year",
        tickmode="linear",
        dtick=2,
        range=[2005.5, 2026.5],
        showgrid=False,
        zeroline=False,
    )
    fig.update_yaxes(
        title="Estimated costs / losses (% of the respective reference metric)",
        rangemode="tozero",
        type="linear",
        ticksuffix="%",
        gridcolor="rgba(17,24,39,0.10)",
        zeroline=False,
    )

    fig.add_annotation(
        xref="paper",
        yref="paper",
        x=0,
        y=-0.18,
        showarrow=False,
        align="left",
        text=(
            "<b>Interpretation:</b> The chart shows orders of magnitude, not perfectly identical macroeconomic accounting. "
            "Investments in the transition are not automatically net costs; many studies report GDP, consumption, income, or welfare losses."
        ),
        font=dict(size=12, color="#4b5563"),
    )
    return fig


ranges_df = load_ranges()
df = load_data()
long_df = long_format(df)

st.title("Climate Damages vs. Climate Action Costs")
st.caption("Comparing 20 years of climate and decarb cost studies")

with st.sidebar:
    st.header("Display")
    view = st.radio(
        "Data selection",
        ["Best comparable / default", "All chartable study points", "Global studies only", "Germany only"],
        index=0,
    )
    kinds = st.multiselect(
        "Cost categories",
        sorted(long_df["kind"].unique()),
        default=sorted(long_df["kind"].unique()),
    )
    show_labels = st.toggle("Show study labels", value=True)
    st.divider()
    st.markdown(
        dedent(
            """
            **Important for publication**  
            This visualization works as a narrative overview. The incorporated studies use different methods, time horizons, and cost concepts.
            """
        )
    )

points = long_df.copy()
if view == "Best comparable / default":
    points = points[points["include_default"]]
elif view == "Global studies only":
    points = points[points["scope"] == "Global"]
elif view == "Germany only":
    points = points[points["scope"] == "Germany"]
points = points[points["kind"].isin(kinds)]

# m1, m2, m3, m4 = st.columns(4)
m1, m2, m3 = st.columns(3)
with m1:
    st.metric("Study points", f"{len(points)}")
with m2:
    mit = points.loc[points["kind"].str.startswith("Climate action"), "mid_pct"]
    st.metric("Median climate action cost", "-" if mit.empty else f"{mit.median():.1f} %")
with m3:
    dmg = points.loc[points["kind"].str.startswith("Climate damages"), "mid_pct"]
    st.metric("Median climate damages", "-" if dmg.empty else f"{dmg.median():.1f} %")
# with m4:
#     pair_source = df[df["comparability"] != "Retracted"].dropna(subset=["damage_mid_pct", "mitigation_mid_pct"]).copy()
#     pair_source["ratio"] = pair_source["damage_mid_pct"] / pair_source["mitigation_mid_pct"]
#     st.metric("Median ratio", "-" if pair_source.empty else f"{pair_source['ratio'].median():.1f}x")

if points.empty:
    st.warning("No chartable data points are available for the current filter combination.")
else:
    fig = make_chart(
        points,
        ranges_df,
        show_labels=show_labels,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False, "toImageButtonOptions": {"format": "png", "scale": 3}})

    with st.sidebar:
        st.divider()
        st.subheader("Downloads")
        st.download_button(
            "Download data as CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="climate_costs_harmonized_studies.csv",
            mime="text/csv",
        )
        st.download_button(
            "Interactive chart as HTML",
            data=fig.to_html(include_plotlyjs="cdn", full_html=True).encode("utf-8"),
            file_name="climate_costs_chart.html",
            mime="text/html",
        )
        try:
            svg = fig.to_image(format="svg", scale=2)
            st.download_button(
                "Publication chart as SVG",
                data=svg,
                file_name="climate_costs_chart.svg",
                mime="image/svg+xml",
            )
        except Exception:
            st.info("Please install kaleido for SVG export. It is already listed in requirements.txt.")

st.divider()

st.subheader("Core takeaway")
st.markdown(
    dedent(
        """
        Ambitious, efficiently organized decarbonization incurs measurable and sometimes substantial transformation costs. However, much of the current economic literature concludes that these costs are significantly lower than the expected long-term damages of a high-temperature warming pathway. And the more systemic risks and persistent growth effects are taken into account, the more pronounced this difference becomes.
        """
    )
)
pair = df[df["comparability"] != "Retracted"].dropna(subset=["damage_mid_pct", "mitigation_mid_pct"])[["short_name", "damage_mid_pct", "mitigation_mid_pct"]].copy()
# if not pair.empty:
#     pair["Damage / climate action cost"] = pair["damage_mid_pct"] / pair["mitigation_mid_pct"]
#     st.dataframe(
#         pair.rename(
#             columns={
#                 "short_name": "Study",
#                 "damage_mid_pct": "Damage (%)",
#                 "mitigation_mid_pct": "Climate action (%)",
#             }
#         ),
#         use_container_width=True,
#         hide_index=True,
#     )

st.subheader("Studies summary and methodological context")
table_cols = [
    "publication_year",
    "short_name",
    "scope",
    "horizon",
    "damage_text",
    "mitigation_text",
    "comparability",
    "harmonisation_note",
]
shown = df[table_cols].rename(
    columns={
        "publication_year": "Year",
        "short_name": "Study",
        "scope": "Scope",
        "horizon": "Horizon",
        "damage_text": "Climate damages / inaction",
        "mitigation_text": "Climate action / decarbonization",
        "comparability": "Comparability",
        "harmonisation_note": "Harmonization note",
    }
)
st.dataframe(shown, use_container_width=True, hide_index=True)

with st.expander("Source URLs"):
    for _, row in df.sort_values("publication_year").iterrows():
        year_min = int(row["publication_year"])
        year_max = year_min
        year_label = f"{year_min}" if year_min == year_max else f"{year_min}-{year_max}"
        st.markdown(f"- **{year_label} - {row['short_name']}**: [Open source]({row['source_url']})")
