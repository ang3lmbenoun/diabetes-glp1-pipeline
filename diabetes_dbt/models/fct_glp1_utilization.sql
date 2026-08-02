with utilization as (
    select * from {{ ref('stg_sdud') }}
),

drug_classes as (
    select * from {{ ref('diabetes_drug_classes') }}
),

matched as (
    select
        u.state,
        u.year,
        u.quarter,
        c.drug,
        c.drug_class,
        u.number_of_prescriptions,
        u.total_amount_reimbursed
    from utilization u
    inner join drug_classes c
        on upper(u.product_name) like '%' || c.keyword || '%'
)

select * from matched