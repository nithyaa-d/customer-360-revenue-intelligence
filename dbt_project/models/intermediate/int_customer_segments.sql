
-- Intermediate model: enrich customers with business segments.

with customers as (

    select *
    from {{ ref('stg_customers') }}

),

customer_segments as (

    select
        *,

        -- Revenue segmentation
        case
            when annual_revenue <= 50000 then 'SMB'
            when annual_revenue <= 200000 then 'Mid-Market'
            else 'Enterprise'
        end as revenue_segment,

        -- Engagement segmentation
        case
            when days_since_last_activity <= 30
                then 'Highly Engaged'
            when days_since_last_activity <= 90
                then 'Moderately Engaged'
            else 'Low Engagement'
        end as engagement_segment,

        -- Customer lifecycle
        case
            when customer_tenure_days <= 90 then 'New'
            when customer_tenure_days <= 365 then 'Established'
            else 'Mature'
        end as customer_lifecycle_stage,

        -- Customer value
        case
            when annual_revenue <= 50000 then 'Low Value'
            when annual_revenue <= 200000 then 'Medium Value'
            else 'High Value'
        end as customer_value_segment

    from customers

)

select *
from customer_segments
