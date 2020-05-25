import datetime

from django.db.models import Q
from django.test import TestCase

from utils.filters.parser import parse_search, EQ, NE, ParsingException
from utils.services import WeatherService


class ParseSearchTestCase(TestCase):
    """ Test cases for parse_search function."""

    def _make_test(self, str_expr, allowed_fields, expected_filters):
        parsed_result = parse_search(str_expr, allowed_fields)
        self.assertEqual(expected_filters, parsed_result)

    def _test_simple_field(self, field, field_type, op, value):
        """Generic simple test wih one filter."""
        str_expression = "{} {} {}".format(field, op, value)
        allowed_fields = {
            field: field_type
        }

        if op not in [EQ, NE]:
            field = "{}__{}".format(field, op)

        args = {
            field: field_type(value)
        }
        expected_filters = Q(**args)
        if op == NE:
            expected_filters = ~expected_filters

        self._make_test(str_expression, allowed_fields, expected_filters)

    def test_simple_eq(self):
        """Test eq operator."""
        self._test_simple_field('city', str, 'eq', "london")

    def test_simple_ne(self):
        """Test ne operator."""
        self._test_simple_field('country', str, 'ne', "romania")

    def test_simple_gt(self):
        """Test gt operator."""
        self._test_simple_field('distance', int, 'gt', 5000)

    def test_simple_gte(self):
        """Test gte operator."""
        self._test_simple_field('user__pk', int, 'gte', 15)

    def test_simple_lt(self):
        """Test lt operator."""
        self._test_simple_field('user__pk', int, 'lt', 10)

    def test_simple_lte(self):
        """Test lte operator."""
        self._test_simple_field('time', int, 'lte', 1800)

    def test_and(self):
        """Test AND operator."""
        str_expr = "date lt 2020-03-20 AND city eq budapest AND time gt 1200 AND user__pk ne 14"
        allowed_fields = {
            'date': datetime.date,
            'city': str,
            'time': int,
            'user__pk': int
        }
        expected_filters =\
            Q(date__lt=datetime.date(year=2020, month=3, day=20)) &\
            Q(city='budapest') &\
            Q(time__gt=1200) &\
            ~Q(user__pk=14)

        self._make_test(str_expr, allowed_fields, expected_filters)

    def test_or(self):
        """Test OR operator."""
        str_expr = "date lt 2020-03-20 OR city eq budapest OR time gt 1200 OR user__pk ne 14"
        allowed_fields = {
            'date': datetime.date,
            'city': str,
            'time': int,
            'user__pk': int
        }
        expected_filters =\
            Q(date__lt=datetime.date(year=2020, month=3, day=20)) |\
            Q(city='budapest') |\
            Q(time__gt=1200) |\
            ~Q(user__pk=14)

        self._make_test(str_expr, allowed_fields, expected_filters)

    def test_complex_parenthesis(self):
        """Test complex expression with parenthesis."""
        str_expr = "((date lt 2020-03-20) AND ((city eq budapest) OR (time gt 1200) OR (user__pk ne 14))) OR (distance lte 3000)"

        allowed_fields = {
            'date': datetime.date,
            'city': str,
            'time': int,
            'user__pk': int,
            'distance': int
        }
        expected_filters =\
            (
                Q(date__lt=datetime.date(year=2020, month=3, day=20)) &
                (
                    Q(city='budapest') |
                    Q(time__gt=1200) |
                    ~Q(user__pk=14)
                )
            ) |\
            Q(distance__lte=3000)

        self._make_test(str_expr, allowed_fields, expected_filters)

    def test_field_not_allowed(self):
        """Raise exception if expression contains fields that are not allowed.
        """
        str_expr = "(date lt 2020-04-15) OR (user__pk eq 16)"
        allowed_fields = {
            'date': datetime.date,
        }

        msg = "Search field not supported: user__pk"
        with self.assertRaisesRegex(ParsingException, msg):
            parsed_result = parse_search(str_expr, allowed_fields)

    def test_operator_not_supported(self):
        """Raise exception if different operators than supported are used."""
        str_expr = "user__pk = 16"
        allowed_fields = {
            'user__pk': 16
        }

        msg = "Operator not supported: ="
        with self.assertRaisesRegex(ParsingException, msg):
            parsed_result = parse_search(str_expr, allowed_fields)

    def test_malformed_expression(self):
        """Raise exception if expression does not follow the format."""
        str_expr = "time lte 600 AND (malformed expression)"
        allowed_fields = {
            'time': int
        }

        msg = "Invalid expression: malformed expression"
        with self.assertRaisesRegex(ParsingException, msg):
            parsed_result = parse_search(str_expr, allowed_fields)

    def test_malformed_random_expression(self):
        """Raise exception if expression does not follow the format."""
        str_expr = "this is random expression"
        allowed_fields = {
            'time': int,
            'date': datetime.date
        }

        msg = "Invalid expression: this is random expression"
        with self.assertRaisesRegex(ParsingException, msg):
            parsed_result = parse_search(str_expr, allowed_fields)

    def test_empty_expression(self):
        """Test return None if empty string provided."""
        str_expr = "           "
        allowed_fields = {
            'time': int,
            'date': datetime.date
        }
        parsed_result = parse_search(str_expr, allowed_fields)
        self.assertIsNone(parsed_result)
