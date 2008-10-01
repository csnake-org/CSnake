// -*- C++ -*-
// This is the default test runner.
//

//#include <cxxtest/XmlPrinter.h>
//#include <stdio.h>

// The CxxTest "world"
<CxxTest world>

int main( int argc, char** argv )
{
	return CxxTest::XmlPrinter( std::ofstream( "testLog.xml" ) ).run();
}
