#include <stdio.h>
#include <unistd.h>

int main(){
	int a=0;
	printf("test\n");
        for(a=0;a<5;a++){
		printf("test print %d\n",a);
		sleep(1);	
	}
	
	printf("sleep done\n");
	return 0;
}
