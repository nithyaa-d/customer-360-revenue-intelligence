
-- Revenue mart: aggregate customer and revenue metrics
-- across country, industry and acquisition channel.

with customer_data as (

    select *
    from {{ ref('dim_customer_360') }}

),

revenue_by_segment as (

    select
        country,
        industry,
        acquisition_channel,

        count(distinct customer_id) as total_customers,

        sum(annual_revenue) as total_annual_revenue,

        round(
            avg(annual_revenue),
            2
        ) as average_annual_revenue,

        count(
            case when account_status = 'Active'
                then customer_id end
        ) as active_customers,

        count(
            case when account_status = 'At Risk'
                then customer_id end
        ) as at_risk_customers,

        count(
            case when is_churned
                then customer_id end
        ) as churned_customers,

        round(
            100.0 * count(
                case when is_churned
                    then customer_id end
            ) / nullif(count(distinct customer_id), 0),
            2
        ) as churn_rate_pct

    from customer_data

    group by
        country,
        industry,
        acquisition_channel

)

select *
from revenue_by_segment
