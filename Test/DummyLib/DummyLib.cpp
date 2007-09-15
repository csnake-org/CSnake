#include "DummyLib.h"
#include "DummyDll.h"

int DummyLib() 
{
	return 2 * DummyDll();
}
