#!/bin/bash

set -o errexit   # abort on nonzero exitstatus
set -o nounset   # abort on unbound variable
set -o pipefail  # don't hide errors within pipes

# Check if lock file exists
if [ -f /tmp/scrape.lock ]; then
    exit 1
fi

# Create lock file
touch /tmp/scrape.lock

#Activate virtual environment
source /home/vicuser/myenv/bin/activate

today=$(date +"%Y-%m-%d")
#USAGE: run_script file
# excecute a python script
run_script() {
    local path="/home/vicuser/Data-Engineering-Project/webscraping_scripts/"
    local file="${1}"
    echo "Running script: ${file}"
    python3 $path$file
}

#USAGE: log message
# log a message to log files
log() {
    local current_date=$(date +"%Y-%m-%d %H:%M:%S")
    local LOGFILE=/home/vicuser/Data-Engineering-Project/logs/logs.txt
    echo "${1} | ${2} | ${current_date}" >> $LOGFILE
}

#Data ophalen
log "Transavia" "start"
touch /home/vicuser/Data-Engineering-Project/data/transavia/transaviaScrapeData_${today}.csv && chmod 666 /home/vicuser/Data-Engineering-Project/data/transavia/transaviaScrapeData_${today}.csv
run_script Transavia2_Scrape.py &
wait
log "Transavia" "completed"

#Data ophalen
log "RyanAir" "start"
touch /home/vicuser/Data-Engineering-Project/data/ryanair/ryanairScrapeData_${today}.csv && chmod 666 /home/vicuser/Data-Engineering-Project/data/ryanair/ryanairScrapeData_${today}.csv
run_script Ryanair_Scrape.py &
wait
log "RyanAir" "completed"

#Data ophalen
log "TUI" "start"
touch /home/vicuser/Data-Engineering-Project/data/tuifly/tuiFlyScrapeData_${today}.csv && chmod 666 /home/vicuser/Data-Engineering-Project/data/tuifly/tuiFlyScrapeData_${today}.csv
run_script TUI_Scrape.py &
wait
log "TUI" "completed"

#Data ophalen
# log "Brussels Airlines" "start"
# run_script BrusselsAirlines2_Scrape.py
# log "Brussels Airlines" "completed"

#Pipeline uitvoeren
log "Pipeline" "start"
run_script csv_to_db.py
log "Pipeline" "completed"

#Deactivate virtual environment
deactivate

# Remove lock file
rm /tmp/scrape.lock

log "Scrape" "completed"