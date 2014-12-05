#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      James
#
# Created:     05/12/2014
# Copyright:   (c) James 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import os, string

def main():
    workbench_path = os.path.join(r'C:\Users\James\Documents\etlondemand', 'Exercise3Complete.fmw')
    with open(workbench_path) as f:
        for line in f.readlines():
            if string.count(line, "LOG_FILENAME \""):
                if '$(FME_MF_DIR)' in line:
                    print line.split(' ')[-1].replace('$(FME_MF_DIR)', r'c:\test\\')
                else:
                    print line.split(' ')[-1]

if __name__ == '__main__':
    main()
