# Define settings for Intel Compiler in Altix 350
OPTION(INTEL_ALTIX350
  "Use Intel Compiler C/C++ in SGI Altix 350" 
  OFF
)

IF(INTEL_ALTIX350)
  SET(CMAKE_BUILD_TYPE "Release" CACHE STRING "Build type" FORCE)

  SET(CMAKE_CXX_COMPILER "icpc" CACHE STRING "Using Intel C++ Compiler" FORCE)
  SET(CMAKE_CXX_FLAGS "-mcpu=itanium2 -tpp2" CACHE STRING "Flag to generate code for Intel Itanium 64" FORCE)
  SET(CMAKE_CXX_FLAGS_DEBUG "-g" CACHE STRING "Flag to generate debug builds" FORCE)
  SET(CMAKE_CXX_FLAGS_MINSIZEREL "-Os" CACHE STRING "Flag to generate minsize builds" FORCE)
  SET(CMAKE_CXX_FLAGS_RELEASE "-O3" CACHE STRING "Flag to generate release builds" FORCE)
  SET(CMAKE_CXX_FLAGS_RELWITHDEBINFO "-O2 -g" CACHE STRING "Flag to generate release builds with debug information" FORCE)

  SET(CMAKE_C_COMPILER "icc" CACHE STRING "Using Intel C Compiler" FORCE)
  SET(CMAKE_C_FLAGS "-mcpu=itanium2 -tpp2" CACHE STRING "Flag to generate code for Intel Itanium 64" FORCE)
  SET(CMAKE_C_FLAGS_DEBUG "-g" CACHE STRING "Flag to generate debug builds" FORCE)
  SET(CMAKE_C_FLAGS_MINSIZEREL "-Os" CACHE STRING "Flag to generate minsize builds" FORCE)
  SET(CMAKE_C_FLAGS_RELEASE "-O3" CACHE STRING "Flag to generate release builds" FORCE)
  SET(CMAKE_C_FLAGS_RELWITHDEBINFO "-O2 -g" CACHE STRING "Flag to generate release builds with debug information" FORCE)
ENDIF ( INTEL_ALTIX350 )

MARK_AS_ADVANCED(INTEL_ALTIX350)

# We have compiled the windows binaries with the MSCV2003. We give the 
# MSCV2003 runtime libraries so it will run in machines that doesn't 
# have it installed or have a different version.
IF(WIN32)
  INSTALL(FILES
    "${CILAB_TOOLKIT_SOURCE_DIR}/thirdParty/MSVC/MSVC7.1/msvcr71.dll"
    "${CILAB_TOOLKIT_SOURCE_DIR}/thirdParty/MSVC/MSVC7.1/msvcp71.dll"
    "${CILAB_TOOLKIT_SOURCE_DIR}/thirdParty/MSVC/MSVC7.1/msvcr71d.dll"
    "${CILAB_TOOLKIT_SOURCE_DIR}/thirdParty/MSVC/MSVC7.1/msvcp71d.dll"
    "${CILAB_TOOLKIT_SOURCE_DIR}/thirdParty/MSVC/MSVC7.1/msvcrtd.dll"
    DESTINATION
    "${CMAKE_INSTALL_PREFIX}/cilabApps/GIMIAS"
  )
ENDIF(WIN32)

# increase heap limit for WIN32. Assumes /Zm1000 is set by ITK or CMAKE
MACRO(INCREASE_MSVC_HEAP_LIMIT _value)
IF(WIN32)
 STRING(REPLACE /Zm1000 "/Zm${_value}" CMAKE_CXX_FLAGS ${CMAKE_CXX_FLAGS})  
ENDIF(WIN32)
ENDMACRO(INCREASE_MSVC_HEAP_LIMIT)


# suppress some warnings in VC8 about using unsafe/deprecated c functions
MACRO(SUPPRESS_VC8_DEPRECATED_WARNINGS)
IF(MSVC90)
  ADD_DEFINITIONS(-D_CRT_SECURE_NO_WARNINGS -D_CRT_NONSTDC_NO_WARNINGS)
ENDIF(MSVC90)
ENDMACRO(SUPPRESS_VC8_DEPRECATED_WARNINGS)

# Supress warning LNK4089: all references to 'ADVAPI32.dll' discarded by /OPT:REF
MACRO(SUPPRESS_LINKER_WARNING_4089 _target)
IF(WIN32)
  SET_TARGET_PROPERTIES(${_target} PROPERTIES LINK_FLAGS "/IGNORE:4089")
ENDIF(WIN32)
ENDMACRO(SUPPRESS_LINKER_WARNING_4089)

# Supress warning C4251: 'blTestParams::m_strVectorInputBaseName' : class 'std::vector<_Ty>'
# needs to have dll-interface to be used by clients of class 'blTestParams'
# warning C4275: non dll-interface class 'blObject' used as base for
# dll-interface class 'blSignalAnnotation'
MACRO(SUPPRESS_COMPILER_WARNING_DLL_EXPORT _target)
IF(WIN32)
  GET_TARGET_PROPERTY(oldProps ${_target} COMPILE_FLAGS)
  if (${oldProps} MATCHES NOTFOUND)
    SET(oldProps "")
  endif(${oldProps} MATCHES NOTFOUND)
  SET(newProperties "${oldProps} /wd4251 /wd4275")
  SET_TARGET_PROPERTIES(${_target} PROPERTIES COMPILE_FLAGS "${newProperties}" )
ENDIF(WIN32)
ENDMACRO(SUPPRESS_COMPILER_WARNING_DLL_EXPORT)



