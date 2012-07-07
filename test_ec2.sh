echo -e "\nTest: Showing that show_all reveals the state of all clusters"
echo "Starting configuration of EC2:"
python ec2.py show_all

echo -e "\nTest: Showing that create can be used to create a cluster"
echo "Creating a cluster named alpha with 2 m1.small instances"
python ec2.py create alpha 2 m1.small
echo "Configuration:"
python ec2.py show_all

echo -e "\nTest: Showing that create won't create duplicate clusters"
echo "Trying to create another cluster named alpha (should fail):"
python ec2.py create alpha 1 m1.small

echo -e "\nTest: Showing the use of create to create a second cluster"
echo "Creating a cluster named beta with 1 m1.large instance"
python ec2.py create beta 1 m1.large
echo "Configuration:"
python ec2.py show_all

echo -e "\nTest: create won't create clusters with more than 20 instances"
echo "Trying to create a cluster named gamma with 27 m1.small instances"
python ec2.py create gamma 27 m1.small

echo -e "\nTest: kill to remove instance 0 from alpha cluster"
python ec2.py kill alpha 0
echo "Configuration:"
python ec2.py show_all

echo -e "\nTest: kill won't kill instances that aren't available"
python ec2.py kill alpha 1

echo -e "\nTest: Using add to add two extra instances to a cluster"
python ec2.py add alpha 2
echo "Configuration:"
python ec2.py show_all

echo -e "\nTest: add won't work on clusters that don't exist"
python ec2.py add gamma 1

echo -e "\nTest: Shutdown cluster alpha"
pyton ec2.py shutdown alpha
echo "Configuration:"
python ec2.py show_all

echo -e "\nTest: Create a new cluster gamma"
pyton ec2.py create gamma 2 m1.small
echo "Configuration:"
python ec2.py show_all

echo -e "\nTest: Shutting down all clusters"
pyton ec2.py shutdown_all
echo "Configuration:"
python ec2.py show_all

echo -e "\nNot tested: login, ssh, ssh_all, scp, scp_all."