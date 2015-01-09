#include <iostream>
#include "./rapidxml/rapidxml.hpp"
#include "./rapidxml/rapidxml_print.hpp"
#include "./rapidxml/rapidxml_utils.hpp"
// #include "zlib.h"
// #include "zconf.h"
// #include <sys/syscall.h>

using namespace std;

// Example:  /vobs/linuxrru/usl/fd_rrh_ca1/i2cfd_rrh_ca1/i2c_bci.c:222
UINT8 filter_records_buffer[FILTER_RECORD_LENGTH];
memset(filter_records_buffer, 0, sizeof(filter_records_buffer));
filter_eeprom_read(0, 0, CONFIG_SYS_FILTER_EEPROM_SIZE, filter_records_buffer);
char filename[]="/tmp/rxadc.bin"; // /vobs/rru/ral/sacapt/SACapture.cc:300

// from int SACapture::writeBufferToFile(char *filename, UINT32 nSamples)
// /vobs/rru/ral/sacapt/SACapture.cc:251
int writeBufferToFile(char *filename, UINT8 buffer, UINT8 buffer_entries){
    FILE *fp;
    UINT32 readBytes, bufLength, size;
    size = sizeof(UINT8);
//    bufLEngth = size
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

void traverse_xml(void) {
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
}



int main(int argc, char *argv[]) {
    // FILE *input = fopen("records.xml.gz", "gz");
    
    
    traverse_xml();    
    return 0;
}

