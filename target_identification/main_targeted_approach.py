# -*- coding: utf-8 -*-
"""
Created on Wed Sep 02 12:59:04 2015

@author: glackner
"""
import emzed
import build_peaks_table
import batch_process
import in_out as io
import os

polarity = "pos"
def select_peakmap(peakmaps):
    pm_dict = {}
    for pm in peakmaps:
        source = pm.meta['source']
        pm_dict[source] = pm
    choice = pm_dict.keys() #create a list of keys
    choice.sort()
    select=emzed.gui.DialogBuilder("Please choose peakmap")\
    .addChoice('Peakmaps',choice)\
    .show()
    select_pm_name = choice[select]
    select_pm = pm_dict[select_pm_name]
    return select_pm

def get_user_adducts(polarity="pos"):
    choice = ["positive", "negative"] #create a list of keys
    select=emzed.gui.DialogBuilder("Please choose polarity")\
    .addChoice('Polarity',choice)\
    .show()
    polarity = choice[select]
    if polarity == "positive":
        adducts=emzed.adducts.positive.buildTableFromUserDialog()
    elif polarity == "negative":
        adducts=emzed.adducts.negative.buildTableFromUserDialog() 
    return adducts

    
def run_workflow(__):
    DialogBuilder = emzed.gui.DialogBuilder
    params = DialogBuilder('Workflow parameters')\
    .addFileOpen('select compound table', formats=['csv', 'table'])\
    .addFilesOpen('select peakmaps',formats=['mzXML', 'mzML'])\
    .addFloat('Min area for adduct filtering', default=1e3, help='Minimal area to define adduct peak as existing')\
    .addDirectory('Please choose result directory')\
    .addText('Give results title')\
    .show()
    compound_file_path, peakmap_pathes, min_area, result_path, result_title = params
    peakmaps = io.load_peakmaps(peakmap_pathes)
    pm=select_peakmap(peakmaps)
        
    
    
    adducts = get_user_adducts()
    peaks_table = build_peaks_table.main_build_peaks_table(pm, adducts, compound_file_path)
    results = batch_process.main_batch_process(peaks_table, peakmaps, min_area)
    batch_process.inspect_and_modify(results)
    io.main_save(results, result_path, result_title) 
    
def reload_and_inspect(__):
    result_path=emzed.gui.askForSingleFile(extensions=['table'])
    results = io.load_result(result_path)
    batch_process.inspect_and_modify(results)
    path, title = os.path.split(result_path)
    io.main_save(result, path,title)
    
#def main_workflow():
#    choice = ['run_workflow', 'inspect_existing_results']
#    select = emzed.gui.DialogBuilder('select mode')\
#    .addChoice('select',choice)\
#    .show()
#    if select==1:
#        reload_and_inspect()
#    elif select==0:
#        run_workflow()        
def main_workflow():
    emzed.gui.DialogBuilder('Please select a task...   ')\
    .addButton('run workflow',run_workflow)\
    .addButton('reload, inspect and modify', reload_and_inspect)\
    .show()
 
    
if __name__=='__main__':
    result = main_workflow()