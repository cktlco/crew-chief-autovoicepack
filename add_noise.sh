#!/bin/bash

input_file="$1"
output_file="$2"

# Apply Bass Cut Equalization, Pit Radio Equalization, Trim Silence, and Normalize in a single chain
sox -V1 -q "$input_file" -n \
  equalizer 100 0.5q -12 equalizer 200 0.5q -6 equalizer 300 0.5q -3 \
  equalizer 3000 0.5q 12 equalizer 6000 0.5q 9 equalizer 12000 0.5q 6 \
  silence 1 0.1 1% -1 2.0 1% \
  norm \
  remix - \
  trim 0 $(soxi -D "$input_file") \
  : newfile : restart \
  gain -h \
  rate -v 44100 \
  $output_file

echo "Processing complete."
