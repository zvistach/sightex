import os
import sys
import pickle

PICKLE_DIR = 'pickles'
OUTPUT_FILE = 'output.txt'

AVERAGE_INTENSITY = 'average_intensity'
GOOD_RBCS_CENTERS = 'good_rbcs_centers'
RBC_FINAL_COUNT = 'rbc_final_count'
CBC_DATA = 'CBC_data' 
UNKNOWN_CANDS = 'unknown_cands'
HEIGHT = 'height'
WIDTH = 'width'
MIN_HEIGHT = 'min_height'
MIN_WIDTH = 'min_width'
MAX_HEIGHT = 'max_height'
MAX_WIDTH = 'max_width'
TAG = 'tag'
SLIDE_ID = 'slide_id'

def get_pickle_file_names (dir):
    validFiles = []
    try:
        file_names = os.listdir(dir)
        for file_name in file_names:
            if file_name.endswith(".pkl"):
                validFiles.append(file_name)
    except:
        print ("Couldn't open directory", dir)

    return validFiles

def read_from_pickle(path):
    with open(path, 'rb') as file:
        try:
            while True:
                yield pickle.load(file)
        except EOFError:
            pass

def getLastChildElement (tree, item_name):
    elements = item_name.split ('.')
    child = tree
    for element in elements:
        if (child.get(element) != None):
            child = child[element]
        else:
            return None
    return child

def gatherData(pickle_file, *keys):
    returnedData = {}
    for key in keys:
        returnedData[key] = []
    
    for items in read_from_pickle(PICKLE_DIR + "/" + pickle_file):
        for item in items:
            for key in keys:
                childElement = getLastChildElement(item, key)
                if (childElement):
                    returnedData[key].append(childElement)
    
    return returnedData

def calc_average (pickles_data, key):
    count = 0
    total = 0
    for pickle_data in pickles_data:
        for value in pickle_data[key]:
            total += value
            count += 1
    return total / count

def gather_data_in_set (pickles_data, key):
    array = set()
    for pickle_data in pickles_data:
        for values in pickle_data[key]:
            for value in values:
                array.add(value)
    return array

def calc_mean (pickle_data, key):
    count = 0
    total = 0
    for value in pickle_data[key]:
        total += value
        count += 1 
    return total / count

def extract_and_calc_data(pickles_data, tags_for_slide, max_height_width_for_tag):
    for pickle_data in pickles_data:
        slide_arrays = pickle_data[CBC_DATA + "." + UNKNOWN_CANDS]
        for slide_array in slide_arrays:
            for slide in slide_array:
                if not slide[SLIDE_ID] in tags_for_slide:
                    tags_for_slide[slide[SLIDE_ID]] = set()
                tags_for_slide[slide[SLIDE_ID]].add(slide[TAG])
                if not slide[TAG] in max_height_width_for_tag:
                    max_height_width_for_tag[slide[TAG]] = { MAX_HEIGHT: 0, MIN_HEIGHT: sys.maxsize, MAX_WIDTH: 0, MIN_WIDTH: sys.maxsize }
                if slide[HEIGHT] > max_height_width_for_tag[slide[TAG]][MAX_HEIGHT]: max_height_width_for_tag[slide[TAG]][MAX_HEIGHT] = slide[HEIGHT] 
                if slide[HEIGHT] < max_height_width_for_tag[slide[TAG]][MIN_HEIGHT]: max_height_width_for_tag[slide[TAG]][MIN_HEIGHT] = slide[HEIGHT] 
                if slide[WIDTH] > max_height_width_for_tag[slide[TAG]][MAX_WIDTH]: max_height_width_for_tag[slide[TAG]][MAX_WIDTH] = slide[WIDTH] 
                if slide[WIDTH] < max_height_width_for_tag[slide[TAG]][MIN_WIDTH]: max_height_width_for_tag[slide[TAG]][MIN_WIDTH] = slide[WIDTH]
    return 

def logTofile (file, obj):
    file.write(str(obj) + "\n")

def main():
    pickle_files = get_pickle_file_names('pickles')
    pickles_data = []
    print ("Loading data...")
    for pickle_file in pickle_files:
        pickle_data = gatherData(pickle_file, AVERAGE_INTENSITY, GOOD_RBCS_CENTERS, RBC_FINAL_COUNT, CBC_DATA + "." + UNKNOWN_CANDS)
        pickles_data.append(pickle_data)
    print ("Saving calculations...")
    
    with open(OUTPUT_FILE, 'w') as output:
        logTofile (output, "Average of all 'average_intensity' fields:");
        logTofile (output, calc_average(pickles_data, AVERAGE_INTENSITY))
        logTofile (output, "\nAll 'good_rbcs_center's:");
        logTofile (output, gather_data_in_set(pickles_data, GOOD_RBCS_CENTERS))
        logTofile (output, "\nMean 'rbc_final_count' per pickle:");
        for pickle_data in pickles_data:
            logTofile (output, calc_mean(pickle_data, RBC_FINAL_COUNT))
        tags_for_slide = {}
        max_height_width_for_tag = {}
        extract_and_calc_data(pickles_data, tags_for_slide, max_height_width_for_tag)
        logTofile (output, "\nReason tags per unknown cands slides:");
        logTofile(output, tags_for_slide)
        logTofile (output, "\nMax/Min height and width for tags:");
        logTofile (output, max_height_width_for_tag)
        output.close()
    print ("Done!")
            
    
main()
