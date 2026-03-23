with skill_unpivot as (
    select job_category, 'Python'      as skill, skill_python      as mentioned from {{ ref('int_job_listings_enriched') }}
    union all
    select job_category, 'SQL'         as skill, skill_sql         as mentioned from {{ ref('int_job_listings_enriched') }}
    union all
    select job_category, 'Spark'       as skill, skill_spark       as mentioned from {{ ref('int_job_listings_enriched') }}
    union all
    select job_category, 'Airflow'     as skill, skill_airflow     as mentioned from {{ ref('int_job_listings_enriched') }}
    union all
    select job_category, 'dbt'         as skill, skill_dbt         as mentioned from {{ ref('int_job_listings_enriched') }}
    union all
    select job_category, 'AWS'         as skill, skill_aws         as mentioned from {{ ref('int_job_listings_enriched') }}
    union all
    select job_category, 'Azure'       as skill, skill_azure       as mentioned from {{ ref('int_job_listings_enriched') }}
    union all
    select job_category, 'GCP'         as skill, skill_gcp         as mentioned from {{ ref('int_job_listings_enriched') }}
    union all
    select job_category, 'Tableau'     as skill, skill_tableau     as mentioned from {{ ref('int_job_listings_enriched') }}
    union all
    select job_category, 'Power BI'    as skill, skill_powerbi     as mentioned from {{ ref('int_job_listings_enriched') }}
    union all
    select job_category, 'ML'          as skill, skill_ml          as mentioned from {{ ref('int_job_listings_enriched') }}
    union all
    select job_category, 'Docker'      as skill, skill_docker      as mentioned from {{ ref('int_job_listings_enriched') }}
    union all
    select job_category, 'Kubernetes'  as skill, skill_kubernetes  as mentioned from {{ ref('int_job_listings_enriched') }}
)

select
    job_category,
    skill,
    count(*)                                        as total_jobs,
    sum(case when mentioned then 1 else 0 end)      as jobs_mentioning_skill,
    round(
        sum(case when mentioned then 1 else 0 end) * 100.0 / count(*), 1
    )                                               as mention_pct
from skill_unpivot
group by job_category, skill
order by job_category, mention_pct desc