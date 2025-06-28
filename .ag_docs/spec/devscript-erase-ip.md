for the devscripts project cli: add subcommands on devscripts for erase_ip and list_ips that will query the successful_spell_ips table. 

list_ips should display a tabular output of what's in the table currently.

erase_ip should accept a required argument of an ip address which will drop that record from the table if present.

Don't rely on docker exec being available, instead do orm queries in python and attach those python functions to devscripts.sh subcommands.