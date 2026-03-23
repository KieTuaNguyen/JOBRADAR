select
    job_id,
    job_title,
    company_name,
    job_location,
    city,
    state,
    job_category,
    date_posted,
    has_salary_info,
    salary_lower,
    job_url,
    scraped_at
from {{ ref('int_job_listings_enriched') }}