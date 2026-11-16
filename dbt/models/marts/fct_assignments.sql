select
    user_id,
    arm,
    arm = 'control' as is_control,
    recency,
    history_segment,
    pre_deposits,
    bought_mens,
    bought_womens,
    zip_code,
    newbie,
    channel
from {{ ref('stg_hillstrom') }}
