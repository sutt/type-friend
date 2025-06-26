# erase and display ips script functions

for the devscripts project cli: add subcommands on devscripts for erase_ip and list_ips that will query the successful_spell_ips table. 

list_ips should display a tabular output of what's in the table currently.

erase_ip should accept a required argument of an ip address which will drop that record from the table if present.

You should run commands while adding code to verify your steps are working, e.g. with "/run" and "/test" commands. Don't forget the guidance here of what environment to use to execute commands.

Also you can run the devscripts.sh script.

Do not need to add modifications for  uv environment to other commands which are built on a virtualenv workflow. Continue to use the uv recipe for this feature.

add tests for this and run them to make sure they work by using the "/test" command.

Prefer the native uv run of python over using docker start or docker container. You do have a databse available to you, the tf-db is currently running on localhost:5432 so your app can start up and connec to it.

After the tests pass, summarize what was tested and suggest improvments.

And give several examples of how to manually test. Supply values based on what you query from the actual database.