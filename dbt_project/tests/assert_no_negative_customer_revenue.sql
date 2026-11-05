
-- Data quality test: no customer should have negative annual revenue.
-- A dbt SQL test passes when this query returns zero rows.

select
    customer_id,
    annual_revenue

from {{ ref('dim_customer_360') }}

where annual_revenue < 0
