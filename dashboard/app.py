
"""Customer 360 | Revenue Intelligence Dashboard."""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# =========================================================
# CONFIGURATION
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_FILE = (
    PROJECT_ROOT / "data" / "processed" / "customer_360.csv"
)

FILTER_COLUMNS = [
    "country",
    "industry",
    "acquisition_channel",
    "account_status",
]

st.set_page_config(
    page_title="Customer 360 | Revenue Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    .stApp {
        background-color: #F4F7FB;
    }

    .block-container {
        max-width: 1500px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    /* Dashboard header */

    .main-header {
        background: linear-gradient(120deg, #142B4A, #234D78);
        padding: 34px 38px;
        border-radius: 16px;
        margin-bottom: 28px;
    }

    .header-tag {
        color: #93C5FD;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 2px;
        margin-bottom: 10px;
    }

    .main-header h1 {
        color: #FFFFFF !important;
        font-size: 32px !important;
        font-weight: 700 !important;
        margin: 0 0 10px 0 !important;
        padding: 0 !important;
    }

    .main-header p {
        color: #E2EAF5 !important;
        font-size: 14px !important;
        margin: 0 !important;
    }

    /* Section headings */

    .section-title {
        color: #1E293B;
        font-size: 21px;
        font-weight: 700;
        margin-top: 22px;
        margin-bottom: 16px;
    }

    /* KPI cards */

    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 13px;
        padding: 20px;
        min-height: 125px;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
    }

    .kpi-label {
        color: #64748B;
        font-size: 12px;
        font-weight: 700;
        margin-bottom: 12px;
    }

    .kpi-value {
        color: #172B4D;
        font-size: 27px;
        font-weight: 750;
        margin-bottom: 7px;
    }

    .kpi-caption {
        color: #64748B;
        font-size: 11px;
    }

    /* Filter panel */

    div[data-testid="stExpander"] {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
    }

    div[data-testid="stExpander"] summary {
        color: #1E293B;
        font-weight: 600;
    }

    /* Buttons */

    div[data-testid="stButton"] button {
        border-radius: 8px;
        min-height: 42px;
        font-weight: 600;
    }

    /* Footer */

    .footer {
        text-align: center;
        color: #64748B;
        font-size: 11px;
        padding-top: 30px;
        line-height: 1.8;
    }

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# LOAD CUSTOMER DATA
# =========================================================

@st.cache_data
def load_customer_data():

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            "Customer 360 dataset not found. "
            "Run the ingestion and transformation pipelines first."
        )

    dataframe = pd.read_csv(DATA_FILE)

    dataframe["signup_date"] = pd.to_datetime(
        dataframe["signup_date"],
        errors="coerce",
    )

    return dataframe


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def format_currency(value):
    return f"${value:,.0f}"


def render_kpi(label, value, caption):

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-caption">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def style_chart(fig):

    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(
            family="Arial",
            color="#334155",
            size=12,
        ),
        title_font=dict(
            size=15,
            color="#1E293B",
        ),
        margin=dict(
            l=15,
            r=15,
            t=55,
            b=20,
        ),
        legend_title_text="",
    )

    fig.update_xaxes(
        tickfont=dict(color="#475569"),
        gridcolor="#F1F5F9",
    )

    fig.update_yaxes(
        tickfont=dict(color="#475569"),
        gridcolor="#E9EEF5",
    )

    return fig


# =========================================================
# FILTER MANAGEMENT
# =========================================================

def initialize_filter_state(dataframe):

    for column in FILTER_COLUMNS:

        options = sorted(
            dataframe[column].dropna().unique().tolist()
        )

        st.session_state[f"all_{column}"] = options

        if f"draft_{column}" not in st.session_state:
            st.session_state[f"draft_{column}"] = options.copy()

        if f"applied_{column}" not in st.session_state:
            st.session_state[f"applied_{column}"] = options.copy()


def apply_filters():

    for column in FILTER_COLUMNS:

        st.session_state[f"applied_{column}"] = (
            st.session_state[f"draft_{column}"].copy()
        )


def reset_filters():

    for column in FILTER_COLUMNS:

        options = st.session_state[f"all_{column}"]

        st.session_state[f"draft_{column}"] = options.copy()
        st.session_state[f"applied_{column}"] = options.copy()


# =========================================================
# MAIN APPLICATION
# =========================================================

def main():

    # -----------------------------------------------------
    # HEADER
    # -----------------------------------------------------

    st.markdown(
        """
        <div class="main-header">
            <div class="header-tag">CUSTOMER ANALYTICS PLATFORM</div>
            <h1>Customer 360 | Revenue Intelligence</h1>
            <p>A unified view of customer performance, revenue,
            engagement and retention insights.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # -----------------------------------------------------
    # DATA
    # -----------------------------------------------------

    try:
        dataframe = load_customer_data()

    except FileNotFoundError as error:
        st.error(str(error))
        st.stop()

    initialize_filter_state(dataframe)

    # -----------------------------------------------------
    # FILTER PANEL
    # -----------------------------------------------------

    with st.expander("⚙️ Dashboard Filters", expanded=False):

        st.caption(
            "Select the required values and click Apply Filters "
            "to update the dashboard."
        )

        left, right = st.columns(2)

        with left:

            st.multiselect(
                "Country",
                options=st.session_state["all_country"],
                key="draft_country",
            )

            st.multiselect(
                "Acquisition Channel",
                options=st.session_state[
                    "all_acquisition_channel"
                ],
                key="draft_acquisition_channel",
            )

        with right:

            st.multiselect(
                "Industry",
                options=st.session_state["all_industry"],
                key="draft_industry",
            )

            st.multiselect(
                "Account Status",
                options=st.session_state["all_account_status"],
                key="draft_account_status",
            )

        button_left, button_right, _ = st.columns([1, 1, 4])

        with button_left:

            st.button(
                "Apply Filters",
                type="primary",
                width="stretch",
                on_click=apply_filters,
            )

        with button_right:

            st.button(
                "Reset Filters",
                width="stretch",
                on_click=reset_filters,
            )

    # -----------------------------------------------------
    # FILTERED DATA
    # -----------------------------------------------------

    filtered = dataframe.copy()

    for column in FILTER_COLUMNS:

        filtered = filtered[
            filtered[column].isin(
                st.session_state[f"applied_{column}"]
            )
        ]

    if filtered.empty:

        st.warning(
            "No customers match the selected filters. "
            "Please adjust your filters."
        )

        st.stop()

    # -----------------------------------------------------
    # KPI CALCULATIONS
    # -----------------------------------------------------

    total_customers = filtered["customer_id"].nunique()

    total_revenue = filtered["annual_revenue"].sum()

    average_revenue = (
        total_revenue / total_customers
        if total_customers > 0 else 0
    )

    churned_customers = int(
        filtered["is_churned"].astype(bool).sum()
    )

    churn_rate = (
        churned_customers / total_customers * 100
        if total_customers > 0 else 0
    )

    # -----------------------------------------------------
    # BUSINESS OVERVIEW
    # -----------------------------------------------------

    st.markdown(
        '<div class="section-title">Business Overview</div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        render_kpi(
            "TOTAL CUSTOMERS",
            f"{total_customers:,}",
            "Customers in selected segment",
        )

    with col2:
        render_kpi(
            "ANNUAL CUSTOMER REVENUE",
            format_currency(total_revenue),
            "Illustrative annual revenue (USD)",
        )

    with col3:
        render_kpi(
            "AVERAGE REVENUE / CUSTOMER",
            format_currency(average_revenue),
            "Average annual customer revenue",
        )

    with col4:
        render_kpi(
            "CUSTOMER CHURN RATE",
            f"{churn_rate:.1f}%",
            f"{churned_customers:,} churned customers",
        )

    # -----------------------------------------------------
    # REVENUE PERFORMANCE
    # -----------------------------------------------------

    st.markdown(
        '<div class="section-title">Revenue Performance</div>',
        unsafe_allow_html=True,
    )

    left, right = st.columns(2)

    country_revenue = (
        filtered.groupby("country", as_index=False)
        .agg(
            total_revenue=("annual_revenue", "sum"),
            customers=("customer_id", "nunique"),
        )
        .sort_values("total_revenue", ascending=False)
    )

    with left:

        fig_country = px.bar(
            country_revenue,
            x="country",
            y="total_revenue",
            title="Annual Revenue by Country",
            text_auto=".2s",
            color_discrete_sequence=["#3478C7"],
            labels={
                "country": "Country",
                "total_revenue": "Annual Revenue (USD)",
            },
        )

        st.plotly_chart(
            style_chart(fig_country),
            width="stretch",
        )

    channel_revenue = (
        filtered.groupby(
            "acquisition_channel",
            as_index=False,
        )
        .agg(
            total_revenue=("annual_revenue", "sum"),
            customers=("customer_id", "nunique"),
        )
        .sort_values("total_revenue", ascending=False)
    )

    with right:

        fig_channel = px.bar(
            channel_revenue,
            x="acquisition_channel",
            y="total_revenue",
            title="Revenue by Acquisition Channel",
            text_auto=".2s",
            color_discrete_sequence=["#17A589"],
            labels={
                "acquisition_channel": "Acquisition Channel",
                "total_revenue": "Annual Revenue (USD)",
            },
        )

        st.plotly_chart(
            style_chart(fig_channel),
            width="stretch",
        )

    # -----------------------------------------------------
    # CUSTOMER SEGMENTATION
    # -----------------------------------------------------

    st.markdown(
        '<div class="section-title">Customer Segmentation</div>',
        unsafe_allow_html=True,
    )

    left, right = st.columns(2)

    industry_revenue = (
        filtered.groupby("industry", as_index=False)
        .agg(
            total_revenue=("annual_revenue", "sum"),
        )
        .sort_values("total_revenue", ascending=False)
    )

    with left:

        fig_industry = px.bar(
            industry_revenue,
            x="industry",
            y="total_revenue",
            title="Revenue by Industry",
            text_auto=".2s",
            color_discrete_sequence=["#8064A2"],
        )

        st.plotly_chart(
            style_chart(fig_industry),
            width="stretch",
        )

    status_summary = (
        filtered["account_status"]
        .value_counts()
        .rename_axis("account_status")
        .reset_index(name="customer_count")
    )

    with right:

        fig_status = px.pie(
            status_summary,
            names="account_status",
            values="customer_count",
            title="Customer Account Status",
            hole=0.55,
            color_discrete_sequence=[
                "#17A589",
                "#E5A13B",
                "#D85B63",
            ],
        )

        st.plotly_chart(
            style_chart(fig_status),
            width="stretch",
        )

    # -----------------------------------------------------
    # CUSTOMER VALUE DISTRIBUTION
    # -----------------------------------------------------

    st.markdown(
        '<div class="section-title">Customer Value Distribution</div>',
        unsafe_allow_html=True,
    )

    value_order = [
        "Low Value",
        "Medium Value",
        "High Value",
    ]

    value_summary = (
        filtered["customer_value_segment"]
        .value_counts()
        .reindex(value_order, fill_value=0)
        .rename_axis("customer_value_segment")
        .reset_index(name="customer_count")
    )

    fig_value = px.bar(
        value_summary,
        x="customer_value_segment",
        y="customer_count",
        title="Customers by Value Segment",
        text_auto=True,
        color="customer_value_segment",
        category_orders={
            "customer_value_segment": value_order,
        },
        color_discrete_map={
            "Low Value": "#3478C7",
            "Medium Value": "#17A589",
            "High Value": "#8064A2",
        },
    )

    fig_value.update_layout(
        xaxis_title="Customer Value Segment",
        yaxis_title="Number of Customers",
        showlegend=False,
    )

    st.plotly_chart(
        style_chart(fig_value),
        width="stretch",
    )

    # -----------------------------------------------------
    # CUSTOMER 360 EXPLORER
    # -----------------------------------------------------

    st.markdown(
        '<div class="section-title">Customer 360 Explorer</div>',
        unsafe_allow_html=True,
    )

    search = st.text_input(
        "Search customer",
        placeholder="Enter customer ID, name or country...",
    )

    display_data = filtered.copy()

    if search:

        search_value = search.lower()

        display_data = display_data[
            display_data["customer_id"].astype(str).str.lower().str.contains(
                search_value,
                na=False,
            )
            | display_data["customer_name"].astype(str).str.lower().str.contains(
                search_value,
                na=False,
            )
            | display_data["country"].astype(str).str.lower().str.contains(
                search_value,
                na=False,
            )
        ]

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
        column
        for column in display_columns
        if column in display_data.columns
    ]

    st.caption(
        f"Showing {len(display_data):,} of "
        f"{total_customers:,} filtered customers"
    )

    st.dataframe(
        display_data[available_columns].sort_values(
            "annual_revenue",
            ascending=False,
        ),
        width="stretch",
        hide_index=True,
    )

    # -----------------------------------------------------
    # FOOTER
    # -----------------------------------------------------

    st.markdown(
        """
        <div class="footer">
            CUSTOMER 360 REVENUE INTELLIGENCE
            | PORTFOLIO PROJECT
            | PYTHON · PANDAS · PLOTLY · STREAMLIT
        </div>
        """,
        unsafe_allow_html=True,
    )

if __name__ == "__main__":
    main()
