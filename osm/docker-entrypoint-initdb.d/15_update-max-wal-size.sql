-- checkpoints are occurring too frequently (18 seconds apart)
-- geox-api-db  | 2022-11-02 04:58:47.233 UTC [129] HINT:  Consider increasing the configuration parameter "max_wal_size".
ALTER SYSTEM
set max_wal_size = 4096;