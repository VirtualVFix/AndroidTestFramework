# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$Apr 7, 2014 10:10:33 PM$"
__doc__ = """
Base config of benchmark application tests

**BENCHMARKS_DATA** format :
    .. code-block:: python 
        
        BENCHMARKS_DATA = {"Example":
        {
           "@": 'CLASSNAME',                                  # (str) Link to class for copy of parameters
           "class": 'Example',                                # (str) Implementation class from "bench" folder
           "package": 'com.android.cm3',                      # (str) Application package
           "name": 'Android CaffeineMark',                    # (str) Benchmark name. This name is displayed in console output
           "version": '1.0',                                  # (str) Application version
           "order": ['Total', 'Res1', 'Res2'],                # (list) Result fields. Only these fields will be stored in the result in the same order. Order should not have identical fields
           "results_summary": 'best',                         # (str) Summary type for results collection. Available: **best**, **average** or **best_and_average**. By default is **best**
           "average_list": ['I/O db read', 'I/O db write'],   # (list) Average list used for **best_and_average** results summary type. 'results_summary' will set to **best_and_average** if this option exists
           "push": ('dmandroid','/data/data/dmandroid'),      # (tuple) Push content for application
           
           "additional_apk": {  # benchmarks apk              # (dict) Additional application required to install
                "name": "AnTuTu v6.1.1 full",                 # (str) Name of additional application
                "apk": 'com.antutu.benchmark.full_611.apk',   # (str) Apk file name of additional application
                "version": '6.1.1',                           # (str) Version of additional application
                "package": 'com.antutu.benchmark.full'},      # (str) Package name of additional application
            
           "_launch_button":{'all':(0.5, 0.25)},              # (dict) Special parameter
           "_apk": 'eu.chainfire.cfbench-13.apk',             # (str) Application package
           "_finish": {'all': 200, 'kinzie': 120}             # (dict) Wait time when benchmark completed. Add device name for provide special value for it device     
        }
    
    Note:
        All variable starts with underline will be send to JUnitRunner. 
        Variable format depends of benchmark implementation.
        
    Note: 
        'class', 'package', 'name' and '_apk' fields if required all another are optional
"""

import os
from config import CONFIG

HOME_DIR = os.path.split(os.path.split(os.path.realpath(os.path.dirname(__file__)))[0])[0]
APKS_DIR = os.path.join(HOME_DIR, 'apk')

#: Count of retries if Test failed. Default value if "retries" variable is not defined in Test function in Test Suite.
COUNT_RETRIES = 2
#: Uninstall application after test completion.
AUTO_UNINSTALL_APP = True if not CONFIG.SYSTEM.DEBUG else False
#: Point decimal symbol will be used as decimal symbol for "float" variables in spreadsheet results.
#: (system decimal simbol will be used if False).
USE_POINT_AS_DECIMAL_SYMBOL = True

#: Benchmark tests configuration dictionary
BENCHMARKS_DATA = {
    "Quadrant":
        {
            "class": 'Quadrant',
            "_apk": 'Quadrant_Pro_2_1_1.apk',
            "package": 'com.aurorasoftworks.quadrant.ui.professional',
            "name": 'Quadrant Professional v2.1.1',
            "result": [(u'benchmark aggregate', 'Total points'),
                       (u'cpu aggregate', 'CPU points'),
                       (u'memory aggregate', 'Memory points'),
                       (u'io aggregate', 'I/O points'),
                       (u'g2d aggregate', '2D points'),
                       (u'g3d aggregate', '3D points'),
                       (u'io_fs_read', 'I/O fs read'),
                       (u'io_fs_write', 'I/O fs write'),
                       (u'io_db_read', 'I/O db read'),
                       (u'io_db_write', 'I/O db write')],
            "average_list": ['I/O db read', 'I/O db write'],
            "version": "2.1.1",
            "junit": 'kernel.bsp.test.ui.benchmarks.benchmarks.Quadrant',
            "_finish": {'all': 140}
        },
        
    "GFXBench4":
        {
            "class": 'GFXBench3Corp',
            "package": 'net.kishonti.gfxbench.gl.v40000.corporate',
            "_apk": 'net.kishonti.gfxbench.gl.v40000.corporate.apk',
            "name": "GFXBench v4.0",
            "results": ['High-Level Tests', 'Car Chase ES 3.1', 'fps', '1080p Car Chase Offscreen ES 3.1', 'fps',
                        'Manhattan ES 3.1', 'fps', '1080p Manhattan Offscreen ES 3.1', 'fps', 'Manhattan ES 3.0',
                        'fps', '1080p Manhattan Offscreen ES 3.0', 'fps', 'T-Rex ES 2.0', 'fps',
                        '1080p T-Rex Offscreen ES 2.0', 'fps', 'Low-Level Tests', 'Tessellation ES 3.1', 'fps',
                        '1080p Tessellation Offscreen ES 3.1', 'fps', 'ALU 2 ES 3.0', 'fps',
                        '1080p ALU 2 Offscreen ES 3.0', 'fps', 'Driver Overhead 2 ES 3.0', 'fps',
                        '1080p Driver Overhead 2 Offscreen ES 3.0', 'fps', 'Texturing ES 3.0',
                        '1080p Texturing Offscreen ES 3.0', 'Special Tests', 'Render Quality ES 2.0',
                        'Render Quality (high precision) ES 2.0'],
            "version": '4.0.0',
            "junit": 'kernel.bsp.test.ui.benchmarks.benchmarks.GFXBench4',
            "_version": 'v40000',  # activity version. Replace * in avtivity name.
            "_finish": {'all': 2800}
        },

    "CFBench13":
        {
            "class": 'CFBench',
            "_apk": 'eu.chainfire.cfbench-13.apk',
            "package": 'eu.chainfire.cfbench',
            "name": "CF-Bench v1.3",
            "order": ['Overall Score','Native Score','Java Score','Native MIPS','Java MIPS','Native MSFLOPS',
                      'Java MSFLOPS','Native MDFLOPS','Java MDFLOPS','Native MALLOCS','Native Memory Read',
                      'Java Memory Read','Native Memory Write','Java Memory Write','Native Disk Read',
                      'Native Disk Write','Java Efficiency MIPS','Java Efficiency MSFLOPS','Java Efficiency MDFLOPS',
                      'Java Efficiency Memory Read','Java Efficiency Memory Write'],
            "version": "1.3",
            "junit": 'kernel.bsp.test.ui.benchmarks.benchmarks.CFBench',
            "_finish": {'all': 180}
        },
        
    "AnTuTu614":
        {
            "class": 'AnTuTu6',
            "_apk": 'com.antutu.ABenchMark_614.apk',
            "name": "AnTuTu v6.1.4",
            "package": 'com.antutu.ABenchMark',
            "version": '6.1.4',
            "junit": 'kernel.bsp.test.ui.benchmarks.benchmarks.Antutu6',
            "_permissions": {'all':('PHONE','STORAGE')},  # should be in uppercase
            "_finish": {'all': 1200},
            "additional_apk": {  # benchmarks apk
                "name": "AnTuTu v6.1.1 full",
                "apk": 'com.antutu.benchmark.full_611.apk',
                "version": '6.1.1',
                "package": 'com.antutu.benchmark.full'
            }
        },
        
    "AnTuTu626":
        {
            "@":"AnTuTu614",
            "_apk": 'com.antutu.ABenchMark_626.apk',
            "name": "AnTuTu v6.2.6",
            "version": '6.2.6',
        },

    "3DMark":
        {
            "class": 'ThreeDMark',
            "package": 'com.futuremark.dmandroid.application',
            "_apk": 'com.futuremark.dmandroid.application-1.apk',
            "push": ('com.futuremark.dmandroid.application','/data/data/com.futuremark.dmandroid.application/'),
            "name": '3DMark Ice Storm Unlimited',
            "order" : ['Score', 'Graphics score', 'Physics score', 'Graphics test 1', 'Graphics test 2',
                       'Physics test'],
            "version": "1.3.1439",
            "junit": 'kernel.bsp.test.ui.benchmarks.benchmarks.ThreeDMark',
            "_demo_button": {'all': (0.59, 0.312)},
            "_start_button": {'all': (0.77, 0.633)},
            "_select": {'all': (0.07, 0.3)},  # select results
            "_finish": {'all': 500}
        },
        
    "Vellamo325":
        {
            "class": 'Vellamo3',
            "name": 'Vellamo v3.2.5',
            "package": 'com.quicinc.vellamo',
            "pull": '/data/data/com.quicinc.vellamo/files/',
            "failed_fields" : {'WebGL Jellyfish':['count','fps','loadDuration','runDuration'],
                               'Text Reflo':['fontScale1','fontScale2','fps1','fps2','length1','length2',
                                             'loadDuration','runDuration','score'],
                               "Octane v1":['Box2D','CodeLoad','Crypto','DeltaBlue','EarleyBoyer','Gameboy','Mandreel',
                                            'NavierStokes','PdfJS','Raytrace','RegularExp','Richards','Splay',
                                            'loadDuration','runDuration','score'],
                               "Deep Crossfader":['loadDuration','runDuration','xps']},
            "junit": 'kernel.bsp.test.ui.benchmarks.benchmarks.Vellamo3',
            "_finish": {'all': 1400},
            "_apk": 'com.quicinc.vellamo_325.apk',
            "version": "3.2.5"
        },
    
    "Sunspider102":
        {
            "class": 'Sunspider',
            "name": 'SunSpider v1.0.2',
            "junit": 'kernel.bsp.test.ui.benchmarks.benchmarks.Sunspider',
            "_finish": {'all': 200},
            "_url": 'http://www.webkit.org/perf/sunspider-1.0.2/sunspider-1.0.2/driver.html'
        },

    "Octane":
        {
            "class": 'Octane',
            "name": 'Octane v2',
            "junit": 'kernel.bsp.test.ui.benchmarks.benchmarks.Octane',
            "_finish": {'all': 200},
            "_url": 'https://chromium.github.io/octane/'
        },
        
    "Kraken":
        {
            "class": "Kraken",
            "name": 'Kraken 1.1',
            "junit": 'kernel.bsp.test.ui.benchmarks.benchmarks.Sunspider',
            "_finish": {'all': 500},
            "_url": 'http://krakenbenchmark.mozilla.org/kraken-1.1/driver.html'
        },
  
    "SDPlayInternal":
        {
            "class": 'SDPlay',
            "_apk": 'SDPlay_v1.6.3.apk',
            "package": 'com.elena.sdplay',
            "name": "SDPlay 1.6 Internal",
            "pull": "/sdcard/sdplay_results/",
            "order": ['db_write_speed','db_rnd_read_speed','db_rnd_write_speed','db_del_speed','fs_create_speed',
                      'fs_list_speed','fs_small_read_speed','fs_del_speed','fs_iops_read_speed','fs_iops_write_speed',
                      'fs_med_read_speed','fs_med_write_speed','fs_large_read_speed','fs_large_write_speed',
                      'fs_threads'],
            "junit": 'kernel.bsp.test.ui.benchmarks.benchmarks.SDPlay',
            "version": "1.6.3",
            "_finish": {'all': 700},
            "_threads": {'all': 0},  # 0 - use default value
            "_test": 'full',
            "_storage": 'internal',
            "_bigfilesize": {'all': '512MB'}  # if not enough space, file size will be changed
        },
        
    "SDPlayUserdata":
        {
            "@": 'SDPlayInternal',
            "name": "SDPlay 1.6 Userdata",
            "_storage": 'userdata',
        },
        
    "AndroBench":
        {
            "class": 'AndroBench',
            "_apk": 'com.andromeda.androbench-41.apk',
            "package": 'com.andromeda.androbench2',
            "name": "AndroBench 4.1",
            "version": "4.1",
            "junit": 'kernel.bsp.test.ui.benchmarks.benchmarks.AndroBench',
            "_finish": {'all':400}
        },
        
    "AndEBenchPro":
        {
            "class": 'AndEBenchPro',
            "_apk": 'com.eembc.andebench-1.apk',
            "package": 'com.eembc.andebench',
            "name": "AndEBench-Pro 2015",
            "push": (os.path.join('com.eembc.andebench','main.2129.com.eembc.andebench.obb'),
                     '/storage/emulated/0/Android/obb/com.eembc.andebench/main.2129.com.eembc.andebench.obb'),
            "version": "2.1.2472",
            "junit": 'kernel.bsp.test.ui.benchmarks.benchmarks.AndEBenchPro',
            "_finish": {'all':600}
        }
}
