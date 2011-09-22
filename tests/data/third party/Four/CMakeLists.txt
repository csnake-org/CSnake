# Root Project CMakeLists file

# Project definition
PROJECT(Four)

# Depends on Three
FIND_PACKAGE(Three REQUIRED)
INCLUDE(${Three_USE_FILE})

# Parse subdirs
ADD_SUBDIRECTORY(src)

# Project include directories
SET(${PROJECT_NAME}_INCLUDE_DIRS "${${PROJECT_NAME}_SOURCE_DIR}/src")

# Project libraries directories
SET(${PROJECT_NAME}_LIBRARY_DIRS "${LIBRARY_OUTPUT_DIRECTORY}")

# Project libraries
SET(${PROJECT_NAME}_LIBRARIES FourLib)

# The project "use" file var
SET(${PROJECT_NAME}_USE_FILE "${${PROJECT_NAME}_BINARY_DIR}/Use${PROJECT_NAME}.cmake")

# Create the config.cmake file with these vars
CONFIGURE_FILE(
    "${${PROJECT_NAME}_SOURCE_DIR}/${PROJECT_NAME}Config.cmake.in"
    "${${PROJECT_NAME}_BINARY_DIR}/${PROJECT_NAME}Config.cmake"
    @ONLY
    IMMEDIATE)

# Create the use.cmake file
CONFIGURE_FILE(
    "${${PROJECT_NAME}_SOURCE_DIR}/Use${PROJECT_NAME}.cmake.in"
    "${${PROJECT_NAME}_USE_FILE}"
    COPYONLY
    IMMEDIATE)
