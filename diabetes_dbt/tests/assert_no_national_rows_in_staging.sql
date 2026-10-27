select *
from {{ ref('stg_sdud') }}
where state = 'XX'
