SELECT pg_terminate_backend (pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = 'patrowlhears_db';
DROP DATABASE IF EXISTS patrowlhears_db;
