import numpy
import math
import os
import re

def covert_videos_to_yuv(video_original, video_distorted):
    """
    Convert videos to YUV format
    """
    yuv_original_video = video_original.split('.')[0] + '.yuv'
    yuv_distorted_video = video_distorted.split('.')[0] + '.yuv'
    os.system(f"ffmpeg -i {video_original} {yuv_original_video}")
    os.system(f"ffmpeg -i {video_distorted} {yuv_distorted_video}")

def psnr(img1, img2):
    mse = numpy.mean( (img1 - img2) ** 2 )
    if mse == 0:
        return 100
    PIXEL_MAX = 255.0
    return 20 * math.log10(PIXEL_MAX / math.sqrt(mse))

def img_read_yuv(src_file, width, height):
    y_img = numpy.fromfile(src_file, dtype=numpy.uint8, count=(width * height)).reshape( (height, width) )
    u_img = numpy.fromfile(src_file, dtype=numpy.uint8, count=(int(width/2) * int(height/2))).reshape(int(height/2), int(width/2))
    v_img = numpy.fromfile(src_file, dtype=numpy.uint8, count=(int(width/2) * int(height/2))).reshape( int(height/2), int(width/2) )
    return (y_img, u_img, v_img)

def main():
    os.chdir('..\\videos\\BarScene_p30')
    ref_file = 'BarScene_p30__1920x1080__420__8__30__300.yuv'
    dist_file  = 'BarScene_p30__1920x1080__420__8__30__300__x264__hq_slow_natural__500.yuv'
    #covert_videos_to_yuv(ref_file, dist_file)
    m = re.search(r"(\d+)x(\d+)", ref_file)

    width, height = int(m.group(1)), int(m.group(2))
    print ("Comparing %s to %s, resolution %d x %d" % (ref_file, dist_file, width, height))

    ref_fh = open(ref_file, "rb")
    dist_fh = open(dist_file, "rb")

    frame_num = 0
    while True:
        ref, _, _ = img_read_yuv(ref_fh, width, height)
        dist, _, _ = img_read_yuv(dist_fh, width, height)
        psnr_value = psnr(ref, dist)
        print ("Frame=%d PSNR=%f " % (frame_num, psnr_value))
        frame_num += 1

if __name__ == "__main__":
    main()