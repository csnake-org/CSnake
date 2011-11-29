-----------------
CSnake test data
------------------

The test data tries to reproduce basic library/third parties relations that are possible.
In the third parties, cmakeMacros and CxxTest are default dependencies. 
CSnake add the cmakeMacros in the CMakeLists it generates. 
CxxTest is used for the test of a library. 

+ my src
---------
Source folder with a space in its path (only for visual studio). Uses csnake without API.
- DummyExe: simple exe that depends on 'my src/DummyLib'
- DummyLib: simple lib with application and test and dependency on third party

  'my src/DummyExe' -> 'my src/DummyLib' -> 'third party/CxxTest'

+ src
------
Basic source folder with dependency on third parties. Uses csnake without API.
- DummyExe: simple exe that depends on 'src/DummyLib'
- DummyLib: simple lib with application and test and dependency on third parties

  'src/DummyExe' -> 'src/DummyLib' -> 'thirdParty/CxxTest'
                                   -> 'thirdParty/Two'
                                   -> 'thirdParty/Three'
                                   -> 'thirdParty/Four' -> 'thirdParty/Three'

+ src_api
----------
Basic source folder with dependency on third parties. Uses csnake *with* API.
- DummyExe: simple exe that depends on 'src_api/DummyLib'
- DummyLib: simple lib with application and test and dependency on third parties

  'src_api/DummyExe' -> 'src_api/DummyLib' -> 'thirdParty_api/CxxTest'
                                           -> 'thirdParty_api/Two'
                                           -> 'thirdParty_api/Three'
                                           -> 'thirdParty_api/Four' -> 'thirdParty_api/Three'

+ src2
-------
Basic source folder with dependency on multiple third parties. Uses csnake without API.
- DummyExe2: simple exe that depends on 'src2/DummyLib2'
- DummyLib2: simple lib with application and test and dependency on third parties

  'src2/DummyExe2' -> 'src2/DummyLib2' -> 'thirdParty/CxxTest'
                                       -> 'thirdParty/Two'
                                       -> 'thirdParty/Three'
                                       -> 'thirdParty/Four' -> 'thirdParty/Three'
                                       -> 'thirdParty2/Five'

+ thirdParty
-------------
Basic third party libraries used in 'src' and 'src2'. Uses csnake without API.

+ third party
--------------
Basic third party libraries used in 'my src'. Test for space in path.
Uses csnake without API.

+ thirdParty_api
-----------------
Basic third party libraries used in 'src' and 'src2'. Uses csnake *with* API.

+ thirdParty2
--------------
Basic third party library used 'src2'. Uses csnake without API.
           