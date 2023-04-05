import os
import random
import argparse

def find_matching_keys(current_key):
    camelot_wheel = {
        '1A': ['12A', '1B', '2A'],
        '1B': ['1A', '2B', '12B'],
        '2A': ['1A', '2B', '3A'],
        '2B': ['1B', '2A', '3B'],
        '3A': ['2A', '3B', '4A'],
        '3B': ['2B', '3A', '4B'],
        '4A': ['3A', '4B', '5A'],
        '4B': ['3B', '4A', '5B'],
        '5A': ['4A', '5B', '6A'],
        '5B': ['4B', '5A', '6B'],
        '6A': ['5A', '6B', '7A'],
        '6B': ['5B', '6A', '7B'],
        '7A': ['6A', '7B', '8A'],
        '7B': ['6B', '7A', '8B'],
        '8A': ['7A', '8B', '9A'],
        '8B': ['7B', '8A', '9B'],
        '9A': ['8A', '9B', '10A'],
        '9B': ['8B', '9A', '10B'],
        '10A': ['9A', '10B', '11A'],
        '10B': ['9B', '10A', '11B'],
        '11A': ['10A', '11B', '12A'],
        '11B': ['10B', '11A', '12B'],
        '12A': ['11A', '12B', '1A'],
        '12B': ['11B', '12A', '1B']
    }
    return camelot_wheel[current_key]

def find_files(folder, matching_keys, target_tempo):
    files = []
    for file in os.listdir(folder):
        key, tempo, artist, sample_type_id = file.split('-')
        sample_type, id_num = sample_type_id[:-4], sample_type_id[-3:]
        tempo_diff = abs(int(tempo) - target_tempo)

        if key in matching_keys and (tempo_diff <= 10 or int(tempo) == target_tempo * 2 or int(tempo) == target_tempo / 2):
            files.append(file)
    return files

def create_mpc_program(target_key, target_tempo):
    base_path = 'samples'
    categories = ['drums', 'bass', 'other', 'vocals']

    matching_keys = find_matching_keys(target_key)

    mpc_program = [[None, None, None, None], 
                   [None, None, None, None],
                   [None, None, None, None], 
                   [None, None, None, None]]

    for category in categories:
        folder = os.path.join(base_path, category)
        files = find_files(folder, matching_keys, target_tempo)
        if not files:
            print(f"No matching files found in {folder}")
            continue

        random_file = random.choice(files)

        if category == 'drums':
            mpc_program[2][0] = random_file
            mpc_program[3][0] = random_file
            mpc_program[2][1] = random_file
            mpc_program[3][1] = random_file
        elif category == 'bass':
            mpc_program[2][2] = random_file
            mpc_program[3][2] = random_file
            mpc_program[2][3] = random_file
            mpc_program[3][3] = random_file
        elif category == 'other':
            mpc_program[0][0] = random_file
            mpc_program[1][0] = random_file
            mpc_program[0][1] = random_file
            mpc_program[1][1] = random_file
        elif category == 'vocals':
            mpc_program[0][2] = random_file
            mpc_program[1][2] = random_file
            mpc_program[0][3] = random_file
            mpc_program[1][3] = random_file

    return mpc_program

def create_pgm_header():
    header = "Akai Program File\n" \
             "FileVersion\t3\n" \
             "Program\tName\tRandom Drum Program\n"
    return header

def create_pad_setting(pad_number, sample_path):
    pad_setting = f"Sample\t{pad_number}\t{sample_path}\n" \
                  f"Volume\t{pad_number}\t100\n" \
                  f"Pan\t{pad_number}\t0\n" \
                  f"Tune\t{pad_number}\t0\n"
    return pad_setting

def create_mpc_program_file(mpc_program, filename):
    with open(filename, 'w') as pgm:
        pgm.write(create_pgm_header())

        for i, row in enumerate(mpc_program):
            for j, sample_path in enumerate(row):
                if sample_path is not None:
                    pad_number = 1 + i * 4 + j
                    pgm.write(create_pad_setting(pad_number, sample_path))

def main():
    parser = argparse.ArgumentParser(description="Generate MPC Drum Program with random samples based on key and tempo.")
    parser.add_argument('--key', type=str, required=True, help="Target key in Camelot notation (e.g., '4A')")
    parser.add_argument('--tempo', type=int, required=True, help="Target tempo in BPM (e.g., 120)")

    args = parser.parse_args()

    target_key = args.key
    target_tempo = args.tempo

    mpc_program = create_mpc_program(target_key, target_tempo)
    create_mpc_program_file(mpc_program, "Random_Drum_Program.pgm")

if __name__ == "__main__":
    main()