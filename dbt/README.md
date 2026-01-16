### To start using DBT:

Run the following commands for resident metrics:
 - ```dbt run --select +metrics.resident+ ```
 - ```dbt run --select (name of model)``` (to build/run only one model)
   - e.g. ```dbt run --select trip_mode```
- ```dbt run --select +(name of model)``` (to include upstream dependencies)
   - e.g. ```dbt run --select +trip_mode```

Tips:
 - Secrets can be added with your profiles.yml file (this is for when trying to connect to a cloud source/protected source).
 - Running ```dbt run``` instead of ```dbt build``` is generally faster as ```build``` will run any tests and run downstream models.
 - Running ```dbt run```/```dbt build``` with a plus sign (+) in the front or back of the model name runs its with its dependencies in that corresponding direction.
    - Example 1: ```dbt run --select +(name of model)``` will build your selected model & all the upstream dependenies (usually staging models, intermediate)
    - Example 2: ```dbt run --select (name of model)+``` will build all the downstream models, on top of your selected model
    - Example 3: ```dbt run --select +(name of model)+``` will build your selected model and all upstream/downstream dependencies

