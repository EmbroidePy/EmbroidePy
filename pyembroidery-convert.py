from __future__ import print_function

import sys
from pyembroidery import *

if len(sys.argv) <= 1:
    print("No command arguments")
    exit(1)
input_file = sys.argv[1]
if len(sys.argv) >= 3:
    output_file = sys.argv[2]
else:
    output_file = input_file + ".csv"
pattern = read(input_file)
write = write(pattern, output_file)
