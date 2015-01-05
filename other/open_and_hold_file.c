#include<stdio.h>
#include<fcntl.h>
#include<unistd.h>

main(int argc, char *argv[])
{
    int result = open(argv[1], O_RDONLY);
    if (result != -1){
      printf("Opening succeeded!\n");
    } else {
      printf("Failure!\n");
    }
    fflush(stdout);
    while(1){
      sleep(1);
    }
}

