WITH
    source
    AS
    (
        SELECT *
        FROM {{ ref
    ('int_job_listings_enriched') }}
),

deduped AS
(
    SELECT *,
    ROW_NUMBER() OVER (
            PARTITION BY job_title, company_name, date_posted
            ORDER BY scraped_at DESC
        ) AS rn
FROM source
)

SELECT
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
FROM deduped
WHERE rn = 1