from moviepy import VideoFileClip, concatenate_videoclips
import numpy as np
import sys
import matplotlib.pyplot as plt

SHOW_VISUAL = True

AUDIO_FPS = 44100 / 2
CLIP_BLANK_SEC_START = 1
CLIP_BLANK_SEC_END = 0.5
MIN_CLIP_SEC = 1.5

def calculate_volume(clip):
    print("Calculating audio volume...")
    audio = clip.audio.to_soundarray(fps=AUDIO_FPS)
    vol = np.abs(audio).mean(axis=1) 

    if(SHOW_VISUAL):
        t = np.arange(len(vol)) / AUDIO_FPS
        plt.plot(t, vol)
        plt.xlabel("Time (sec)")
        plt.ylabel("Volume")
        plt.show(block=False)

    return vol

def find_groups(arr, offset=1):
    arr = np.asarray(arr)
    non_zero_idx = np.where(arr != 0)[0]
    if len(non_zero_idx) == 0:
        return []

    groups = []
    start = non_zero_idx[0]
    prev = start

    for idx in non_zero_idx[1:]:
        if idx - prev > offset:
            if prev - start + 1 >= MIN_CLIP_SEC * AUDIO_FPS:
                clip_start = max(0, start / AUDIO_FPS - CLIP_BLANK_SEC_START)
                clip_end = min(len(arr) - 1, prev / AUDIO_FPS + CLIP_BLANK_SEC_END)
                groups.append((clip_start, clip_end))
            start = idx
        prev = idx
    if prev - start + 1 >= MIN_CLIP_SEC * AUDIO_FPS:
        clip_start = max(0, start / AUDIO_FPS - CLIP_BLANK_SEC_START)
        clip_end = min(len(arr) - 1, prev / AUDIO_FPS + CLIP_BLANK_SEC_END)
        groups.append((clip_start, clip_end))

    if SHOW_VISUAL:
        colors = ['red', 'green', 'blue', 'orange', 'purple', 'cyan']
        color_index = 0
        for start, end in groups:
            plt.axvspan(start, end, color=colors[color_index % len(colors)], alpha=0.3)
            plt.title("Audio Volume Over Time with Clip Groupings")
            color_index += 1
        plt.show(block=False)
    
    print(f"Found {len(groups)} groups of non-silent audio.")

    return groups

def create_clips(clip, groups):
    clips = []
    print("Creating subclips...")
    for start, end in groups:
        end = min(end, clip.duration)
        subclip = clip.subclipped(start, end)
        clips.append(subclip)
    print(f"Concatenating clips into final video...")
    final_clip = concatenate_videoclips(clips)
    return final_clip

def main():
    video_file = sys.argv[1] if len(sys.argv) > 1 else "Test.mp4"
    print(f"Processing video file: {video_file}")

    clip = VideoFileClip(video_file)

    vol_arr = calculate_volume(clip)
    max_offset = max(CLIP_BLANK_SEC_START * AUDIO_FPS, CLIP_BLANK_SEC_END * AUDIO_FPS)
    groups = find_groups(vol_arr, offset=max_offset)

    if SHOW_VISUAL:
        exit_choice = input("Insert q to quit, or any other key to continue: ")
        plt.close('all')
        if exit_choice.lower() == 'q':
            exit(0)

    print("Creating output video...")
    final_clip = create_clips(clip, groups)
    output_name = video_file.rsplit('.', 1)[0] + "_edited.mp4"
    final_clip.write_videofile(output_name, codec="libx264", audio_codec="aac")

    final_clip.close()
    clip.close()

if __name__ == "__main__":
    main()
