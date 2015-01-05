DELAY=15
DELAY_MIN=-1
ITERATOR=0
ITERATIONS_MAX=2

while [ $DELAY -gt $DELAY_MIN ]; do
    while [ $ITERATOR -lt $ITERATIONS_MAX ]; do
	echo "start!"
	/etc/init.d/appli_andrew start
	echo "after start!"
	sleep $DELAY
	echo "before stop!"ls

	/etc/init.d/appli_andrew stop
	echo "after stop!"
	sleep $DELAY
	echo $DELAY
	lsmod
	ITERATOR=$((ITERATOR+1))
    done
    ITERATOR=0
    DELAY=$((DELAY-1))
done