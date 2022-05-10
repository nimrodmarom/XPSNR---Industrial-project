import os
import matplotlib.pyplot as plt
from PIL import Image
from functions_for_script import *

def handle_video(video_name: str):
    """ Create for a video_name 2 folders - all_data and results """
    os.chdir("{0}".format(video_name)) 
    print(os.getcwd()) #TODO: Delete - helps for debugging

    if not os.path.exists('all_data_psnr'):
        os.mkdir('all_data_psnr')
    if not os.path.exists('results_psnr'):
        os.mkdir('results_psnr')
    if not os.path.exists("all_data_xpsnr"):
        os.mkdir("all_data_xpsnr")
    if not os.path.exists("results_xpsnr"):
        os.mkdir("results_xpsnr")
    directory_files = os.listdir()
    original = ''
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
    if len(directory_files) == 0:
        os.chdir("..")
        return
    current_folder = os.getcwd()
    for file in directory_files:
        # make directory all_data
        all_data_name = 'all_data_' + file.split('.')[0] + '.txt'
        result_name = 'results_' + file.split('.')[0] + '.txt'
        os.system("docker run -v \"{0}:/data/orig\" -v \"{0}:/data/comp\" -v \"{0}\\all_data_psnr:/data/frame_out\" ffmpeg_docker:1_xpsnr -i \"/data/orig/{1}\" -i \"/data/comp/{2}\" -lavfi psnr=stats_file=\"/data/frame_out/{3}\" -f null - > results_psnr\\{4} 2>&1".format(current_folder, original, file , all_data_name, result_name))
        os.system("docker run -v \"{0}:/data/orig\" -v \"{0}:/data/comp\" -v \"{0}\\all_data_xpsnr:/data/frame_out\" ffmpeg_docker:1_xpsnr -i \"/data/orig/{1}\" -i \"/data/comp/{2}\" -lavfi xpsnr=stats_file=\"/data/frame_out/{3}\" -f null - > results_xpsnr\\{4} 2>&1".format(current_folder, original, file , all_data_name, result_name))
        os.chdir("results_psnr")
        # change psnr files
        psnr_averge_value = 0
        bit_rate_value = 0
        with open(result_name, 'r') as result_file:
            # find the 2nd line which start with word "Duration"
            bit_rate_line = ""                
            found_first = False
            # copy result file to result_file_temp
            result_file_temp = result_file.readlines()
            for line in result_file_temp:
                line = line.strip()
                if line.startswith("Duration"):
                    if found_first:
                        bit_rate_line = line
                        break
                    else:
                        found_first = True
            last_line = result_file_temp[-1].split(' ')
            
            for i in range(len(last_line)):
                if last_line[i].split(':')[0] == 'average':
                    psnr_averge_value = last_line[i].split(':')[1]
                    break
            bit_rate_line = bit_rate_line.split(', ')
            for i in range(len(bit_rate_line)):
                if bit_rate_line[i].split(': ')[0] == 'bitrate':
                    bit_rate_value = bit_rate_line[i].split(': ')[1].split(' ')[0]
                    break
        with open(result_name, 'w') as result:
            result.write("bitrate: {0}".format(bit_rate_value))
            result.write("\nPSNR average: {0}".format(psnr_averge_value))
        last_index = result_name.index('.')
        new_result_name = result_name[0 : last_index] + '__{0}.txt'.format(bit_rate_value)
        if (os.path.exists(new_result_name)):
            os.remove(new_result_name)
        os.rename(result_name, new_result_name)  
        # change XPSNR files      

        os.chdir("..\\results_xpsnr")
        xpsnr_averge_value = 0
        bit_rate_value = 0
        with open(result_name, 'r') as result_file:
            # find the 2nd line which start with word "Duration"
            bit_rate_line = ""                
            found_first = False
            # copy result file to result_file_temp
            result_file_temp = result_file.readlines()
            for line in result_file_temp:
                line = line.strip()
                if line.startswith("Duration"):
                    if found_first:
                        bit_rate_line = line
                        break
                    else:
                        found_first = True
            last_line = result_file_temp[-1].split(' ')
            
            xpsnr_averge_value = calculate_average_of_all_frames(file_name=all_data_name)
            bit_rate_line = bit_rate_line.split(', ')
            for i in range(len(bit_rate_line)):
                if bit_rate_line[i].split(': ')[0] == 'bitrate':
                    bit_rate_value = bit_rate_line[i].split(': ')[1].split(' ')[0]
                    break
        with open(result_name, 'w') as result:
            result.write("bitrate: {0}".format(bit_rate_value))
            result.write("\nXPSNR average: {0}".format(xpsnr_averge_value))
        last_index = result_name.index('.')
        new_result_name = result_name[0 : last_index] + '__{0}.txt'.format(bit_rate_value)
        if (os.path.exists(new_result_name)):
            os.remove(new_result_name)
        os.rename(result_name, new_result_name)  

        os.chdir("..")

    os.chdir("..")

def create_graph(video_name: str, different_codecs: str):
    """ create graph for video_name"""
    """ different_codecs is True if there are different VERSIONS of codecs in the video, otherwise it is the same codec with different extension """
    os.chdir(video_name)
    # remove graph if exists
    if os.path.exists('{0}_graph.png'.format(video_name)):
        os.remove('{0}_graph.png'.format(video_name))
    os.chdir("results_psnr")
    
    all_codecs = []
    legend_title = 'Different codecs'
    for file in os.listdir():
        if not (file.endswith('.txt')):
            continue
        if len(file.split('__')) == 6:
            continue
        if different_codecs:
            if file.split('__')[6] not in all_codecs:
                all_codecs.append(file.split('__')[6])
        else:
            if file.split('__')[7] not in all_codecs:
                all_codecs.append(file.split('__')[7])
                legend_title = file.split('__')[6]
    directory_files = os.listdir()

    directory_files.sort(key=lambda x: float(x.split('__')[-1].split('.')[0]))

    a_x, a_y = [], []
    b_x, b_y = [], []
    c_x, c_y = [], []
    for file in directory_files:
        file_attributes = file.split('__')
        if len(file_attributes) == 6:
            continue
        if different_codecs:
            current_codec = file.split('__')[6] 
        else:
            current_codec = file.split('__')[7]
        x_value = 0
        y_value = 0
        with open(file, 'r') as f:
            lines = f.readlines()
            x_value_line = lines[0].strip()
            y_value_line = lines[1].strip()
            x_value = float(x_value_line.split(': ')[-1])
            y_value = float( y_value_line.split(': ')[-1])
        if current_codec == all_codecs[0]:
            a_x.append(x_value)
            a_y.append(y_value)
        if len(all_codecs) >= 2 and current_codec == all_codecs[1]:
            b_x.append(x_value)
            b_y.append(y_value)
        if len(all_codecs) >= 3 and current_codec == all_codecs[2]:
            c_x.append(x_value)
            c_y.append(y_value)
    
    os.chdir ("..\\results_xpsnr")
    directory_files = os.listdir()
    directory_files.sort(key=lambda x: float(x.split('__')[-1].split('.')[0]))
    a_x_XPSNR, a_y_XPSNR = [], []
    b_x_XPSNR, b_y_XPSNR = [], []
    c_x_XPSNR, c_y_XPSNR = [], []
    for file in directory_files:
        file_attributes = file.split('__')
        if len(file_attributes) == 6:
            continue
        if different_codecs:
            current_codec = file.split('__')[6] 
        else:
            current_codec = file.split('__')[7]
        x_value = 0
        y_value = 0
        with open(file, 'r') as f:
            lines = f.readlines()
            x_value_line = lines[0].strip()
            y_value_line = lines[1].strip()
            x_value = float(x_value_line.split(': ')[-1])
            y_value = float( y_value_line.split(': ')[-1])
        if current_codec == all_codecs[0]:
            a_x_XPSNR.append(x_value)
            a_y_XPSNR.append(y_value)
        if len(all_codecs) >= 2 and current_codec == all_codecs[1]:
            b_x_XPSNR.append(x_value)
            b_y_XPSNR.append(y_value)
        if len(all_codecs) >= 3 and current_codec == all_codecs[2]:
            c_x_XPSNR.append(x_value)
            c_y_XPSNR.append(y_value)
    plt.figure()

    plt.title('{0}'.format(video_name))
    plt.xlabel('Bit rate')
    plt.ylabel('PSNR value')

    if len(all_codecs) >= 1:
        plt.plot(a_x, a_y, label = "PSNR {0} (base)".format(all_codecs[0]), color='green', linestyle='solid' , linewidth = 3,
             marker='o', markerfacecolor='red', markersize=6)
        plt.plot(a_x_XPSNR, a_y_XPSNR, label = "XPSNR {0} (base)".format(all_codecs[0]), color='green', linestyle='dashed' , linewidth = 3,
                marker='o', markerfacecolor='red', markersize=6)
    if len(all_codecs) >= 2:
        bd_rate_psnr = calculate_BD_rate(a_x, a_y, b_x, b_y)
        bd_rate_psnr = round(bd_rate_psnr, 1)
        bd_rate_xpsnr = calculate_BD_rate(a_x_XPSNR, a_y_XPSNR, b_x_XPSNR, b_y_XPSNR)
        bd_rate_xpsnr = round(bd_rate_xpsnr, 1)
        
        plt.plot(b_x, b_y, label = "PSNR {0} BD-rate: {1}".format(all_codecs[1], bd_rate_psnr), color='blue', linestyle='solid', linewidth = 3,
            marker='o', markerfacecolor='red', markersize=6)
        plt.plot(b_x_XPSNR, b_y_XPSNR, label = "XPSNR {0} BD-rate: {1}".format(all_codecs[1], bd_rate_xpsnr), color='blue', linestyle='dashed', linewidth = 3,
            marker='o', markerfacecolor='red', markersize=6)
        
    if len(all_codecs) >= 3:
        bd_rate_psnr = calculate_BD_rate(a_x, a_y, c_x, c_y)
        bd_rate_psnr = round(bd_rate_psnr, 1)
        bd_rate_xpsnr = calculate_BD_rate(a_x_XPSNR, a_y_XPSNR, c_x_XPSNR, c_y_XPSNR)
        bd_rate_xpsnr = round(bd_rate_xpsnr, 1)

        plt.plot(c_x, c_y, label = "PSNR {0} BD-rate: {1}".format(all_codecs[2], bd_rate_psnr), color='yellow', linestyle='solid', linewidth = 3,
             marker='o', markerfacecolor='red', markersize=6)
        plt.plot(c_x_XPSNR, c_y_XPSNR, label = "XPSNR {0} BD-rate: {1}".format(all_codecs[2], bd_rate_xpsnr), color='yellow', linestyle='dashed', linewidth = 3,
                marker='o', markerfacecolor='red', markersize=6)
    
    if len(all_codecs) != 0:
        plt.legend(title="{0}".format(legend_title))
    #  plt.show()
    os.chdir('..')
    plt.savefig("{0}_graph.png".format(video_name))
    plt.close()

    os.chdir('..')



def main():
    os.chdir("..\\videos")
    # move_videos_to_folders()
    # count_videos()
    
    ''' Produce the database: in each video folder'''
    # for folder_name in os.listdir():
    #     if not os.path.isdir(folder_name):
    #         continue

    #     handle_video(folder_name)

    ''' Produce the graphs for each video: '''
    for folder_name in os.listdir():
        if not os.path.isdir(folder_name):
            continue
        files_in_folder = os.listdir(folder_name)
        codec = ''
        different_codecs = False
        for video_name in files_in_folder: # check if all codecs are the same
            if not (video_name.endswith('.mp4') or video_name.endswith('.avi')):
                continue
            if len(video_name.split('__')) == 6:
                continue
            current_codec = video_name.split('__')[6]
            if codec == '':
                codec = current_codec
            else:
                if current_codec != codec:
                    different_codecs = True
                    break

        create_graph(folder_name, different_codecs)
        

    
    """ Produce the graphs for all videos to one PDF file: """
    image_lst = []
    for folder_name in os.listdir():
        if not os.path.isdir(folder_name):
            continue
        os.chdir(folder_name)
        for file in os.listdir():
            if file.endswith('.png'):
                png = Image.open(file)
                png.load()
                background = Image.new("RGB", png.size, (255, 255, 255))
                background.paste(png, mask=png.split()[3])
                image_lst.append(background)
        os.chdir("..")  
    pdf_path = os.getcwd() + '\\' + 'report.pdf'
    image_lst[0].save(pdf_path, "PDF", resoultion = 100.0, save_all=True, append_images=image_lst[1:])

if __name__ == "__main__":
    main()