#!/bin/bash

PATROWLHEARSDATA_REPO="https://github.com/Patrowl/PatrowlHearsData"

lastrelease() { git ls-remote --tags "$1" | cut -d/ -f3- | tail -n1; }

# Create a temporary directory
tmp_dir=$(mktemp -d -t ci-XXXXXXXXXX)
echo "Using tmp dir: $tmp_dir"

echo "[+] Download and untar the latest release of PatrowlHearsData"
last_release=$(lastrelease $PATROWLHEARSDATA_REPO)
wget -P $tmp_dir $PATROWLHEARSDATA_REPO/archive/${last_release}.tar.gz

echo "[+] Untar archive"
tar -xzf $tmp_dir/${last_release}.tar.gz -C $tmp_dir

# Catch the right extracted directory
data_dir=`ls $tmp_dir | grep PatrowlHearsData`

lastupdate=""
[ -f var/data/lastupdate.txt ] && lastupdate="-l $(cat var/data/lastupdate.txt)"
echo "[i] Last update: $lastupdate"

echo "[+] Import data (diff from base)"
env/bin/python manage.py importcwes -i ${tmp_dir}/${data_dir}/CWE/data/cwes-diff.json
env/bin/python manage.py importcpes -i ${tmp_dir}/${data_dir}/CPE/data/cpes-diff.json
env/bin/python manage.py importcves -d ${tmp_dir}/${data_dir}/CVE/data/ $lastupdate
env/bin/python manage.py importvias -i ${tmp_dir}/${data_dir}/VIA/data/via-diff.json

echo "[+] Remove tmp dir"
rm -rf $tmp_dir

current_date=$(env/bin/python -c 'from datetime import datetime as dt; print(dt.today().strftime("%Y-%m-%d"))')
echo $current_date > var/data/lastupdate.txt
