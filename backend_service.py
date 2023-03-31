from fastapi import FastAPI, HTTPException
from scandb import ScanDB

REJECTED_KEY = 'rejected'

app = FastAPI()
scanDB = ScanDB()

@app.get("/{machine_id}")
def get_rejects_per_machine (machine_id):
    result = scanDB.get_rejected_by_machine(machine_id)
    if (result == []):
        raise HTTPException(status_code=404, detail="Item not found")

    # Sum up all rejects from all flags in machine
    total = 0
    for result_for_flag in result:
        total += result_for_flag[REJECTED_KEY]
    return {REJECTED_KEY : total}

@app.get("/total/{flag_name}")
def get_total_per_flag (flag_name):
    result = scanDB.get_rejected_by_flag(flag_name)
    if (result == []):
        raise HTTPException(status_code=404, detail="Item not found")
   
    return {REJECTED_KEY : result[0][REJECTED_KEY]}

@app.get("/{machine_id}/{flag_name}")
def get_rejects_per_flag_for_machine (machine_id, flag_name):
    result = scanDB.get_rejected_by_machine_and_flag(machine_id, flag_name)
    if (result == []):
        raise HTTPException(status_code=404, detail="Item not found")
   
    return {REJECTED_KEY : result[0][REJECTED_KEY]}

