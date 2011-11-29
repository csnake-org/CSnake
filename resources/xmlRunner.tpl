// -*- C++ -*-
// This is the default test runner.
//

#include <cxxtest/XmlPrinter.h>
#include <fstream>

// The CxxTest "world"
<CxxTest world>

/**
\brief Main method to run project tests.
\param argc The number of arguments (should be 2).
\param argv The arguments: the name of the command and the name of the xml file where to output test results. 
*/
int main( int argc, char** argv )
{
    if ( argc != 2 )
    {
        fprintf( stderr, "Usage: %s <output file name>\n", argv[0] );
        return -1;
    }
    std::ofstream ofs( argv[1] );
    const int ret = CxxTest::XmlPrinter( ofs ).run();
    ofs.close();
    return ret;
}
