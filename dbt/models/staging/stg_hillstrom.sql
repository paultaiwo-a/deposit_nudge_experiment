select
    user_id,
    case segment
        when 'No E-Mail' then 'control'
        when 'Mens E-Mail' then 'mens_email'
        when 'Womens E-Mail' then 'womens_email'
    end as arm,
    recency,
    history_segment,
    history as pre_deposits,
    mens as bought_mens,
    womens as bought_womens,
    zip_code,
    newbie,
    channel,
    visit as visited,
    conversion as funded,
    spend as deposit_amount
from {{ source('raw', 'raw_hillstrom') }}
