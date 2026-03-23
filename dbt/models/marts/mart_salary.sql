select
    job_category,
    state,
    count(*)                        as job_count,
    avg(salary_lower)               as avg_salary,
    min(salary_lower)               as min_salary,
    max(salary_lower)               as max_salary
from {{ ref('int_job_listings_enriched') }}
where salary_lower is not null
group by job_category, state