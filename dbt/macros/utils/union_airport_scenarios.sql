{% macro union_airport_trips() %}
  {% set scenarios = var('airport_scenarios') %}
  {% for scenario in scenarios %}
    SELECT '{{ scenario }}' as scenario,
           * EXCLUDE (origin),
           origin as origin_mgra 
    FROM {{ source(scenario, 'final_santrips') }}
    {% if not loop.last %}
    UNION ALL BY NAME
    {% endif %}
  {% endfor %}
{% endmacro %}

{% macro union_airport_tours() %}
  {% set scenarios = var('airport_scenarios') %}
  {% for scenario in scenarios %}
    SELECT '{{ scenario }}' as scenario,
           tour_id, 
           tour_type 
    FROM {{ source(scenario, 'final_santours') }}
    {% if not loop.last %}
    UNION ALL BY NAME
    {% endif %}
  {% endfor %}
{% endmacro %}
