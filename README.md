EC2 Tools
=========

EC2 Tools provides simple EC2 cluster management with Python. It's
mostly a convenience wrapper around the `boto` library, but adds two
useful features:

+ Makes it easy to create and work with named clusters.
+ Easily integrated with `fabric`.

I wrote it for my own use, and it's both rough and _very_ incomplete.
The goal was to make it easier for me to test code out on EC2.  It's
not even close to providing the control you need for deploying real
applications to EC2 --- it doesn't handle things like security groups,
control over ports, and so on.

Installation
------------

To install, from within your project's base directory, clone the EC2
Tools repository into a new directory named `ec2`

    git clone https://github.com/mnielsen/ec2_tools.git ec2
 
Then add `ec2/*` to your `.gitignore` file, and commit:
 
    git commit -am "Added ec2_tools"

Edit `ec2/ec2.py` and change the value of `HOME` to point to your home
directory.

To update
---------

If EC Tools changes, you may run the following from within the `ec2`
directory to update to the latest version:

    git pull

Usage from the command line
---------------------------

    python ec2/ec2.py create CLUSTER_NAME n type 

Create a cluster with name `CLUSTER_NAME`, containing `n` machines of
type `type`.  The allowed types are `m1.small`, `c1.medium`,
`m1.large`, `m1.xlarge`, `m2.xlarge`, `m2.2xlarge`, `m2.4xlarge`,
`c1.xlarge`, `cc1.4xlarge`.  The resulting instances are basic Ubuntu
machine images provided by alestic.com.

    python ec2.py show CLUSTER_NAME

Show details of named cluster, including the instance type of
instances in the cluster, indices for all machines, the EC2 id, and
the public domain name.

    python ec2/ec2.py show_all

Run the `show` command for all clusters now running.

    python ec2/ec2.py shutdown CLUSTER_NAME

Shutdown CLUSTER_NAME entirely.

    python ec2/ec2.py shutdown_all

Shutdown all clusters.

    python ec2/ec2.py login CLUSTER_NAME [n]

Login to CLUSTER_NAME, to the instance with index `n` (default 0).

    python ec2.py kill CLUSTER_NAME n

Kill the instance with index `n` in CLUSTER_NAME.  If it's the sole
remaining instance in the cluster, running this command shuts the
cluster down entirely.

    python ec2.py add CLUSTER_NAME n

Add `n` extra instances to CLUSTER_NAME.  Those instances are of the
same instance type as the cluster as a whole.

    python ec2.py ssh CLUSTER_NAME n cmd

Run `cmd` on instance number `n` on CLUSTER_NAME.  Output from the
command is directed to `foo.out` and `foo.err` on the instance.

    python ec2.py ssh_all CLUSTER_NAME cmd

As for `ssh`, but executed on all instances in CLUSTER_NAME, not just
a single instance.

    python ec2.py scp CLUSTER_NAME n local_filename [remote_filename]

Copies `local_filename` to `remote_filename` on instance `n` on
CLUSTER_NAME.  `remote_filename` defaults to `.`.

    python ec2.py scp_all CLUSTER_NAME local_filename [remote_filename]

As for `scp`, but executed on all instances in CLUSTER_NAME, not just
a single instance.

Integration with fabric
-----------------------

The function `ec2.public_dns_names(cluster_name)` is designed to make
integration with `fabric` easy.  In particular, we can tell `fabric`
about the cluster by running `import ec2.ec2 as ec2` in our fabfile,
and then putting the line:

    env.hosts = ec2.public_dns_names(CLUSTER_NAME)

into the fabfile.

Testing
-------

Run:

    bash ec2/test_ec2.sh > ec2/test.out

Note that the test results must be manually inspected to determine if
they are executing correctly.
