{% macro get_scenario_paths(table_name, folder_path) %}
  {% set scenarios = var('scenarios') %}
  {% set base = var('base_path') %}
  [
    {% for scenario in scenarios %}
    '{{ base }}/{{ scenario }}/{{ folder_path }}/{{ table_name }}.csv'
    {% if not loop.last %},{% endif %}
    {% endfor %}
  ]
{% endmacro %}