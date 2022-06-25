# XPSNR - Industrial Project. Nimrod Marom & Ran Braschinsky

1. PSNR_calculate.py:
   A script that creates the database of profiling, psnr/xpsnr running times and histograms as explained:

   The main function contains 7 commands to run all the features, note: some features can't be used without running previous commands.,

   1. The script assumes all the videos are in a folder name "videos"
   2. The video names are in format:
      a. original video: VideoName\_\_Resolution\_\_subSampling\_\_pixelDepth\_\_FramePerSecond\_\_totalFrames.mp4
      b. distorted video: VideoName\_\_Resolution\_\_subSampling\_\_pixelDepth\_\_FramePerSecond\_\_totalFrames\_\_CodecName\_\_bitRate.mp4

   3. The script moves all the videos and the distorted versions of them to folders, by the name of the video.
      Using the command: move_videos_to_folders()
   4. The script generates 4 folders for each video, 2 for xpsnr, 2 for psnr, for each one of them:
      a. "all_data" - contains files with information of the distorted video by frame
      b. "results" - contains conclusion of avg.PSNR/XPSNR and actual bit-rate of distorted video
      c. "profling" - a sub-folder inside results. contains 3 files which shows data for profiling for each codec.
      Using the command: produce_database()

   5. The script generates graph for each video, save in the video folder, name - "%video_name%psnr_graph.png" and "%video_name%xpsnr_graph.png"
   6. The script saves a PDF file named "report.pdf" - which contains the grahs of the results of all the videos.
      Using the command: produce_graphs()

   7. The script saves a PDF file named "histogram.pdf" - which contains a graph of running time for calculation xpsnr and psnr for each video.
      Using the command: produce_times_graph_from_dictionary(produce_database_for_times_graph)

   8. inside the first video folder, the script generates histogram of 500 running times of xpsnr and psnr, and shows how many runnings finished in
      time ranges
      Using the command: produce_time_histogram_for_specific_video()

2. psnr.py:
   A script that runs PSNR and prints the output frame by frame, and total in the video folder, in the sub-folder: "xpsnr_values"
   To runt the xpsnr on specific video, change the variables in the top of the code:
   example:
   video_name = 'Aerial_p30'
   original_video_input = 'Aerial_p30\_\_1920x1080\_\_420\_\_8\_\_30\_\_100.mp4'
   encoded_video_input = 'encoded_video_input = 'Aerial_p30\_\_1920x1080\_\_420\_\_8\_\_30\_\_100\_\_x264\_\_hq\_\_medium\_\_natural\_\_1000.mp4'
3. wpsnr.py:
   A script that runs WPSNR and prints the output frame by frame, and total in the video folder, in the sub-folder: "xpsnr_values"
   To runt the xpsnr on specific video, change the variables in the top of the code:
   example:
   video_name = 'Aerial_p30'
   original_video_input = 'Aerial_p30\_\_1920x1080\_\_420\_\_8\_\_30\_\_100.mp4'
   encoded_video_input = 'encoded_video_input = 'Aerial_p30\_\_1920x1080\_\_420\_\_8\_\_30\_\_100\_\_x264\_\_hq\_\_medium\_\_natural\_\_1000.mp4'

4. xpsnr.py:
   A script that runs XPSNR and prints the output frame by frame, and total in the video folder, in the sub-folder: "xpsnr_values"
   To runt the xpsnr on specific video, change the variables in the top of the code:
   example:
   video_name = 'Aerial_p30'
   original_video_input = 'Aerial_p30\_\_1920x1080\_\_420\_\_8\_\_30\_\_100.mp4'
   encoded_video_input = 'encoded_video_input = 'Aerial_p30\_\_1920x1080\_\_420\_\_8\_\_30\_\_100\_\_x264\_\_hq\_\_medium\_\_natural\_\_1000.mp4'

5. Docker\_\_ffmpeg\ffmpeg:
   FFMPEG Docker Submodule (from https://github.com/jrottenberg/ffmpeg)

Installations and Builds:

1. To build the docker:
   change directory using: cd .\Docker_ffmpeg\ffmpeg\docker-images\4.4\ubuntu2004\
   and run:
   $RAND_VAL=%{Get-Random} ; docker build . --build-arg DUMMY=$RAND_VAL -t ffmpeg_docker:1_xpsnr
   Then run: docker run
2. do pip install for these libaries:
   matplotlib
   numpy
   scipy
