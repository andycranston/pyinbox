# pyinbox - A Python CGI script to implement a web based inbox (caution: totally insecure !!!)

These bits of code implement a web based inbox. Developed on Ubuntu 22.04 LTS using postfix to allow email
delivery and lighttpd to serve up the index GUI. Also uses a small bit of C code to put the email files
in a subdirectory called `.smua` in each users home directory.

## WARNING ::: WARNING ::: WARNING

This is for experimentation / debugging only. It is not an email system!!!

I recommend using a separate host / virtual machine guest to run just this. While this seems wasteful
you will not be regretting it if/when (and more likely when) the host gets compromised.

At the very least put a firewall around it to only allow incoming SMTP traffic on port 25 from the local LAN and nowhere else.

## Assumptions

The `lighttpd` web server is running as user `arris53` and ggroup `general`.

## Install postfix

Install postfix and mailutils:

```
sudo apt install postfix mailutils
```

During the configuration of postfix select:

```
Internet
```

for the operating mode (this allows incoming mail on SMTP port 25) and specify a domain
name that also includes the hostname - for example:

```
audt.espmap.lab
```

So mail can now be sent to users such as:

```
arris53@audt.espmap.lab
localadm@audt.espmap.lab
```

## Create a .forward file

For each local Linux user that wants to use the Python inbox create a directory called:

```
$HOME/.smua
```

Ensure it has the following mode, owner and group:

```
drwx------   arris53   general 
```

Create a $HOME/.forward file with just one line:

```
|"/usr/local/bin/smua"

## Create the ~arris53 directory and run make

The arris53 directory in the HTML root needs to be created:

```
mkdir '/home/arris53/www/html/~arris53'
```

Set up an empty smua entry in /usr/local/bin:

```
sudo touch /usr/local/bin/smua
sudo chown arris53:general /usr/local/bin/smua
```

Now run make:

```
make
```

Send email to:

```
arris53@audt.espmad.lab
```

Visit:

```
https://10.20.30.40/~arris53/inbox.py
```

Change 10.20.30.40 to the IP address of the lighttpd web server.



---------------
End of Document
