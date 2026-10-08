# Admin exact searches no longer use numeric indexes

Admin searches using explicit exact lookups on non-text fields have a performance regression. An exact search on an indexed numeric primary key generates a comparison that converts the database column to text, rather than making effective use of its normal numeric index. On large tables this causes full-table scans and timeouts. The regression was reported in Django 5.2.

## Reproduction

Use an admin model backed by a table with an integer primary key and enough rows to make scanning expensive. Configure its admin search fields with `search_fields = ["pk__exact"]`. Search the changelist for an existing numeric primary key such as `123`.

Inspect the generated query and its database execution plan. The reported PostgreSQL predicate has the form `("table"."id")::varchar = '123'` and does not use the ordinary primary-key index.

Expected: numeric exact searches return the matching record while remaining compatible with the ordinary index on that numeric column.

## Constraints

Preserve normal admin search behavior, including multiple search terms and searches spanning multiple fields. Invalid terms for a non-text exact field must not make the changelist raise an exception or return unrelated records.
