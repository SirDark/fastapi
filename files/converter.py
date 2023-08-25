import time
import shutil
import sys


status = 0
while status < 100:
    time.sleep(1.5)
    status += 10
    print(str(status) + "%")
filename = (sys.argv[1].split('/')[2].split('.')[0]) + sys.argv[2]
print(sys.argv[3])
print(filename)
shutil.copy(sys.argv[1], sys.argv[3] + filename)
print("Done")

