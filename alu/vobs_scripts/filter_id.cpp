UINT32 DAS_MODE_REG = 0x000A;

UINT8 getFilterHWID(void)
{
    UINT16 regvalue = 0;
    UINT8 hwid = 0;
    regvalue = readFpgaRegister(DAS_MODE_REG);
    hwid = ((regvalue >> 10) && 0x001F)
    return hwid
}

void printFilterHWID(void)
{
    if ((HwId == HWID_CU_LOW_BAND_DAS) || (HwId == HWID_CU_HIGH_BAND_DAS))
    {
	UINT8 id = getFilterHWID();
	bci_printf("Filter HWID = 0x%x\n", id);
    } else {
	bci_printf("Error: Not a DAS Project.");
    }
}

// void bsp_bci_fpga_read(void)
// 	{
// 		UINT32 offset = 0;
// 		UINT32 value = 0;
// 		char *bcioption = NULL;

// 		bcioption = bci_read_option() ;   
// 		if(NULL == bcioption)
// 		{
// 			bsp_bci_fpga_read_usage();
// 			return;
// 		}     

// 	    if((!sscanf(bcioption,"0x%x", &offset)))
// 		{
// 			bsp_bci_fpga_read_usage();
// 			return;       
// 		}         

// 		bci_printf("FPGA read from offset(0x%04x)\n", offset);
//         value = readFpgaRegister(offset);
// 		bci_printf("FPGA value = 0x%04x\n", value);
//     }

// UINT8 uslGetHwId(void)
// {
//     UINT8 hwId;
    
//     hwId =  (bsp_u_Get_GPIO_Dat(0, GPIO_HWID_BIT_4) << 4) |
//             (bsp_u_Get_GPIO_Dat(0, GPIO_HWID_BIT_3) << 3) |
//             (bsp_u_Get_GPIO_Dat(0, GPIO_HWID_BIT_2) << 2) |
//             (bsp_u_Get_GPIO_Dat(0, GPIO_HWID_BIT_1) << 1) |
//             (bsp_u_Get_GPIO_Dat(0, GPIO_HWID_BIT_0) << 0) ;

//     return hwId;
// }
