# erase and display ips script functions

for the devscripts project cli: add subcommands on devscripts for erase_ip and list_ips that will query the successful_spell_ips table. 

list_ips should display a tabular output of what's in the table currently.

erase_ip should accept a required argument of an ip address which will drop that record from the table if present.

add tests for this and run them to make sure they work.