
-- Staging model: standardise raw customer records.

with source_data as (

    select *
    from read_csv_auto(
        'data/processed/customers_silver.csv',
        header = true
    )

),

renamed_and_cleaned as (

    select
        customer_id,
        trim(customer_name) as customer_name,
        lower(trim(email)) as email,
        cast(signup_date as date) as signup_date,
        cast(last_activity_date as date) as last_activity_date,
        trim(country) as country,
        trim(industry) as industry,
        cast(annual_revenue as decimal(18, 2)) as annual_revenue,
        trim(acquisition_channel) as acquisition_channel,
        trim(account_status) as account_status,
        cast(customer_tenure_days as integer) as customer_tenure_days,
        cast(days_since_last_activity as integer) as days_since_last_activity,
        cast(is_churned as boolean) as is_churned

    from source_data

)

select *
from renamed_and_cleaned
