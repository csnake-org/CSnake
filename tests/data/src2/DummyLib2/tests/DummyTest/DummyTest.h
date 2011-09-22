#ifndef DUMMYTEST_H
#define DUMMYTEST_H

#include "DummyClass2.h"

/**
*\brief Tests for DummyLib
*\ingroup DummyLibTests
*/
class DummyTest
{
public:

int TestOne()
{
	dummy::DummyClass2 myClass;
	if( myClass.getCount() != 10 )
	{
	   // errror
      return 1;
	}
   // all good
   return 0;
}

}; // class DummyTest

#endif //DUMMYTEST_H
