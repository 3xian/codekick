# Deferred fields in a reverse foreign-key query

A reverse foreign-key queryset unexpectedly performs one extra database query per child when only the child's primary key is requested. Iteration should not load fields that the caller deferred and never accesses.

## Reproduction

Define a `Company` model and an `Employee` model with `company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="employees")`. Create a company and ten employees belonging to it. After setup, iterate over `company.employees.only("pk")`, accessing only each employee's primary key.

Observed: eleven queries run during iteration: one query selecting the employee IDs followed by ten queries loading the individual employees' company IDs.

Expected: iteration runs just one query selecting the employee IDs belonging to the company. Unselected fields remain deferred.

## Constraints

Preserve ordinary reverse foreign-key query behavior and deferred-field semantics. Accessing a genuinely deferred field later may fetch it normally; merely producing an instance or accessing its primary key must not eagerly fetch the excluded relationship field.
