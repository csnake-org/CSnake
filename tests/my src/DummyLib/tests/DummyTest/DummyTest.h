#ifndef DUMMYTEST_H
#define DUMMYTEST_H

#include "DummyClass.h"

/**
*\brief Tests for DummyLib
*\ingroup DummyLibTests
*/
class DummyTest
{
public:

int TestOne()
{
	dummy::DummyClass myClass;
	if( myClass.getCount() != 6 )
	{
	   // errror
      return 1;
	}
   // all good
   return 0;
}

}; // class DummyTest

#endif //DUMMYTEST_H
