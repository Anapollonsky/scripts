#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

/******************************************************************************
 *  Name:  FE_readFileToBuffer
 *  Description: Reads from a given file for the entire length of the file to a given buffer.
 *  Returns: 0 if successful, -1 otherwise.
 ******************************************************************************/
/* int readFileToBuffer (char *fname, unsigned char *wrbuffer) { */
/*     FILE *fp = fopen(fname, "r"); */
/*     if (fp == NULL) */
/*     { */
/*         printf("cannot open the file %s\n", fname); */
/*         return -1; */
/*     }     */
/*     if (fseek(fp, 0L, SEEK_END) == 0) { */
/*         int bufsize = ftell(fp); */
/*         fseek(fp, 0L, SEEK_SET); */
/*         if (fread(wrbuffer, sizeof(unsigned char), bufsize, fp) == 0){ */
/*             printf("Error reading file %s\n", fname); */
/* 	    return -1 */
/*         } */
/*     } */
/*     fclose(fp); */
/*     return 0; */
/* } */

int print_hexdump_line(char *buffer, int offset, int len, int absoffset){
    printf("%08x | ", absoffset - (absoffset % 16));
    
    for (int i = 0; i < offset; i++){
	printf("  ");
	if (i % 2 == 1) printf(" ");
    }
    for (int i = offset; i < len + offset; i++){
	printf("%02x", *(buffer + (i - offset)));
	if (i % 2 == 1) printf(" ");
    }
    for (int i = len + offset; i < 16; i++){
	printf("  ");
	if (i % 2 == 1) printf(" ");
    }
    
    printf(" | ");
    for (int i = 0; i < offset; i++){
	printf(" ");
    }    
    for (int i = offset; i < len + offset; i++){
	if (isprint(*(buffer + (i - offset)))){
	    printf("%c", *(buffer + (i - offset)));
	} else {
	    printf("%c", '.');
	}
    }
    for (int i = len + offset; i < 16; i++){
	printf(" ");
    }    
    printf("\n"); 
} 

int print_hexdump(char *buffer, int offset, int len){
    int lineiter = offset % 16;
    int linelen = 0;
    int lineoff = 0;
    int lineabsoffset = 0;
	
    while (len > 0){
	lineoff = lineiter % 16;
	if (len > 16 - lineoff) {
	    linelen = 16 - lineoff;
	} else {
	    linelen = len;
	}
	lineabsoffset = (lineiter + offset - offset % 16) - (lineiter + offset - offset % 16) % 16;
	print_hexdump_line(buffer + lineiter - (offset%16), lineoff, linelen, lineabsoffset);
	lineiter += linelen;
	len -= linelen;
    }
    return 0;
}

int main (int argc, char *argv[]) {


    char buf[25]="This is a very big deal";
    print_hexdump(buf, 15, 23);

    /* char buf[25]="This is a"; */
    /* print_hexdump(buf, 10, 10); */
}
