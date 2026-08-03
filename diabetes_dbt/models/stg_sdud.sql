with source as (
    select * from {{ source('raw', 'sdud_2024') }}
),

cleaned as (
    select
        -- descriptive columns (dimensions) — trim the messy trailing spaces
        utilization_type,
        state,
        ndc,
        trim(product_name) as product_name,
        year,
        quarter,
        suppression_used,

        -- measures: text -> numeric, with blanks turned to NULL so the cast can't crash
        nullif(units_reimbursed, '')::numeric        as units_reimbursed,
        nullif(number_of_prescriptions, '')::numeric as number_of_prescriptions,
        nullif(total_amount_reimbursed, '')::numeric as total_amount_reimbursed
    from source
)

select * from cleaned
where state != 'XX'