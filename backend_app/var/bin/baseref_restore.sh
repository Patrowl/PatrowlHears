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
      -f|--file)
      DUMP_FILE="$2"; shift; shift;;
      *)    # unknown option
      POSITIONAL+=("$1"); shift;;
  esac
done

DB_NAME=${DB_NAME:-patrowlhears_db}
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}
DB_USERNAME=${DB_USERNAME:-patrowlhears}
DB_PASSWORD=${DB_PASSWORD:-}
DUMP_FILE=${DUMP_FILE:-"var/db/dump.sql"}

if [ -f "$DUMP_FILE" ]; then
  echo "[+] Restore base ref data from SQL dump file (pg_restore)"
  echo "--- Use file: "$DUMP_FILE
else
  echo "[!] Unable to find SQL dump file: "$DUMP_FILE
  exit
fi

CMD=""
[[ pg_isready ]] && { CMD="psql"; }
[[ $CMD == "" && `sudo -u postgres pg_isready 2>/dev/null` ]] && { CMD="sudo -u postgres psql"; }
[[ $CMD == "" ]] && { echo "Unable to find/use psql. Check PATH vars"; exit;}

$CMD --quiet -d $DB_NAME -h $DB_HOST -p $DB_PORT -U $DB_USERNAME -f $DUMP_FILE

echo "[+] Restore done."
exit
