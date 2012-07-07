"""
ec2_classes.py
~~~~~~~~~~~~~~

Defines the Cluster and Instance classes used by `ec2.py`.  
"""

# Why are these classes stored in a separate module from ec2.py?
#
# These classes are put in a separate module because ec2.py stores
# instances of these classes by pickling (through shelves).  Pickling
# classes defined within ec2.py creates namespace problems that can be
# solved by putting the class definitions into a separate module. See:
#
# http://stackoverflow.com/questions/3614379/attributeerror-when-unpickling-an-object

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
