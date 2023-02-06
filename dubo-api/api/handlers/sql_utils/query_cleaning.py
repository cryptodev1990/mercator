import re

import sqlglot
from sqlglot import select, condition

import sqlparse


def guard_against_divide_by_zero(sql: str) -> str:
    if not '/' in sql:
        return sql
    parsed = sqlparse.parse(sql)[0]
    tokens = (token for token in parsed.flatten() if not token.is_whitespace)
    add_to_where = []
    for token in tokens:
        if token.value == '/':
            next_token = next(tokens)
            # If the token is a parenthesis, we need to grab all the contents until the closing parenthesis
            if next_token.value == '(':
                paren_count = 1
                paren_contents = []
                while paren_count > 0:
                    next_token = next(tokens)
                    if next_token.value == '(':
                        paren_count += 1
                    elif next_token.value == ')':
                        paren_count -= 1
                    paren_contents.append(next_token.value)
                paren_contents = '(' + ' '.join(paren_contents)
                print(paren_contents)
                add_to_where.append(paren_contents)
            # If the token is a CASE statement, we need to grab all the contents until the END
            elif next_token.value == 'CASE':
                case_count = 1
                case_contents = []
                while case_count > 0:
                    next_token = next(tokens)
                    if next_token.value == 'CASE':
                        case_count += 1
                    elif next_token.value == 'END':
                        case_count -= 1
                    case_contents.append(next_token.value)
                case_contents = 'CASE ' + ' '.join(case_contents)
                add_to_where.append(case_contents)
            else:
                add_to_where.append(next_token.value)
    if len(add_to_where) == 0:
        return sql
    new_query = sqlglot.parse_one(sql)
    for i, col in enumerate(add_to_where):
        if i == 0:
            new_query = new_query.where(condition(f'{col} != 0'))
        else:
            new_query = new_query.and_(condition(f'{col} != 0'))
    return new_query.sql()


def grab_from_select_onwards(sql: str) -> str:
    """Use a regex to grab the select onwards from a SQL query"""
    select_re = r'SELECT\s.*'

    match = re.search(select_re, sql, re.IGNORECASE)
    if match is None:
        raise ValueError(f'Could not find select in {sql}')
    return match.group()
