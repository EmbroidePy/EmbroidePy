#!/usr/bin/env python


import re
import sys
import embroidepy

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(embroidepy.run())