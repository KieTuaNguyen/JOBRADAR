select
    job_category,
    state,
    count(*)                                                    as total_jobs,
    sum(case when has_salary_info then 1 else 0 end)            as jobs_with_salary_mention,
    round(
        sum(case when has_salary_info then 1 else 0 end) * 100.0 / count(*), 1
    )                                                           as salary_mention_pct
from {{ ref
('int_job_listings_enriched') }}
group by job_category, state
order by job_category, total_jobs desc