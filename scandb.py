from datalayer import DataLayer

SCAN_DB_PATH = 'scandb.db'
SCAN_TABLE = 'scan'
REJECTED_SCAN_TABLE = 'rejected'
MACHINE_KEY = 'machine'
NACHINE_AND_FLAG_KEY = 'machine_and_flag'
REJECTED_KEY = 'rejected'
FLAG_KEY = 'flag'

class ScanDB:
    def __init__(self) -> None:
        self.scans = DataLayer(SCAN_DB_PATH, SCAN_TABLE)
        self.rejected_scans = DataLayer(SCAN_DB_PATH, REJECTED_SCAN_TABLE)
    
    def add_scan (self, machine_name, scan):
        scans_per_machine = self.scans.read(MACHINE_KEY, machine_name)
        if len(scans_per_machine) == 0:
            self.scans.create({MACHINE_KEY : machine_name, 'scans' : [scan]})
        else:
            machine_scans_from_db = scans_per_machine[0]
            machine_scans_from_db['scans'].append(scan)
            self.scans.update(MACHINE_KEY, machine_name, machine_scans_from_db)

    def add_rejected_scan (self, machine_name, flag_name, amount):
        machine_and_flag = machine_name + "_" + flag_name;
        scans_per_machine = self.rejected_scans.read(NACHINE_AND_FLAG_KEY, machine_and_flag)
        if len(scans_per_machine) == 0:
            self.rejected_scans.create({NACHINE_AND_FLAG_KEY : machine_and_flag, REJECTED_KEY : amount})
        else:
            machine_total_rjected_from_db = scans_per_machine[0]
            machine_total_rjected_from_db[REJECTED_KEY] += + amount

            self.rejected_scans.update(NACHINE_AND_FLAG_KEY, machine_and_flag, machine_total_rjected_from_db)

        scans_per_flag = self.rejected_scans.read(FLAG_KEY, flag_name)
        if len(scans_per_flag) == 0:
            self.rejected_scans.create({FLAG_KEY : flag_name, REJECTED_KEY : amount})
        else:
            machine_total_rjected_from_db = scans_per_flag[0]
            machine_total_rjected_from_db[REJECTED_KEY] += + amount
            
            self.rejected_scans.update(FLAG_KEY, flag_name, machine_total_rjected_from_db)

    def get_rejected_by_flag(self, flag):
        return self.rejected_scans.read(FLAG_KEY, flag)

    def get_rejected_by_machine_and_flag(self, machine_name, flag):
        return self.rejected_scans.read(NACHINE_AND_FLAG_KEY, machine_name + "_" + flag)
    
    def get_rejected_by_machine(self, machine_name):
        return self.rejected_scans.read_start_with(NACHINE_AND_FLAG_KEY, machine_name)

