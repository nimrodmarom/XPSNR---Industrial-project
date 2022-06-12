"""
https://github.com/arthurcerveira/PSNR
"""

import numpy as np
import os


class VideoCaptureYUV(object):
    def __init__(self, filename, resolution, bitdepth):
        self.file = open(filename, 'rb')
        self.width, self.height = resolution
        self.u_width = self.width // 2
        self.v_width = self.width // 2
        self.u_height = self.height // 2
        self.v_height = self.height // 2
        self.bitdepth = bitdepth

    def read_frame(self):
        Y = self.read_channel(self.height, self.width)
        U = self.read_channel(self.u_height, self.u_width)
        V = self.read_channel(self.v_height, self.v_width)

        return Y, U, V

    def read_channel(self, height, width):
        channel_len = height * width
        shape = (height, width)

        if self.bitdepth == 8:
            raw = self.file.read(channel_len)
            channel_8bits = np.frombuffer(raw, dtype=np.uint8)
            #  channel = np.array(channel_8bits, dtype=np.uint16) << 2  # Convert 8bits to 10 bits 
            channel = channel_8bits

        elif self.bitdepth == 10:
            raw = self.file.read(2 * channel_len)  # Read 2 bytes for every pixel
            channel = np.frombuffer(raw, dtype=np.uint16)

        channel = channel.reshape(shape)

        return channel

    def close(self):
        self.file.close()


def psnr_channel(original, encoded, resolution : tuple, MAX_VALUE : int):
    # Convert frames to double
    original = np.array(original, dtype=np.double)
    encoded = np.array(encoded, dtype=np.double)

    # Calculate mean squared error
    mse = np.mean((original - encoded) ** 2)
    # PSNR in dB
    psnr = 10 * np.log10((MAX_VALUE * MAX_VALUE) / mse)
    return psnr, mse


def calculate_psnr(original, encoded, resolution, frames, original_bitdepth, encoded_bitdepth):
    original_video = VideoCaptureYUV(original, resolution, original_bitdepth)
    encoded_video = VideoCaptureYUV(encoded, resolution, encoded_bitdepth)
    
    MAX_VALUE  = 2 ** 8 - 1

    psnr_y_array = list()
    psnr_u_array = list()
    psnr_v_array = list()
    mse_array = list()
    i = 1
    for frame in range(frames):
        original_y, original_u, original_v = original_video.read_frame()
        encoded_y, encoded_u, encoded_v = encoded_video.read_frame()

        psnr_y, mse_y = psnr_channel(original_y, encoded_y, resolution, MAX_VALUE)
        mse_y = mse_y.round(2)
        psnr_y = psnr_y.round(2)
        psnr_y_array.append(psnr_y)

        psnr_u, mse_u = psnr_channel(original_u, encoded_u, resolution, MAX_VALUE)
        mse_u = mse_u.round(2)
        psnr_u = psnr_u.round(2)
        psnr_u_array.append(psnr_u)


        psnr_v, mse_v = psnr_channel(original_v, encoded_v, resolution, MAX_VALUE)
        mse_v = mse_v.round(2)
        psnr_v = psnr_v.round(2)
        psnr_v_array.append(psnr_v)
        
        mse = (4 * mse_y + mse_u + mse_v) / 6  # Weighted MSE
        mse = mse.round(2)
        mse_array.append(mse)

        # np mean weight with 4,1,1
        psnr = (4 * psnr_y + psnr_u + psnr_v) / 6
        psnr = psnr.round(2)
        # print to file 'try.txt'
        with open('try.txt', 'a') as f:
            f.write (f'n:{i}: mse_avg:{mse} mse_y:{mse_y} mse_u:{mse_u} mse_v:{mse_v}, psnr_avg:{psnr} psnr_y:{psnr_y}, psnr_u:{psnr_u} psnr_v:{psnr_v}\n')


        
        i += 1
    # Close YUV streams
    original_video.close()
    encoded_video.close()

    # Average PSNR between all frames
    psnr_y = np.average(psnr_y_array)
    psnr_u = np.average(psnr_u_array)
    psnr_v = np.average(psnr_v_array)

    # Calculate YUV-PSNR based on average MSE
    mse_yuv = np.average(mse_array)
    psnr_yuv = 10 * np.log10((MAX_VALUE * MAX_VALUE) / mse_yuv)

    return psnr_y, psnr_u, psnr_v, psnr_yuv

def covert_videos_to_yuv(video_original, video_distorted):
    """
    Convert videos to YUV format
    """
    yuv_original_video = video_original.split('.')[0] + '.yuv'
    yuv_distorted_video = video_distorted.split('.')[0] + '.yuv'
    os.system(f"ffmpeg -i {video_original} {yuv_original_video}")
    os.system(f"ffmpeg -i {video_distorted} {yuv_distorted_video}")

def delete_converted_videos(original_video, encoded_video):
    """
    Delete converted videos
    """
    yuv_original_video = original_video.split('.')[0] + '.yuv'
    yuv_encoded_video = encoded_video.split('.')[0] + '.yuv'
    os.remove(yuv_original_video)
    os.remove(yuv_encoded_video)

if __name__ == "__main__":
    os.chdir('..\\videos\\AC4BF')
    original_video = 'AC4BF__1920x1080__420__8__60__300.y4m'
    encoded_video = 'AC4BF__1920x1080__420__8__60__300__aom__ll_gaming__500.y4m'
    covert_videos_to_yuv(original_video, encoded_video)
    original_video = original_video.split('.')[0] + '.yuv'
    encoded_video = encoded_video.split('.')[0] + '.yuv'

    resolution = original_video.split('__')[1].split('x')
    resolution = (int(resolution[0]), int(resolution[1]))
    frames = int(encoded_video.split('__')[5])
    original_bitdepth = int(original_video.split('__')[3])
    encoded_bitdepth = int(encoded_video.split('__')[3])
    # resolution = (1920, 1080)
    # frames = 5
    # original_bitdepth, encoded_bitdepth = 8, 8


    psnr_y, pnsr_u, psnr_v, psnr_yuv = calculate_psnr(
        original_video, encoded_video, resolution, 
        frames, original_bitdepth, encoded_bitdepth
    )
    with open('try.txt', 'a') as f:
        f.write(f'Y-PSNR: {psnr_y:.4f}dB\n')
        f.write(f'U-PSNR: {pnsr_u:.4f}dB\n')
        f.write(f'V-PSNR: {psnr_v:.4f}dB\n')
        f.write(f'YUV-PSNR: {psnr_yuv:.4f}\ndB')

    delete_converted_videos(original_video, encoded_video)