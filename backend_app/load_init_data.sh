#!/bin/bash
display_usage() {
	echo "This script load initial data into DB."
	echo -e "\nUsage: $0 [var/data] \n"
}

DUMPDIR=${1:-var/data}
echo "Using dump dir: $DUMPDIR"

tmp_dir=$(mktemp -d -t ci-XXXXXXXXXX)
echo $tmp_dir

# Reassemble split parts
cat $DUMPDIR/data.tgz.part* > $DUMPDIR/data.tgz

# Untar it
tar -xzvf $DUMPDIR/data.tgz -C $tmp_dir

# ls  $tmp_dir
[ -f $tmp_dir/CWE.json ] && env/bin/python manage.py loaddata $tmp_dir/CWE.json -v 3
[ -f $tmp_dir/Vendor.json ] && env/bin/python manage.py loaddata $tmp_dir/Vendor.json -v 3
[ -f $tmp_dir/Product.json ] && cat $tmp_dir/Product.json | jq 'del(.[]|.fields.versions)' > $tmp_dir/Product_clean.json
[ -f $tmp_dir/Product.json ] && env/bin/python manage.py loaddata $tmp_dir/Product_clean.json -v 3
[ -f $tmp_dir/PackageType.json ] && env/bin/python manage.py loaddata $tmp_dir/PackageType.json -v 3
[ -f $tmp_dir/Package.json ] && env/bin/python manage.py loaddata $tmp_dir/Package.json -v 3
[ -f $tmp_dir/CPE.json ] && env/bin/python manage.py loaddata $tmp_dir/CPE.json -v 3
[ -f $tmp_dir/CVE.json ] && env/bin/python manage.py loaddata $tmp_dir/CVE.json -v 3
[ -f $tmp_dir/Vuln.json ] && env/bin/python manage.py loaddata $tmp_dir/Vuln.json -v 3
[ -f $tmp_dir/HistoricalVuln.json ] && env/bin/python manage.py loaddata $tmp_dir/HistoricalVuln.json -v 3
[ -f $tmp_dir/ExploitMetadata.json ] && env/bin/python manage.py loaddata $tmp_dir/ExploitMetadata.json -v 3
[ -f $tmp_dir/HistoricalExploitMetadata.json ] && env/bin/python manage.py loaddata $tmp_dir/HistoricalExploitMetadata.json -v 3
[ -f $tmp_dir/ThreatMetadata.json ] && env/bin/python manage.py loaddata $tmp_dir/ThreatMetadata.json -v 3
[ -f $tmp_dir/HistoricalThreatMetadata.json ] && env/bin/python manage.py loaddata $tmp_dir/HistoricalThreatMetadata.json -v 3

rm -rf $DUMPDIR/data.tgz
rm -rf $tmp_dir

trap "rm -rf $tmp_dir" EXIT HUP INT QUIT TERM STOP
