import os
import json
import numpy as np
import re
from tqdm import tqdm


def analyse_sizes(directory, size_num, size_as_string):
    # List to store the sizes of the JSON files
    file_sizes = []

    # Iterate through all files in the directory
    for filename in os.listdir(directory):
        if filename.endswith(".json"):  # Check if the file is a JSON file
            file_path = os.path.join(directory, filename)

            # Get the size of the file in bytes
            file_size = os.path.getsize(file_path)

            # Append the file size to the list
            file_sizes.append(file_size)

    # Now file_sizes contains the size of all the JSON files in the specified directory
    print(file_sizes)
    print(sum(file_sizes))

    num_above = 0
    num_below = 0
    total_size_above = 0
    total_size_below = 0

    for size in file_sizes:
        if size > size_num:
            total_size_above += size
            num_above += 1
        else:
            total_size_below += size
            num_below += 1

    # Output the total size in bytes
    print(f"Total size of files above {size_as_string}: {total_size_above/size_num} * {size_as_string} across {num_above} files")
    print(f"Total size of files below {size_as_string}: {total_size_below/size_num} * {size_as_string} across {num_below} files")

    log_file_sizes = np.log1p(file_sizes)

    # # Plotting the histogram of file sizes
    # plt.figure(figsize=(10, 6))
    # plt.hist(log_file_sizes, bins=10, color='skyblue', edgecolor='black')
    #
    # # Adding titles and labels
    # plt.title("Histogram of File Sizes", fontsize=14)
    # plt.xlabel("File Size (bytes)", fontsize=12)
    # plt.ylabel("Frequency", fontsize=12)
    #
    # # Display the histogram
    # plt.show()


# Specify the directory containing JSON files
directory = r"C:\Users\semme\Desktop\test_data"  # Using raw string for Windows path
output_directory = r"C:\Users\semme\Desktop\clean_data"

size_num = 1*1024*1024
size_as_string = "MB"
analyse_sizes(directory, size_num, size_as_string)

