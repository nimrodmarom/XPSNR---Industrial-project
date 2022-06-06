from fileinput import filename
import os
import csv
from tracemalloc import start
import matplotlib.pyplot as plt
import matplotlib.patches as mpl_patches
import numpy as np
from PIL import Image
import time
import typing
import pandas as pd

def move_videos_to_folders():
    """ Move all videos to its folder. """
    for file in os.listdir():
        # if file is folder continue
        if os.path.isdir(file):
            continue
        if file.endswith('.mp4') or file.endswith('.avi'):
            folder_name = file.split('__')[0]
            if not os.path.exists(folder_name):
                os.mkdir(folder_name)
            os.system("move {0} {1}".format(file, folder_name))     

def count_videos():
    """ Count the videos in the folder. """
    count = 0
    for folder in os.listdir():
        os.chdir(folder)
        files = os.listdir()
        #delete from files all files that are not mp4
        for file in files:
            if not (file.endswith('.mp4') or file.endswith('.avi')):
                files.remove(file)
        count += len(files)
        os.chdir('..')
    print(count)
        
def calculate_average_of_all_frames(file_name) -> float:
    # print (os.getcwd())
    os.chdir("..\\all_data_xpsnr")
    count = 0
    avg_sum = 0
    with open(file_name, "r") as f:
        lines = f.readlines()
        line = lines[-1]
        Y_value = float(line.split(": ")[1].split(" ")[0])
        U_value = float(line.split(": ")[2].split(" ")[0])
        V_value = float(line.split(": ")[3].split(" ")[0].strip())
        #for line in lines:
            # skip last line
        #    if count == len(lines) - 2:
        #        break
            # make line to dictionary by key (": ") value
            # if len(line.split(": ")) >=2:
            #     Y_value = float(line.split(": ")[2].split(" ")[0])
            #     U_value = float(line.split(": ")[3].split(" ")[0])
            #     V_value = float(line.split(": ")[4].split(" ")[0].strip())
                
            #     avg_frame = (Y_value + U_value + V_value) / 3
            #     count += 1
            #     avg_sum += avg_frame
    os.chdir("..\\results_xpsnr")
    return (4*Y_value + U_value + V_value)/6

def calculate_avg_by_folder(video_name):
    # print (os.getcwd())
    os.chdir("..\\videos\\AC4BF\\all_data")
    count = 0
    sum_Y, sum_U, sum_V = 0, 0, 0
    for file in os.listdir():
        if file.endswith(".txt"):
            with open(file, "r") as f:
                lines = f.readlines()
                for line in lines:
                    # skip last line
                    if count == len(lines) - 2:
                        break
                    # make line to dictionary by key (": ") value
                    if len(line.split(": ")) >=2:
                        Y_value = float(line.split(": ")[2].split(" ")[0])
                        U_value = float(line.split(": ")[3].split(" ")[0])
                        V_value = float(line.split(": ")[4].split(" ")[0])
                        
                        sum_Y += Y_value
                        sum_U += U_value
                        sum_V += V_value

                        count += 1

    print("AVG Y: ", sum_Y/count)
    print("AVG U: ", sum_U/count)
    print("AVG V: ", sum_V/count)

def calculate_BD_rate(R1, PSNR1, R2, PSNR2):
    lR1 = np.log(R1)
    lR2 = np.log(R2)

     # least squares polynomial fit
    p1 = np.polyfit(lR1, PSNR1, 3)
    p2 = np.polyfit(lR2, PSNR2, 3)

    # integration interval
    min_int = max(min(lR1), min(lR2))
    max_int = min(max(lR1), max(lR2))

    # indefinite integral of both polynomial curves
    p_int1 = np.polyint(p1)
    p_int2 = np.polyint(p2)

    # evaluates both poly curves at the limits of the integration interval
    # to find the area
    int1 = np.polyval(p_int1, max_int) - np.polyval(p_int1, min_int)
    int2 = np.polyval(p_int2, max_int) - np.polyval(p_int2, min_int)

    # find avg diff between the areas to obtain the final measure
    avg_diff = (int2-int1)/(max_int-min_int)

    return avg_diff

def deleteAllPngsAndAllMp4s():
    for folder in os.listdir():
        # check if folder is a folder
        if not os.path.isdir(folder):
            continue
        os.chdir(folder)
        files = os.listdir()
        for file in files:
            if os.path.isdir(file) and (file == 'results' or file == 'all_data'):
                os.chdir(file)
                for file2 in os.listdir():
                    os.remove(file2)
                os.chdir('..')
                os.rmdir(file)
            if file.endswith('.mp4') and not len(file.split('__')) == 6:
                os.remove(file)
            if file.endswith('.png'):
                os.remove(file)
        os.chdir('..')

def convertVideosToY4M():
    for folder in os.listdir():
        # check if folder is a folder
        if not os.path.isdir(folder):
            continue
        os.chdir(folder)
        if not os.path.exists('y4m_videos'):
            os.mkdir('y4m_videos')
        else:
            files = os.listdir('y4m_videos')
            os.chdir('y4m_videos')
            for file in files:
                os.remove(file)
            os.chdir('..')
        files = os.listdir()
        for file in files:
            if file.endswith('mp4') or file.endswith('avi'):
                new_video_name = file.split('.')[0] + '.y4m'
                os.system("ffmpeg -y -i {0} y4m_videos\\{1}".format(file, new_video_name))
        os.chdir('..')

def get_time_from_file(sub_folder: str, VQM_type: str):
    # if exists folder sub_folder\\profling
    last_line = []
    if os.path.exists(f'{sub_folder}\\profiling'):
        os.chdir(f'{sub_folder}\\profiling')
        with open(f'Full_{VQM_type}_profiling.csv' , 'r') as csvfile:
            rows = list(csv.reader(csvfile))
            if (len(rows[-1]) > 0):
                last_line = rows[-1]
            else:
                last_line = rows[-2]
        os.chdir('..\\..')
        return last_line[-1]
    return 0

def get_videos():
    directory_files = os.listdir()
    has_changed = True
    while (has_changed):
        has_changed = False
        for file in directory_files:
            if len(file.split('__')) == 6:
                original = file
                directory_files.remove(file)
                has_changed = True
                break
            elif not (file.endswith('.mp4') or file.endswith('.avi')):
                directory_files.remove(file)
                has_changed = True
                break

    return original, directory_files

def make_folders_for_video():
    if not os.path.exists('all_data_psnr'):
        os.mkdir('all_data_psnr')
    if not os.path.exists('results_psnr'):
        os.mkdir('results_psnr')
    if not os.path.exists("all_data_xpsnr"):
        os.mkdir("all_data_xpsnr")
    if not os.path.exists("results_xpsnr"):
        os.mkdir("results_xpsnr")

def clear_csv_files():
    if not os.path.exists('results_psnr'):
        return 
    os.chdir('results_psnr')
    if not os.path.exists('profiling'):
        os.chdir('..')
        return
    os.chdir('profiling')
    if os.path.exists('Full_PSNR_profiling.csv'):
        os.remove('Full_PSNR_profiling.csv')
    
    os.chdir('..\\..')
    if not os.path.exists('results_xpsnr'):
        return 
    os.chdir('results_xpsnr')
    if not os.path.exists('profiling'):
        os.chdir('..')
        return
    os.chdir('profiling')
    if os.path.exists('Full_XPSNR_profiling.csv'):
        os.remove('Full_XPSNR_profiling.csv')
    os.chdir('..\\..')

def calculate_full_profiling_average(type):
    folder = 'results_' + type +'\\profiling'
    os.chdir(folder)
    average = 0
    with open('full_' + type + '_profiling.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        average = 0
        rows = list(reader)
        del rows[0]
        for row in rows:
            if len(row) > 0:
                average += float(row[-1])
        average /= len(rows)
    with open('full_' + type + '_profiling.csv', 'a') as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
        writer.writerow(['Average', '' , '', average])

    os.chdir('..\\..')

def profiling_precentage_xpsnr_functions():
    time_list = {}
    os.chdir('results_xpsnr\\profiling')
    with open('full_xpsnr_profiling.csv', 'r', newline='') as csvfile:
        reader = csv.reader(csvfile, quoting=csv.QUOTE_ALL)
        for row in reader:
            if row == []:
                continue 
            if row[0] == 'file name' or row[0] == 'Average':
                continue
            file_name = row[0].split('.')[0]
            diff = row[3]
            time_list[file_name] = float(diff)
    new_file_rows = []
    header_row = []
    header_row.append('file name')
    with open('xpsnr_functions_profiling.csv', 'r', newline='') as csvfile:
        reader = csv.reader(csvfile, quoting=csv.QUOTE_ALL)
        for row in reader:
            if row[0] == 'file name':
                for i in range(1, len(row)):
                    name = row[i].split(" ")[0].split("['")[1]
                    header_row.append(name)
                new_file_rows.append(header_row)
                continue
            video_row = [row[0].split('.')[0]]
            video_name = video_row[0]
            for i in range(1, len(row)):
                time  = float(row[i].split('[')[1].split(',')[0])
                counter = float(row[i].split('[')[1].split(',')[1].split(']')[0])
                video_row.append(str(time * counter / time_list[video_name] * 100) + '%')
            new_file_rows.append(video_row)
    with open('functions_profiling_percentage.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
        writer.writerows(new_file_rows)
    os.chdir('..\\..')