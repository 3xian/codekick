"""Controller-only supplement; uses real upstream models and admin queries.

This verifies SQLite SQL shape and query planning, not PostgreSQL performance.
The historical upstream behavioral regressions are replayed separately alongside it.
"""

from django.contrib import admin
from django.db import connection
from django.test import RequestFactory, TestCase

from .admin import site as custom_site
from .models import Child


class ExactSearchIndexTests(TestCase):
    def test_numeric_primary_key_search_shape(self):
        self.assertEqual(connection.vendor, "sqlite")
        child = Child.objects.create(name="Index probe", age=10)
        model_admin = admin.ModelAdmin(Child, custom_site)
        model_admin.search_fields = ["pk__exact"]
        request = RequestFactory().get("/")
        queryset, duplicates = model_admin.get_search_results(
            request, Child.objects.all(), str(child.pk)
        )
        sql, params = queryset.query.sql_with_params()
        with connection.cursor() as cursor:
            cursor.execute("EXPLAIN QUERY PLAN " + sql, params)
            plan = cursor.fetchall()
        print("CK-REAL-06 SQL:", sql)
        print("CK-REAL-06 params:", repr(params))
        print("CK-REAL-06 SQLite plan:", repr(plan))
        self.assertCountEqual(queryset, [child])
        self.assertFalse(duplicates)
        self.assertNotIn("CAST(", sql.upper())
        self.assertTrue(
            any("SEARCH" in row[3].upper() and "PRIMARY KEY" in row[3].upper()
                for row in plan),
            plan,
        )
