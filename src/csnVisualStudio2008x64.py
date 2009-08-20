import csnContext
import csnProject
import csnUtility
import os

class Context(csnContext.Context):
    def __init__(self):
        csnContext.Context.__init__(self)
        self.postProcessor = PostProcessor()
        
    def CreateProject(self, _name, _type, _sourceRootFolder = None, _categories = None):
        project = csnProject.GenericProject(_name, _type, _sourceRootFolder, _categories, _context = self)
        project.compileManager.private.definitions.append("/Zm200")        
        return project

    def IsForPlatform(self, _WIN32, _NOT_WIN32):
        return _WIN32 or (not _WIN32 and not _NOT_WIN32)

    def GetOutputFolder(self, _configuration = "${CMAKE_CFG_INTDIR}"):
        """
        Returns the folder where the compiler should place binaries for _configuration.
        The default value for _configuration returns the output folder for the current configuration.
        for storing binaries.
        """
        if _configuration == "DebugAndRelease":
            return "%s/bin" % self.buildFolder
        else:
            return "%s/bin/%s" % (self.buildFolder, _configuration)
        
class PostProcessor:
    def Do(self, _project):
        """
        Post processes the vcproj file generated for _project.
        """
        # vc proj to patch
        vcprojFilename = "%s/%s.vcproj" % (_project.GetBuildFolder(), _project.name)
        if not _project.dependenciesManager.isTopLevel:
            slnFilename = "%s/%s.sln" % (_project.GetBuildFolder(), _project.name)
            if os.path.exists(slnFilename):
                os.remove(slnFilename)

         # if there is a vcproj, and we want a precompiled header
        if _project.compileManager.precompiledHeader != "" and os.path.exists(vcprojFilename):
          
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
           
          #set precompiled header
          searchString = "RuntimeTypeInfo=\"TRUE\"\n"
          replaceString = \
"""RuntimeTypeInfo="TRUE"
UsePrecompiledHeader="2"
PrecompiledHeaderThrough="%s" 
PrecompiledHeaderFile="%s"
 """ % (_project.compileManager.precompiledHeader, releasePchFilename)
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
					Name="Debug|x64">
					<Tool
						Name="VCCLCompilerTool"
						UsePrecompiledHeader="1"/>
				</FileConfiguration>
				<FileConfiguration
					Name="Release|x64">
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
""" % _project.compileManager.precompiledHeader
          vcproj = vcproj.replace(searchString, replaceString)
        
          # create file pchCppFilename
          precompiledHeaderCppFilename = "%s/%s" % (_project.GetBuildFolder(), pchCppFilename);
          precompiledHeaderCppFilenameText = \
"""// Automatically generated file for building the precompiled headers file. DO NOT EDIT
#include "%s"
""" % _project.compileManager.precompiledHeader
          
 
          if( csnUtility.FileToString(precompiledHeaderCppFilename) != precompiledHeaderCppFilenameText ):
                f = open(precompiledHeaderCppFilename, 'w')
                f.write(precompiledHeaderCppFilenameText)
                f.close() 
                
          # write patched vcproj
          f = open(vcprojFilename, 'w')
          f.write(vcproj)
          f.close()
               