// #ident "$Id: file.c,v 1.2.3 2006/08/30 17:53:53 hoser Exp $"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* char * searchBufferForString(char *buffer, int cnt, char *searchstr){ */
/*     int interim_buffer_size = 100; */
/*     int serlen = strlen(searchstr); */
/*     char *searchbuffer; */
/*     int move_size = interim_buffer_size - serlen; */
/*     int i = 0; */
/*     int k = 0; */
/*     for (i = 0; i < cnt; i += move_size){ */
/* 	searchbuffer = buffer + i; */
/* 	for (k = 0; k < move_size; k++){ */
/* 	    if (memcmp(searchbuffer+k, searchstr, serlen) == 0){ */ 
/* 	    } */
/* 	} * / 
/*     } */ 
/* } */
 


char * findident(char *buffer, int cnt) {
    char *identbegstr = "#ident \"";
    char *identendstr = "\"";
    int identbegstrlen = strlen(identbegstr);
    int identendstrlen = strlen(identendstr);
    char *beg = (char *) memmem(buffer, cnt, identbegstr, identbegstrlen);
    beg += identbegstrlen;
    char *end = (char *) memmem(beg, cnt - (int)(beg - buffer), identendstr, identendstrlen);
    int fullstrlen = (int)(end - beg);
    char *output = (char *) malloc((int)(fullstrlen) + 1);
    memcpy(output, beg, fullstrlen);
    output[fullstrlen+1] = '\0';
    return output;
}

int main(int argc, char *argv[])
{
    char *buffer = "This is a test buffer;  #ident \"Extract this!\" thesty testy";   
    printf("%s", findident(buffer, 59));
    return 0;
}
