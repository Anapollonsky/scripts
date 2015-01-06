#include <iostream>
#include "./rapidxml-1.13/rapidxml.hpp"
#include "./rapidxml-1.13/rapidxml_print.hpp"
#include "./rapidxml-1.13/rapidxml_utils.hpp"
// #include "zlib.h"
// #include "zconf.h"
// #include <sys/syscall.h>

using namespace std;




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

