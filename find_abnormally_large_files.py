import os
import sys


def find_large_files_in_subdirs(directory: str, percentage: float) -> None:
    for root, _, files in os.walk(directory):
        file_sizes = []
        file_paths = []

        # Collect sizes and paths of all files in the current directory
        for file in files:
            file_path = os.path.join(root, file)
            file_size = os.path.getsize(file_path)
            file_sizes.append(file_size)
            file_paths.append(file_path)

        if not file_sizes:
            continue

        # Calculate average file size in the current directory
        average_size = sum(file_sizes) / len(file_sizes)
        threshold = average_size * (1 + percentage / 100)

        # Identify and print files larger than the threshold
        large_files = [
            file_paths[i] for i, size in enumerate(file_sizes) if size > threshold
        ]

        if large_files:
            print(f"\nIn directory: {root}")
            print(f"Files larger than {percentage}% of the average size:")
            for file in large_files:
                print(file)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python find_abnormally_large_files.py <directory> <percentage>")
        sys.exit(1)

    input_directory = sys.argv[1]
    percentage_larger = float(sys.argv[2])

    find_large_files_in_subdirs(input_directory, percentage_larger)
