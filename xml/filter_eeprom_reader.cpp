#include <iostream>
#include <string>
#include <stdio.h>
#include <stdlib.h>
#include "./rapidxml-1.13/rapidxml.hpp"
#include "./rapidxml-1.13/rapidxml_print.hpp"
#include "./rapidxml-1.13/rapidxml_utils.hpp"

// #include "i2c_eeprom.c"

using namespace std;

// Example:  /vobs/linuxrru/usl/fd_rrh_ca1/i2cfd_rrh_ca1/i2c_bci.c:222
UINT8 filter_records_buffer[FILTER_RECORD_LENGTH];
memset(filter_records_buffer, 0, sizeof(filter_records_buffer));

int FE_readFilterEepromToBuffer(UINT8 buffer){
    char fname[] = "eeprom_filter_records.xml.gz";  // /vobs/rru/ral/sacapt/SACapture.cc:300

    UINT8 filter_records_buffer[FILTER_RECORD_LENGTH];
    memset(filter_records_buffer, 0, sizeof(filter_records_buffer));

    int rcode = filter_eeprom_read(0, 0, CONFIG_SYS_FILTER_EEPROM_SIZE, filter_records_buffer);
    
    if (rcode != OK){
	_ERR("Reading filter eeprom contents failed.");
	return ERROR;
    }

    rcode = FE_writeBufferToFile(fname, filter_records_buffer, CONFIG_SYS_FILTER_EEPROM_SIZE);
    if (rcode != OK){
	_ERR("Writing filter record file failed.");
	return ERROR;
    }

    rcode = FE_command_unzip(fname);
    
}
    

// from int SACapture::writeBufferToFile(char *filename, UINT32 nSamples)
// /vobs/rru/ral/sacapt/SACapture.cc:251
int FE_writeBufferToFile(char *filename, UINT8 buffer, UINT8 buffer_entries){
    UINT32 readBytes, bufLength, size;
    size = sizeof(UINT8);
    buflength = size * buffer_entries;
    FILE *fp = fopen(filename, "wb");
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

// /vobs/linuxrru/usl/fd_rrh_ca1/rs485fd_rrh_ca1/ampAccess.cc:4164
int FE_readFileToBuffer (char *filename, UINT8 *buffer, INT32 filesize) {
    UINT32 rc;
    FILE *fp = fopen(filename, "r");
    if (fp == NULL)
    {
        _ERR("cannot open the file %s\n", filename);
        return ERROR;
    }    

    UINT8 *tmpBuf = bufPtr;
    while(1)
    {
	rc = fread(tmpBuf, 1, filesize, fp);
	if( rc < 0 )
	{
	    ERR("Failed to read file%s\n", filename);
	    return ERROR;
	}
	if( rc == 0 )
	    break;
 
	tmpBuf += rc;
	taskDelay(1); /* Ensure other task can be scheduled */
    }
    fclose(fp);
}

// http://stackoverflow.com/questions/8465006/how-to-concatenate-2-strings-in-c
int FE_command_unzip(char *filename){
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
        _ERR("Ungzip system call failed.");
        return ERROR;
    }
    return OK;
}

long FE_getFileSize(std::string filename)
{
    struct stat stat_buf;
    int rc = stat(filename.c_str(), &stat_buf);
    return rc == 0 ? stat_buf.st_size : -1;
}


int FE_parse_xml(void) {
    int intval;
    rapidxml::file<> xmlFile("records.xml");
    rapidxml::xml_document<> doc;
    doc.parse<rapidxml::parse_declaration_node | rapidxml::parse_no_data_nodes>(xmlFile.data());
    rapidxml::xml_node<>* records = doc.first_node("records");
    rapidxml::xml_node<>* record = records->first_node("record");
    while (record != NULL) { 
        bci_printf("id:%s\n" , record->first_attribute("id")->value());
        rapidxml::xml_node<>* sing_data = record->first_node("sing_data");
        rapidxml::xml_node<>* sing_datum = sing_data->first_node("sing_datum");
        while (sing_datum != NULL) {
            bci_printf(" datum:%s\n" , sing_datum->value());
            sing_datum = sing_datum -> next_sibling("sing_datum");
        }
        rapidxml::xml_node<>* axes = record->first_node("axes");
        rapidxml::xml_node<>* axis = axes->first_node("axis");
        while (axis != NULL) {
            bci_printf("  axis name:%s\n" , axis->first_attribute("name")->value());
            rapidxml::xml_node<>* entry = axis -> first_node("entry");
            while (entry != NULL) {
		sscanf(entry->value(), "%d", &intval);
                bci_printf("   entry: %d\n" , intval);
                entry = entry -> next_sibling("entry");
            }
            axis = axis -> next_sibling("axis");
        }
        record = record->next_sibling("record");
    }
    return 0;
}



int main(int argc, char *argv[]) {
    // FILE *input = fopen("records.xml.gz", "gz");
    
    
    FE_parse_xml();    
    return 0;
}

