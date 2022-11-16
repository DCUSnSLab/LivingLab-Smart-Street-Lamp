# import fcntl
# import os
# import smbus
# import time

# bus = smbus.SMBus(1)

# # i2c 통신 채널 주소
# i2c_address = 0x28
# # CDS 센서 채널 주소
# Cds_channel = 0x03

def map(x,input_min,input_max,output_min,output_max):
    return (x-input_min)*(output_max-output_min)/(input_max-input_min)+output_min

# try:
#     # fcntl.ioctl(bus, 703, 0x28)
#     while True:
#         # 송신
#         bus.write_byte(i2c_address, Cds_channel)
        
#         time.sleep(0.1)
#         a = []
        
#         # 수신
#         for i in range(0, 30):
#             a.append(bus.read_byte(i2c_address))
#             # a.append(bus.read_i2c_block_data(0x28, 713, 16))
#         time.sleep(5)
#         # humd = map(256*a[7]+a[8], 50, 990, 5, 99)
#         # temp = map(256*a[9]+a[10], 100, 1350, -40, 85)
#         print(a)
#         #print(256*a[7]+a[8], 256*a[9]+a[10])
# except KeyboardInterrupt:
#     pass

import os
import fcntl
import time

I2C_SLAVE = 0x703
sensor = 0x28

# FIFO_FILENAME = './fifo-test'

# if not os.path.exists(FIFO_FILENAME):
#     os.mkfifo(FIFO_FILENAME)
#     if os.path.exists(FIFO_FILENAME):
#     fp_fifo = open(FIFO_FILENAME, "w")

# for i in range(128):
#     fp_fifo.write("Hello,MakeCode\n")
#     fp_fifo.write("")


fd = os.open('/dev/i2c-1',os.O_RDWR)
if fd < 0 :
    print("Failed to open the i2c bus\n")
io = fcntl.ioctl(fd,I2C_SLAVE,sensor)
if io < 0 :
    print("Failed to acquire bus access/or talk to salve\n")

try:
    while True:
        data = os.read(fd,32)
        # for i in range(0, 32):
        #     print(int(data[i]), end=" ")
        # print()
        humd = map(256*data[7]+data[8], 50, 990, 5, 99)
        temp = map(256*data[9]+data[10], 100, 1350, -40, 85)
        print("co2 : ", 256*int(data[3])+int(data[4]))
        print("humidity : ", int(humd))
        print("temperature : ", int(temp))
        print("fine dust : ", 256*int(data[15])+int(data[16]))
        print("ultra fine dust : ", 256*int(data[13])+int(data[14]))
        print("-----------------------------")
        time.sleep(5)
except KeyboardInterrupt:
    os.close(fd)
