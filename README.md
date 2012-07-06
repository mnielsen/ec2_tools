ec2_tools
=========

Simple EC2 cluster management with Python. Mostly a convenience
wrapper around the `boto` library, but with two nice features:

+ Makes it easy to create named clusters, to add and kill instances,
  and to shutdown entire cluster.
+ Designed for easy integration with `fabric`.

Installation
============

From within your project's base directory, run the following shell
commands.  Note that USERNAME is the GitHub username of whoever's copy
of `ec_tools` you are using --- you may use `mnielsen` as the value,
or choose some other value, if you prefer a fork.

> git submodule add git://github.com/USERNAME/ec2_tools.git ec2
> git add .gitmodules
> git commit -am "Added ec2_tools submodule"

To update
=========

Run the following from within the `ec2` directory:

> git submodule update

Usage from the command line
===========================

> python ec2.py create CLUSTER_NAME n type 

Create a cluster with name `CLUSTER_NAME`, containing `n` machines of
type `type`.  The allowed types are `m1.small`, `c1.medium`,
`m1.large`, `m1.xlarge`, `m2.xlarge`, `m2.2xlarge`, `m2.4xlarge`,
`c1.xlarge`, `cc1.4xlarge`.


> python ec2.py show_all

Run the `show` command for all clusters now running.


> python ec2.py show CLUSTER_NAME

Show details of named cluster, including the instance type of
instances in the cluster, indices for all machines, the EC2 id, and
the public domain name.


> python ec2.py shutdown CLUSTER_NAME

Shutdown CLUSTER_NAME entirely


> python ec2.py shutdown_all

Shutdown all clusters.

> python ec2.py login CLUSTER_NAME [n]

Login to CLUSTER_NAME, to the instance with index `n` (default 0).


> python ec2.py kill CLUSTER_NAME n

Kill the instance with index `n` in CLUSTER_NAME.  If it's the last
instance in the cluster, shuts the cluster down entirely.


> python ec2.py add CLUSTER_NAME n

Add `n` extra instances to CLUSTER_NAME.  Those instances are of the
same instance type as the cluster as a whole.


Integration with Fabric
=======================

The function `ec2.public_dns_names(cluster_name)` is designed to make
integration with Fabric easy.  In particular, we can tell `fabric`
about the cluster by importing `ec2` in our fabfile, and then putting
the line:

> env.hosts = ec2.public_dns_names(CLUSTER_NAME)

into the fabfile.


Future expansion
================


To export an additional method:

> ec2.boto_object(CLUSTER_NAME, index=0)

Returns the boto object for the instance represented by CLUSTER_NAME
and index.
