# Source CMakeLists file

# Include directories
INCLUDE_DIRECTORIES(${${PROJECT_NAME}_SOURCE_DIR}/src)
# Link directories
LINK_DIRECTORIES(${${PROJECT_NAME}_BINARY_DIR})

# Library name
SET(LIBRARY_NAME FourLib)

# File list
FILE(GLOB SOURCES "*.cpp" "*.h")

# Create library
ADD_LIBRARY(${LIBRARY_NAME} STATIC ${SOURCES}) 
ADD_DEPENDENCIES(${LIBRARY_NAME} ThreeLib)
