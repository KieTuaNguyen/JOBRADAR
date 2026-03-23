with base as (
    select * from {{ ref('stg_job_listings') }}
),

enriched as (
    select
        *,

        case
            when upper(job_location) like '%NSW%'
              or upper(job_location) like '%NEW SOUTH WALES%'   then 'NSW'
            when upper(job_location) like '%VIC%'
              or upper(job_location) like '%VICTORIA%'          then 'VIC'
            when upper(job_location) like '%QLD%'
              or upper(job_location) like '%QUEENSLAND%'        then 'QLD'
            when upper(job_location) like '%WA%'
              or upper(job_location) like '%WESTERN AUSTRALIA%' then 'WA'
            else 'Other'
        end                                                      as state,

        trim(split_part(job_location, ',', 1))                  as city,

        case
            when regexp_like(job_description, '\\$[0-9]{2,3}[kK]')
            then try_to_number(
                regexp_substr(job_description, '[0-9]{2,3}(?=[kK])')
            ) * 1000
            else null
        end                                                      as salary_lower,

        case when lower(job_description) like '%python%'         then true else false end as skill_python,
        case when lower(job_description) like '%sql%'            then true else false end as skill_sql,
        case when lower(job_description) like '%spark%'          then true else false end as skill_spark,
        case when lower(job_description) like '%airflow%'        then true else false end as skill_airflow,
        case when lower(job_description) like '%dbt%'            then true else false end as skill_dbt,
        case when lower(job_description) like '%aws%'            then true else false end as skill_aws,
        case when lower(job_description) like '%azure%'          then true else false end as skill_azure,
        case when lower(job_description) like '%gcp%'            then true else false end as skill_gcp,
        case when lower(job_description) like '%tableau%'        then true else false end as skill_tableau,
        case when lower(job_description) like '%power bi%'       then true else false end as skill_powerbi,
        case when lower(job_description) like '%machine learning%' then true else false end as skill_ml,
        case when lower(job_description) like '%docker%'         then true else false end as skill_docker,
        case when lower(job_description) like '%kubernetes%'     then true else false end as skill_kubernetes

    from base
)

select * from enriched