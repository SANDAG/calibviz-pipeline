with

source as (
    select 
        ptype, 
        count(*) * 100.0 / sum(count(*)) over () as percentage 
    from {{ ref('stg_persons') }} 
    group by ptype

),

-- adding description after group by to check if that speeds up code
person_type_by_description_counts as (

   select
    *,
    case ptype
        when 1 then 'full-time worker'
        when 2 then 'part-time worker'
        when 3 then 'college student'
        when 4 then 'non-working adult'
        when 5 then 'non-working senior'
        when 6 then 'driving age student'
        when 7 then 'non-driving student'
        when 8 then 'pre-school'
        else 'unknown'
        end as person_type_description
    from source
    
    )
 
select * from person_type_by_description_counts