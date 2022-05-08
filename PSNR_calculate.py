import os
import matplotlib.pyplot as plt
from PIL import Image

def move_videos_to_folders():
    """ Move all videos to its folder. """
    for file in os.listdir():
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
        

def handle_video(video_name: str):
    """ Create for a video_name 2 folders - all_data and results """
    #TODO: adding to reuslts the bit rate from the video ffmpeg
    os.chdir("{0}".format(video_name)) 

    if not os.path.exists("all_data"):
        os.mkdir("all_data")
    if not os.path.exists("results"):
        os.mkdir("results")
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
    os.chdir("all_data")
    if len(directory_files) == 0:
        os.chdir("..\\..")
        return
    for file in directory_files:
        # make directory all_data
        all_data_name = 'all_data_' + file.split('.')[0] + '.txt'
        result_name = 'results_' + file.split('.')[0] + '.txt'
        os.system("ffmpeg.exe -i ..\\{0} -i ..\\{1} -lavfi psnr=stats_file={2} -f null - > ..\\results\\{3} 2>&1".format(original, file, all_data_name, result_name))
        os.chdir("..\\results")
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
        os.rename(result_name, new_result_name)

        os.chdir("..\\all_data")

    os.chdir("..\\..")

def create_graph(video_name: str, different_codecs: str):
    """ create graph for video_name"""
    """ different_codecs is True if there are different VERSIONS of codecs in the video, otherwise it is the same codec with different extension """
    os.chdir(video_name)
    # remove graph if exists
    if os.path.exists('{0}_graph.png'.format(video_name)):
        os.remove('{0}_graph.png'.format(video_name))
    os.chdir("results")
    
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

    a_x_AC4BF, a_y_AC4BF = [], []
    b_x_AC4BF, b_y_AC4BF = [], []
    c_x_AC4BF, c_y_AC4BF = [], []
    title = "extention of x264 (natural)"
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
            a_x_AC4BF.append(x_value)
            a_y_AC4BF.append(y_value)
        if len(all_codecs) >= 2 and current_codec == all_codecs[1]:
            b_x_AC4BF.append(x_value)
            b_y_AC4BF.append(y_value)
        if len(all_codecs) >= 3 and current_codec == all_codecs[2]:
            c_x_AC4BF.append(x_value)
            c_y_AC4BF.append(y_value)
    
    plt.figure()

    plt.title('{0}'.format(video_name))
    plt.xlabel('Bit rate')
    plt.ylabel('PSNR value')

    if len(all_codecs) >= 1:
        plt.plot(a_x_AC4BF, a_y_AC4BF, label = "{0}".format(all_codecs[0]), color='green', linestyle='solid' , linewidth = 3,
             marker='o', markerfacecolor='red', markersize=6)
    if len(all_codecs) >= 2:
        plt.plot(b_x_AC4BF, b_y_AC4BF, label = "{0}".format(all_codecs[1]), color='blue', linestyle='solid', linewidth = 3,
            marker='o', markerfacecolor='red', markersize=6)
    if len(all_codecs) >= 3:
        plt.plot(c_x_AC4BF, c_y_AC4BF, label = "{0}".format(all_codecs[2]), color='yellow', linestyle='solid', linewidth = 3,
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
    for folder_name in os.listdir():
        if not os.path.isdir(folder_name):
            continue
        handle_video(folder_name)

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