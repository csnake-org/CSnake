#ifndef DUMMYTEST_H
#define DUMMYTEST_H

#include "DummyClass.h"

#include "CISTIBToolkit.h"
#ifndef CISTIB_TOOLKIT_FOLDER
#error CISTIB_TOOLKIT_FOLDER is not defined. Problem with the CreateHeader csnake method.
#endif

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
