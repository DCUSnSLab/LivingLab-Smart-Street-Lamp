#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <linux/i2c-dev.h>
#include <time.h>

#define PACKETSIZE	32


int openi2c(int slave_addr) {	
	//----- OPEN THE I2C BUS -----
	char *filename = (char*)"/dev/i2c-1";
	int fd = open(filename, O_RDWR);
	if (fd < 0) { printf("Failed to open the i2c bus"); return fd; }
	
	int io = ioctl(fd, I2C_SLAVE, slave_addr);
	printf("%d %d\n", I2C_SLAVE,slave_addr);
	if ( io < 0) printf("Failed to acquire bus access and/or talk to slave.\n");
	return fd;
}

int map(x, input_min, input_max, output_min, output_max){
	int res = (x-input_min)*(output_max-output_min)/(input_max-input_min)+output_min;
	return res;
}
	
int main (int argc, char *argv[]) {
	int fd = openi2c(0x28);
	if (fd < 0) {
		printf("Error in opening i2c. fd=%d\n", fd);
		return fd;
	}
	while (1) {
		// i2c 읽어오기
		FILE *op;
		op=fopen("./rpi-rgb-led-matrix/examples-api-use/test.txt","a");
		unsigned char data[PACKETSIZE];
		int n = read(fd, data, PACKETSIZE);
		if (n!=PACKETSIZE) { // 요청한 읽기 크기와 실제 읽어 온 크기 비교
			printf("Error in reading i2c. n=%d\n", n);
			return -1;
		}

		time_t rawTime;
		struct tm* pTimeInfo;
		rawTime = time(NULL);
		pTimeInfo = localtime(&rawTime);
		int year = pTimeInfo->tm_year + 1900;
		int month = pTimeInfo->tm_mon + 1;
		
		int day = pTimeInfo->tm_mday;
		int hour = pTimeInfo->tm_hour;
		int min = pTimeInfo->tm_min;
		int sec = pTimeInfo->tm_sec;
		printf("%d-%d-%d %d:%d:%d, ", year, month, day, hour, min, sec);
		//fprintf(op, "%d:%d\n", hour, min);

		int humd = map(256*data[7]+data[8], 50, 990, 5, 99);//256*data[7]+data[8]
		int temp = map(256*data[9]+data[10], 100, 1350, -40, 85);

		// 읽어 온 값 디스플레이
		//printf("Status : %d\n", data[23]);
		//fprintf(op, "Co2 : %d, VOC : %d, humid : %d, temp : %d\n PM1.0 : %d, PM2.5 : %d, PM10 : %d\n", 256*data[3]+data[4], 256*data[5]+data[6], humd, temp, 256*data[11]+data[12], 256*data[13]+data[14], 256*data[15]+data[16]);
		//fprintf(op, "%d, %d, %d\n", 256*data[17]+data[18], 256*data[19]+data[20], 256*data[21]+data[22]);
		printf("%d, CO2, %d\nHUM, %d\nTEMP, %d\nFINE, %d\nULTRA, %d\n", data[0], 256*data[3]+data[4], humd, temp, 256*data[15]+data[16], 256*data[13]+data[14]);
		//printf("====\n%d\n%d\n====\n", data[7], data[8]);
		// for(int i = 0; i < 23; i++){
		// 	printf("%d ", data[i]);
		// }
		// printf("\n");
		fclose(op);
		sleep(5);
	}

	return 0;
}