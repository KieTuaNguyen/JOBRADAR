with
    source
    as
    (
        select *
        from {{ source
    
    ('raw', 'job_listings') }}
),

cleaned as
(
    select
    job_id,
    trim(title)                         as job_title,
    trim(company)                       as company_name,
    trim(location)                      as job_location,
    date_posted,
    description                         as job_description,
    job_url,
    search_title,
    search_location,
    TRY_CAST(
    REGEXP_SUBSTR(scraped_at::VARCHAR, '\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2}')
    AS TIMESTAMP_NTZ
) as scraped_at,

    case
            when lower(search_title) like '%data engineer%'   then 'Data Engineer'
            when lower(search_title) like '%data analyst%'    then 'Data Analyst'
            when lower(search_title) like '%data scientist%'  then 'Data Scientist'
            when lower(search_title) like '%ml engineer%'     then 'ML Engineer'
            else 'Other'
        end                                 as job_category,

    case
            when lower(description) like '%$%'
        or lower(description) like '%salary%'
        or lower(description) like '%per annum%'
        or lower(description) like '%pa%'
            then true
            else false
        end                                 as has_salary_info

from source
where job_id is not null
)

select *
from cleaned