UINT8 get_filter_hwid(void) 
{
    UINT16 regvalue = 0;
    UINT8 hwid = 0; 
    regvalue = readFpgaRegister(DAS_REGISTER);
    hwid = ((regvalue >> 10) & 0x1F);
    return hwid;
}

UINT8 get_slotid(void) 
{
    UINT16 regvalue = 0;
    UINT8 slotid = 0; 
    regvalue = readFpgaRegister(DAS_REGISTER);
    slotid = ((regvalue >> 7) & 0x1);
    return slotid;
}

UINT16 readDasRegister()
{
    return readFpgaRegister(DAS_REGISTER);
}
