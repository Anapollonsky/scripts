/*
 * =====================================================================================
 *
 *       Filename:  i2c_filter_eeprom.h
 *
 *    Description:  header interface to access filter eeprom for DAS board
 *
 *        Version:  1.0
 *        Created:  1/14/15 12:18:32
 *       Revision:  none
 *       Compiler:  gcc
 *
 *         Author:  Andrew Apollonsky (2833 3689), Andrew.Apollonsky@Alcatel-Lucent.com
 *        Company:  Alcatel-Lucent 
 *
 * =====================================================================================
 */


#ifndef _USL_RFH_FILTER_EEPROM_
#define _USL_RFH_FILTER_EEPROM_


#ifdef __cplusplus
extern "C" {
#endif

/* function prototypes  */
INT32 filter_eeprom_read(INT32 eeprom_id, UINT32 offset, UINT32 cnt, UINT8 *buffer);
INT32 filter_eeprom_write(INT32 eeprom_id, UINT32 offset, UINT32 cnt, UINT8 *buffer);

#ifdef __cplusplus
}
#endif    
