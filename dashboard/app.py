
"""Customer 360 Revenue Intelligence Dashboard."""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "processed" / "customer_360.csv"


st.set_page_config(
    page_title="Customer 360 | Revenue Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ---------------------------------------------------------
# APPLICATION STYLING
# ---------------------------------------------------------

st.markdown(
    """
    <style>
        .stApp {
            background-color: #F5F7FB;
        }

        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 3rem;
            max-width: 1500px;
        }

        [data-testid="stHeader"] {
            background: transparent;
        }

        .main-header {
            background: linear-gradient(120deg, #142B4A, #234D78);
            padding: 30px 34px;
            border-radius: 16px;
            margin-bottom: 25px;
            color: white;
        }

        .main-header h1 {
            color: white;
            font-size: 31px;
            font-weight: 700;
            margin: 5px 0 8px 0;
        }

        .main-header p {
            color: #D5E2F1;
            font-size: 14px;
            margin: 0;
        }

        .header-tag {
            color: #93C5FD;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 2px;
        }

        .section-title {
            color: #1E293B;
            font-size: 20px;
            font-weight: 700;
            margin-top: 12px;
            margin-bottom: 15px;
        }

        .kpi-card {
            background: white;
            border: 1px solid #E7ECF3;
            border-radius: 13px;
            padding: 19px 20px;
            min-height: 120px;
            box-shadow: 0 2px 8px rgba(15, 23, 42, 0.03);
        }

        .kpi-label {
            color: #64748B;
            font-size: 12px;
            font-weight: 600;
            margin-bottom: 10px;
        }

        .kpi-value {
            color: #172B4D;
            font-size: 27px;
            font-weight: 750;
            margin-bottom: 5px;
        }

        .kpi-caption {
            color: #94A3B8;
            font-size: 11px;
        }

        div[data-testid="stExpander"] {
            background: white;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
        }

        div[data-testid="stButton"] button {
            border-radius: 8px;
            font-weight: 600;
            min-height: 42px;
        }

        div[data-testid="stDataFrame"] {
            border: 1px solid #E2E8F0;
            border-radius: 10px;
            overflow: hidden;
        }

        .footer {
            text-align: center;
            color: #94A3B8;
            font-size: 11px;
            padding-top: 25px;
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


# ---------------------------------------------------------
# DATA LOADING
# ---------------------------------------------------------

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
        dataframe["signup_date"],
        errors="coerce",
    )

    return dataframe


def format_currency(value):
    """Format revenue values in USD."""

    return f"${value:,.0f}"


def render_kpi(label, value, caption):
    """Render a reusable KPI card."""

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
    """Apply consistent styling to Plotly charts."""

    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(
            family="Arial",
            color="#334155",
            size=12,
        ),
        title_font=dict(
            size=15,
            color="#1E293B",
        ),
        margin=dict(l=15, r=15, t=55, b=20),
        legend_title_text="",
    )

    return fig


# ---------------------------------------------------------
# FILTER MANAGEMENT
# ---------------------------------------------------------

def initialize_filter_state(dataframe):
    """Initialize filter selections and applied filters."""

    filter_columns = [
        "country",
        "industry",
        "acquisition_channel",
        "account_status",
    ]

    for column in filter_columns:
        options = sorted(dataframe[column].dropna().unique().tolist())

        if f"draft_{column}" not in st.session_state:
            st.session_state[f"draft_{column}"] = options

        if f"applied_{column}" not in st.session_state:
            st.session_state[f"applied_{column}"] = options


def apply_filters():
    """Apply selected filters to the dashboard."""

    for column in [
        "country",
        "industry",
        "acquisition_channel",
        "account_status",
    ]:
        st.session_state[f"applied_{column}"] = (
            st.session_state[f"draft_{column}"]
        )


def reset_filters():
    """Restore all filters to their default selections."""

    for column in [
        "country",
        "industry",
        "acquisition_channel",
        "account_status",
    ]:
        options = st.session_state[f"all_{column}"]

        st.session_state[f"draft_{column}"] = options
        st.session_state[f"applied_{column}"] = options


# ---------------------------------------------------------
# MAIN DASHBOARD
# ---------------------------------------------------------

def main():

    # Header
    st.markdown(
        """
        <div class="main-header">
            <div class="header-tag">CUSTOMER ANALYTICS PLATFORM</div>
            <h1>Customer 360 | Revenue Intelligence</h1>
            <p>
                A unified view of customer performance, revenue,
                engagement and retention insights.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        dataframe = load_customer_data()
    except FileNotFoundError as error:
        st.error(str(error))
        st.stop()

    initialize_filter_state(dataframe)

    for column in [
        "country",
        "industry",
        "acquisition_channel",
        "account_status",
    ]:
        st.session_state[f"all_{column}"] = sorted(
            dataframe[column].dropna().unique().tolist()
        )

    # Filter panel
    with st.expander("⚙️  Dashboard Filters", expanded=False):

        st.caption(
            "Select your criteria and click Apply Filters "
            "to refresh the dashboard."
        )

        col1, col2 = st.columns(2)

        with col1:
            st.multiselect(
                "Country",
                options=st.session_state["all_country"],
                key="draft_country",
            )

            st.multiselect(
                "Acquisition Channel",
                options=st.session_state["all_acquisition_channel"],
                key="draft_acquisition_channel",
            )

        with col2:
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

        button_col1, button_col2, _ = st.columns([1, 1, 4])

        with button_col1:
            st.button(
                "Apply Filters",
                type="primary",
                use_container_width=True,
                on_click=apply_filters,
            )

        with button_col2:
            st.button(
                "Reset Filters",
                use_container_width=True,
                on_click=reset_filters,
            )

    # Apply committed selections
    filtered = dataframe.copy()

    for column in [
        "country",
        "industry",
        "acquisition_channel",
        "account_status",
    ]:
        filtered = filtered[
            filtered[column].isin(
                st.session_state[f"applied_{column}"]
            )
        ]

    if filtered.empty:
        st.warning(
            "No customers match the applied filters. "
            "Open Dashboard Filters and adjust your selection."
        )
        st.stop()

    # KPI calculations
    total_customers = filtered["customer_id"].nunique()

    total_revenue = filtered["annual_revenue"].sum()

    average_revenue = (
        total_revenue / total_customers
        if total_customers else 0
    )

    churned_customers = int(
        filtered["is_churned"].astype(bool).sum()
    )

    churn_rate = (
        churned_customers / total_customers * 100
        if total_customers else 0
    )

    active_customers = int(
        (filtered["account_status"] == "Active").sum()
    )

    # Business overview
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
            "Synthetic annual revenue (USD)",
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

    st.write("")

    # Revenue performance
    st.markdown(
        '<div class="section-title">Revenue Performance</div>',
        unsafe_allow_html=True,
    )

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
            title="Annual Revenue by Country",
            text_auto=".2s",
            color_discrete_sequence=["#3478C7"],
            labels={
                "country": "Country",
                "total_revenue": "Annual Revenue (USD)",
            },
        )

        fig_country.update_layout(xaxis_title=None)
        st.plotly_chart(
            style_chart(fig_country),
            use_container_width=True,
        )

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
            text_auto=".2s",
            color_discrete_sequence=["#17A589"],
            labels={
                "acquisition_channel": "Acquisition Channel",
                "total_revenue": "Annual Revenue (USD)",
            },
        )

        fig_channel.update_layout(xaxis_title=None)
        st.plotly_chart(
            style_chart(fig_channel),
            use_container_width=True,
        )

    # Customer segmentation
    st.markdown(
        '<div class="section-title">Customer Segmentation</div>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    industry_revenue = (
        filtered.groupby("industry", as_index=False)
        .agg(total_revenue=("annual_revenue", "sum"))
        .sort_values("total_revenue", ascending=False)
    )

    with col1:
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
            use_container_width=True,
        )

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
            hole=0.55,
            color_discrete_sequence=[
                "#17A589",
                "#E5A13B",
                "#D85B63",
            ],
        )

        st.plotly_chart(
            style_chart(fig_status),
            use_container_width=True,
        )

    # Customer value
    st.markdown(
        '<div class="section-title">Customer Value Distribution</div>',
        unsafe_allow_html=True,
    )

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
        text_auto=True,
        color="customer_value_segment",
        color_discrete_sequence=[
            "#3478C7",
            "#17A589",
            "#8064A2",
        ],
    )

    fig_value.update_layout(
        xaxis_title="Customer Value Segment",
        yaxis_title="Number of Customers",
        showlegend=False,
    )

    st.plotly_chart(
        style_chart(fig_value),
        use_container_width=True,
    )

    # Customer explorer
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
        search = search.lower()

        display_data = display_data[
            display_data["customer_id"].str.lower().str.contains(
                search, na=False
            )
            | display_data["customer_name"].str.lower().str.contains(
                search, na=False
            )
            | display_data["country"].str.lower().str.contains(
                search, na=False
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
        column for column in display_columns
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
        use_container_width=True,
        hide_index=True,
    )

    # Footer
    st.markdown(
        """
        <div class="footer">
            CUSTOMER 360 REVENUE INTELLIGENCE
            &nbsp; | &nbsp; Portfolio Project
            &nbsp; | &nbsp; Powered by Python, Pandas, Plotly & Streamlit
            <br><br>
            Demonstration using synthetic customer data.
            Revenue figures are illustrative, not actual business results.
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
