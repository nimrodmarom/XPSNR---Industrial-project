from wpsnr import *

gamma = 3


class XPSNR(WPSNR):
    def __init__(self, filename, resolution, bitdepth, conv):
        super().__init__(filename, resolution, bitdepth, conv)

    def calculate_h_t(self, encoded, prev_encoded):
        if len(prev_encoded) == 0:
            return 0
        diff = 0
        for i in range(len(encoded)):
            for j in range(len(encoded[0])):
                diff += abs((int(encoded[i, j]) - int(prev_encoded[i, j])))
        return diff

    def calculate_weight_k_array(self, encoded_video, encoded, alpha_pic, beta, N, width, height, prev_encoded):
        # initialize to np array to empty
        weight_k_array = np.array([])

        prev_encoded_block = np.array([])
        for i in range(0, height, N):
            for j in range(0, width, N):
                encoded_video_block = encoded[i: i + N, j: j + N]
                if len(prev_encoded) != 0:
                    prev_encoded_block = prev_encoded[i: i + N, j: j + N]
                encoded_conv = signal.convolve2d(
                    encoded_video_block, encoded_video.conv, boundary='symm', mode='same')

                alpha_k = max((2 ** (encoded_bitdepth - 6)) ** 2,
                              ((1 / (4 * (N ** 2))) * self.calculate_h_s(encoded_conv) + gamma * self.calculate_h_t(encoded_video_block, prev_encoded_block)) ** 2)
                weight_k = (alpha_pic / alpha_k) ** beta
                weight_k_array = np.append(weight_k_array, weight_k)
        return weight_k_array


def calculate_xpsnr(original, encoded, resolution, frames, original_bitdepth, encoded_bitdepth):
    conv = [[-1, -2, -1], [-2, 12, -2], [-1, -2, -1]]
    # make conv as numpy 3x3 array
    conv = np.array(conv)

    plt.imshow(conv)

    plt.colorbar()

    original_video = XPSNR(original, resolution, original_bitdepth, conv)
    encoded_video = XPSNR(encoded, resolution, encoded_bitdepth, conv)

    MAX_VALUE = 2 ** 8 - 1

    mse_array = list()
    mse_y_array = list()
    mse_u_array = list()
    mse_v_array = list()
    i = 1

    prev_encoded_y = np.array([])

    for frame in range(frames):
        original_y, original_u, original_v = original_video.read_frame()
        encoded_y, encoded_u, encoded_v = encoded_video.read_frame()

        alpha_pic = (2 ** encoded_bitdepth) * math.sqrt(3840 *
                                                        2160 / (encoded_video.width * encoded_video.height))

        beta = 0.5
        N = round(128 * math.sqrt(encoded_video.width *
                                  encoded_video.height / (3840 * 2160)))

        weight_k_array = original_video.calculate_weight_k_array(
            encoded_video, encoded_y, alpha_pic, beta, N, encoded_video.width, encoded_video.height, prev_encoded_y)

        xpsnr_y, mse_y = original_video.wpsnr_channel(
            original_y, encoded_y, MAX_VALUE, weight_k_array, N, encoded_video.width, encoded_video.height)
        mse_y = mse_y.round(2)
        xpsnr_y = xpsnr_y.round(2)
        mse_y_array.append(mse_y)

        # N = round(128 * math.sqrt(encoded_video.u_width *
        #           encoded_video.u_height / (3840*2160)))
        # weight_k_array = calculate_wpsnr_weight_k_array(
        #    encoded_video, encoded_u, alpha_pic, beta, N, encoded_video.u_width, encoded_video.u_height)

        xpsnr_u, mse_u = original_video.wpsnr_channel(
            original_u, encoded_u, MAX_VALUE, weight_k_array, N, encoded_video.u_width, encoded_video.u_height)
        mse_u = mse_u.round(2)
        xpsnr_u = xpsnr_u.round(2)
        mse_u_array.append(mse_u)

        # N = round(128 * math.sqrt(encoded_video.v_width *
        #          encoded_video.v_height / (3840*2160)))
        # weight_k_array = calculate_wpsnr_weight_k_array(
        #    encoded_video, encoded_v, alpha_pic, beta, N, encoded_video.v_width, encoded_video.v_height)

        xpsnr_v, mse_v = original_video.wpsnr_channel(
            original_v, encoded_v, MAX_VALUE, weight_k_array, N, encoded_video.v_width, encoded_video.v_height)
        mse_v = mse_v.round(2)
        xpsnr_v = xpsnr_v.round(2)
        mse_v_array.append(mse_v)

        mse = (4 * mse_y + mse_u + mse_v) / 6  # Weighted MSE
        mse = mse.round(2)
        mse_array.append(mse)

        # np mean weight with 4,1,1
        xpsnr = (4 * xpsnr_y + xpsnr_u + xpsnr_v) / 6
        xpsnr = xpsnr.round(2)
        # print to file 'try.txt'
        os.chdir('xpsnr_values')
        with open(f'{encoded.split(".")[0]}_python_xpsnr_out.txt', 'a') as f:
            f.write(
                f'n:{i}: mse_avg:{mse} mse_y:{mse_y} mse_u:{mse_u} mse_v:{mse_v}, xpsnr_avg:{xpsnr} xpsnr_y:{xpsnr_y}, xpsnr_u:{xpsnr_u} xpsnr_v:{xpsnr_v}\n')
        os.chdir('..')

        i += 1
        prev_encoded_y = encoded_y
    # Close YUV streams
    original_video.close()
    encoded_video.close()

    # Average xpsnr between all frames
    mse_y = np.average(mse_y_array)
    xpsnr_y = 10 * np.log10((MAX_VALUE * MAX_VALUE) / mse_y)
    mse_u = np.average(mse_u_array)
    xpsnr_u = 10 * np.log10((MAX_VALUE * MAX_VALUE) / mse_u)
    mse_v = np.average(mse_v_array)
    xpsnr_v = 10 * np.log10((MAX_VALUE * MAX_VALUE) / mse_v)

    # Calculate YUV-xpsnr based on average MSE
    mse_yuv = np.average(mse_array)
    xpsnr_yuv = 10 * np.log10((MAX_VALUE * MAX_VALUE) / mse_yuv)

    return xpsnr_y, xpsnr_u, xpsnr_v, xpsnr_yuv


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
    frame_rate = int(encoded_video.split('__')[4])

    if not os.path.exists('xpsnr_values'):
        os.makedirs('xpsnr_values')

    os.chdir('xpsnr_values')
    with open(f'{encoded_video.split(".")[0]}_python_xpsnr_out.txt', 'w') as f:
        f.truncate()
    os.chdir('..')

    xpsnr_y, xpnsr_u, xpsnr_v, xpsnr_yuv = calculate_xpsnr(original_video, encoded_video, resolution,
                                                           frames, original_bitdepth, encoded_bitdepth)

    os.chdir('xpsnr_values')
    with open(f'{encoded_video.split(".")[0]}_python_xpsnr_out.txt', 'a') as f:
        f.write(f'Y-PSNR: {xpsnr_y:.4f}dB\n')
        f.write(f'U-PSNR: {xpnsr_u:.4f}dB\n')
        f.write(f'V-PSNR: {xpsnr_v:.4f}dB\n')
        f.write(f'YUV-PSNR: {xpsnr_yuv:.4f}dB\n')
    os.chdir('..')
    delete_converted_videos(original_video, encoded_video)
