{% macro include_gq_where(column='unittype') -%}
  {%- if var('include_gq', false) -%}
    /* include GQ: no filter */
    1 = 1
  {%- else -%}
    /* exclude GQ: keep only non-GQ rows where column == 0 */
    {{ column }} = 0
  {%- endif -%}
{%- endmacro %}