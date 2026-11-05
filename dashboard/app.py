
"""Customer 360 Revenue Intelligence Dashboard."""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_FILE = (
    PROJECT_ROOT / "data" / "processed" / "customer_360.csv"
)


st.set_page_config(
    page_title="Customer 360 | Revenue Intelligence",
    page_icon="📊",
    layout="wide",
)


@st.cache_data
def load_customer_data():
    """Load the Gold Customer 360 dataset."""

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            "Customer 360 dataset not found. "
            "Run the ingestion, Silver and Gold pipelines first."
        )

    dataframe = pd.read_csv(DATA_FILE)

    dataframe["signup_date"] = pd.to_datetime(
        dataframe["signup_date"]
    )

    return dataframe


def format_currency(value):
    """Format revenue values in USD."""

    return f"${value:,.0f}"


def main():
    st.title("Customer 360 Revenue Intelligence")
    st.caption(
        "Explore customer behaviour, revenue performance "
        "and acquisition insights."
    )

    try:
        dataframe = load_customer_data()
    except FileNotFoundError as error:
        st.error(str(error))
        st.stop()

    # Sidebar filters
    st.sidebar.header("Dashboard Filters")

    countries = st.sidebar.multiselect(
        "Country",
        options=sorted(dataframe["country"].dropna().unique()),
        default=sorted(dataframe["country"].dropna().unique()),
    )

    industries = st.sidebar.multiselect(
        "Industry",
        options=sorted(dataframe["industry"].dropna().unique()),
        default=sorted(dataframe["industry"].dropna().unique()),
    )

    channels = st.sidebar.multiselect(
        "Acquisition Channel",
        options=sorted(
            dataframe["acquisition_channel"].dropna().unique()
        ),
        default=sorted(
            dataframe["acquisition_channel"].dropna().unique()
        ),
    )

    statuses = st.sidebar.multiselect(
        "Account Status",
        options=sorted(
            dataframe["account_status"].dropna().unique()
        ),
        default=sorted(
            dataframe["account_status"].dropna().unique()
        ),
    )

    # Apply filters
    filtered = dataframe[
        dataframe["country"].isin(countries)
        & dataframe["industry"].isin(industries)
        & dataframe["acquisition_channel"].isin(channels)
        & dataframe["account_status"].isin(statuses)
    ].copy()

    st.sidebar.divider()
    st.sidebar.metric(
        "Filtered Customers",
        f"{filtered['customer_id'].nunique():,}",
    )

    if filtered.empty:
        st.warning("No customers match the selected filters.")
        st.stop()

    # KPI calculations
    total_customers = filtered["customer_id"].nunique()

    total_revenue = filtered["annual_revenue"].sum()

    average_revenue = (
        total_revenue / total_customers
        if total_customers else 0
    )

    churned_customers = (
        filtered["is_churned"].astype(bool).sum()
    )

    churn_rate = (
        churned_customers / total_customers * 100
        if total_customers else 0
    )

    active_customers = (
        filtered["account_status"] == "Active"
    ).sum()

    # KPI cards
    st.subheader("Business Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Customers",
        f"{total_customers:,}",
    )

    col2.metric(
        "Annual Customer Revenue",
        format_currency(total_revenue),
    )

    col3.metric(
        "Average Revenue / Customer",
        format_currency(average_revenue),
    )

    col4.metric(
        "Customer Churn Rate",
        f"{churn_rate:.1f}%",
    )

    st.divider()

    # Revenue analysis
    st.subheader("Revenue Performance")

    col1, col2 = st.columns(2)

    country_revenue = (
        filtered.groupby("country", as_index=False)
        .agg(
            total_revenue=("annual_revenue", "sum"),
            customers=("customer_id", "nunique"),
        )
        .sort_values("total_revenue", ascending=False)
    )

    with col1:
        fig_country = px.bar(
            country_revenue,
            x="country",
            y="total_revenue",
            title="Annual Customer Revenue by Country",
            labels={
                "country": "Country",
                "total_revenue": "Annual Revenue (USD)",
            },
            text_auto=".2s",
        )

        fig_country.update_layout(
            xaxis_title=None,
            yaxis_title="Annual Revenue (USD)",
        )

        st.plotly_chart(fig_country, use_container_width=True)

    channel_revenue = (
        filtered.groupby("acquisition_channel", as_index=False)
        .agg(
            total_revenue=("annual_revenue", "sum"),
            customers=("customer_id", "nunique"),
        )
        .sort_values("total_revenue", ascending=False)
    )

    with col2:
        fig_channel = px.bar(
            channel_revenue,
            x="acquisition_channel",
            y="total_revenue",
            title="Revenue by Acquisition Channel",
            labels={
                "acquisition_channel": "Acquisition Channel",
                "total_revenue": "Annual Revenue (USD)",
            },
            text_auto=".2s",
        )

        fig_channel.update_layout(
            xaxis_title=None,
            yaxis_title="Annual Revenue (USD)",
        )

        st.plotly_chart(fig_channel, use_container_width=True)

    # Customer segmentation
    st.subheader("Customer Segmentation")

    col1, col2 = st.columns(2)

    industry_revenue = (
        filtered.groupby("industry", as_index=False)
        .agg(
            total_revenue=("annual_revenue", "sum"),
        )
        .sort_values("total_revenue", ascending=False)
    )

    with col1:
        fig_industry = px.bar(
            industry_revenue,
            x="industry",
            y="total_revenue",
            title="Revenue by Industry",
            labels={
                "industry": "Industry",
                "total_revenue": "Annual Revenue (USD)",
            },
            text_auto=".2s",
        )

        st.plotly_chart(fig_industry, use_container_width=True)

    status_summary = (
        filtered["account_status"]
        .value_counts()
        .rename_axis("account_status")
        .reset_index(name="customer_count")
    )

    with col2:
        fig_status = px.pie(
            status_summary,
            names="account_status",
            values="customer_count",
            title="Customer Account Status",
            hole=0.45,
        )

        st.plotly_chart(fig_status, use_container_width=True)

    # Customer value segments
    st.subheader("Customer Value Distribution")

    value_summary = (
        filtered["customer_value_segment"]
        .value_counts()
        .rename_axis("customer_value_segment")
        .reset_index(name="customer_count")
    )

    fig_value = px.bar(
        value_summary,
        x="customer_value_segment",
        y="customer_count",
        title="Customers by Value Segment",
        labels={
            "customer_value_segment": "Customer Value",
            "customer_count": "Number of Customers",
        },
        text_auto=True,
    )

    st.plotly_chart(fig_value, use_container_width=True)

    # Customer-level data
    st.subheader("Customer 360 Explorer")

    display_columns = [
        "customer_id",
        "customer_name",
        "country",
        "industry",
        "annual_revenue",
        "account_status",
        "acquisition_channel",
        "revenue_segment",
        "engagement_segment",
        "customer_lifecycle_stage",
        "customer_value_segment",
        "days_since_last_activity",
    ]

    available_columns = [
        column for column in display_columns
        if column in filtered.columns
    ]

    st.dataframe(
        filtered[available_columns].sort_values(
            "annual_revenue",
            ascending=False,
        ),
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "Portfolio demonstration using synthetic customer data. "
        "Revenue figures represent synthetic annual customer revenue."
    )


if __name__ == "__main__":
    main()
