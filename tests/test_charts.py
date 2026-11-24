import plotly.graph_objects as go
import pytest

from charts import (
    monthly_sales_chart,
    product_revenue_chart,
    regional_revenue_chart,
    customer_gender_chart,
    customer_age_chart,
    sales_channel_chart,
    store_type_chart,
    render_chart,
)


@pytest.mark.parametrize(
    "builder,args",
    [
        (monthly_sales_chart, ([], [])),
        (product_revenue_chart, ([], [])),
        (regional_revenue_chart, ([], [])),
        (customer_gender_chart, ([], [])),
        (customer_age_chart, ([], [])),
        (sales_channel_chart, ([], [])),
        (store_type_chart, ([], [])),
    ],
)
def test_chart_builders_return_empty_state_for_no_data(builder, args):
    figure = builder(*args)
    assert isinstance(figure, go.Figure)
    assert any(
        "No data available" in str(annotation.text)
        for annotation in figure.layout.annotations
    )


@pytest.mark.parametrize(
    "builder,args",
    [
        (monthly_sales_chart, (["2026-01", "2026-02"], [100.0, 200.0])),
        (product_revenue_chart, (["Frames", "Lenses"], [100.0, 200.0])),
        (regional_revenue_chart, (["Karnataka", "Maharashtra"], [100.0, 200.0])),
        (customer_gender_chart, (["Female", "Male"], [4, 6])),
        (customer_age_chart, (["20-29", "30-39"], [4, 6])),
        (sales_channel_chart, (["Online", "Store"], [100.0, 200.0])),
        (store_type_chart, (["Mall", "High Street"], [100.0, 200.0])),
    ],
)
def test_chart_builders_return_figures_for_data(builder, args):
    figure = builder(*args)
    assert isinstance(figure, go.Figure)
    assert len(figure.data) == 1


def test_render_chart_returns_embedded_plotly_div():
    figure = monthly_sales_chart(["2026-01"], [100.0])
    html = render_chart(figure, "testChart")
    assert 'id="testChart"' in html
    assert "Plotly.newPlot" in html

def test_customer_gender_chart_handles_zero_total():
    figure = customer_gender_chart(
        ["Female", "Male"],
        [0, 0],
    )

    assert isinstance(figure, go.Figure)
    assert any(
        "No data available" in str(annotation.text)
        for annotation in figure.layout.annotations
    )