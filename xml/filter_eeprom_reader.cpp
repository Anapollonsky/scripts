#include <iostream>
#include <string>
#include <stdio.h>
#include <stdlib.h>
#include "./rapidxml/rapidxml.hpp"
#include "./rapidxml/rapidxml_print.hpp"
#include "./rapidxml/rapidxml_utils.hpp"
// #include "zlib.h"
// #include "zconf.h"
// #include <sys/syscall.h>

#include "i2c_eeprom.c"

using namespace std;

// Example:  /vobs/linuxrru/usl/fd_rrh_ca1/i2cfd_rrh_ca1/i2c_bci.c:222
UINT8 filter_records_buffer[FILTER_RECORD_LENGTH];
memset(filter_records_buffer, 0, sizeof(filter_records_buffer));

if (!filter_eeprom_read(0, 0, CONFIG_SYS_FILTER_EEPROM_SIZE, filter_records_buffer)){
    _ERR("Reading filter eeprom contents failed.");
    return ERROR;
}
char filename[]="/tmp/rxadc.bin"; // /vobs/rru/ral/sacapt/SACapture.cc:300

char* fname = "eeprom_filter_records.xml.gz";

if (!writeBufferToFile(fname, filter_records_buffer, CONFIG_SYS_FILTER_EEPROM_SIZE)){
    _ERR("Writing filter record file failed.");
    return ERROR;
}
    

// from int SACapture::writeBufferToFile(char *filename, UINT32 nSamples)
// /vobs/rru/ral/sacapt/SACapture.cc:251
int writeBufferToFile(char *filename, UINT8 buffer, UINT8 buffer_entries){
    FILE *fp;
    UINT32 readBytes, bufLength, size;
    size = sizeof(UINT8);
    fp = fopen(filename, "wb");
    if (fp == NULL)
    {
        _ERR("cannot open the file %s\n", filename);
        return ERROR;
    }    
    bci_printf("outputfile is %s, fp is 0x%08x\n", filename, (unsigned int)fp);    
    readBytes = 0;
    while (readBytes < bufLength)
    {
            bci_printf("copying and writing %d bytes\n", bufLength - readBytes);
            fwrite(buffer, size, (bufLength - readBytes) / size, fp);
            readBytes += (bufLength - readBytes);
    }    
    fclose(fp);
    return OK;
}

// http://stackoverflow.com/questions/8465006/how-to-concatenate-2-strings-in-c
int command_unzip(char *filename){
    char *precommand = "gunzip ";
    char *command = (char*)malloc(strlen(precommand) + strlen(filename) + 1);
    if (command != NULL){
	strncpy(command, precommand);
	strncat(command, filename);
    } else {
	_ERR("cannot allocate memory for gunzip command.\n");
	return ERROR;
    }
    if (system(&command) == ERROR){
	_ERR("Ungzipping system call failed.");
	return ERROR;
    }
    return OK;
}

int parse_xml(void) {
    rapidxml::file<> xmlFile("records.xml");
    rapidxml::xml_document<> doc;
    doc.parse<rapidxml::parse_declaration_node | rapidxml::parse_no_data_nodes>(xmlFile.data());
    rapidxml::xml_node<>* records = doc.first_node("records");
    rapidxml::xml_node<>* record = records->first_node("record");
    while (record != NULL) { 
        cout << "id:" << record->first_attribute("id")->value() << endl;
	rapidxml::xml_node<>* sing_data = record->first_node("sing_data");
	rapidxml::xml_node<>* sing_datum = sing_data->first_node("sing_datum");
	while (sing_datum != NULL) {
	    cout << "datum: " << sing_datum->value() << endl;
	    sing_datum = sing_datum -> next_sibling("sing_datum");
	}
        rapidxml::xml_node<>* axes = record->first_node("axes");
        rapidxml::xml_node<>* axis = axes->first_node("axis");
        while (axis != NULL) {
            cout << "axis name: " << axis->first_attribute("name")->value() << endl;
            rapidxml::xml_node<>* entry = axis -> first_node("entry");
            while (entry != NULL) {
                cout << "entry: " << entry->value() << endl;
                entry = entry -> next_sibling("entry");
            }
            axis = axis -> next_sibling("axis");
        }
        record = record->next_sibling("record");
    }
    return OK;
}



int main(int argc, char *argv[]) {
    // FILE *input = fopen("records.xml.gz", "gz");
    
    
    parse_xml();    
    return 0;
}

