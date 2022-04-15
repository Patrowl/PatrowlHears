while [[ $# -gt 0 ]]; do
  key="$1"

  case $key in
      -d|--database)
      DB_NAME="$2"; shift; shift;;
      -h|--host)
      DB_HOST="$2"; shift; shift;;
      -p|--port)
      DB_PORT="$2"; shift; shift;;
      -u|--username)
      DB_USERNAME="$2"; shift; shift;;
      -w|--password)
      DB_PASSWORD="$2"; shift; shift;;
      *)    # unknown option
      # POSITIONAL+=("$1");
      shift;;
  esac
done

DB_NAME=${DB_NAME:-patrowlhears_db}
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}
DB_USERNAME=${DB_USERNAME:-patrowlhears}
DB_PASSWORD=${DB_PASSWORD:-patrowlhears}

echo "[+] Create DB schema"

CMD=""
[[ pg_isready ]] && { CMD="psql"; }
[[ $CMD == "" && `sudo -u postgres pg_isready 2>/dev/null` ]] && { CMD="sudo -u postgres psql"; }
[[ $CMD == "" ]] && { echo "Unable to find/use psql. Check PATH vars"; exit;}

$CMD <<EOF

SELECT 'CREATE USER $DB_USERNAME WITH PASSWORD "$DB_PASSWORD"' WHERE NOT EXISTS (SELECT FROM pg_user WHERE usename = '$DB_USERNAME')\gexec
SELECT 'CREATE DATABASE $DB_NAME WITH OWNER $DB_USERNAME' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$DB_NAME')\gexec
ALTER ROLE "$DB_USERNAME" SET client_encoding TO 'utf8';
ALTER ROLE "$DB_USERNAME" SET default_transaction_isolation TO 'read committed';
ALTER ROLE "$DB_USERNAME" SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE '$DB_NAME' TO '$DB_USERNAME';
EOF

echo "[+] Done."
exit

# CREATE USER $DB_USERNAME WITH PASSWORD '$DB_PASSWORD';
# CREATE DATABASE "$DB_NAME" WITH OWNER "$DB_USERNAME";
# ALTER ROLE "$DB_NAME" SET client_encoding TO 'utf8';
# ALTER ROLE "$DB_NAME" SET default_transaction_isolation TO 'read committed';
# ALTER ROLE "$DB_NAME" SET timezone TO 'UTC';
# GRANT ALL PRIVILEGES ON DATABASE "$DB_NAME" TO "$DB_USERNAME";
