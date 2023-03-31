import csv
import os
from datetime import datetime
from scandb import ScanDB

CSV_DIR = 'csv'
RBC = "rbc [10^6/uL]"
FLAGS = "flags"
EOS = "eos% [%]"
BASO = "baso% [%]"
SCAN_DATE = "scan_date"
SCAN_TIME = "scan_time"
MACHINE_NAME = "machine_name"
TIMESTAMP = 'timestamp'
ACCEPTED_KEY = 'accepted'
DATES_KEY = 'dates'

def get_csv_file_names (dir):
    validFiles = []
    try:
        file_names = os.listdir(dir)
        for file_name in file_names:
            if file_name.endswith(".csv"):
                validFiles.append(file_name)
    except:
        print ("Couldn't open directory", dir)

    return validFiles

def get_index(col_name, titles_row):
    index = 0
    while titles_row[index] != col_name:
        index +=1
    return index

def binary_search(array, to_match):
    lo = 0
    hi = len(array) - 1
    best_ind = lo
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if array[mid] < to_match:
            lo = mid + 1
        elif array[mid] > to_match:
            hi = mid - 1
        else:
            best_ind = mid
            break
        # check if data[mid] is closer to to_match than array[best_ind] 
        if abs(array[mid] - to_match) < abs(array[best_ind] - to_match):
            best_ind = mid
    return best_ind

def get_match_in_qc (flagged_scan_date, dates):
    matched_date = dates[binary_search(dates, flagged_scan_date)]
    if (flagged_scan_date - matched_date > 7*24*60*60*1000):
        return 0.0
    return matched_date

def handle_wb_csv(allscans, scan_type, machine_name, scan_serie, titles_row, rbc_index, flags_index, eos_index, baso_index, date_index, time_index, row):
    # Creating timestamp from data and time
    datetime_str = row[date_index] + " " + row[time_index]
    timestamp = datetime.timestamp(datetime.strptime(datetime_str, '%Y-%m-%d %H:%M'))

    # Extract relevant data for validation
    if row[flags_index] != '':
        scan = {}
        scan[RBC] = float(row[rbc_index])
        scan[EOS] = float(row[eos_index])
        scan[BASO] = float(row[baso_index])
        scan[FLAGS] = row[flags_index]
        scan[TIMESTAMP] = timestamp
        scan[MACHINE_NAME] = machine_name
        scan_serie[scan_type].append(scan)
    scan_data = {}
    current_index = 0
    for cell in row:
        scan_data[titles_row[current_index]] = cell
        current_index += 1
    scan_data[ACCEPTED_KEY] = True

    # Keep in allscan dict that will later be used to be persisted in the db
    allscans[machine_name + "_" + str(timestamp)] = scan_data

def handle_qc_csv(scan_type, scan_serie, rbc_index, eos_index, baso_index, date_index, time_index, row, dates_array):
    scan = {}
    datetime_str = row[date_index] + " " + row[time_index]
    timestamp = datetime.timestamp(datetime.strptime(datetime_str, '%Y-%m-%d %H:%M'))
    scan[RBC] = float(row[rbc_index])
    scan[EOS] = float(row[eos_index])
    scan[BASO] = float(row[baso_index])
    scan_serie[scan_type][timestamp] = scan
    dates_array.append(timestamp)

def perform_validation(scanDB, data, allscans):
    for scan_instance in data:
        for flagged_scan in data[scan_instance]['WB']:
            flag = flagged_scan[FLAGS]
            lowered_case_flag = flag.lower().replace(" ", "_")
            if 'QC' in data[scan_instance]:
                # Find the closest scan in QC
                match_date_in_QC = get_match_in_qc (flagged_scan[TIMESTAMP], data[scan_instance][DATES_KEY])
                if (match_date_in_QC != 0.0):
                    flagged_scan_all_data = allscans[flagged_scan[MACHINE_NAME] + "_" + str(flagged_scan[TIMESTAMP])]
                    QC_matched_scan = data[scan_instance]['QC'][match_date_in_QC]
                    # Validate according to the flag
                    if flag == 'Suspected Dual RBC population':
                        rbc_wb = flagged_scan[RBC]
                        rbc_qc = QC_matched_scan[RBC]
                        if abs(rbc_wb - rbc_qc) > 0.5:
                            flagged_scan_all_data[ACCEPTED_KEY] = False
                            scanDB.add_rejected_scan(flagged_scan[MACHINE_NAME], lowered_case_flag, 1)
                        else:
                            flagged_scan_all_data[ACCEPTED_KEY] = True
                    elif flag == 'Suspected IG':
                        eos_wb = flagged_scan[EOS]
                        eos_qc = QC_matched_scan[EOS]
                        baso_wb = flagged_scan[BASO]
                        baso_qc = QC_matched_scan[BASO]
                        if abs(eos_wb - eos_qc) >= 9 or abs(baso_wb - baso_qc) >= 9:
                            flagged_scan_all_data[ACCEPTED_KEY] = False
                            scanDB.add_rejected_scan(flagged_scan[MACHINE_NAME], lowered_case_flag, 1)                          
                        else:
                            flagged_scan_all_data[ACCEPTED_KEY] = True
                    else:
                        flagged_scan_all_data[ACCEPTED_KEY] = False
                        scanDB.add_rejected_scan(flagged_scan[MACHINE_NAME], lowered_case_flag, 1)
            else:
                flagged_scan_all_data[ACCEPTED_KEY] = False
                scanDB.add_rejected_scan(flagged_scan[MACHINE_NAME], lowered_case_flag, 1)

def main(): 
    print ("Starting CSV import...")
    scanDB = ScanDB()
    csv_files = get_csv_file_names(CSV_DIR)
    data = {}
    allscans = {}

    # Read CSV Files
    for file_name in csv_files:
        with open(CSV_DIR + '/' + file_name, newline='') as csvfile:

            # Get titles
            scan_type = file_name[-6:][:2]
            scan_id = file_name[:len(file_name)-7]
            machine_name = file_name.split("_")[1]
            if (not scan_id in data):
                data[scan_id] = {}   
            scan_serie = data[scan_id]
            csv_reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            titles_row = next(csv_reader)
            rbc_index = get_index(RBC, titles_row)
            flags_index = get_index(FLAGS, titles_row)
            eos_index = get_index(EOS, titles_row)
            baso_index = get_index(BASO, titles_row)
            date_index = get_index(SCAN_DATE, titles_row)
            time_index = get_index(SCAN_TIME, titles_row)

            # Handle WB or QC CSV differently
            if scan_type == 'WB':
                scan_serie[scan_type] = []
                for row in csv_reader:
                    handle_wb_csv(allscans, scan_type, machine_name, scan_serie, titles_row, rbc_index, flags_index, eos_index, baso_index, date_index, time_index, row)
            else:
                scan_serie[scan_type] = {}
                dates_array = []
                for row in csv_reader:
                    handle_qc_csv(scan_type, scan_serie, rbc_index, eos_index, baso_index, date_index, time_index, row, dates_array)
                dates_array.sort()
                scan_serie[DATES_KEY] = dates_array

    # Perform validation, persist results in DB
    perform_validation(scanDB, data, allscans)
    
    # Persist all scans from WB CSV in the DB        
    for scan_id in allscans.keys():
        machine_name = scan_id.split("_")[0]
        scanDB.add_scan(machine_name, allscans[scan_id])

    print ("CSV Import Done!")
main()