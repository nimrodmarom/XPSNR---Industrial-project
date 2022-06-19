"""
https://github.com/arthurcerveira/PSNR
"""

import numpy as np
import os
import math


class WPSNR(object):
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

        # channel = channel.reshape(shape)

        return channel

    def close(self):
        self.file.close()

def calculate_mse(original, encoded, weight_k_array, N,  width, height):
    c = 0
    sum  = 0
    for i in range(0, width * height, N ** 2):
        diff = 0
        for j in range(i, i + N**2):
            if(j >= width * height):
                break
            diff += (original[j] - encoded[j]) ** 2
        diff *= weight_k_array[c]
        sum += diff
        c += 1
    return sum


def wpsnr_channel(original, encoded, MAX_VALUE : int, weight_k_array, N, width, height):
    # Convert frames to double
    original = np.array(original, dtype=np.double)
    encoded = np.array(encoded, dtype=np.double)

    mse = calculate_mse(original, encoded, weight_k_array, N,  width, height)
    # PSNR in dB
    psnr = 10 * np.log10((MAX_VALUE * MAX_VALUE) / mse)
    return psnr, mse

def calculate_h_k(encoded_conv):
    imx = len(encoded_conv)
    sum = 0
    for i in range(imx):
            sum += abs(encoded_conv[i])
    return sum

def calculate_wpsnr_weight_k_array(encoded_video, encoded, alpha_pic, beta, N, width, height):
    conv = [-1, -2, -1, -2, 12, -2, -1, -2, -1]
    # initialize to np array to empty
    weight_k_array = np.array([])

    for i in range(0, height * width, N ** 2):
        encoded_video_block = encoded[i : i + N ** 2]
        # encoded_cov is np.convolve of encoded_video_block and conv
        encoded_conv = np.convolve(encoded_video_block, conv)
        alpha_k = max((2 ** (encoded_bitdepth - 6)) ** 2, ((1 / ( N ** 2)) * calculate_h_k(encoded_conv)) ** 2)
        weight_k = (alpha_pic / alpha_k) ** beta
        weight_k_array = np.append(weight_k_array, weight_k)
    return weight_k_array

def calculate_wpsnr(original, encoded, resolution, frames, original_bitdepth, encoded_bitdepth):
    original_video = WPSNR(original, resolution, original_bitdepth)
    encoded_video = WPSNR(encoded, resolution, encoded_bitdepth)
    
    MAX_VALUE  = 2 ** 8 - 1

    wpsnr_y_array = list()
    wpsnr_u_array = list()
    wpsnr_v_array = list()
    mse_array = list()
    i = 1


    for frame in range(frames):
        original_y, original_u, original_v = original_video.read_frame()
        encoded_y, encoded_u, encoded_v = encoded_video.read_frame()

        alpha_pic = (2 ** encoded_bitdepth) * math.sqrt(3840 * 2160 / (encoded_video.width * encoded_video.height))

        beta = 0.5
        N = round(128 * math.sqrt(encoded_video.width * encoded_video.height / (3840 * 2160)))

        weight_k_array = calculate_wpsnr_weight_k_array(encoded_video, encoded_y, alpha_pic, beta, N, encoded_video.width, encoded_video.height)

        wpsnr_y, mse_y = wpsnr_channel(original_y, encoded_y, MAX_VALUE, weight_k_array, N, encoded_video.width, encoded_video.height)
        mse_y = mse_y.round(2)
        wpsnr_y = wpsnr_y.round(2)
        wpsnr_y_array.append(wpsnr_y)

        N = round(128 * math.sqrt(encoded_video.u_width * encoded_video.u_height / (3840*2160)))
        weight_k_array = calculate_wpsnr_weight_k_array(encoded_video, encoded_u, alpha_pic, beta, N, encoded_video.u_width, encoded_video.u_height)

        wpsnr_u, mse_u = wpsnr_channel(original_u, encoded_u, MAX_VALUE, weight_k_array, N, encoded_video.u_width, encoded_video.u_height)
        mse_u = mse_u.round(2)
        wpsnr_u = wpsnr_u.round(2)
        wpsnr_u_array.append(wpsnr_u)

        N = round(128 * math.sqrt(encoded_video.v_width * encoded_video.v_height / (3840*2160)))
        weight_k_array = calculate_wpsnr_weight_k_array(encoded_video, encoded_v, alpha_pic, beta, N, encoded_video.v_width, encoded_video.v_height)


        wpsnr_v, mse_v = wpsnr_channel(original_v, encoded_v, MAX_VALUE, weight_k_array, N, encoded_video.v_width, encoded_video.v_height)
        mse_v = mse_v.round(2)
        wpsnr_v = wpsnr_v.round(2)
        wpsnr_v_array.append(wpsnr_v)
        
        mse = (4 * mse_y + mse_u + mse_v) / 6  # Weighted MSE
        mse = mse.round(2)
        mse_array.append(mse)

        # np mean weight with 4,1,1
        wpsnr = (4 * wpsnr_y + wpsnr_u + wpsnr_v) / 6
        wpsnr = wpsnr.round(2)
        # print to file 'try.txt'
        os.chdir('wpsnr_values')
        with open(f'{encoded.split(".")[0]}_python_psnr_out.txt', 'a') as f:
            f.write (f'n:{i}: mse_avg:{mse} mse_y:{mse_y} mse_u:{mse_u} mse_v:{mse_v}, wpsnr_avg:{wpsnr} wpsnr_y:{wpsnr_y}, wpsnr_u:{wpsnr_u} wpsnr_v:{wpsnr_v}\n')
        os.chdir('..')

        
        i += 1
    # Close YUV streams
    original_video.close()
    encoded_video.close()

    # Average WPSNR between all frames
    wpsnr_y = np.average(wpsnr_y_array)
    wpsnr_u = np.average(wpsnr_u_array)
    wpsnr_v = np.average(wpsnr_v_array)

    # Calculate YUV-WPSNR based on average MSE
    mse_yuv = np.average(mse_array)
    wpsnr_yuv = 10 * np.log10((MAX_VALUE * MAX_VALUE) / mse_yuv)

    return wpsnr_y, wpsnr_u, wpsnr_v, wpsnr_yuv

def covert_videos_to_yuv(video_original, video_distorted):
    """
    Convert videos to YUV format
    """
    yuv_original_video = video_original.split('.')[0] + '.yuv'
    yuv_distorted_video = video_distorted.split('.')[0] + '.yuv'
    #os.system(f"ffmpeg -i {video_original} {yuv_original_video}")
    #os.system(f"ffmpeg -i {video_distorted} {yuv_distorted_video}")
    os.system(f"ffmpeg -i {video_original} -c:v rawvideo -pix_fmt yuv420p {yuv_original_video}")
    os.system(f"ffmpeg -i {video_distorted} -c:v rawvideo -pix_fmt yuv420p {yuv_distorted_video}")

def delete_converted_videos(original_video, encoded_video):
    """
    Delete converted videos
    """
    yuv_original_video = original_video.split('.')[0] + '.yuv'
    yuv_encoded_video = encoded_video.split('.')[0] + '.yuv'
    os.remove(yuv_original_video)
    os.remove(yuv_encoded_video)



if __name__ == "__main__":
    os.chdir('..\\videos\\Aerial_p30')
    original_video = 'Aerial_p30__1920x1080__420__8__30__100.mp4'
    encoded_video = 'Aerial_p30__1920x1080__420__8__30__100__x264__hq__medium__natural__1000.mp4'
    covert_videos_to_yuv(original_video, encoded_video)
    original_video = original_video.split('.')[0] + '.yuv'
    encoded_video = encoded_video.split('.')[0] + '.yuv'

    resolution = original_video.split('__')[1].split('x')
    resolution = (int(resolution[0]), int(resolution[1]))
    frames = int(encoded_video.split('__')[5])
    original_bitdepth = int(original_video.split('__')[3])
    encoded_bitdepth = int(encoded_video.split('__')[3])

    # resolution = (1920, 1080)
    # frames = 100
    # original_bitdepth, encoded_bitdepth = 8, 8

    if not os.path.exists('wpsnr_values'):
        os.makedirs('wpsnr_values')

    os.chdir('wpsnr_values')
    with open(f'{encoded_video.split(".")[0]}_python_psnr_out.txt', 'w') as f:
        f.truncate()
    os.chdir('..')

    wpsnr_y, wpnsr_u, wpsnr_v, wpsnr_yuv = calculate_wpsnr(
        original_video, encoded_video, resolution, 
        frames, original_bitdepth, encoded_bitdepth
    )

    os.chdir('wpsnr_values')
    with open(f'{encoded_video.split(".")[0]}_python_psnr_out.txt', 'a') as f:
        f.write(f'Y-WPSNR: {wpsnr_y:.4f}dB\n')
        f.write(f'U-WPSNR: {wpnsr_u:.4f}dB\n')
        f.write(f'V-WPSNR: {wpsnr_v:.4f}dB\n')
        f.write(f'YUV-WPSNR: {wpsnr_yuv:.4f}\ndB')
    os.chdir('..')
    delete_converted_videos(original_video, encoded_video)