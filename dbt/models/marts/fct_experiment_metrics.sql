select
    a.user_id,
    a.arm,
    a.pre_deposits,
    s.visited,
    s.funded,
    s.deposit_amount
from {{ ref('fct_assignments') }} as a
inner join {{ ref('stg_hillstrom') }} as s using (user_id)
