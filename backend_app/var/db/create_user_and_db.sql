CREATE USER "patrowlhears" WITH PASSWORD 'patrowlhears';
CREATE DATABASE "patrowlhears_db" WITH OWNER "patrowlhears";
ALTER ROLE "patrowlhears" SET client_encoding TO 'utf8';
ALTER ROLE "patrowlhears" SET default_transaction_isolation TO 'read committed';
ALTER ROLE "patrowlhears" SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE "patrowlhears_db" TO "patrowlhears";
