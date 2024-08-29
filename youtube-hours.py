import subprocess
import re
from datetime import timedelta


# Function to run a command and return its output
def run_command(command):
    process = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    out, err = process.communicate()
    return out.decode("utf-8"), err.decode("utf-8"), process.returncode


# Replace with multiple channel IDs (e.g., UCzwLEvNi0__N9BHbgTqJKeQ, UCN_h_1w3ofp1qMgrwcnaykw)

total_durations = []
video_counts = []

channel_ids = [
    "UCzwLEvNi0__N9BHbgTqJKeQ",
    "UCN_h_1w3ofp1qMgrwcnaykw",
    "UC0JADezsbV-CWlDscvVOT3g",
]
for channel_id in channel_ids:

    command = f"yt-dlp --get-id --sleep-interval 5 --max-sleep-interval 10 --get-duration https://www.youtube.com/channel/{channel_id}"

    # Running the command
    output, error, return_code = run_command(command)

    # If there is an error, print it
    if return_code != 0:
        print(f"Error: {error}")
    else:
        # Process the output to calculate the total time
        # write 'output' variable to a file
        with open("youtube-output.txt", "w") as f:
            f.write(output)

    with open("youtube-output.txt", "r") as f:
        output = f.read()

    lines = output.strip().split("\n")
    total_duration = timedelta()
    video_count = 0

    for i in range(0, len(lines), 2):
        video_id = lines[i]
        duration_str = lines[i + 1]

        # print(f'{ i }/{(len(lines)/2) }')

        # Convert duration string to timedelta
        match = re.match(r"(\d+):(\d+):(\d+)", duration_str)
        if match:
            hours, minutes, seconds = map(int, match.groups())
            video_duration = timedelta(hours=hours, minutes=minutes, seconds=seconds)
        else:
            match = re.match(r"(\d+):(\d+)", duration_str)
            if match:
                minutes, seconds = map(int, match.groups())
                video_duration = timedelta(minutes=minutes, seconds=seconds)
            else:
                match = re.match(r"(\d+)", duration_str)
                if match:
                    seconds = int(duration_str)
                    video_duration = timedelta(seconds=seconds)
                else:
                    # If the duration is not in the expected format, skip this video
                    continue

        total_duration += video_duration
        video_count += 1
    total_durations.append(total_duration)
    video_counts.append(video_count)

    # Print the results
    total_days = total_duration.days
    total_hours = (total_duration.seconds // 3600) + (total_days * 24)
    print(f"Channel ({channel_id}):")
    print(f"Total duration: {total_duration} ({total_days} days, {total_hours} hours)")
    print(f"Video count: {video_count}")


# for i, (channel_id, total_duration, video_count) in enumerate(
#     zip(channel_ids, total_durations, video_counts)
# ):
#     print(f"Channel {i+1} ({channel_id}):")
#     print(f"Total duration: {total_duration} ({total_days} days, {total_hours} hours)")
#     print(f"Video count: {video_count}")
