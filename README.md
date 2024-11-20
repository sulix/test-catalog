# Linux Kernel Test Catalog

An attempt to map kernel subsystems to kernel tests that should be run on
patches or code by humans and CI systems.  


Examples:  

Find test info for a subsystem  
```
./get_tests.py -s 'KUNIT TEST' --info
```
```
Subsystem:    KUNIT TEST
Maintainer:   
  David Gow <davidgow@google.com>
Mailing List: None
Version:      None
Dependency:   ['python3-mypy']
Test:         
  smoke:
    Url: None
    Working Directory: None
    Cmd: ./tools/testing/kunit/kunit.py
    Env: None
    Param: run --kunitconfig lib/kunit
Hardware:     arm64, x86_64
```

Find copy-n-pastable tests for a subsystem
```
./get_tests.py -s 'KUNIT TEST'
```
```
./tools/testing/kunit/kunit.py run --kunitconfig lib/kunit
```

