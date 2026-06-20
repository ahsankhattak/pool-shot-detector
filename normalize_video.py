import subprocess
import os
import imageio_ffmpeg

INPUT_VIDEO = 'data/input_videos/match1.mp4'
OUTPUT_VIDEO = 'data/input_videos/standard_input.mp4'


def normalize_video(input_path, output_path):
    if not os.path.exists(input_path):
        print(f"❌ Input video not found at: {os.path.abspath(input_path)}")
        return False

    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
    print(f"Using ffmpeg at: {ffmpeg_path}")

    cmd = [
        ffmpeg_path, '-y',
        '-i', input_path,
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        output_path
    ]

    print("Running FFmpeg normalization...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print("❌ FFmpeg failed:")
        print(result.stderr)
        return False

    print(f"✅ Normalized video saved to: {output_path}")
    return True


if __name__ == '__main__':
    normalize_video(INPUT_VIDEO, OUTPUT_VIDEO)