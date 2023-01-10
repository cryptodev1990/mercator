We show a model:

0) A table schema (with column descriptions?)

```sql
CREATE TABLE tmp (
  id BIGINT,  -- This is the primary key of the table and will always be a UUID
  name VARCHAR, -- This is the name of the user
  ...
)
```

1) Column summary stats  # Using ``df.describe(include='all')`` or something else?
2) An English language query on top of the SQL
3) a) The ideal formatted SQL output
3) b) The ideal vega-lite chart


Could optionally use

Other possibilities -- 

Train https://huggingface.co/google/flan-t5-xxl on the same data set as https://huggingface.co/tscholak/cxmefzzi?text=How+many+singers+do+we+have%3F+%7C+concert_singer+%7C+stadium+%3A+stadium_id%2C+location%2C+name%2C+capacity%2C+highest%2C+lowest%2C+average+%7C+singer+%3A+singer_id%2C+name%2C+country%2C+song_name%2C+song_release_year%2C+age%2C+is_male+%7C+concert+%3A+concert_id%2C+concert_name%2C+theme%2C+stadium_id%2C+year+%7C+singer_in_concert+%3A+concert_id%2C+singer_id
Train https://huggingface.co/google/flan-t5-xxl



    Convert text to SQL.

    You have the following DDLs:

    ```
	CREATE TABLE tmp (
	  id BIGINT,  -- This is the primary key of the table and will always be a UUID
	  name VARCHAR, -- This is the name of the user
	  ...
	)
    
    ```

    The tables have the following summary statistics:

    ```
    
    ```

    Write the SQL that answers the following question:

    """{user_query}"""

    Respond with only one concise SQL statement.

