#!/bin/bash

#############################################
# v1.1 of script by Su Morton
# date 6/5/2020
#############################################

#writing a script to generate a fix log

# First step is to generate the logon messages

TODAY=`date "+%Y-%m-%d"`

# open the log file
LOGFILENAME="fixlog"`date "+%Y%m%d%H%M%S"`".log"

touch $LOGFILENAME

# Need to setup some of the variables we will need

CLIENT="WILEYEDGE"
BROKER="MS"

HEARTBEAT=""
HEARTBEATRESPONSE=""

CLIENTSEQNUMBER=1
BROKERSEQNUMBER=1

CURRENTTIME=`date "+%Y-%m-%d-%T"`

# initial login messages on the session

INITIALLOGON="8=FIX4.4; 35=A; 34=$CLIENTSEQNUMBER; 49=$CLIENT; 56=$BROKER; 52=$CURRENTTIME; 108=30; 10=0015;"
INITIALLOGONACK="8=FIX4.4; 35=A; 34=$BROKERSEQNUMBER; 49=$BROKER; 56=$CLIENT; 52=$CURRENTTIME; 108=30; 10=0016;"

echo $INITIALLOGON >> $LOGFILENAME
echo $INITIALLOGONACK >> $LOGFILENAME

# now we will put some heartbeat messages in the log before trading starts - we will make the number of heart beat messages configurable
# To be authentic the sleep variable should be set to 30 in here

TOTALHEARTBEATS=50

until [ $CLIENTSEQNUMBER -gt $TOTALHEARTBEATS ]
do
        let "CLIENTSEQNUMBER++"
        let "BROKERSEQNUMBER++"
        CURRENTTIME=`date "+%Y-%m-%d-%T"`


        INITIALHEARTBEAT="8=FIX4.4; 35=0; 34=$CLIENTSEQNUMBER; 49=$CLIENT; 56=$BROKER; 52=$CURRENTTIME; 108=30; 10=0015;"
        INITIALHEARTBEATACK="8=FIX4.4; 35=0; 34=$BROKERSEQNUMBER; 49=$BROKER; 56=$CLIENT; 52=$CURRENTTIME; 108=30; 10=0015;"
        sleep 2

        echo $INITIALHEARTBEAT >> $LOGFILENAME
        echo $INITIALHEARTBEATACK >> $LOGFILENAME

done

#now we will look to setup some trading messages

Stocks=('AAPL' 'MSFT' 'AMZN' 'FB' 'GOOG' 'GOOGL' 'INTC' 'PEP' 'NFLX' 'CSCO' 'AMGN' 'PYPL' 'TSLA' 'TXN' 'AVGO' 'GILD' 'SBUX' 'QCOM' 'TMUS' 'MDLZ' 'BAC' 'DDD' 'MMM' 'WBAI' 'WUBA' 'EGHT' 'AHC' 'AOS' 'ATEN' 'AIR' 'AAN' 'ABB' 'ABT' 'ABBV' 'ANF' 'ABM' 'AAPL' 'PEP' )
Prices=('1276.37' '59.89' '133.47' '430.62' '42.05' '289.20' '339.13' '36.21' '306.71' '233.73' '116.62' '723.61' '503.77' '112.46' '262.99' '82.91' '75.71' '75.47' '90.74' '52.26' '22.03' '8.01' '146.98' '4.10' '51.41' '17.03' '1.40' '40.38' '6.45' '16.31' '25.68' '17.42' '94.04' '83.60' '9.10' '31.64' '284.65' '45.43' )


CURRENTSTOCK=""
CURRENTPRICE=""
ORDERID=""
QTY=""
TOTALNEWORDERS=`echo "${#Stocks[@]}"`
i=0
until [ $i -gt $TOTALNEWORDERS ]
do
        CURRENTSTOCK="`echo ${Stocks[$i]}`"
        CURRENTTIME=`date "+%Y-%m-%d-%T"`
        QTY="";
        SIDE=1;
        CURRENTPRICE="`echo ${Prices[$i]}`"
        ORDERID="algo"`date "+%Y%m%d%H%M%S"`
        SIDE="`echo $((1 + RANDOM % 2))`"
        QTY="`echo $(($RANDOM + 10))`"

        let "CLIENTSEQNUMBER++"
