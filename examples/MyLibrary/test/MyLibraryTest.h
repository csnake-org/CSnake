#ifndef MYLIBRARYTEST_H
#define MYLIBRARYTEST_H

// Copyright 2007 Pompeu Fabra University (Computational Imaging Laboratory), Barcelona, Spain. Web: www.cilab.upf.edu.
// This software is distributed WITHOUT ANY WARRANTY; 
// without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

#include "cxxtest/TestSuite.h"
#include "MyLibrary.h"

class MyLibraryTest : public CxxTest::TestSuite 
{
public:
	void TestMyLibrary()
	{
		TS_ASSERT_EQUALS(123, MyLibrary());
	}
};

#endif //MYLIBRARYTEST_H
