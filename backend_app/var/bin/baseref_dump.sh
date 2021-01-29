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
      POSITIONAL+=("$1"); shift;;
  esac
done

DB_NAME=${DB_NAME:-patrowlhears_db}
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}
DB_USERNAME=${DB_USERNAME:-patrowlhears}
DB_PASSWORD=${DB_PASSWORD:-}
DUMP_FILE="var/db/patrowlhears_db_dump_"$(date "+%Y%m%d%H%M%S")".sql"


# source env/bin/activate
echo "[+] Search the last update entry from referential"
echo -e "\
from django.conf import settings\r\
from data.models import DataSync\r\
from data.utils import _export_data_info\r\
import datetime\r\
data = _export_data_info(since=datetime.datetime.strptime(settings.HEARS_DATASYNC_BASEDATE, '%Y-%m-%d').strftime('%s'))\r\
print(data)\r\n
since = data['oldest_update']\r\n
ds = DataSync.objects.create(
        since_date=since,
        comments='Local SQL dump "${DUMP_FILE}"'
    )
" | env/bin/python manage.py shell --settings backend_app.settings_replica


echo "[+] Dump base ref data from DB (pg_dump)"
# pg_dump $DB_NAME -h $DB_HOST -p $DB_PORT -U $DB_USERNAME \
#   --column-inserts -a \
#   -t exploits_metadata \
#   -t kb_bulletin \
#   -t kb_cpe \
#   -t kb_cve \
#   -t kb_cve_bulletins \
#   -t kb_cve_products \
#   -t kb_cve_productversions \
#   -t kb_cwe \
#   -t kb_product \
#   -t kb_product_version \
#   -t kb_vendor \
#   -t threats_metadata \
#   -t vulns \
#   -t vulns_products \
#   -t vulns_productversions \
#   > $DUMP_FILE

echo "[+] Dump done: "$DUMP_FILE
