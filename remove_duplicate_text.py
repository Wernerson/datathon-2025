import json
import time

from datasketch import MinHash, MinHashLSH
import mmh3
from collections import OrderedDict
import os
from multiprocessing import Pool

from vector_ingest import segment_pages
from vector_ingest import load_documents
from vector_ingest import load_files



def save_json_data(data, file_path):
    """Save data to JSON file with pretty formatting"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def dedupe_json_values(data, new_file_path, window_size=500,shift_size=250, threshold=0.9):
    """
    Main processing function:
    1. Loads JSON dictionary from file
    2. Removes duplicate sequences across all values
    3. Saves cleaned dictionary to new file
    """
    # Load original data
    data_dict = data['text_by_page_url']
    if not isinstance(data_dict, dict):
        raise ValueError("JSON data must be a dictionary")

    # Process the data
    clean_start = time.time()
    cleaned_data_dict = dedupe_dict_values(data_dict, window_size,shift_size, threshold)
    clean_end = time.time()
    print(f"clean time: {clean_end - clean_start}")
    data['text_by_page_url'] = cleaned_data_dict
    # Save results
    save_json_data(data, new_file_path)
    print(f"Successfully processed and saved to {new_file_path}")


def dedupe_dict_values(data_dict, window_size=500, shift_size=250, threshold=0.9):
    """
    Processes a dictionary to remove duplicate sequences across all values.
    Returns a new dictionary with duplicates removed from values.
    """
    # Combine all values with boundary markers
    # combined_text, value_map = _combine_values(data_dict)

    # Find duplicate windows across entire text
    duplicates = _find_cross_value_duplicates(
        data_dict=data_dict,
        window_size=window_size,
        shift_size=shift_size,
        threshold=threshold
    )

    # Rebuild dictionary with duplicates removed
    return _rebuild_dict(data_dict, duplicates)


# def _combine_values(data_dict):
#     """Concatenates values with unique separators"""
#     combined = []
#     value_positions = {}
#     current_pos = 0
#
#     for key, value in data_dict.items():
#         # Add separator that won't appear in normal text
#         separator = f"␞{key}␞"
#         combined.append(separator)
#         current_pos += len(separator)
#
#         # Record value's position range
#         value_positions[key] = (current_pos, current_pos + len(value))
#         combined.append(value)
#         current_pos += len(value)
#
#     return ''.join(combined), value_positions


def _remove_batch_duplicates(windows,duplicates,lsh,window_size):
    for window_key, values in windows.items():
        duplicates[window_key] = []
        for pos, mh in values:
            matches = lsh.query(mh)
            if len(matches) > 1:
                for key_match_pos in matches:
                    match_key, match_pos = str(key_match_pos).split("^", 1)
                    # print(f"key: {window_key}, match_key: {match_key}, pos: {pos}, match_pos: {match_pos}")
                    match_pos = int(match_pos)  # Convert back to int
                    if match_pos != pos:
                        if match_key == window_key:  # Same document duplicate
                            start = max(pos, match_pos)
                            end = max(start, min(pos + window_size, match_pos + window_size))
                        else:  # Cross-document duplicate
                            start = pos
                            end = pos + window_size

                        # Add as tuple and avoid duplicates
                        if (start, end) not in duplicates[window_key]:
                            duplicates[window_key].append((start, end))

                        # Sort immediately after collection
                    duplicates[window_key].sort(key=lambda x: x[0])


def _find_cross_value_duplicates(data_dict, window_size,shift_size, threshold):
    """Identifies duplicate windows across entire text"""
    lsh = MinHashLSH(threshold=threshold, num_perm=128)
    windows = {}

    duplicates = {}
    count_len = 0
    max_thresh = 1000000
    total_len = 0

    for key, text in data_dict.items():
        count_len+=len(text)
        windows[key]=[]
        new_text = ""
        for i in range(0, len(text) - window_size + 1, shift_size):
            window = text[i:i + window_size]
            mh = MinHash(num_perm=128)

            # Process each shingle
            for j in range(0, len(window) - 5 + 1):
                shingle = window[j:j + 5]
                # Convert to bytes and hash
                mh.update(shingle.encode('utf-8'))  # Directly pass bytes

            lsh.insert(key+"^"+str(i), mh)  # Use string as key
            windows[key].append((i, mh))
        if count_len > max_thresh:
            total_len += count_len
            print(f"{total_len} characters processed")
            count_len = 0
        #
        #     _remove_batch_duplicates(windows,duplicates,lsh,window_size)
        #     lsh = MinHashLSH(threshold=threshold, num_perm=128)
        #     windows = {}
        #
        #     duplicates = {}
    _remove_batch_duplicates(windows, duplicates, lsh, window_size)

    return duplicates


def _rebuild_dict(original_dict, duplicates_dict):
    new_dict = {}

    for key, text in original_dict.items():
        # print(key)
        if not duplicates_dict.get(key):
            new_dict[key] = original_dict[key]
            continue

        # Build list of keep ranges (inverse of duplicates)
        keep_ranges = []
        last_end = 0
        for start, end in duplicates_dict[key]:
            # print(f"start: {start}, end: {end}")
            if start > last_end:
                keep_ranges.append((last_end, start))
                # print(f"key: {key} start: {last_end}, end: {start}, next_end: {end}")
            last_end = end
        # print("done")
        if last_end < len(text):
            keep_ranges.append((last_end, len(text)))

        # Rebuild clean text
        # clean_text = ''
        # start_per = 0
        # end_per = 0
        # for start, end in keep_ranges:
        #
        #     clean_text = clean_text.join(text[start:end])

        clean_text = ''.join(text[start:end] for start, end in keep_ranges)
        new_dict[key]=clean_text
    return new_dict


def process_file(args):
    filename, orig_file_path, new_file_path = args
    if filename.endswith('.json'):
        file_path = os.path.join(orig_file_path, filename)
        doc = load_documents(file_path)
        dedupe_json_values(
            data=doc,
            new_file_path=f"{new_file_path}/{filename}",
            window_size=100,
            shift_size=50,
            threshold=0.8
        )



def main(parallel=False):

    orig_file_path = "./../data/hackathon_data"
    # orig_file_path = "./../data/test_data"
    new_file_path = "./../data/rd_data"

    files_in_folder = load_files(orig_file_path)
    if parallel:
        with Pool() as pool:
            args = [(filename, orig_file_path, new_file_path) for filename in files_in_folder[:10]]
            pool.map(process_file, args)
    else:
        for file_index, filename in enumerate(files_in_folder[:2]):
            print(f"Processing {filename}...")
            args = (filename,orig_file_path,new_file_path)
            process_file(args)


if __name__ == "__main__":
    main(parallel=True)