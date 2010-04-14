#!/usr/bin/python
import re
import getopt
import sys

# Faking test creation the same way CxxTests does

def main():
    '''Main entry.'''
    print "cxxtestgen fake cpp generation."
    # parse options
    try:
        options, patterns = getopt.getopt( sys.argv[1:], 'o:r:',
                                     ['version', 'output=', 'runner=', 'gui=',
                                      'error-printer', 'abort-on-fail', 'have-std', 'no-std',
                                      'have-eh', 'no-eh', 'template=', 'include=',
                                      'root', 'part', 'no-static-init', 'factor', 'longlong='] )
    except getopt.error:
        raise Exception("Error parsing input options.")

    # get the output file name
    outputFileName = None
    for o, a in options:
        if o in ('-o', '--output'):
            outputFileName = a
    if outputFileName == None:
        raise Exception("Cannot find the output file name.")

    # read input file
    if len(patterns) == 0:
        raise Exception("Cannot find the input file name.")
    inputFileName = patterns[0]
    inputFile = open( inputFileName )
    suite_re = re.compile( r'\bclass\s+(\w+)\b' )
    test_re = re.compile( r'^([^/]|/[^/])*\bint\s+([Tt]est\w+)\s*\(\s*(void)?\s*\)' )
    className = None
    testName = None
    while 1:
        line = inputFile.readline(80)
        if not line:
            break
        res = suite_re.search( line )
        if res:
            className = res.group(1)
        res = test_re.search( line )
        if res:
            testName = res.group(2)
    inputFile.close()

    # check read names
    if className == None:
        raise Exception("Cannot find the class name.")
    if testName == None:
        raise Exception("Cannot find the test name.")
    
    # write output file
    outputFile = open( outputFileName, 'w' )
    outputFile.write("// main: entry point for dummy tests.\n")
    outputFile.write("#include \"%s\"\n" % inputFileName)
    outputFile.write("int main( int argc, char** argv)\n")
    outputFile.write("{\n")
    outputFile.write("    %s test = %s();\n" % (className, className) )
    outputFile.write("    return test.%s();\n" % testName)
    outputFile.write("}\n")
    outputFile.write("\n")
    outputFile.close()
         
if __name__ == "__main__":
    main() 
