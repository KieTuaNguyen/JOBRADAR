WITH
    deduped
    AS
    (
        SELECT *,
            ROW_NUMBER() OVER (
            PARTITION BY job_title, company_name, date_posted
            ORDER BY scraped_at DESC
        ) AS rn
        FROM {{ ref
    ('int_job_listings_enriched') }}
)

SELECT
    job_category,
    state,
    COUNT(*)                                                    AS total_jobs,
    SUM(CASE WHEN has_salary_info THEN 1 ELSE 0 END)            AS jobs_with_salary_mention,
    ROUND(
        SUM(CASE WHEN has_salary_info THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1
    )                                                           AS salary_mention_pct
FROM deduped
WHERE rn = 1
GROUP BY job_category, state
ORDER BY job_category, total_jobs DESC