"""
https://github.com/arthurcerveira/PSNR
"""

import numpy as np
import os


class PSNR(object):
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
            # Read 2 bytes for every pixel
            raw = self.file.read(2 * channel_len)
            channel = np.frombuffer(raw, dtype=np.uint16)

        channel = channel.reshape(shape)

        return channel

    def close(self):
        self.file.close()

    def psnr_channel(self, original, encoded, resolution: tuple, MAX_VALUE: int):
        # Convert frames to double
        original = np.array(original, dtype=np.double)
        encoded = np.array(encoded, dtype=np.double)

        # Calculate mean squared error
        mse = np.mean((original - encoded) ** 2)
        # PSNR in dB
        psnr = 10 * np.log10((MAX_VALUE * MAX_VALUE) / mse)
        return psnr, mse


def calculate_psnr(original, encoded, resolution, frames, original_bitdepth, encoded_bitdepth):
    original_video = PSNR(original, resolution, original_bitdepth)
    encoded_video = PSNR(encoded, resolution, encoded_bitdepth)

    MAX_VALUE = 2 ** 8 - 1

    mse_y_array = list()
    mse_u_array = list()
    mse_v_array = list()
    mse_array = list()
    i = 1
    for frame in range(frames):
        original_y, original_u, original_v = original_video.read_frame()

        encoded_y, encoded_u, encoded_v = encoded_video.read_frame()

        psnr_y, mse_y = original_video.psnr_channel(
            original_y, encoded_y, resolution, MAX_VALUE)
        mse_y = mse_y.round(2)
        psnr_y = psnr_y.round(2)
        mse_y_array.append(mse_y)

        psnr_u, mse_u = original_video.psnr_channel(
            original_u, encoded_u, resolution, MAX_VALUE)
        mse_u = mse_u.round(2)
        psnr_u = psnr_u.round(2)
        mse_u_array.append(mse_u)

        psnr_v, mse_v = original_video.psnr_channel(
            original_v, encoded_v, resolution, MAX_VALUE)
        mse_v = mse_v.round(2)
        psnr_v = psnr_v.round(2)
        mse_v_array.append(mse_v)

        mse = (4 * mse_y + mse_u + mse_v) / 6  # Weighted MSE
        mse = mse.round(2)
        mse_array.append(mse)

        # np mean weight with 4,1,1
        psnr = (4 * psnr_y + psnr_u + psnr_v) / 6
        psnr = psnr.round(2)
        # print to file 'try.txt'
        os.chdir('psnr_values')
        with open(f'{encoded.split(".")[0]}_python_psnr_out.txt', 'a') as f:
            f.write(
                f'n:{i}: mse_avg:{mse} mse_y:{mse_y} mse_u:{mse_u} mse_v:{mse_v}, psnr_avg:{psnr} psnr_y:{psnr_y}, psnr_u:{psnr_u} psnr_v:{psnr_v}\n')
        os.chdir('..')

        i += 1
    # Close YUV streams
    original_video.close()
    encoded_video.close()

    # Average PSNR between all frames
    mse_y = np.average(mse_y_array)
    psnr_y = 10 * np.log10((MAX_VALUE * MAX_VALUE) / mse_y)
    mse_u = np.average(mse_u_array)
    psnr_u = 10 * np.log10((MAX_VALUE * MAX_VALUE) / mse_u)
    mse_v = np.average(mse_v_array)
    psnr_v = 10 * np.log10((MAX_VALUE * MAX_VALUE) / mse_v)

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
    #os.system(f"ffmpeg -i {video_original} {yuv_original_video}")
    #os.system(f"ffmpeg -i {video_distorted} {yuv_distorted_video}")
    os.system(
        f"ffmpeg -i {video_original} -c:v rawvideo -pix_fmt yuv420p {yuv_original_video}")
    os.system(
        f"ffmpeg -i {video_distorted} -c:v rawvideo -pix_fmt yuv420p {yuv_distorted_video}")


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

    if not os.path.exists('psnr_values'):
        os.makedirs('psnr_values')

    os.chdir('psnr_values')
    with open(f'{encoded_video.split(".")[0]}_python_psnr_out.txt', 'w') as f:
        f.truncate()
    os.chdir('..')

    psnr_y, pnsr_u, psnr_v, psnr_yuv = calculate_psnr(
        original_video, encoded_video, resolution,
        frames, original_bitdepth, encoded_bitdepth
    )

    os.chdir('psnr_values')
    with open(f'{encoded_video.split(".")[0]}_python_psnr_out.txt', 'a') as f:
        f.write(f'Y-PSNR: {psnr_y:.4f}dB\n')
        f.write(f'U-PSNR: {pnsr_u:.4f}dB\n')
        f.write(f'V-PSNR: {psnr_v:.4f}dB\n')
        f.write(f'YUV-PSNR: {psnr_yuv:.4f}dB\n')
    os.chdir('..')
    delete_converted_videos(original_video, encoded_video)
