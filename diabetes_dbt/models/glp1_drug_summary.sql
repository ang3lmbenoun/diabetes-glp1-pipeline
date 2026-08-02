with fact as (
    select * from {{ ref('fct_glp1_utilization') }}
),

summarized as (
    select
        drug,
        drug_class,
        sum(number_of_prescriptions) as total_prescriptions,
        sum(total_amount_reimbursed)  as total_spend
    from fact
    group by drug, drug_class
),

final as (
    select
        drug,
        drug_class,
        total_prescriptions,
        total_spend,
        -- the divergence metric: dollars per prescription
        round(total_spend / nullif(total_prescriptions, 0), 2) as dollars_per_prescription
    from summarized
)

select * from final
order by total_spend desc