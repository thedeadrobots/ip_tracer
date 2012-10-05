## ip_tracer

* This script will pull your public and private IP addresses and upload them to pastebin as either a private, public or unlisted paste.
* Set up a cron job for any interval of time and whenever your IP address changes it will be uploaded to pastebin.  
example:
```bash
    crontab -e
    */20 * * * * /usr/bin/python ~/path/to/ip_tracer.py 
```
