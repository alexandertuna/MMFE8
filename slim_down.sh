#
# slim_down.sh : shell script for taking AZ FW to the barebones necessities
#
# source ~/Downloads/MMFE8/slim_down.sh
#

topdir="/home/mmfe8/Downloads/X-3-slimmingdown"

echo rm -f ${topdir}/*.jou
echo rm -f ${topdir}/*.log
echo rm -f ${topdir}/*.xlsx
echo rm -f ${topdir}/*.zip

echo rm -f ${topdir}/*.pyc
echo rm -f ${topdir}/*/*.pyc
echo rm -f ${topdir}/*/*/*.pyc
echo rm -f ${topdir}/*/*/*/*.pyc
echo rm -f ${topdir}/*/*/*/*/*.pyc

echo rm -f ${topdir}/*~
echo rm -f ${topdir}/*/*~
echo rm -f ${topdir}/*/*/*~
echo rm -f ${topdir}/*/*/*/*~
echo rm -f ${topdir}/*/*/*/*/*~

# breaks
# echo rm -rf ${topdir}/X-3.srcs/sources_1/ip/*

