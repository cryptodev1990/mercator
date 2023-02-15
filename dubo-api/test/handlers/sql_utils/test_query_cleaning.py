import pytest
from fastapi import Query
from api.handlers.sql_utils.query_cleaning import QueryCleaner


def test_add_limit():
    sql = "SELECT * FROM tbl"
    new_sql = QueryCleaner(sql).add_limit()
    assert new_sql == "SELECT * FROM tbl LIMIT 1000"


def test_add_limit_with_limit():
    sql = "SELECT * FROM tbl LIMIT 100"
    new_sql = QueryCleaner(sql).add_limit()
    assert new_sql == "SELECT * FROM tbl LIMIT 100"


def test_add_limit_with_limit_and_offset():
    sql = "SELECT * FROM tbl LIMIT 100 OFFSET 100"
    new_sql = QueryCleaner(sql).add_limit()
    assert new_sql == "SELECT * FROM tbl LIMIT 100 OFFSET 100"


def test_select_statement():
    sql = "SELECT * FROM tbl"
    assert QueryCleaner(sql).is_select_statement() is True


def test_select_statement_with_limit():
    sql = "SELECT * FROM tbl LIMIT 100"
    assert QueryCleaner(sql).has_limit() is True


def test_complicated_select_statement():
    sql = "WITH tbl AS (SELECT 1) SELECT col, (SELECT 1 FROM tbl) AS val FROM tbl WHERE col1 = 'val1' AND col2 = 'val2' LIMIT 100"
    assert QueryCleaner(sql).is_select_statement() is True


def test_complicated_insert_statement():
    sql = "WITH tbl AS (SELECT 1) INSERT INTO tbl (col1, col2) VALUES ('val1', 'val2')"
    qc = QueryCleaner(sql)
    assert qc.is_select_statement() is False
    assert qc.is_insert_statement() is True


def test_guard_against_div_by_0():
    TEST_TABLE = [
        # Query is a simply case and will be rewritten
        ["SELECT tmp / (other_column + another_column) FROM tbl WHERE 1=1 AND is_bool_true LIMIT 100 OFFSET 100",
         "SELECT tmp / (other_column + another_column) FROM tbl WHERE (1 = 1 AND is_bool_true) AND (other_column + another_column) <> 0 LIMIT 100 OFFSET 100"],
        # Query contains multiple divisions and will be rewritten
        ["SELECT tmp / (other_column + another_column) / (another_column + 1) FROM tbl WHERE 1=1 AND is_bool_true LIMIT 100 OFFSET 100",
            "SELECT tmp / (other_column + another_column) / (another_column + 1) FROM tbl WHERE ((1 = 1 AND is_bool_true) AND (another_column + 1) <> 0) AND (other_column + another_column) <> 0 LIMIT 100 OFFSET 100"],
        # Query contains multiple columns with divisions and will be rewritten
        ["SELECT tmp / tmp1 AS tmp1_ratio, tmp / tmp2 AS tmp2_ratio FROM tbl WHERE 1=1 AND is_bool_true LIMIT 100 OFFSET 100",
         "SELECT tmp / tmp1 AS tmp1_ratio, tmp / tmp2 AS tmp2_ratio FROM tbl WHERE ((1 = 1 AND is_bool_true) AND tmp1 <> 0) AND tmp2 <> 0 LIMIT 100 OFFSET 100"],
        # Query is a simply CASE statement and will be rewritten
        ["SELECT tmp / CASE WHEN (other_column + another_column) = 1 THEN 0 ELSE 1 END AS new_col FROM tbl WHERE 1=1 AND is_bool_true LIMIT 100 OFFSET 100",
         "SELECT tmp / CASE WHEN (other_column + another_column) = 1 THEN 0 ELSE 1 END AS new_col FROM tbl WHERE (1 = 1 AND is_bool_true) AND CASE WHEN (other_column + another_column) = 1 THEN 0 ELSE 1 END <> 0 LIMIT 100 OFFSET 100"],
        # Query has a HAVING filter
        ["SELECT SUM(total_population_if_over_16_years) / SUM(total_population) AS population FROM acs_aggregates GROUP BY zcta",
         "SELECT SUM(total_population_if_over_16_years) / SUM(total_population) AS population FROM acs_aggregates GROUP BY zcta HAVING SUM(total_population) <> 0"],
        #
        ["SELECT zcta, total_population / (num_white_alone + num_black_or_african_american_alone + num_hispanic_alone) AS population FROM acs_race",
         "SELECT zcta, total_population / (num_white_alone + num_black_or_african_american_alone + num_hispanic_alone) AS population FROM acs_race WHERE (num_white_alone + num_black_or_african_american_alone + num_hispanic_alone) <> 0"]
    ]
    for sql, expected_sql in TEST_TABLE:
        qc = QueryCleaner(sql)
        new_sql = qc.guard_against_divide_by_zero().text()
        assert new_sql == expected_sql


def test_pipelining():
    example_query = "SELECT Close / Open AS Total_USD_Exchanged FROM `dubo-375020.crypto.matic_to_usd` WHERE Date = '2020-12-15'"
    expected_query = "SELECT Close / Open AS Total_USD_Exchanged FROM `dubo-375020.crypto.matic_to_usd` WHERE Date = '2020-12-15' AND Open <> 0 LIMIT 100"
    qc = QueryCleaner(example_query, sql_flavor="bigquery")
    actual_query = qc.add_limit(100).guard_against_divide_by_zero().text()
    assert actual_query == expected_query
    qc.reset()
    actual_query = qc.guard_against_divide_by_zero().add_limit(100).text()
    assert actual_query == expected_query


def test_remove_100():
    sql = "SELECT (close_price / open_price) * 100.0 AS percent FROM tbl LIMIT 100"
    new_sql = QueryCleaner(sql).replace_100_with_1().text()
    assert new_sql == "SELECT (close_price / open_price) * 1.0 AS percent FROM tbl LIMIT 100"

    sql = "SELECT (close_price / open_price) * 100 AS percent FROM tbl LIMIT 100"
    new_sql = QueryCleaner(sql).replace_100_with_1().text()
    assert new_sql == "SELECT (close_price / open_price) * 1.0 AS percent FROM tbl LIMIT 100"


def test_remove_groupby_with_no_aggregates():
    TEST_TABLE = [
        # ["SELECT * FROM tbl GROUP BY col1, col2", "SELECT * FROM tbl"],
        ["SELECT col3, SUM(col1), AVG(col2) FROM tbl GROUP BY col3",
         "SELECT col3, SUM(col1), AVG(col2) FROM tbl GROUP BY col3"],
        ["SELECT col3, SUM(col1), AVG(col2) FROM tbl GROUP BY col3, col4",
         "SELECT col3, SUM(col1), AVG(col2) FROM tbl GROUP BY col3, col4"],
        ["SELECT col3 FROM tbl GROUP BY col3, col4 HAVING SUM(col1) > 0",
         "SELECT col3 FROM tbl GROUP BY col3, col4 HAVING SUM(col1) > 0"],
        ["SELECT col3, SUM(col1), AVG(col2) FROM tbl GROUP BY col3, col4 HAVING SUM(col1) > 0 AND AVG(col2) > 0",
         "SELECT col3, SUM(col1), AVG(col2) FROM tbl GROUP BY col3, col4 HAVING SUM(col1) > 0 AND AVG(col2) > 0"],
        ["WITH tbl1 AS (SELECT a, b FROM tbl GROUP BY a) SELECT col3, SUM(col1), AVG(col2) FROM tbl CROSS JOIN tbl1 GROUP BY col3, col4 HAVING SUM(col1) > 0 AND AVG(col2) > 0",
         "WITH tbl1 AS (SELECT a, b FROM tbl) SELECT col3, SUM(col1), AVG(col2) FROM tbl CROSS JOIN tbl1 GROUP BY col3, col4 HAVING SUM(col1) > 0 AND AVG(col2) > 0"],
    ]
    for sql, expected_sql in TEST_TABLE:
        qc = QueryCleaner(sql)
        new_sql = qc.remove_groupby_if_no_aggregates().text()
        assert new_sql == expected_sql


@pytest.mark.skip(reason="Not implemented yet")
def test_force_table_alias_on_inner_join():
    TEST_TABLE = [
        ["SELECT * FROM tbl1 INNER JOIN tbl2 ON tbl1.col1 = tbl2.col1",
         "SELECT * FROM tbl1 INNER JOIN tbl2 ON tbl1.col1 = tbl2.col1"],
        ["SELECT col1, col2 FROM tbl1 INNER JOIN tbl2 ON tbl1.col1 = tbl2.col1 AND tbl1.col2 = tbl2.col2",
         "SELECT tbl1.col1, tbl1.col2 FROM tbl1 INNER JOIN tbl2 ON tbl1.col1 = tbl2.col1 AND tbl1.col2 = tbl2.col2"],
    ]

    for sql, expected_sql in TEST_TABLE:
        qc = QueryCleaner(sql)
        # new_sql = qc.force_table_alias_on_inner_join().text()
        # assert new_sql == expected_sql
