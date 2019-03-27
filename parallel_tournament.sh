#!/bin/bash
echo "Start Virtual Environment"
source venv/bin/activate

n_maps=2

ts=$(date "+%Y%m%d%H%M%S")
log_name=$(echo logs/tournament_result_$ts.log)
log_name_rev=$(echo logs/tournament_result_rev_$ts.log)

script1=chriweb_A1
script2=pduegg_A1
player1=IntrepidIbex
player2=AwesomeAgent


for i in $(seq 1 $n_maps)
do
    python map_generator.py -n "tournament_$i";
done

for i in $(seq 1 $n_maps)
do
    python kingsheep_tournament.py resources/random_maps/tournament_$i.map -p1m $script1 -p1n $player1 -p2m $script2 -p2n $player2 >> "$log_name" &
    python kingsheep_tournament.py resources/random_maps/tournament_$i.map -p1m $script2 -p1n $player2 -p2m $script1 -p2n $player1 >> "$log_name_rev" &
done
wait


deactivate

