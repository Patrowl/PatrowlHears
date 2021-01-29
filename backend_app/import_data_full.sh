#!/bin/bash

PATROWLHEARSDATA_REPO="https://github.com/Patrowl/PatrowlHearsData"

lastrelease() { git ls-remote --tags "$1" | cut -d/ -f3- | tail -n1; }

# Create a temporary directory
tmp_dir=$(mktemp -d -t ci-XXXXXXXXXX)
echo "Using tmp dir: $tmp_dir"

echo "[+] Download and untar the latest release of PatrowlHearsData"
last_release=$(lastrelease $PATROWLHEARSDATA_REPO)
wget -P $tmp_dir $PATROWLHEARSDATA_REPO/archive/${last_release}.tar.gz
tar -xzf $tmp_dir/${last_release}.tar.gz -C $tmp_dir

# Catch the right extracted directory
data_dir=`ls $tmp_dir | grep PatrowlHearsData`

# Prepare vars
END_YEAR=$(env/bin/python -c 'from datetime import datetime as dt; print(dt.today().strftime("%Y"))')

echo "[+] Import data (full)"
env/bin/python manage.py importcwes -i ${tmp_dir}/${data_dir}/CWE/data/cwes-base.json
env/bin/python manage.py importcpes -i ${tmp_dir}/${data_dir}/CPE/data/cpes-base.json
# env/bin/python manage.py importcves -d ${tmp_dir}/${data_dir}/CVE/data/
for i in $(seq 1999 $END_YEAR); do
  echo "[I] Year: $i"
  env/bin/python manage.py importcves -d ${tmp_dir}/${data_dir}/CVE/data/ -y $i
done
env/bin/python manage.py importvias -i ${tmp_dir}/${data_dir}/VIA/data/via-base.json

echo "[+] Remove tmp dir"
rm -rf $tmp_dir

current_date=$(env/bin/python -c 'from datetime import datetime as dt; print(dt.today().strftime("%Y-%m-%d"))')
echo $current_date > var/data/lastupdate.txt
