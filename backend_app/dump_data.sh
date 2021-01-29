#!/bin/bash
display_usage() {
	echo "This script dump data from DB."
	echo -e "\nUsage: $0 [var/data] \n"
}

DUMPDIR=${1:-var/data}
echo "Using dump dir: $DUMPDIR"

tmp_dir=$(mktemp -d -t ci-XXXXXXXXXX)
echo "tmp dir: $tmp_dir"

echo "[+] Dump CWE" && env/bin/python manage.py dumpdata cves.CWE -o $tmp_dir/CWE.json -v 3
echo "[+] Dump CPE" && env/bin/python manage.py dumpdata cves.CPE -o $tmp_dir/CPE.json -v 3
echo "[+] Dump Vendor" && env/bin/python manage.py dumpdata cves.Vendor -o $tmp_dir/Vendor.json -v 3
echo "[+] Dump Product" && env/bin/python manage.py dumpdata cves.Product -o $tmp_dir/Product.json -v 3
echo "[+] Dump PackageType" && env/bin/python manage.py dumpdata cves.PackageType -o $tmp_dir/PackageType.json -v 3
echo "[+] Dump Package" && env/bin/python manage.py dumpdata cves.Package -o $tmp_dir/Package.json -v 3
echo "[+] Dump CVE" && env/bin/python manage.py dumpdata cves.CVE -o $tmp_dir/CVE.json -v 3
echo "[+] Dump Vuln" && env/bin/python manage.py dumpdata vulns.Vuln -o $tmp_dir/Vuln.json -v 3
echo "[+] Dump HistoricalVuln" && env/bin/python manage.py dumpdata vulns.HistoricalVuln -o $tmp_dir/HistoricalVuln.json -v 3
echo "[+] Dump ExploitMetadata" && env/bin/python manage.py dumpdata vulns.ExploitMetadata -o $tmp_dir/ExploitMetadata.json -v 3
echo "[+] Dump HistoricalExploitMetadata" && env/bin/python manage.py dumpdata vulns.HistoricalExploitMetadata -o $tmp_dir/HistoricalExploitMetadata.json -v 3
echo "[+] Dump ThreatMetadata" && env/bin/python manage.py dumpdata vulns.ThreatMetadata -o $tmp_dir/ThreatMetadata.json -v 3
echo "[+] Dump HistoricalThreatMetadata" && env/bin/python manage.py dumpdata vulns.HistoricalThreatMetadata -o $tmp_dir/HistoricalThreatMetadata.json -v 3

echo "[+] Dumps finidhed. Tar, Compress, Split and Store"
tar -czvf $DUMPDIR/data.tgz -C $tmp_dir/ .
split -b 20m $DUMPDIR/data.tgz $DUMPDIR/"data.tgz.part"
rm -rf $DUMPDIR/data.tgz
rm -rf $tmp_dir
