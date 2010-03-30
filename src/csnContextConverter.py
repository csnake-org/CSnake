import ConfigParser
import csnContext
import sys

class Converter:
    def __init__(self, optionsFilename):
        self.section = "CSnake"
        self.optionsFilename = optionsFilename
        self.convertedOptionsFilename = optionsFilename + ".archiveFromVersion"
        
    def ConvertOptions(self):
        parserOptions = ConfigParser.ConfigParser()
        try:
            parserOptions.read([self.optionsFilename])
        except ConfigParser.ParsingError as error:
            sys.stdout.write( "Warning: %s" % error.message )
            return False
            
        versionNumber = 0.0
        if parserOptions.has_option(self.section, "version"):
            versionNumber = parserOptions.getfloat(self.section, "version")
            
        if versionNumber == 0.0:
            parserNewOptions = ConfigParser.ConfigParser()

            # rename an option within the input options file
            self.MoveOption(parserOptions, self.section, "currentguisettingsfilename", toOption = "contextfilename")
            self.MoveOption(parserOptions, self.section, "askToLaunchVisualStudio", toOption = "askToLaunchIDE")

            # move options from input options file to new options file
            self.MoveOption(parserOptions, self.section, "visualstudiopath", toParser = parserNewOptions, toOption = "idepath")
            self.MoveOption(parserOptions, self.section, "pythonpath", toParser = parserNewOptions)
            self.MoveOption(parserOptions, self.section, "cmakepath", toParser = parserNewOptions)
            self.MoveOption(parserOptions, self.section, "compiler", toParser = parserNewOptions)
            self.MoveOption(parserOptions, self.section, "cmakebuildtype", toParser = parserNewOptions,  toOption = "configurationname")
            
            parserOptions.set(self.section, "version", str(csnContext.latestFileFormatVersion))
            f = open(self.optionsFilename, 'w')
            parserOptions.write(f)
            f.close()            

            f = open(self.convertedOptionsFilename, 'w')
            parserNewOptions.write(f)
            f.close() 
            
        # all good
        return True           
            
    def Convert(self, contextFilename):
        parserOptions = ConfigParser.ConfigParser()
        parserOptions.read([self.convertedOptionsFilename])
        
        parserContext = ConfigParser.ConfigParser()
        parserContext.read([contextFilename])
        
        inputVersion = 0.0
        validFile = False
        if parserContext.has_option(self.section, "version"):
            inputVersion = parserContext.getfloat(self.section, "version")
            validFile = True
        else:
            validFile = parserContext.has_section(self.section)

        if not validFile:
            return False

        if inputVersion <= 0.0:
            self.CopyOption(parserOptions, self.section, "idepath", toParser = parserContext)
            self.CopyOption(parserOptions, self.section, "askToLaunchIDE", toParser = parserContext)
            self.CopyOption(parserOptions, self.section, "pythonpath", toParser = parserContext)
            self.CopyOption(parserOptions, self.section, "cmakepath",  toParser = parserContext)
            self.CopyOption(parserOptions, self.section, "compiler",  toParser = parserContext)
            self.CopyOption(parserOptions, self.section, "configurationname", toParser = parserContext)
            
            self.MoveOption(parserContext, self.section, "binfolder",  toOption = "buildfolder")
            
            index = 0
            while parserContext.has_section("RecentlyUsedCSnakeFile%s" % index):
                self.MoveOption(
                    parserContext, 
                    "RecentlyUsedCSnakeFile%s" % index,
                    "instance",
                    toSection = "RecentlyUsedCSnakeFiles",
                    toOption = "instance%s" % index
                )
                self.MoveOption(
                    parserContext, 
                    "RecentlyUsedCSnakeFile%s" % index,
                    "csnakeFile",
                    toSection = "RecentlyUsedCSnakeFiles",
                    toOption = "csnakeFile%s" % index
                )
                index += 1

        if inputVersion <= 1.0:
            self.MoveOption(parserContext, self.section, "thirdpartybinfolder",  toOption = "thirdpartybuildfolder")

        if inputVersion < csnContext.latestFileFormatVersion:
            parserContext.set(self.section, "version", str(csnContext.latestFileFormatVersion))
            f = open(contextFilename, 'w')
            parserContext.write(f)
            f.close() 
        
        return True

    def MoveOption(self, fromParser, fromSection, fromOption, toParser = None, toSection = None, toOption = None):
        self.CopyOption(fromParser, fromSection, fromOption, toParser, toSection, toOption)
        fromParser.remove_option(fromSection, fromOption)
            
    def CopyOption(self, fromParser, fromSection, fromOption, toParser = None, toSection = None, toOption = None):
        if toParser is None:
            toParser = fromParser
        if toSection is None:
            toSection = fromSection
        if toOption is None:
            toOption = fromOption

        if not (fromParser.has_section(fromSection) and fromParser.has_option(fromSection, fromOption)):
            return
            
        if not toParser.has_section(toSection):
            toParser.add_section(toSection)

        toParser.set(toSection, toOption, fromParser.get(fromSection, fromOption))
