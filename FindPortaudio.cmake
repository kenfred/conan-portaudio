# The module defines the following variables:
#  PORTAUDIO_FOUND - the system has Portaudio
#  PORTAUDIO_ROOT - where to find includes
#  PORTAUDIO_INCLUDE_DIRS - qwt includes
#  PORTAUDIO_LIBRARIES - aditional libraries
#  PORTAUDIO_VERSION_STRING - version (ex. 5.2.1)
#  PORTAUDIO_ROOT_DIR - root dir (ex. /usr/local)

#=============================================================================
# Copyright 2010-2013, Julien Schueller
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met: 
# 
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer. 
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution. 
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# The views and conclusions contained in the software and documentation are those
# of the authors and should not be interpreted as representing official policies, 
# either expressed or implied, of the FreeBSD Project.
#=============================================================================
find_path(PORTAUDIO_INCLUDE_DIR
            NAMES portaudio.h
            HINTS ${PORTAUDIO_ROOT}
            )

find_library ( PORTAUDIO_LIBRARY
                NAMES portaudio portaudio_x86 portaudio_static_x86 portaudio_x64 portaudio_static_x64
                PATHS lib
                )
            
set ( PORTAUDIO_LIBRARies ${PORTAUDIO_LIBRARY} )

IF(CMAKE_SYSTEM_NAME STREQUAL "Linux")
   SET(EXTRA_LIBS rt m asound pthread)
ENDIF()

macro(ADD_OSX_FRAMEWORK fwname)
    find_library(FRAMEWORK_${fwname}
                NAMES ${fwname}
                PATHS ${CMAKE_OSX_SYSROOT}/System/Library
                PATH_SUFFIXES Frameworks
                NO_DEFAULT_PATH)
    if( ${FRAMEWORK_${fwname}} STREQUAL FRAMEWORK_${fwname}-NOTFOUND)
        message(ERROR ": Framework ${fwname} not found")
    else()
        set(EXTRA_LIBS ${EXTRA_LIBS} "${FRAMEWORK_${fwname}}/${fwname}")
        message(STATUS "Framework ${fwname} found at ${FRAMEWORK_${fwname}}")
    endif()
endmacro(ADD_OSX_FRAMEWORK)

if(APPLE)
   # This frameworks are needed for macos: http://portaudio.com/docs/v19-doxydocs/compile_mac_coreaudio.html
   ADD_OSX_FRAMEWORK(CoreServices)
   ADD_OSX_FRAMEWORK(Carbon)
   ADD_OSX_FRAMEWORK(AudioUnit)
   ADD_OSX_FRAMEWORK(AudioToolbox)
   ADD_OSX_FRAMEWORK(CoreAudio)
endif(APPLE)

set(PORTAUDIO_INCLUDE_DIRS ${PORTAUDIO_INCLUDE_DIR})
set(PORTAUDIO_LIBRARIES ${PORTAUDIO_LIBRARY} ${EXTRA_LIBS})

mark_as_advanced(PORTAUDIO_LIBRARY PORTAUDIO_INCLUDE_DIR)

set(PORTAUDIO_FOUND TRUE)

if (${PORTAUDIO_FOUND})
add_library(Portaudio::Portaudio INTERFACE IMPORTED)
set_target_properties(Portaudio::Portaudio PROPERTIES
    INTERFACE_INCLUDE_DIRECTORIES "${PORTAUDIO_INCLUDE_DIRS}"
    INTERFACE_LINK_LIBRARIES "${PORTAUDIO_LIBRARIES}")
endif()