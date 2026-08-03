with fact as (
    select * from {{ ref('fct_glp1_utilization') }}
),

summarized as (
    select
        drug_class,
        sum(number_of_prescriptions) as total_prescriptions,
        sum(total_amount_reimbursed)  as total_spend,
        round(sum(total_amount_reimbursed) / nullif(sum(number_of_prescriptions),0), 2) as dollars_per_prescription
    from fact
    group by drug_class
)

select * from summarized
order by total_spend desc
