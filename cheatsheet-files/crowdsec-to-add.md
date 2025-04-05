Setup

    Setup and Start crowdsec metabase dashboard

sudo cscli dashboard setup

Optional arguments:

    -l |--listen : ip address to listen on for docker (default is 127.0.0.1)
    -p |--port : port to listen on for docker (default is 8080)
    --password : password for metabase user (default is generated randomly)
    -f | --force : override existing setup

cscli dashboard setup
tip

The dashboard setup command will output generated credentials for metabase.

Those are stored in /etc/crowdsec/metabase/metabase.yaml

Now you can connect to your dashboard, sign-in with your saved credentials then click on crowdsec Dashboard to get this:

Dashboard docker image can be managed by cscli and docker cli also. Look at the cscli help command using

sudo cscli dashboard -h

Remove the dashboard

    Remove crowdsec metabase dashboard

sudo cscli dashboard remove [-f]

Optional arguments:

    -f | --force : will force remove the dashboard

Stop the dashboard

    Stop crowdsec metabase dashboard

sudo cscli dashboard stop

Start the dashboard

    Start crowdsec metabase dashboard

sudo cscli dashboard start

Note: Please look at this documentation for those of you that would like to deploy metabase without using docker.
