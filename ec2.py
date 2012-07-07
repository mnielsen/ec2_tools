"""
ec2.py
~~~~~~

Simple EC2 cluster management with Python, designed to make it easy to
name and work with clusters, and to integrate with `fabric`.  

For usage information see README.md.
"""

# Standard library
import os
import shelve
import subprocess
import sys
import time

# Third party libraries
from boto.ec2.connection import EC2Connection

# The list of EC2 AMIs to use, from alestic.com
AMIS = {"m1.small" : "ami-e2af508b",
        "c1.medium" : "ami-e2af508b",
        "m1.large" : "ami-68ad5201",
        "m1.xlarge" : "ami-68ad5201",
        "m2.xlarge" : "ami-68ad5201",
        "m2.2xlarge" : "ami-68ad5201",
        "m2.4xlarge" : "ami-68ad5201",
        "c1.xlarge" : "ami-68ad5201",
        "cc1.4xlarge" : "ami-1cad5275"
        }

# The global variable `clusters` defined below is a persistent shelf
# which is used to represent all the clusters.  Note that it's
# naturally a global object because it represents a global external
# state.
#
# The keys in `clusters` are the `cluster_names`, and the values will
# be Cluster objects, defined below, which represent named EC2
# clusters.
HOME = "/home/mnielsen"
clusters = shelve.open("%s/.ec2-shelf" % HOME, writeback=True)

#### Check that required the environment variables exist
def check_environment_variables_exist(*args):
    """
    Check that the environment variables in `*args` have all been
    defined.  If any do not, print an error message and exit.
    """
    vars_exist = True
    for var in args:
        if var not in os.environ:
            print "Need to set $%s environment variable" % var
            vars_exist = False
    if not vars_exist:
        print "Exiting"
        sys.exit()

check_environment_variables_exist(
    "AWS_HOME", "AWS_KEYPAIR", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY")

# EC2 connection object
ec2_conn = EC2Connection(
    os.environ["AWS_ACCESS_KEY_ID"], os.environ["AWS_SECRET_ACCESS_KEY"])

#### The following are the wrapper functions: create, show, show_all
#### etc, which correspond to the command line API calls.

def create(cluster_name, n, instance_type):
    """
    Create an EC2 cluster with name `cluster_name`, and `n` instances
    of type `instance_type`.  Update the `clusters` shelf to include a
    description of the new cluster.
    """
    # Parameter check
    if cluster_name in clusters:
        print "A cluster with name %s already exists.  Exiting."
        sys.exit()
    if n < 1 or n > 20:
        print "Clusters must contain between 1 and 20 instances.  Exiting."
        sys.exit()
    if not instance_type in AMIS:
        print "Instance type not recognized, setting it to be 'm1.small'."
        instance_type = "m1.small"
    # Create the EC2 instances
    instances = create_ec2_instances(n, instance_type)
    # Update clusters
    clusters[cluster_name] = Cluster(cluster_name, instance_type, instances)
    clusters.close()

def show_all():
    """
    Print the details of all clusters to stdout.
    """
    if len(clusters) == 0:
        print "No clusters present."
        sys.exit()
    print "Showing all clusters."
    for cluster_name in clusters:
        show(cluster_name)

def show(cluster_name):
    """
    Print the details of cluster `cluster_name` to stdout.
    """
    cluster = get_cluster(cluster_name)
    print "Displaying instances from cluster: %s" % cluster_name
    print "Instances of type: %s" % cluster.instance_type
    print "{0:8}{1:13}{2:35}".format(
        "index", "EC2 id", "public dns name")
    for (j, instance) in enumerate(cluster.instances):
        print "{0:8}{1:13}{2:35}".format(
            str(j), instance.id, instance.public_dns_name)

def shutdown(cluster_name):
    """
    Shutdown all EC2 instances in `cluster_name`, and remove
    `cluster_name` from ` the `clusters` shelf.
    """
    cluster = get_cluster(cluster_name)
    print "Shutting down cluster %s." % cluster_name
    ec2_conn.terminate_instances(
        [instance.id for instance in clusters[cluster_name].instances])
    del clusters[cluster_name]
    clusters.close()

def shutdown_all():
    """
    Shutdown all EC2 instances in all clusters, and remove all
    clusters from the `clusters` shelf.
    """
    if len(clusters) == 0:
        print "No clusters to shut down.  Exiting."
        sys.exit()
    for cluster_name in clusters:
        shutdown(cluster_name)

def login(cluster_name, instance_index):
    """
    ssh to `instance_index` in `cluster_name`.
    """
    cluster = get_cluster(cluster_name)
    try:
        instance = cluster.instances[instance_index]
    except IndexError:
        print ("The instance index must be in the range 0 to %s. Exiting." %
               len(cluster)-1)
        sys.exit()
    print "SSHing to instance with address %s" % (instance.public_dns_name)
    keypair = "%s/%s.pem" % (os.environ["AWS_HOME"], os.environ["AWS_KEYPAIR"])
    os.system("ssh -i %s ubuntu@%s" % (keypair, instance.public_dns_name))

def kill(cluster_name, instance_index):
    """
    Shutdown instance `instance_index` in cluster `cluster_name`, and
    remove from the `clusters` shelf.  If we're killing off the last
    machine in the cluster then it runs `shutdown(cluster_name)`
    instead.
    """
    cluster = get_cluster(cluster_name)
    if instance_index < 0 or instance_index >= len(cluster.instances):
        print ("The instance index must be between 0 and %s.  Exiting." %
               (len(cluster.instances)-1,))
        sys.exit()
    if len(cluster.instances)==1:
        print "Last machine in cluster, shutting down entire cluster."
        shutdown(cluster_name)
        sys.exit()
    print ("Shutting down instance %s on cluster %s." % 
           (instance_index, cluster_name))
    ec2_conn.terminate_instances([cluster.instances[instance_index].id])
    del cluster.instances[instance_index]
    clusters[cluster_name] = cluster
    clusters.close()

def add(cluster_name, n):
    """
    Add `n` instances to `cluster_name`, of the same instance type as
    the other instances already in the cluster.
    """
    cluster = get_cluster(cluster_name)
    if n < 1:
        print "Must be adding at least 1 instance to the cluster.  Exiting."
        sys.exit()
    # Create the EC2 instances
    instances = create_ec2_instances(n, cluster.instance_type)
    # Update clusters
    cluster.add(instances)
    clusters[cluster_name] = cluster
    clusters.close()

def ssh(cluster_name, instance_index, cmd, background=False):
    """
    Run `cmd` on instance number `instance_index` on `cluster_name`.

    Runs in the background if `background == True`.  This feature is
    not currently exposed from the command line API, but may be useful
    in future.
    """
    cluster = get_cluster(cluster_name)
    try:
        instance = cluster.instances[instance_index]
    except IndexError:
        print ("The instance index must be in the range 0 to %s. Exiting." %
               len(cluster)-1)
        sys.exit()
    keypair = "%s/%s.pem" % (os.environ["AWS_HOME"], os.environ["AWS_KEYPAIR"])
    append = {True: " &", False: ""}[background]
    remote_cmd = ("'nohup %s > foo.out 2> foo.err < /dev/null %s'" %
                  (cmd, append))
    os.system(("ssh -o BatchMode=yes -i %s ubuntu@%s %s" %
               (keypair, instance.public_dns_name, remote_cmd)))

def ssh_all(cluster_name, cmd):
    """
    Run `cmd` on all instances in `cluster_name`.
    """
    cluster = get_cluster(cluster_name)
    for j in range(len(cluster.instances)):
        ssh(cluster_name, j, cmd)

def scp(cluster_name, instance_index, local_filename, remote_filename=False):
    """
    scp `local_filename` to `remote_filename` on instance
    `instance_index` on cluster `cluster_name`.  If `remote_filename`
    is not set or is set to `False` then `remote_filename` is set to
    `local_filename`.
    """
    cluster = get_cluster(cluster_name)
    try:
        instance = cluster.instances[instance_index]
    except IndexError:
        print ("The instance index must be in the range 0 to %s. Exiting." %
               len(cluster)-1)
        sys.exit()
    keypair = "%s/%s.pem" % (os.environ["AWS_HOME"], os.environ["AWS_KEYPAIR"])
    if not remote_filename:
        remote_filename = local_filename
    os.system(("scp -r -i %s %s ubuntu@%s:%s" %
               (keypair, local_filename, 
               instance.public_dns_name, remote_filename)))

def start():
    """
    Create an EC2 instance, set it up, and login.
    """
    instance = create_ec2_instance("m1.small")
    subprocess.call(["fab", "first_deploy"])
    login(instance)

#### Cluster and Instance classes

class Cluster():
    """
    Cluster objects represent a named EC2 cluster.  This class does
    relatively little, it exists mostly to encapsulate the data
    structures used to represent clusters.
    """

    def __init__(self, cluster_name, instance_type, boto_instances):
        self.cluster_name = cluster_name
        self.instance_type = instance_type
        self.instances = [Instance(boto_instance) 
                          for boto_instance in boto_instances]

    def add(self, boto_instances):
        """
        Add extra instances to the cluster.
        """
        self.instances.extend(
            [Instance(boto_instance) for boto_instance in boto_instances])

class Instance():
    """
    Instance objects represent EC2 instances in a Cluster object.  As
    with Cluster, this class does relatively little, it exists mostly
    to encapsulate the data structures used to represent instances.
    """

    def __init__(self, boto_instance):
        self.id = boto_instance.id
        self.public_dns_name = boto_instance.public_dns_name

#### Helper functions

def get_cluster(cluster_name):
    """
    Check that a cluster with name `cluster_name` exists, and return
    the corresponding Cluster object if so.
    """
    if cluster_name not in clusters:
        print "No cluster with the name %s exists.  Exiting." % cluster_name
        sys.exit()
    return clusters[cluster_name]

def create_ec2_instances(n, instance_type):
    """
    Create an EC2 cluster with `n` instances of type `instance_type`.
    Return the corresponding boto `reservation.instances` object.
    This code is used by both the `create` and `add` functions, which
    is why it was factored out.
    """
    ami = AMIS[instance_type]
    image = ec2_conn.get_all_images(image_ids=[ami])[0]
    reservation = image.run(
        n, n, os.environ["AWS_KEYPAIR"], instance_type=instance_type)
    for instance in reservation.instances:  # Wait for the cluster to come up
        while instance.update()== u'pending':
            time.sleep(1)
    time.sleep(120) # Give the ssh daemon time to start
    return reservation.instances

#### Methods to export externally

def public_dns_names(cluster_name):
    """
    Return a list containing the public dns names for `cluster_name`.

    See the docstring for this module to see how this enables easy
    integration with Fabric.
    """
    if cluster_name not in clusters:
        print ("Cluster name %s not recognized.  Exiting ec2.ec2_hosts()." %
               cluster_name)
        sys.exit()
    else:
        cluster = clusters[cluster_name]
        return [instance.public_dns_name for instance in cluster.instances]

#### External interface

if __name__ == "__main__":
    args = sys.argv[1:]
    l = len(args)
    try:
        cmd = args[0]
    except:
        cmd = None
    if cmd=="create" and l==4:
        create(args[1], int(args[2]), args[3])
    elif cmd=="show_all" and l==1:
        show_all()
    elif cmd=="show" and l==2:
        show(args[1])
    elif cmd=="shutdown" and l==2:
        shutdown(args[1])
    elif cmd=="shutdown_all" and l==1:
        shutdown_all()
    elif cmd=="login" and l==2:
        login(args[1], 0)
    elif cmd=="login" and l==3:
        login(args[1], int(args[2]))
    elif cmd=="kill" and l==3:
        kill(args[1], int(args[2]))
    elif cmd=="add" and l==3:
        add(args[1], int(args[2]))
    elif cmd=="ssh" and l==4:
        ssh(args[1], int(args[2]), args[3])
    elif cmd=="ssh_all" and l==3:
        ssh_all(args[1], args[2])
    elif cmd=="scp" and l==4:
        scp(args[1], int(args[2]), args[3])
    elif cmd=="scp" and l==5:
        scp(args[1], int(args[2]), args[3], args[4])
    else:
        print ("Command not recognized. "
               "For usage information, see README.md.")
