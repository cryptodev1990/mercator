from typing import List, Literal
import warnings
import re

import sqlglot
from sqlglot import exp
from sqlglot.expressions import condition
from sqlglot.optimizer.optimizer import optimize

ONE_HUNDRED_RE = r'100(.0)?|100(.00)?'


class QueryCleaner:
    def __init__(self, sql: str, sql_flavor='sqlite'):
        self.sql = sql
        self.sql_flavor = sql_flavor
        self.parsed = sqlglot.parse_one(sql, read=sql_flavor)
        self._new_parsed = self.parsed.copy()

    def grab_from_select_onwards(self, sql: str) -> str:
        """Use a regex to grab the select onwards from a SQL query"""
        select_re = r'SELECT\s.*'

        match = re.search(select_re, sql, re.IGNORECASE)
        if match is None:
            raise ValueError(f'Could not find select in {sql}')
        return match.group()

    def is_create_statement(self) -> bool:
        return len([x for x in self.parsed.find_all(exp.Create)]) > 0

    def is_insert_statement(self) -> bool:
        return len([x for x in self.parsed.find_all(exp.Insert)]) > 0

    def is_update_statement(self) -> bool:
        return len([x for x in self.parsed.find_all(exp.Update)]) > 0

    def is_delete_statement(self) -> bool:
        return len([x for x in self.parsed.find_all(exp.Delete)]) > 0

    def is_write_statement(self) -> bool:
        return len([x for x in self.parsed.find_all(exp.Create, exp.Insert, exp.Update, exp.Delete)]) > 0

    def is_select_statement(self) -> bool:
        not_write_op = self.is_write_statement() is False
        return len([x for x in self.parsed.find_all(exp.Select)]) > 0 and not_write_op

    def has_limit(self) -> bool:
        return len([x for x in self.parsed.find_all(exp.Limit)]) > 0

    def add_limit(self, n=1000) -> 'QueryCleaner':
        """Return a new SQL query with a limit added"""
        if self.has_limit():
            return self
        self._new_parsed = self._new_parsed.limit(n)
        return self

    def text(self) -> str:
        return self._new_parsed.sql(dialect=self.sql_flavor)

    def __eq__(self, other):
        return self.text() == str(other)

    def __repr__(self):
        return self.text()

    def is_aggregate(self, sql: str) -> bool:
        return len([x for x in self.parsed.find_all(exp.AggFunc)]) > 0

    def guard_against_divide_by_zero(self) -> 'QueryCleaner':
        """Rewrite a SQL query to avoid divide by zero errors

        Only works for WHERE filters and not HAVING filters
        """
        division_expressions = [x for x in self._new_parsed.find_all(exp.Div)]
        if len(division_expressions) == 0:
            return self
        rhs_expressions = []
        for div in division_expressions:
            rhs_expressions.append(div.right)
        for col in rhs_expressions:
            aggs = [x for x in col.find_all(exp.AggFunc)]
            if len(aggs) > 0:
                self._new_parsed = self._new_parsed.having(
                    condition(f'{col} != 0'))
            # Add a where clause to the query to avoid divide by zero errors
            else:
                self._new_parsed = self._new_parsed.where(
                    condition(f'{col} != 0'))
        self._new_parsed = self._new_parsed
        return self

    def reset(self) -> 'QueryCleaner':
        self._new_parsed = self.parsed.copy()
        return self

    def replace_literal_in_select_clause(self, regex_match, replace_with: str) -> 'QueryCleaner':
        def replace_(node):
            if not isinstance(node, exp.Literal):
                return node
            literal_node = node
            if re.match(regex_match, str(literal_node.this)) and literal_node.find_ancestor(exp.Select, exp.Mul) is not None and literal_node.find_ancestor(exp.Limit, exp.Order, exp.Join) is None:
                # Set the literal value to the replacement value
                literal_node.args['this'] = replace_with
            return literal_node
        self._new_parsed = self._new_parsed.transform(replace_)
        return self

    def has_aggregates(self) -> bool:
        """Check if the query has aggregates"""
        return len([x for x in self._new_parsed.find_all(exp.AggFunc)]) > 0

    def has_groupbys(self) -> bool:
        """Check if the query has a group by clause"""
        return len([x for x in self._new_parsed.find_all(exp.Group)]) > 0

    def remove_groupby_if_no_aggregates(self) -> 'QueryCleaner':
        """Remove the group by clause if there are no aggregates"""
        def replace_(node):
            if not isinstance(node, exp.Group):
                return node
            group_node = node
            # If the SELECT clause of the GROUP BY...
            # ...does not have any aggregates, remove the GROUP BY
            parent_select = group_node.find_ancestor(exp.Select)
            if parent_select is not None and parent_select.find(exp.AggFunc) is None:
                # Set the literal value to the replacement value
                return None
            # Otherwise return the node
            return group_node

        self._new_parsed = self._new_parsed.transform(replace_)

        return self

    def replace_100_with_1(self) -> 'QueryCleaner':
        """Replace 100 with 1 in the select clause of a query"""
        return self.replace_literal_in_select_clause(ONE_HUNDRED_RE, '1.0')
