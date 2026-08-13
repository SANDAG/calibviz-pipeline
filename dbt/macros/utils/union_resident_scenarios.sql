{% macro union_resident_trips() %}
  {% set scenarios = var('resident_scenarios') %}
  {% for scenario in scenarios %}
    SELECT '{{ scenario }}' as scenario,
           *
    FROM {{ source(scenario, 'final_trips') }}
    {% if not loop.last %}
    UNION ALL BY NAME
    {% endif %}
  {% endfor %}
{% endmacro %}

{% macro union_resident_households() %}
  {% set scenarios = var('resident_scenarios') %}
  {% for scenario in scenarios %}
    SELECT '{{ scenario }}' as scenario,
           *
    FROM {{ source(scenario, 'final_households') }}
    {% if not loop.last %}
    UNION ALL BY NAME
    {% endif %}
  {% endfor %}
{% endmacro %}

{% macro union_resident_persons() %}
  {% set scenarios = var('resident_scenarios') %}
  {% for scenario in scenarios %}
    SELECT '{{ scenario }}' as scenario,
           *
    FROM {{ source(scenario, 'final_persons') }}
    {% if not loop.last %}
    UNION ALL BY NAME
    {% endif %}
  {% endfor %}
{% endmacro %}

{% macro union_resident_tours() %}
  {% set scenarios = var('resident_scenarios') %}
  {% for scenario in scenarios %}
    SELECT '{{ scenario }}' as scenario,
           *
    FROM {{ source(scenario, 'final_tours') }}
    {% if not loop.last %}
    UNION ALL BY NAME
    {% endif %}
  {% endfor %}
{% endmacro %}

{% macro union_resident_land_use() %}
  {% set scenarios = var('resident_scenarios') %}
  {% for scenario in scenarios %}
    SELECT '{{ scenario }}' as scenario,
           *
    FROM {{ source(scenario, 'final_land_use') }}
    {% if not loop.last %}
    UNION ALL BY NAME
    {% endif %}
  {% endfor %}
{% endmacro %}
