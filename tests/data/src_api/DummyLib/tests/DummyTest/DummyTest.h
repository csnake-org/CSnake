#ifndef DUMMYTEST_H
#define DUMMYTEST_H

#include "DummyClass.h"

#include "ToolkitHeader.h"
#ifndef TESTTK_FOLDER
#error CreateHeader did not define the test *_FOLDER variable.
#endif
#ifndef TESTTK_BUILD_FOLDER
#error CreateHeader did not define the test *_BUILD_FOLDER variable.
#endif
#ifndef TESTTK_ANSWER_TO_LIFE_THE_UNIVERSE_AND_EVERYTHING
#error CreateHeader did not define the test variable.
#endif
#if TESTTK_ANSWER_TO_LIFE_THE_UNIVERSE_AND_EVERYTHING != 42
#error The test variable does not have the good value.
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
