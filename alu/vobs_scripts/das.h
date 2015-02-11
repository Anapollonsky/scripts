#ifndef _DAS_H_
#define _DAS_H_

#include "vxWorks.h"


class DAS {

public:
    UINT16 DAS_REGISTER

    UINT8 get_filter_hwid(void);
    UINT8 get_slotid(void);

    DAS(UINT16 DAS_REGISTER);

private:
    UINT16 = readDasRegister();
}
