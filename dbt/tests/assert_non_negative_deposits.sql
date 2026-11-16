select *
from {{ ref('fct_experiment_metrics') }}
where deposit_amount < 0 or pre_deposits < 0
