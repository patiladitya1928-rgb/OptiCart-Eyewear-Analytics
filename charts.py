
"""Reusable Plotly chart builders for OptiCart."""

from __future__ import annotations

from typing import Sequence

import plotly.graph_objects as go
import plotly.io as pio


# Light dashboard theme
NAVY = "#172033"
PANEL = "#FFFFFF"
TEAL = "#0D9488"
BLUE = "#4F78B8"
MUTED = "#64748B"
GRID = "rgba(100,116,139,0.16)"

PALETTE = [
    TEAL,
    BLUE,
    "#8B5CF6",
    "#E69A38",
    "#D977A8",
    "#16A36A",
    "#7C9CE8",
]


def _base_layout(title: str, *, height: int = 360) -> dict:
    return dict(
        title=dict(
            text=title,
            x=0.02,
            xanchor="left",
            font=dict(
                family="Manrope, sans-serif",
                size=24,
                color=NAVY,
            ),
        ),
        height=height,
        autosize=True,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="DM Sans, Arial, sans-serif",
            color="#334155",
            size=16,
        ),
        margin=dict(l=78, r=34, t=82, b=76),
        hoverlabel=dict(
            bgcolor=NAVY,
            bordercolor=NAVY,
            font=dict(
                family="DM Sans, Arial, sans-serif",
                color="#FFFFFF",
                size=16,
            ),
            namelength=-1,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(
                family="DM Sans, Arial, sans-serif",
                color="#334155",
                size=15,
            ),
        ),
    )


def _empty_figure(title: str, height: int = 360) -> go.Figure:
    fig = go.Figure()

    fig.add_annotation(
        text="No data available for the selected criteria",
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(size=14, color=MUTED),
    )

    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    fig.update_layout(**_base_layout(title, height=height))

    return fig


def _bar(
    labels: Sequence,
    values: Sequence,
    title: str,
    series: str,
    *,
    horizontal: bool = False,
    height: int = 360,
) -> go.Figure:

    if len(labels) == 0 or len(values) == 0:
        return _empty_figure(title, height)

    pairs = [
        (str(label), float(value or 0))
        for label, value in zip(labels, values)
    ]

    pairs.sort(key=lambda item: item[1], reverse=True)

    names, nums = zip(*pairs)

    colors = [
        TEAL if i == 0 else BLUE
        for i in range(len(nums))
    ]

    fig = go.Figure(
        go.Bar(
            x=list(nums) if horizontal else list(names),
            y=list(names) if horizontal else list(nums),
            orientation="h" if horizontal else "v",
            name=series,
            marker=dict(
                color=colors,
                line=dict(color="#FFFFFF", width=1.5),
                cornerradius=6,
            ),
            text=[f"₹{v:,.0f}" for v in nums],
            textposition="auto",
            textfont=dict(color="#FFFFFF", size=13),
            customdata=[f"₹{v:,.2f}" for v in nums],
            hovertemplate=(
                "%{y}<br>Revenue: %{customdata}<extra></extra>"
                if horizontal
                else "%{x}<br>Revenue: %{customdata}<extra></extra>"
            ),
        )
    )

    layout = _base_layout(title, height=height)
    layout["showlegend"] = False

    fig.update_layout(**layout)

    if horizontal:
        fig.update_xaxes(
            title="Revenue (₹)",
            tickformat=",.0f",
            gridcolor=GRID,
            zeroline=False,
            tickfont=dict(color="#475569", size=14),
            title_font=dict(color="#334155"),
        )

        fig.update_yaxes(
            autorange="reversed",
            gridcolor="rgba(0,0,0,0)",
            tickfont=dict(color="#334155", size=14),
        )

    else:
        fig.update_yaxes(
            title="Revenue (₹)",
            tickformat=",.0f",
            gridcolor=GRID,
            zeroline=False,
            tickfont=dict(color="#475569", size=14),
            title_font=dict(color="#334155"),
        )

        fig.update_xaxes(
            tickangle=-25,
            tickfont=dict(color="#475569", size=13),
        )

    return fig


def monthly_sales_chart(labels: Sequence, values: Sequence) -> go.Figure:
    title = "Monthly Sales Trend"

    if len(labels) == 0 or len(values) == 0:
        return _empty_figure(title)

    fig = go.Figure(
        go.Scatter(
            x=list(labels),
            y=[float(v or 0) for v in values],
            mode="lines+markers",
            name="Monthly Revenue",
            line=dict(color=TEAL, width=3.5, shape="spline"),
            marker=dict(
                size=9,
                color=TEAL,
                line=dict(color="#FFFFFF", width=2),
            ),
            fill="tozeroy",
            fillcolor="rgba(13,148,136,0.08)",
            hovertemplate=(
                "%{x}<br>Revenue: ₹%{y:,.2f}<extra></extra>"
            ),
        )
    )

    fig.update_layout(**_base_layout(title))

    fig.update_yaxes(
        title="Revenue (₹)",
        tickformat=",.0f",
        gridcolor=GRID,
        zeroline=False,
        tickfont=dict(color="#475569", size=14),
        title_font=dict(color="#334155"),
    )

    fig.update_xaxes(
        title="Month",
        gridcolor=GRID,
        tickangle=0,
        tickfont=dict(color="#475569", size=14),
        title_font=dict(color="#334155"),
    )

    return fig





def product_revenue_chart(labels: Sequence, values: Sequence) -> go.Figure:
    title = "Revenue by Product Category"

    if not labels or not values:
        return _empty_figure(title, 700)

    # Prepare and sort category revenue
    pairs = [
        (str(label), float(value or 0))
        for label, value in zip(labels, values)
    ]

    pairs.sort(key=lambda item: item[1], reverse=True)

    names = [item[0] for item in pairs]
    revenues = [item[1] for item in pairs]

    total_revenue = sum(revenues)

    if total_revenue <= 0:
        return _empty_figure(title, 700)

    percentages = [
        (revenue / total_revenue) * 100
        for revenue in revenues
    ]

    positions = list(range(len(names)))

    axis_max = max(30, max(percentages) * 1.15)

    fig = go.Figure()

    # Background tracks
    fig.add_trace(
        go.Bar(
            x=[axis_max] * len(names),
            y=positions,
            orientation="h",
            marker=dict(color="#E9EDF4"),
            width=0.55,
            hoverinfo="skip",
            showlegend=False,
        )
    )

    # Revenue contribution bars
    fig.add_trace(
        go.Bar(
            x=percentages,
            y=positions,
            orientation="h",
            marker=dict(
                color=[
                    TEAL if i == 0 else BLUE
                    for i in range(len(names))
                ],
                cornerradius=7,
            ),
            width=0.55,
            customdata=[
                [revenue, percentage]
                for revenue, percentage in zip(
                    revenues, percentages
                )
            ],
            hovertemplate=(
                "<b>Revenue: ₹%{customdata[0]:,.2f}</b><br>"
                "Contribution: %{customdata[1]:.2f}%"
                "<extra></extra>"
            ),
            showlegend=False,
        )
    )

    # Percentage labels
    for position, percentage in zip(positions, percentages):
        fig.add_annotation(
            x=axis_max,
            y=position,
            text=f"<b>{percentage:.1f}%</b>",
            showarrow=False,
            xanchor="right",
            xshift=-12,
            font=dict(
                size=16,
                color="#334155",
            ),
        )

    # Revenue labels below each bar
    for position, revenue in zip(positions, revenues):
        fig.add_annotation(
            x=0,
            y=position + 0.45,
            xref="x",
            yref="y",
            text=f"₹{revenue:,.2f}",
            showarrow=False,
            xanchor="left",
            yanchor="middle",
            font=dict(
                family="Arial, sans-serif",
                size=14,
                color="#64748B",
            ),
        )

    fig.update_layout(
        title=dict(
            text=title,
            x=0.02,
            xanchor="left",
            font=dict(
                size=24,
                color=NAVY,
            ),
        ),

        height=max(380, len(names) * 90 + 100),

        barmode="overlay",
        bargap=0.38,
        autosize=True,

        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",

        margin=dict(
            l=175,
            r=35,
            t=85,
            b=55,
        ),

        showlegend=False,

        font=dict(
            size=16,
            color="#334155",
        ),

        xaxis=dict(
            range=[0, axis_max],
            visible=False,
            fixedrange=True,
        ),

        yaxis=dict(
            tickmode="array",
            tickvals=positions,
            ticktext=[
                f"{i + 1}. {name}"
                for i, name in enumerate(names)
            ],
            range=[-0.5, len(names) - 0.5],
            autorange="reversed",
            showgrid=False,
            zeroline=False,
            tickfont=dict(
                size=17,
                color="#334155",
            ),
            fixedrange=True,
        ),
    )

    return fig



def regional_revenue_chart(labels: Sequence, values: Sequence) -> go.Figure:
    return _bar(
        labels,
        values,
        "Revenue by State",
        "State Revenue",
        horizontal=True,
        height=max(360, 28 * len(labels) + 100),
    )


def customer_gender_chart(labels: Sequence, values: Sequence) -> go.Figure:
    title = "Sales-record Gender Distribution"

    if (
        len(labels) == 0
        or len(values) == 0
        or sum(float(v or 0) for v in values) == 0
    ):
        return _empty_figure(title, 410)

    fig = go.Figure(
        go.Pie(
            labels=list(labels),
            values=[int(v or 0) for v in values],
            hole=0.62,
            sort=False,
            marker=dict(
                colors=PALETTE,
                line=dict(color="#FFFFFF", width=3),
            ),
            textinfo="label+percent",
            textfont=dict(color="#334155", size=14),
            hovertemplate=(
                "%{label}<br>Sales records: %{value:,}"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(**_base_layout(title, height=410))

    fig.update_layout(
        title=dict(font=dict(size=19, color=NAVY)),
        margin=dict(l=35, r=35, t=65, b=100),
        showlegend=True,
        legend=dict(
            orientation="h",
            y=-0.18,
            x=0.5,
            xanchor="center",
            font=dict(color="#334155", size=14),
        ),
    )

    return fig


def customer_age_chart(labels: Sequence, values: Sequence) -> go.Figure:
    title = "Sales-record Age Group Distribution"

    if len(labels) == 0 or len(values) == 0:
        return _empty_figure(title, 410)

    fig = go.Figure(
        go.Bar(
            x=list(labels),
            y=[int(v or 0) for v in values],
            marker=dict(color=BLUE, cornerradius=5),
            name="Sales records",
            hovertemplate=(
                "%{x}<br>Sales records: %{y:,}<extra></extra>"
            ),
        )
    )

    fig.update_layout(**_base_layout(title, height=410))

    fig.update_layout(
        title=dict(font=dict(size=19, color=NAVY)),
        margin=dict(l=75, r=30, t=65, b=85),
        showlegend=False,
    )

    fig.update_yaxes(
        title="Sales records",
        rangemode="tozero",
        gridcolor=GRID,
        tickfont=dict(color="#475569", size=14),
        title_font=dict(color="#334155", size=15),
        automargin=True,
    )

    fig.update_xaxes(
        tickangle=0,
        automargin=True,
        tickfont=dict(color="#475569", size=13),
    )

    return fig


def sales_channel_chart(labels: Sequence, values: Sequence) -> go.Figure:
    title = "Revenue by Sales Channel"

    if len(labels) == 0 or len(values) == 0:
        return _empty_figure(title)

    fig = go.Figure(
        go.Pie(
            labels=list(labels),
            values=[float(v or 0) for v in values],
            hole=0.58,
            sort=False,
            marker=dict(
                colors=PALETTE,
                line=dict(color="#FFFFFF", width=3),
            ),
            textinfo="label+percent",
            textfont=dict(color="#334155", size=14),
            hovertemplate=(
                "%{label}<br>Revenue: ₹%{value:,.2f}"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(**_base_layout(title))

    fig.update_layout(
        legend=dict(
            orientation="h",
            y=-0.12,
            x=0.5,
            xanchor="center",
            font=dict(color="#334155", size=14),
        )
    )

    return fig


def store_type_chart(labels: Sequence, values: Sequence) -> go.Figure:
    return _bar(
        labels,
        values,
        "Revenue by Store Type",
        "Store Revenue",
        horizontal=True,
    )


def render_chart(fig: go.Figure, element_id: str) -> str:
    """Render a responsive Plotly chart."""

    return pio.to_html(
        fig,
        full_html=False,
        include_plotlyjs=False,
        include_mathjax=False,
        div_id=element_id,
        config={
            "responsive": True,
            "displaylogo": False,
            "modeBarButtonsToRemove": [
                "lasso2d",
                "select2d",
            ],
        },
    )
