from functions_for_script import *


def profiling_functions(type, video_name):
    os.chdir(f'results_{type}\\profiling')
    # delete csv file if exists
    if os.path.exists(f'{type}_{video_name}_functions_profiling.csv'):
        os.remove(f'{type}_{video_name}_functions_profiling.csv')
    profiling_functions_rows = []
    for file in os.listdir():
        function_dict = {}
        if file.endswith(".txt"):
            with open(file, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    line_split = line.split(': ')
                    key = line_split[0].split('******')[1]
                    data = line_split[2].split(' ')[0]
                    # data_t is a tupple of (data, count)
                    # count++ if the key is already in the dictionary
                    data_t = function_dict.get(key)
                    if data_t is None:
                        function_dict[key] = (float(data), 1)
                    else:
                        function_dict[key] = (
                            data_t[0] + float(data), data_t[1] + 1)
            file_name = file.split('profiling_')[1]
            profiling_functions_row = [file_name] + [[function_dict[key][0] /
                                                      function_dict[key][1]] + [function_dict[key][1]] for key in function_dict]
            profiling_functions_rows.append(profiling_functions_row)

            os.remove(file)
    with open(f'{type}_{video_name}_functions_profiling.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
        if os.stat(f'{type}_{video_name}_functions_profiling.csv').st_size == 0:
            writer.writerow(['file name'] + [[str(key) + ' average time'] +
                            [str(key) + ' counter'] for key in function_dict])
        writer.writerows(profiling_functions_rows)
    os.chdir('..\\..')


def calcualte_full_psnr_xpsnr_time(file: str, VQM_type: str, result_name: str, profiling_file: str, video_name: str):
    os.chdir(f'results_{VQM_type}\\profiling')
    with open(f'full_{VQM_type}_{video_name}_profiling.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
        # check if csvfile is empty:
        if os.stat(f'full_{VQM_type}_{video_name}_profiling.csv').st_size == 0:
            writer.writerow(
                ['file name', f'calculation time for {VQM_type} (secs)'])
        calculation_time = calculate_do_psnr_xpsnr(
            VQM_type=VQM_type, result_name=profiling_file)
        writer.writerow([file, calculation_time])
    os.chdir('..\\..')


def call_PSNR_XPSNR(current_folder, original, file, all_data_name, result_name):
    if not os.path.exists('results_xpsnr'):
        os.mkdir('results_xpsnr')
    os.chdir('results_xpsnr')
    if not os.path.exists('profiling'):
        os.mkdir('profiling')
    os.chdir('..')
    os.system("docker run -v \"{0}:/data/orig\" -v \"{0}:/data/comp\" -v \"{0}\\all_data_xpsnr:/data/frame_out\" ffmpeg_docker:1_xpsnr -r 30 -i \"/data/orig/{1}\" -i \"/data/comp/{2}\" -threads 1 -lavfi [0:v][1:v]xpsnr=stats_file=\"/data/frame_out/{3}\" -f null - > results_xpsnr\\{4} 2>&1".format(
        current_folder, original, file, all_data_name, result_name))

    if not os.path.exists('results_psnr'):
        os.mkdir('results_psnr')
    os.chdir('results_psnr')
    if not os.path.exists('profiling'):
        os.mkdir('profiling')
    os.chdir('..')
    os.system("docker run -v \"{0}:/data/orig\" -v \"{0}:/data/comp\" -v \"{0}\\all_data_psnr:/data/frame_out\" ffmpeg_docker:1_xpsnr -r 30 -i \"/data/orig/{1}\"  -i \"/data/comp/{2}\" -threads 1 -lavfi [0:v][1:v]psnr=stats_file=\"/data/frame_out/{3}\" -f null - > results_psnr\\{4} 2>&1".format(
        current_folder, original, file, all_data_name, result_name))


def handle_profiling(video_name):
    calculate_full_profiling_average('xpsnr', video_name)
    calculate_full_profiling_average('psnr', video_name)
    profiling_functions('psnr', video_name)
    profiling_functions('xpsnr', video_name)
    profiling_precentage_xpsnr_functions(video_name)


def calculate_XPSNR_PSNR_files(VQM_type: str, result_name: str, all_data_name: str, file: str, video_name: str):
    os.chdir('results_' + VQM_type)
    averge_value = 0
    bit_rate_value = 0
    profiling_file = 'profiling_' + result_name.split('results_')[1]
    if not os.path.exists('profiling'):
        os.mkdir('profiling')
    file_content = []
    with open(result_name, 'r') as result_file:
        # check if lines starts with '******'
        results_lines = result_file.readlines()
        os.chdir('profiling')
        with open(profiling_file, 'w') as profiling:
            profiling.truncate()
        profiling_lines = []
        for line in results_lines:
            if line.endswith('******\n') or line.endswith('******'):
                profiling_lines.append(line)
            elif not line.strip().startswith('Last message repeated'):
                file_content.append(line)
        with open(profiling_file, 'w') as profiling:
            for line in profiling_lines:
                profiling.write(line)

        os.chdir('..')

    with open(result_name, 'w') as result_file:
        result_file.truncate()
        for line in file_content:
            result_file.write(line)
    with open(result_name, 'r') as result_file:
        # find the 2nd line which start with word "Duration"
        bit_rate_line = ""
        found_first = False
        # copy result file to result_file_temp
        result_file_lines = result_file.readlines()
        for line in result_file_lines:
            line = line.strip()
            if line.startswith("Duration"):
                if found_first:
                    bit_rate_line = line
                    break
                else:
                    found_first = True

        if (VQM_type == 'xpsnr'):
            averge_value = calculate_average_of_all_frames(
                file_name=all_data_name)
        else:
            assert(VQM_type == 'psnr')
            last_line = result_file_lines[-1].split(' ')
            for i in range(len(last_line)):
                if last_line[i].split(':')[0] == 'average':
                    averge_value = last_line[i].split(':')[1]
                    break

        bit_rate_line = bit_rate_line.split(', ')
        for i in range(len(bit_rate_line)):
            if bit_rate_line[i].split(': ')[0] == 'bitrate':
                bit_rate_value = bit_rate_line[i].split(': ')[1].split(' ')[0]
                break

    last_index = result_name.index('.')
    new_result_name = result_name[0: last_index] + f'__{bit_rate_value}.txt'
    with open(new_result_name, 'w') as result:
        result.write(f'bitrate: {bit_rate_value}')
        result.write(f'\n{VQM_type} average: {averge_value}')
    os.chdir('..')
    calcualte_full_psnr_xpsnr_time(
        file, VQM_type, result_name, profiling_file, video_name)
    os.remove(f'results_{VQM_type}\\{result_name}')


def make_folders_for_video():
    if not os.path.exists('all_data_psnr'):
        os.mkdir('all_data_psnr')
    if not os.path.exists('results_psnr'):
        os.mkdir('results_psnr')
    if not os.path.exists("all_data_xpsnr"):
        os.mkdir("all_data_xpsnr")
    if not os.path.exists("results_xpsnr"):
        os.mkdir("results_xpsnr")


def handle_plot(video_name: str, VQM_type: str, all_codecs: list, a_x: list, a_y: list, b_x: list, b_y: list, c_x: list, c_y: list, legend_title: str):
    os.chdir('results_' + VQM_type)
    plt.figure()
    ax = plt.subplot(111)

    plt.title(f'{video_name} {VQM_type} Values')
    plt.xlabel('Bit Rate')
    plt.ylabel(f'{VQM_type} Value')
    line_style = 'solid'
    if (VQM_type == 'psnr'):
        line_style = 'dashed'
    if len(all_codecs) >= 1:
        plt.plot(a_x, a_y, label=f'{VQM_type} {all_codecs[0]} (base)', color='green', linestyle=line_style, linewidth=3,
                 marker='o', markerfacecolor='red', markersize=6)
    if len(all_codecs) >= 2:
        bd_rate = calculate_BD_rate(a_x, a_y, b_x, b_y)
        bd_rate = round(bd_rate, 1)

        plt.plot(b_x, b_y, label=f'{VQM_type} {all_codecs[1]} BD-rate: {bd_rate}', color='blue', linestyle=line_style, linewidth=3,
                 marker='o', markerfacecolor='red', markersize=6)

    if len(all_codecs) >= 3:
        bd_rate = calculate_BD_rate(a_x, a_y, c_x, c_y)
        bd_rate = round(bd_rate, 1)

        plt.plot(c_x, c_y, label=f'{VQM_type} {all_codecs[1]} BD-rate: {bd_rate}', color='yellow', linestyle=line_style, linewidth=3,
                 marker='o', markerfacecolor='red', markersize=6)

    if len(all_codecs) != 0:
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height *
                        0.25, box.width, box.height * 0.75])
        ax.legend(loc='upper center', bbox_to_anchor=(
            0.5, -0.16), ncol=2, title=f'{legend_title}')
    os.chdir('..')
    plt.savefig(f'{video_name} {VQM_type} graph.png')
    plt.close()


def handle_video(video_name: str):
    """ Create for a video_name 2 folders - all_data and results """
    os.chdir(f'{video_name}')
    make_folders_for_video()
    original, directory_files = get_videos()

    if len(directory_files) == 0:  # If video does not contain distorted videos
        os.chdir("..")
        return
    current_folder = os.getcwd()
    clear_csv_files()
    for file in directory_files:
        all_data_name = 'all_data_' + file.split('.')[0] + '.txt'
        result_name = 'results_' + file.split('.')[0] + '.txt'
        call_PSNR_XPSNR(current_folder, original, file,
                        all_data_name, result_name)
        calculate_XPSNR_PSNR_files("psnr", result_name=result_name,
                                   all_data_name=all_data_name, file=file, video_name=video_name)
        calculate_XPSNR_PSNR_files("xpsnr", result_name=result_name,
                                   all_data_name=all_data_name, file=file, video_name=video_name)
    handle_profiling(video_name)
    os.chdir("..")


def produce_psnr_axis(directory_files, all_codecs, different_codecs):
    a_x, a_y, b_x, b_y, c_x, c_y = [], [], [], [], [], []
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
            y_value = float(y_value_line.split(': ')[-1])
        if current_codec == all_codecs[0]:
            a_x.append(x_value)
            a_y.append(y_value)
        if len(all_codecs) >= 2 and current_codec == all_codecs[1]:
            b_x.append(x_value)
            b_y.append(y_value)
        if len(all_codecs) >= 3 and current_codec == all_codecs[2]:
            c_x.append(x_value)
            c_y.append(y_value)

    os.chdir('..')
    return a_x, a_y, b_x, b_y, c_x, c_y


def produce_xpsnr_axis(directory_files, all_codecs, different_codecs):
    os.chdir('results_xpsnr')
    directory_files = os.listdir()
    # remove folders from directory_files
    for file in directory_files:
        if os.path.isdir(file):
            directory_files.remove(file)
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
            y_value = float(y_value_line.split(': ')[-1])
        if current_codec == all_codecs[0]:
            a_x_XPSNR.append(x_value)
            a_y_XPSNR.append(y_value)
        if len(all_codecs) >= 2 and current_codec == all_codecs[1]:
            b_x_XPSNR.append(x_value)
            b_y_XPSNR.append(y_value)
        if len(all_codecs) >= 3 and current_codec == all_codecs[2]:
            c_x_XPSNR.append(x_value)
            c_y_XPSNR.append(y_value)
    os.chdir('..')
    return a_x_XPSNR, a_y_XPSNR, b_x_XPSNR, b_y_XPSNR, c_x_XPSNR, c_y_XPSNR


def create_graph(video_name: str, different_codecs: str):
    """ create graph for video_name"""
    """ different_codecs is True if there are different VERSIONS of codecs in the video, otherwise it is the same codec with different extension """
    os.chdir(video_name)
    # remove graph if exists
    if os.path.exists(f'{video_name}_graph.png'):
        os.remove(f'{video_name}_graph.png')
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
    # remove folders from directory_files
    for file in directory_files:
        if os.path.isdir(file):
            directory_files.remove(file)
    directory_files.sort(key=lambda x: float(x.split('__')[-1].split('.')[0]))

    a_x, a_y, b_x, b_y, c_x, c_y = produce_psnr_axis(
        directory_files, all_codecs, different_codecs)
    a_x_XPSNR, a_y_XPSNR, b_x_XPSNR, b_y_XPSNR, c_x_XPSNR, c_y_XPSNR = produce_xpsnr_axis(
        directory_files, all_codecs, different_codecs)

    handle_plot(video_name, "xpsnr", all_codecs, a_x_XPSNR, a_y_XPSNR,
                b_x_XPSNR, b_y_XPSNR, c_x_XPSNR, c_y_XPSNR, legend_title)
    handle_plot(video_name, "psnr", all_codecs, a_x,
                a_y, b_x, b_y, c_x, c_y, legend_title)
    os.chdir('..')


def produce_database():
    os.chdir("videos")
    for folder_name in os.listdir():
        print(os.getcwd())
        if not os.path.isdir(folder_name):
            continue
        handle_video(folder_name)

    os.chdir("..")


def produce_database_for_times_graph():
    os.chdir("videos")

    running_xpsnr_times, running_psnr_times = {}, {}
    for folder_name in os.listdir():
        if not os.path.isdir(folder_name):
            continue
        running_xpsnr_times[folder_name] = []
        running_psnr_times[folder_name] = []
        for i in range(3):
            handle_video(folder_name)
            os.chdir(folder_name)
            running_xpsnr_times[folder_name].append(
                float(get_time_from_file(folder_name, 'results_xpsnr', 'xpsnr')))
            running_psnr_times[folder_name].append(
                float(get_time_from_file(folder_name, 'results_psnr', 'psnr')))
            os.chdir('..')

    os.chdir("..")
    return running_xpsnr_times, running_psnr_times


def produce_graphs():
    os.chdir("videos")
    for folder_name in os.listdir():
        if not os.path.isdir(folder_name):
            continue
        files_in_folder = os.listdir(folder_name)
        codec = ''
        different_codecs = False
        for video_name in files_in_folder:  # check if all codecs are the same
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

    produce_PDF()
    os.chdir("..")


def produce_PDF():
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
    pdf_path = os.getcwd() + '\\' + 'xpsnr_psnr_results.pdf'
    image_lst[0].save(pdf_path, "PDF", resoultion=100.0,
                      save_all=True, append_images=image_lst[1:])


def produce_time_histogram_for_specific_video():
    os.chdir("videos")
    # get all the dirs in the videos folder
    dirs = os.listdir()

    os.chdir(dirs[0])
    original, directory_files = get_videos()
    test_video = directory_files[0]
    current_folder = os.getcwd()
    all_data_name = 'temp_data.txt'
    result_name = 'temp_result.txt'
    produce_time_histogram("psnr", current_folder, original,
                           test_video, all_data_name, result_name)
    produce_time_histogram("xpsnr", current_folder,
                           original, test_video, all_data_name, result_name)

    os.chdir("..")


def produce_times_graph_from_dictionary(running_xpsnr_times, running_psnr_times):
    os.chdir("videos")
    plt.style.use('seaborn-deep')
    psnr_times = []
    xpsnr_times = []
    video_names = running_xpsnr_times

    index = 0
    for folder_name in os.listdir():  # all videos
        if not os.path.isdir(folder_name):
            continue
        psnr_value = min(running_psnr_times[folder_name])
        xpsnr_value = min(running_xpsnr_times[folder_name])
        psnr_times.append(float(psnr_value))
        xpsnr_times.append(float(xpsnr_value))

    N = len(psnr_times)

    # make tupple out of psnr_times and xpsnr_times until N / 2
    psnr_times_tuple = tuple(psnr_times[:int(N)])
    xpsnr_times_tuple = tuple(xpsnr_times[:int(N)])

    ind = np.arange(N)  # the x locations for the groups
    width = 0.3       # the width of the bars

    fig, ax = plt.subplots()
    ax.bar(ind, psnr_times_tuple, width, color='purple')
    # add text for each each one of i bars str(xpsnr_times_tuple[i] / psnr_times_tuple[i]
    # for i in range(len(psnr_times_tuple)):
    #     ax.text(i, psnr_times_tuple[i], str(xpsnr_times_tuple[i] / psnr_times_tuple[i]),
    #             ha='center', va='bottom')

    ax.bar(ind + width, xpsnr_times_tuple, width, color='orange')

    ax.set_ylabel('Time (s)')
    ax.set_xlabel('# Video')
    ax.set_title('Calculation time for each video')
    ax.set_xticks(ind + width / 2)
    index_list = [i for i in range(1, N + 1)]
    ax.set_xticklabels(index_list)
    handles = [mpl_patches.Rectangle((0, 0), 1, 1, fc="white", ec="white",
                                     lw=0, alpha=0)] * (N + 3)

    video_names_list = []
    video_names_list.append('Orange: XPSNR')
    video_names_list.append('Purple: PSNR')
    video_names_list.append(' ')

    index = 0
    for key in video_names.keys():
        index += 1
        # add to video_names_list the video name and the index
        # get average of list lst
        ratio = round(
            min(running_xpsnr_times[key]) / min(running_psnr_times[key]), 2)

        video_names_list.append(
            f'{index}: {key} |      xpsnr/psnr time-ratio: {ratio}')

    ax.legend(handles, video_names_list, fontsize='small',
              fancybox=False, framealpha=0.7, bbox_to_anchor=(1, 1), loc='upper left', borderaxespad=0,
              handlelength=0, handletextpad=0)
    # save as pdf
    plt.savefig('xpsnr_psnr_running_times.pdf', bbox_inches='tight')

    os.chdir("..")


# def produce_histogram():
#     os.chdir("videos")
#     plt.style.use('seaborn-deep')
#     psnr_times = []
#     xpsnr_times = []
#     video_names = {}
#     index = 0
#     for folder_name in os.listdir():  # all videos
#         if not os.path.isdir(folder_name):
#             continue

#         os.chdir(folder_name)  # inside a video folder
#         for sub_folder in os.listdir():
#             if os.path.isdir(sub_folder):
#                 if sub_folder == 'results_psnr':
#                     psnr_value = get_time_from_file(
#                         folder_name, sub_folder, 'psnr')
#                     if (psnr_value != -1):
#                         index += 1
#                         video_names[index] = folder_name
#                         psnr_times.append(float(psnr_value))
#                 if sub_folder == 'results_xpsnr':
#                     xpsnr_value = get_time_from_file(
#                         folder_name, sub_folder, 'xpsnr')
#                     if (xpsnr_value != -1):
#                         xpsnr_times.append(float(xpsnr_value))
#         os.chdir('..')

#     N = index
#     # make tupple out of psnr_times and xpsnr_times until N / 2
#     psnr_times_tuple = tuple(psnr_times[:int(N)])
#     xpsnr_times_tuple = tuple(xpsnr_times[:int(N)])

#     ind = np.arange(N)  # the x locations for the groups
#     width = 0.3       # the width of the bars

#     fig, ax = plt.subplots()
#     ax.bar(ind, psnr_times_tuple, width, color='purple')

#     ax.bar(ind + width, xpsnr_times_tuple, width, color='orange')

#     ax.set_ylabel('Time (s)')
#     ax.set_xlabel('# Video')
#     ax.set_title('Calculation time for each video')
#     ax.set_xticks(ind + width / 2)
#     ax.set_xticklabels(video_names.keys())
#     handles = [mpl_patches.Rectangle((0, 0), 1, 1, fc="white", ec="white",
#                                      lw=0, alpha=0)] * (N + 3)

#     video_names_list = []
#     video_names_list.append('Orange: XPSNR')
#     video_names_list.append('Purple: PSNR')
#     video_names_list.append(' ')

#     index = 0
#     for key in video_names.keys():
#         index += 1
#         # add to video_names_list the video name and the index
#         video_names_list.append(f'{index}: {video_names[key]}')

#     ax.legend(handles, video_names_list, fontsize='small',
#               fancybox=False, framealpha=0.7, bbox_to_anchor=(1, 1), loc='upper left', borderaxespad=0,
#               handlelength=0, handletextpad=0)
#     # save as pdf
#     plt.savefig('histogram.pdf', bbox_inches='tight')

#     os.chdir("..")


def main():

    os.chdir("..")

    # move_videos_to_folders()

    produce_database()

    produce_graphs()

    produce_times_graph_from_dictionary(produce_database_for_times_graph)

    produce_time_histogram_for_specific_video()


if __name__ == "__main__":
    main()
