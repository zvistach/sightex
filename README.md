# Sight Exercise

#### Prerequisites
- This excerise was tested on Python 3.11
- Csv and pickle folders should be populated with the files shared in the email (program was not tested with empty folders)
- Dependencies to be installed before running the program: `fastapi`, `uvicorn`, `tinydb` (I didn't create a clean environment to test it so I hope I didn't miss anything) 


#### Section 1
##### How to run it?
`python pickle_manipulation.py`

##### What does it do?
This program reads all pickle files from pickles/ directory and performs the requested maipulations required in the excerise. The output is saved in output.txt (also pushed to github).

##### Assumption and limitations
- Calculating the average intensity of all fields is based on the average of all "average_intensity" fields in the pickle files.
- "good_rbc_center" fields contain list of pairs with two integers for each pair. I provided a list of all of them from all pickles. I used a set data structure to eliminate duplicates.
- Mean of RBC final count was caluclated as the average of all "rbc_final_count" fields for each pickle file, and is provided as a list of means.
- For all slides I provided a set (to eliminate duplicates) of their reason tags, and for each tag I calculated the max and min height and width. I used dicts to map tags to their corresponding slides and tags to their corresponding max and min height and width.
- The assumption is that the largest pickle file can be loaded into memory (I didn't make optimizations regarding loading a partial file). After each pickle file is loaded into the memory, the loaded data is being traversed only once (O(n)) and only the relvant data is stored in a dict (with list of values for each attribute). Then the full pickle data that is irrelvant to the calculation is cleared from memory (or left out of scope) before the next pickle file is loaded.

#### Section 2
##### How to run it?
`python csvimport.py`

`uvicorn backend_service:app --port 80`

##### What does it do?
- Import: You first need to import the csv files to be persisted in the database. The import works in an append strategy - in case the import runs again, the imported data will be appended to the existing data. To clear the data, you can delete the `scandb.db` file.
- Server: The API server is based on Fast API and Uviron. You may need to use `sudo` to run the server in port 80.

##### Assumption and limitations
- I used TinyDB for this excercise. This DB is simply stored in a file, but the data layer is implemented separately and this database can be easily migrated to another NoSQL document based database (such as MongoDB).
- Data from all scans is persisted in 'scan' table. The key for each entry is the machine name and the value is a list of json documents for each scan, with all attributes from the csv files, with an addition of a new boolean field "accepted" that indicates if the scan is accepted or rejected.
- To optimize performance, I denormalized the scan data and created a dedicated table for the api requirements: a "rejected" table that sums up rejected scans. The rejected scans are persisted in two maps with the keys: flags (maps flag to total rejects scans), and machine_and_flags (maps machine and flags to the total rejects). To get all rejected scans for a single machine, I get all rejects for all flags in a particular machine. The access time to get the data for each api call is O(1), assuming the number of flags is small and constant.

#### General assumptions and limitations
- No unit tests / integration test were performed due to time constratins, but manual tests were conducted
- There's not much error handling in the code. The assumptions is that the data in pickle and csv files is valid and the names of the attributes are constant