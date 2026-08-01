{% macro aggregate_sum_percentages(
    source_table,
    dimension_columns,
    weight_column,
    partition_column=None,
    where_clause=None
) %}

select 
    {% for col in dimension_columns %}
    {{ col }},
    {% endfor %}
    sum({{ weight_column }}) as {{ weight_column }},
    sum({{ weight_column }}) * 100.0 / sum(sum({{ weight_column }})) over (
        {% if partition_column %}
        partition by {{ partition_column }}
        {% endif %}
    ) as percentage
from {{ source_table }}
{% if where_clause %}
where {{ where_clause }}
{% endif %}
group by 
    {% for col in dimension_columns %}
    {{ loop.index }}{% if not loop.last %},{% endif %}
    {% endfor %}

{% endmacro %}