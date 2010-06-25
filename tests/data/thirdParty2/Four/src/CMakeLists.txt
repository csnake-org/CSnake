# Library name
SET(LIBRARY_NAME FourLib)

# File list
FILE(GLOB SOURCES "*.cpp" "*.h")

# Create library
ADD_LIBRARY(${LIBRARY_NAME} STATIC ${SOURCES}) 
