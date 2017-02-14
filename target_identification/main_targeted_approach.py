# -*- coding: utf-8 -*-
"""
Created on Wed Sep 02 12:59:04 2015

@author: glackner

Version 0.9.1

"""
import emzed
import build_peaks_table
import batch_process
import in_out as io
import os




   
def run_workflow(__):
    DialogBuilder = emzed.gui.DialogBuilder
    params = DialogBuilder('Workflow parameters')\
    .addFileOpen('select compound table', formats=['csv', 'table'])\
    .addFilesOpen('select peakmaps',formats=['mzXML', 'mzML'])\
    .addFloat('Min area for peak filtering', default=1e3, help='Minimal area to define adduct peak as existing')\
    .addFloat("MZ tolerance in ppm", default=5.0, help="relative MZ tolerance for targeted identification")\
    .addDirectory('Please choose result directory')\
    .addText('Give results title')\
    .show()
    compound_file_path, peakmap_pathes, min_area, mz_tol_ppm, result_path, result_title = params
    mz_tol = mz_tol_ppm*1e-6    
    peakmaps = io.load_peakmaps(peakmap_pathes)

    peaks_table = build_peaks_table.main_build_peaks_table(peakmaps, mz_tol=mz_tol, compound_table_path=compound_file_path)   
    results = batch_process.main_batch_process(peaks_table, peakmaps, min_area)
    batch_process.inspect_and_modify(results)
    io.main_save(results, result_path, result_title) 
    
def reload_and_inspect(__):
    result_path=emzed.gui.askForSingleFile(extensions=['table'])
    results = io.load_result(result_path)
    batch_process.inspect_and_modify(results)
    path, title = os.path.split(result_path)
    io.main_save(result, path,title)
    
       
def main_workflow():
    emzed.gui.DialogBuilder('Please select a task...   ')\
    .addButton('Run targeted identification',run_workflow)\
    .addButton('Reload, inspect and modify', reload_and_inspect)\
    .show()
 
    
if __name__=='__main__':
    result = main_workflow()