// -*- C++ -*-
// This is the default test runner.
//

#include <cxxtest/XmlPrinter.h>

// The CxxTest "world"
<CxxTest world>

int main( int argc, char** argv )
{
    std::ofstream ofs( "test_log.xml" );
    return CxxTest::XmlPrinter( ofs ).run();
    ofs.close();
}
