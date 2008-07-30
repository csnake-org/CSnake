import os
import csnUtility
import csnCompiler

class Compiler(csnCompiler.Compiler):
    def __init__(self):
        csnCompiler.Compiler.__init__(self)
        self.private.definitions.append("/Zm200")        

    def IsForPlatform(self, _WIN32, _NOT_WIN32):
        return _WIN32 or (not _WIN32 and not _NOT_WIN32)
        
class PostProcessor:
    def Do(self, _project, _binaryFolder):
        """
        Post processes the vcproj file generated for _project, where the vc proj file was written
        to _binaryFolder.         
        """
        # vc proj to patch
        vcprojFilename = "%s/%s.vcproj" % (_project.GetBuildFolder(), _project.name)

        # if there is a vcproj, and we want a precompiled header
        if _project.precompiledHeader != "" and os.path.exists(vcprojFilename):
            # binary pch file to generate
            debugPchFilename = "%s/%s.debug.pch" % (_project.GetBuildFolder(), _project.name)
            releasePchFilename = "%s/%s.release.pch" % (_project.GetBuildFolder(), _project.name)
            # this is the name of the cpp file that will build the precompiled headers
            pchCppFilename = "%sPCH.cpp" % (_project.name)

            # patch the vcproj            
            f = open(vcprojFilename, 'r')
            vcproj = f.read()
            f.close()
            vcprojOrg = vcproj 
            
            # add release project pch settings to all configurations
            searchString = "RuntimeTypeInfo=\"TRUE\"\n"
            replaceString = \
"""RuntimeTypeInfo="TRUE"
UsePrecompiledHeader="3"
PrecompiledHeaderThrough="%s" 
PrecompiledHeaderFile="%s"
""" % (_project.precompiledHeader, releasePchFilename)
            vcproj = vcproj.replace(searchString, replaceString)
            
            # in the first occurence of the release pch filename, correct it to the debug pch filename
            vcproj = vcproj.replace(releasePchFilename, debugPchFilename, 1)
            
            # add pchCpp to the solution
            searchString = "<Files>\n"
            replaceString = \
"""
    <Files>
		<Filter
			Name="PCH Files"
			Filter="">
			<File
				RelativePath="%s">
				<FileConfiguration
					Name="Debug|Win32">
					<Tool
						Name="VCCLCompilerTool"
						UsePrecompiledHeader="1"/>
				</FileConfiguration>
				<FileConfiguration
					Name="Release|Win32">
					<Tool
						Name="VCCLCompilerTool"
						UsePrecompiledHeader="1"/>
				</FileConfiguration>
			</File>
		</Filter>
""" % pchCppFilename             
            vcproj = vcproj.replace(searchString, replaceString)
            
            # force include of the pch header file
            searchString = "CompileAs=\"2\"\n"
            replaceString = \
"""CompileAs="2"
ForcedIncludeFiles="%s"
""" % _project.precompiledHeader
            vcproj = vcproj.replace(searchString, replaceString)

            # create file pchCppFilename
            precompiledHeaderCppFilename = "%s/%s" % (_project.GetBuildFolder(), pchCppFilename);
            precompiledHeaderCppFilenameText = \
"""// Automatically generated file for building the precompiled headers file. DO NOT EDIT
#include "%s"
""" % _project.precompiledHeader
   
            if( csnUtility.FileToString(precompiledHeaderCppFilename) != precompiledHeaderCppFilenameText ):
                f = open(precompiledHeaderCppFilename, 'w')
                f.write(precompiledHeaderCppFilenameText)
                f.close()
            
            # write patched vcproj
            f = open(vcprojFilename, 'w')
            f.write(vcproj)
            f.close()
    