# Library name
SET(LIBRARY_NAME TwoLib)

# File list
FILE(GLOB SOURCES "*.cpp" "*.h")

# Create library
ADD_LIBRARY(${LIBRARY_NAME} SHARED ${SOURCES}) 
