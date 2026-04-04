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
),

clean AS
(
    SELECT *
FROM deduped
WHERE rn = 1
)
,

skill_unpivot AS
(
    SELECT job_category, 'Python'     AS skill, skill_python     AS mentioned
    FROM clean
UNION ALL
    SELECT job_category, 'SQL'        AS skill, skill_sql        AS mentioned
    FROM clean
UNION ALL
    SELECT job_category, 'Spark'      AS skill, skill_spark      AS mentioned
    FROM clean
UNION ALL
    SELECT job_category, 'Airflow'    AS skill, skill_airflow    AS mentioned
    FROM clean
UNION ALL
    SELECT job_category, 'dbt'        AS skill, skill_dbt        AS mentioned
    FROM clean
UNION ALL
    SELECT job_category, 'AWS'        AS skill, skill_aws        AS mentioned
    FROM clean
UNION ALL
    SELECT job_category, 'Azure'      AS skill, skill_azure      AS mentioned
    FROM clean
UNION ALL
    SELECT job_category, 'GCP'        AS skill, skill_gcp        AS mentioned
    FROM clean
UNION ALL
    SELECT job_category, 'Tableau'    AS skill, skill_tableau    AS mentioned
    FROM clean
UNION ALL
    SELECT job_category, 'Power BI'   AS skill, skill_powerbi    AS mentioned
    FROM clean
UNION ALL
    SELECT job_category, 'ML'         AS skill, skill_ml         AS mentioned
    FROM clean
UNION ALL
    SELECT job_category, 'Docker'     AS skill, skill_docker     AS mentioned
    FROM clean
UNION ALL
    SELECT job_category, 'Kubernetes' AS skill, skill_kubernetes AS mentioned
    FROM clean
)

SELECT
    job_category,
    skill,
    COUNT(*)                                        AS total_jobs,
    SUM(CASE WHEN mentioned THEN 1 ELSE 0 END)      AS jobs_mentioning_skill,
    ROUND(
        SUM(CASE WHEN mentioned THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1
    )                                               AS mention_pct
FROM skill_unpivot
GROUP BY job_category, skill
ORDER BY job_category, mention_pct DESC