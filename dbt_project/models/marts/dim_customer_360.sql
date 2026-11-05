
-- Gold mart: business-ready Customer 360 dimension.

with customer_data as (

    select *
    from {{ ref('int_customer_segments') }}

),

customer_360 as (

    select
        customer_id,
        customer_name,
        email,
        signup_date,
        last_activity_date,
        country,
        industry,
        acquisition_channel,

        annual_revenue,
        account_status,
        is_churned,

        customer_tenure_days,
        days_since_last_activity,

        revenue_segment,
        engagement_segment,
        customer_lifecycle_stage,
        customer_value_segment,

        case
            when is_churned then 'Churned'
            when days_since_last_activity >= 150 then 'At Risk'
            else 'Active'
        end as customer_health_status,

        current_timestamp as dbt_updated_at

    from customer_data

)

select *
from customer_360
