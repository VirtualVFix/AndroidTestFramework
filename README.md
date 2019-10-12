# AndroidTestFramework
Android Test Framework was developed for test automation of Motorola's products based on Android.<br> 
Most feature should work on pure Android devices.<br><br>
The framework may be used as unittest shell for any tests.<br>
The following files are required for Framework functioning: <b>/src/launcher.py</b>, <b>/src/config.py</b>, and whole <b>/src/libs/core/</b> folder, all another are additional.

### Install
- Require python 3.5+ version
- Use "python3 -m pip install requirements.txt" to install all required libraries  

### Usage
cd /src<br>
python3 launcher.py --help

### Tests
Available the following tests:
- benchmarks: Popular benchmark tests like Vellamo, Antutu, Octane etc.
- storage: Iozone and memory tests.

Test structure:
<pre>
|   +-- mytest/             # Test name     
|   |   +-- suite.list      # Default suite lists
|   |   +-- suites/
|   |   |   +-- regular.py  # Test suite
|   |   +-- tools/
|   |   |   +-- test_tk.py  # Tests implimentation toolkit
</pre>
This test will be available via <b>-i "mytest"</b> option<br>

### Documentation
Is in progress...