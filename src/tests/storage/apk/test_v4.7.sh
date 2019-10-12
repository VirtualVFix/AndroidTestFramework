#!/system/bin/sh

DIR=/mnt/obb
#IOZONE=/mnt/obb/iozone
IOZONE=/data/iozone
TEST_DIR=/data
TEST_FILE=iozone_test
EXTERNAL_DIR=/mnt/media_rw/
TARGET=`getprop ro.board.platform`
DEVICE=`getprop ro.boot.device`
BARCODE=`getprop ro.serialno`
DATE_TIME=`date +%Y%m%d-%H%M`
CONFIG_MMC=0
THREAD_NUM=4
MULTI_TEST_FILE_PATH=""
DRY_RUN=0

__init_dir()
{
TEST_FILE_PATH=${TEST_DIR}/${TEST_FILE}
REPORT_PREFIX=${DEVICE}_${BARCODE}_${DATE_TIME}
REPORT_FOLDER=$REPORT_PREFIX
REPORT_FOLDER_PATH=/data/tmp/iozone/${REPORT_FOLDER}
__init_multiple_testfiles $THREAD_NUM
}

RAM_SIZE=`free -m | grep Mem | busybox awk -F ' ' '{print $2}'`
(( RAM_SIZE/=1024 ))
(( TEST_SIZE=RAM_SIZE+1 ))
(( MULTITH_TEST_SIZE=TEST_SIZE ))

CHECKRESULT=0
TEST_MODE=0


__init_multiple_testfiles()
{
	start=0
	end=$1
	while (($start<$end));do
		MULTI_TEST_FILE_PATH="$MULTI_TEST_FILE_PATH ${TEST_FILE_PATH}_$start"
		let start++
	done

}

__clean_test_file()
{

	while [ "$1" != "" ]; do
		if [ -e $1 ];
		then
			rm $1;

		fi

		if [ CHECKRESULT -ne 0 ];
		then
			echo "rm $1"
		fi

		shift
	done

}

__check_result()
{
	if [ CHECKRESULT -ne 0 ];
	then
		echo $1 `cat $1`;
	fi
}

#input value , str
__set_to()
{
	#echo "$1 > $2";
	echo $1 > $2;
	__check_result $2;
}
__sync()
{
	sync
	sync
	__set_to 3 "/proc/sys/vm/drop_caches"
}


#input CPU#, govenor
__set_governor()
{
	local str="/sys/devices/system/cpu/cpu$1/cpufreq/scaling_governor"

	if [ -e $str ];
	then
		__set_to $2 $str
	fi

}

#input CPU#
__set_max_freq()
{

	local strMax="/sys/devices/system/cpu/cpu$1/cpufreq/scaling_max_freq"
	local strMin="/sys/devices/system/cpu/cpu$1/cpufreq/scaling_min_freq"

	if [ -e $strMax ] && [ -e $strMin ];
	then
		__set_to `cat $strMax` $strMax
		__set_to `cat $strMax` $strMin
	fi
}

#input CPU#
__set_cpu_online()
{

	#local str="/sys/devices/system/cpu/cpu$1/online"
	__set_to 1 "/sys/devices/system/cpu/cpu$1/online" 
}

#enable, cpu_from, cpu_to
__config_by_cpu()
{

	local end=$3
	local index=$2

	while (($index<=$end));do

		if [ $1 -ne 0 ];
		then
			__set_cpu_online $index
		fi

		__set_governor $index "performance"
		__set_max_freq $index

		let index++
	done
}
__disable_cpuidle()
{
	#local str="/sys/module/lpm_levels/parameters/sleep_disabled"
	__set_to "Y" "/sys/module/lpm_levels/parameters/sleep_disabled"
}
__disable_thermal()
{
	#local str="/sys/module/msm_thermal/core_control/enabled"
	__set_to  0 "/sys/module/msm_thermal/core_control/enabled"
}
__config_mmc()
{
	local str="/sys/class/mmc_host/mmc0/clk_scaling/enable"

	local str_max_lock="/sys/kernel/debug/mmc0/max_clock"
	local str_mmc_clock="/sys/kernel/debug/mmc0/clock"
	local str_read_ahead="/sys/block/mmcblk0/queue/read_ahead_kb"

	__set_to 0 $str
	__set_to `cat $str_max_lock` $str_mmc_clock
	__set_to 0 $str_read_ahead
}
__config_product()
{
	case "$TARGET" in
	"msm8916")
		case "$DEVICE" in
		"osprey")
			__config_by_cpu 0 0 3
			;;
		"lux"|"merlin")
			__config_by_cpu 0 4 7
			__config_by_cpu 1 0 3

			;;
		esac
		;;
	"msm8992")
		__config_by_cpu 0 0 3
		__config_by_cpu 1 4 5
		;;
	"msm8994")
		__config_by_cpu 0 0 3
		__config_by_cpu 1 4 7
		;;
	"msm8937")
		case "$DEVICE" in
		"cedric")
			__config_by_cpu 0 4 7
			__config_by_cpu 1 0 3
			;;
		"perry"|"owens")
			__config_by_cpu 0 0 3
			__config_by_cpu 1 4 5
			;;
		esac
		;;
	"msm8996")
		__config_by_cpu 0 0 1 
		__config_by_cpu 1 2 3
		;;
	"msm8952"|"msm8953")
		__config_by_cpu 0 4 7
		__config_by_cpu 1 0 3
		CONFIG_MMC=0
		;;
        "msm8998")
		__config_by_cpu 0 0 3 
		__config_by_cpu 1 4 7
		;;
	esac
}

__env_config()
{
	stop bug2go
	stop thermal-engine
	stop perfd

	settings put global airplane_mode_on 1
	am broadcast -a android.intent.action.AIRPLANE_MODE --ez state true

	__init_dir

	mkdir -p $REPORT_FOLDER_PATH

	echo "test file size is ${TEST_SIZE}g"
	echo "multiple threads test file size is ${MULTITH_TEST_SIZE}g"
	echo "single test file is ${TEST_FILE_PATH}"
	echo "multiple test files are ${MULTI_TEST_FILE_PATH}"

	__config_product
		
	# to avoid cpuidle
	__disable_cpuidle

	if [ $CONFIG_MMC -ne 0 ];
	then
		__config_mmc
	fi

	__disable_thermal

	__sync
}

#input: 1)record_size 2) file_size 3)cmd 4)"s" 5)is_need_xls
__iozone_run()
{
	if [ "$4" = "s" ];then
		IOZONE_THREAD_STR="-f ${TEST_FILE_PATH}"
	else
		IOZONE_THREAD_STR="-t${THREAD_NUM} -F ${MULTI_TEST_FILE_PATH}"
	fi


	if [ $5 -ne 0 ]; then
		IOZONE_XLS_PATH="-Rb ${REPORT_FOLDER_PATH}/${REPORT_PREFIX}_${3}_${4}${1}.xls"
	else
		IOZONE_XLS_PATH=""
	fi

	cmd=0
	case "$3" in
	"seq_w" )
		cmd=0
		;;

	"seq_r" )
		cmd=1
		;;

	"random")
		cmd=2

	esac

	if [ ${DRY_RUN} -eq 0 ];
	then
		$IOZONE -ecI -r${1}k -s${2} -i${cmd} -w $IOZONE_THREAD_STR $IOZONE_XLS_PATH
	else
		echo "$IOZONE -ecI -r${1}k -s${2} -i${cmd} -w $IOZONE_THREAD_STR $IOZONE_XLS_PATH"
	fi

}
__clean_file()
{
	str=""

	if [ $1 = "s" ];
	then
		str=${TEST_FILE_PATH}
	else
		str=${MULTI_TEST_FILE_PATH}
	fi

	__clean_test_file $str
}
#input 1) "s" or "m" (single thread or multiple)  
__seq_rw()
{

	if [ $1 = "s" ];
	then
		file_size=${TEST_SIZE}
	else
		file_size=${MULTITH_TEST_SIZE}
	fi

	__clean_file $1
	__sync
	#$IOZONE -ecI -r128k -s${TEST_SIZE}g -i0 -w -f $TEST_FILE_PATH -Rb ${REPORT_FOLDER_PATH}/${REPORT_PREFIX}_seq_w_128.xls
	__iozone_run 128 ${file_size}g "seq_w" $1 1
	__sync
	#$IOZONE -ecI -r128k -s${TEST_SIZE}g -i1 -w -f $TEST_FILE_PATH -Rb ${REPORT_FOLDER_PATH}/${REPORT_PREFIX}_seq_r_128.xls
	__iozone_run 128 ${file_size}g "seq_r" $1 1

	__clean_file $1
	__sync
	#$IOZONE -ecI -r512k -s${TEST_SIZE}g -i0 -w -f ${TEST_FILE_PATH} -Rb ${REPORT_FOLDER_PATH}/${REPORT_PREFIX}_seq_w_512.xls
	__iozone_run 512 ${file_size}g "seq_w" $1 1

	__sync
	#$IOZONE -ecI -r512k -s${TEST_SIZE}g -i1 -w -f ${TEST_FILE_PATH} -Rb ${REPORT_FOLDER_PATH}/${REPORT_PREFIX}_seq_r_512.xls
	__iozone_run 512 ${file_size}g "seq_r" $1 1
}

#input 1) "s" or "m" (single thread or multiple) ; 2) test file
__rand_rw()
{

	__clean_file $1
	__sync
	# prepare a file
	#$IOZONE -ecI -r4k -s100m -i0 -w -f ${TEST_FILE_PATH}
	__iozone_run 4 100m "seq_w" $1 0

	__sync
	#$IOZONE -ecI -r4k -s100m -i2 -f ${TEST_FILE_PATH} -Rb ${REPORT_FOLDER_PATH}/${REPORT_PREFIX}_random_r_w_4.xls
	__iozone_run 4 100m "random" $1 1
}

__auto_mode()
{
	__sync
	$IOZONE -a -s${TEST_SIZE}g  -f ${TEST_FILE_PATH} > ${REPORT_FOLDER_PATH}/${REPORT_PREFIX}_config.out
}


run_test()
{

	__env_config

	case "$TEST_MODE" in
	0 )
		echo "Only Run Multithread Testing..."
		__seq_rw m
		__rand_rw m
		;;
	1 )
		echo "Only Run Single Thread Testing..."
		__seq_rw s
		__rand_rw s
		;;
	2 )
		echo "Run both Single Thread &  Multithread Testing..."
		__seq_rw s
		__rand_rw s
		__seq_rw m
		__rand_rw m
		;;
	3 )
		echo "Run IOZONE Automode Testing..."
		__auto_mode
		;;
	esac


}
close_test()
{
	CURRENT_PWD=`pwd`
	cd $REPORT_FOLDER_PATH
	cd ..
	#tar zcvf ./${REPORT_FOLDER}.tgz ./${REPORT_FOLDER}
	#echo "Report is zipped @ `pwd`/${REPORT_FOLDER}.tgz"

	echo "Report is in `pwd`/${REPORT_FOLDER}/"
	cd $CURRENT_PWD

}

usage()
{
	echo "usage: $0 [-c | check_setting ] [-s | --test_size size] [ -m | --test_mode mode] [ -d dir ] [--dryrun] [-t thread_number (default=4)] [-T targe] [-ms | --multithread-test_size size]"
}

while [ "$1" != "" ]; do
	case $1 in
	    -c | --check_setting )
			CHECKRESULT=1
			;;

	    -s | --test_size )
			shift
			TEST_SIZE=$1
			;;
	    -m | --test_mode )
			shift
			TEST_MODE=$1
			;;
	    -d )
			shift
			TEST_DIR=$1
			;;

	    -t )
			shift
			THREAD_NUM=$1
			;;
	    --dryrun )
			DRY_RUN=1
			;;
	    -T )
			shift
			TARGET=$1
			;;

	    -ms | --multithread-test_size )
			shift
			MULTITH_TEST_SIZE=$1
			;;
	    * )
		usage
		exit 1
	esac
	shift

done

run_test

close_test
