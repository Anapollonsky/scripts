/*
 * =====================================================================================
 *
 *       Filename:  i2c_filter_eeprom.c
 *
 *    Description:  interface to access filter eeprom for DAS board
 *
 *        Version:  1.0
 *        Created:  1/14/15 12:14:38
 *       Revision:  none
 *       Compiler:  gcc
 *
 *         Author:  Andrew Apollonsky (2833 3689), Andrew.Apollonsky@Alcatel-Lucent.com
 *        Company:  Alcatel-Lucent 
 *
 * =====================================================================================
 */

#include <stdio.h>
#include <unistd.h>
#include <pthread.h>

#include "i2c_u.h"
#include "i2c_log.h"
#include "uslRFHi2c.h"
#include "i2c_lib.h"
#include "i2c_hw.h"
#include "i2c_filter_eeprom.h"

/******************************************************************************
 *  Name:  filter_eeprom_read
 *
 *  Description: provide read interface to access EEPROM on filter
 *
 *  Inputs:     None
 *
 *  Outputs:    None
 *
 *  Returns:
 *
 ******************************************************************************/

INT32 filter_eeprom_read(INT32 eeprom_id, UINT32 offset, UINT32 cnt, UINT8 *buffer)
{
    unsigned end = offset + cnt;
    int rcode = 0;
    (void) eeprom_id;
    int mutex_rcode;
	
    /* avoid compiler error */
    eeprom_id = 0;
    if( (offset > CONFIG_SYS_FILTER_EEPROM_SIZE) || (offset + cnt > CONFIG_SYS_FILTER_EEPROM_SIZE) )
    {
        I2C_ERR("%s: out of range offset: 0x%x, count: 0x%x max size: 0x%x\n", __func__, offset, cnt, CONFIG_SYS_FILTER_EEPROM_SIZE);
        rcode = 1;
        return rcode;
    }

    while( offset < end )
    {
        unsigned len = 0;
        len = end - offset;
#if defined(CONFIG_SYS_I2C_FRAM)
	len = (len > 128 - offset % 128) ? 128 - offset % 128 : end - offset;
#else
	len = end - offset;
#endif

	mutex_rcode = I2CMUX_MUTEX_LOCK();
	if( mutex_rcode != 0 )
	{
	    I2C_ERR("%s: Failed to initialize i2c mutex \n", __func__);
	    return 1;
	}
	uslSetI2cMux(CONFIG_SYS_I2C_MUX_SF);
	rcode = i2c_read(CONFIG_SYS_I2C_FILTER_EEPROM_PORT, CONFIG_SYS_I2C_FILTER_EEPROM_ADDR, CONFIG_SYS_I2C_FILTER_EEPROM_ADDR_LEN, offset, len, buffer);
	uslSetI2cMux(CONFIG_SYS_I2C_MUX_DISCONNECT);
	I2CMUX_MUTEX_UNLOCK();	

	if(rcode != 0 )
	{
	    I2C_ERR("%s: i2c read from filter eeprom failed - details as follow\n", __func__);
	    I2C_ERR("---------------------------------------------------\n");
	    I2C_ERR("bus - %d\n", CONFIG_SYS_I2C_FILTER_EEPROM_PORT);
	    I2C_ERR("addr - %d\n", CONFIG_SYS_I2C_FILTER_EEPROM_ADDR);
	    I2C_ERR("addr len - %d\n", CONFIG_SYS_I2C_FILTER_EEPROM_ADDR_LEN);
	    I2C_ERR("offset - %d\n", offset);
	    I2C_ERR("length - %d\n", len);
	    I2C_ERR("---------------------------------------------------\n");
	    rcode = 1;
	    return rcode;
	}   
        buffer += len;
        offset += len;
    }
    return rcode;
}

/******************************************************************************
 *  Name:  eeprom_write_filter
 *
 *  Description:
 *
 *  Inputs:     None
 *
 *  Outputs:    None
 *
 *  Returns:
 *
 ******************************************************************************/
INT32 filter_eeprom_write(INT32 eeprom_id, UINT32 offset, UINT32 cnt, UINT8 *buffer)
{
    unsigned end = offset + cnt;
    int rcode = 0;
    (void) eeprom_id;
    int mutex_rcode;
    if( (offset > CONFIG_SYS_FILTER_EEPROM_SIZE) || (offset + cnt > CONFIG_SYS_FILTER_EEPROM_SIZE) )
    {
        I2C_ERR("%s: out of range offset: 0x%x, count: 0x%x max size: 0x%x\n", __func__, offset, cnt, CONFIG_SYS_EEPROM_SIZE);
        rcode = 1;
        return rcode;
    }

    while( offset < end )
    {
        unsigned len = 0;
        len = end - offset;
#if defined(CONFIG_SYS_I2C_FRAM)
	len = (len > 128 - offset % 128) ? 128 - offset % 128 : end - offset;
#else
	len = end - offset;
#endif

	mutex_rcode = I2CMUX_MUTEX_LOCK();
	if( mutex_rcode != 0 )
	{
	    I2C_ERR("%s: Failed to initialize i2c mutex \n", __func__);
	    return 1;
	}
	uslSetI2cMux(CONFIG_SYS_I2C_MUX_SF);		
	rcode = i2c_write(CONFIG_SYS_I2C_FILTER_EEPROM_PORT, CONFIG_SYS_I2C_FILTER_EEPROM_ADDR, CONFIG_SYS_I2C_FILTER_EEPROM_ADDR_LEN, offset, len, buffer);
	uslSetI2cMux(CONFIG_SYS_I2C_MUX_DISCONNECT);
	I2CMUX_MUTEX_UNLOCK();
		
        if(rcode != 0)
        {
            I2C_ERR("%s: write to filter eeprom failed\n", __func__);
            I2C_ERR("---------------------------------------------------\n");
            I2C_ERR("bus - %d\n", CONFIG_SYS_I2C_FILTER_EEPROM_PORT);
            I2C_ERR("addr - %d\n", CONFIG_SYS_I2C_FILTER_EEPROM_ADDR);
            I2C_ERR("addr len - %d\n", CONFIG_SYS_I2C_FILTER_EEPROM_ADDR_LEN);
            I2C_ERR("offset - %d\n", offset);
            I2C_ERR("length - %d\n", len);
            I2C_ERR("---------------------------------------------------\n");
            rcode = 1;
            return rcode;
        }

        buffer += len;
        offset += len;
    }
    return 0;
}
