Docker__ffmpeg\ffmpeg:
    A folder for the docker.
PSNR_calculate.py:
    1. A script that runs on the folder of all the videos which contains the videos
    2. Assuming all the videos are in a folder name "videos"
    3. The video names are in format: 
        1) original video: VideoName__Resolution__subSampling__pixelDepth__FramePerSecond__totalFrames.mp4
        2) distorted video: VideoName__Resolution__subSampling__pixelDepth__FramePerSecond__totalFrames__CodecName__bitRate.mp4
    4. The script generates 2 folders for each video: 
        1) "all_data" - contains files with information of the distorted video by frame 
        2) "results" - contains conclusion of avg.PSNR and actual bit-rate of distorted video
    5. The script generates graph for each video, save in the video folder, name - "%video_name%.png"
    6. The script saves a PDF file named "report.pdf"
