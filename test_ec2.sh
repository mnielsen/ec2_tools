# Test suite for the ec2.py module

echo -e "\nRunning test suite for the ec2.py module"
echo "Note that test output needs to be inspected manually."

echo -e "\nThis will shut down all running clusters, including clusters that"
echo "you may have running other tasks.  Do you want to continue (y/n)?"
read choice
if [ $choice = "y" ]
then
echo "Ok, continuing."
else
echo "Okay, quitting"
exit 0
fi

echo -e "\nTest: python ec2.py show_all"
echo "Starting configuration of EC2:"
python ec2.py show_all

echo -e "\nTest: python ec2.py create alpha 2 m1.small"
echo "Creating a cluster named alpha with 2 m1.small instances"
python ec2.py create alpha 2 m1.small
python ec2.py show_all

echo -e "\nTest: 'create' won't create duplicate clusters"
echo "Code: python ec2.py create alpha 1 m1.small"
echo "Trying to create another cluster named alpha (should fail):"
python ec2.py create alpha 1 m1.small

echo -e "\nTest: python ec2.py create beta 1 m1.large"
echo "Creating a cluster named beta with 1 m1.large instance"
python ec2.py create beta 1 m1.large
python ec2.py show_all

echo -e "\nTest: 'create' won't create clusters with more than 20 instances"
echo "Code: python ec2.py create gamma 27 m1.small"
echo "Trying to create a cluster named gamma with 27 m1.small instances"
python ec2.py create gamma 27 m1.small

echo -e "\nTest: python kill alpha 0"
python ec2.py kill alpha 0
python ec2.py show_all

echo -e "\nTest: 'kill' won't kill instances that aren't available"
echo "python ec2.py kill alpha 1" 
python ec2.py kill alpha 1

echo -e "\nTest: python ec2.py add alpha 2"
python ec2.py add alpha 2
python ec2.py show_all

echo -e "\nTest: 'add' won't work on clusters that don't exist"
echo "Code: python ec2.py add gamma 1"
python ec2.py add gamma 1

echo -e "\nTest: python ec2.py shutdown alpha"
python ec2.py shutdown alpha
python ec2.py show_all

echo -e "\nTest: python ec2.py create gamma 2 m1.small"
python ec2.py create gamma 2 m1.small
python ec2.py show_all

echo -e "\nTest: python ec2.py shutdown_all"
python ec2.py shutdown_all
python ec2.py show_all

echo -e "\nTest: Using Amazon's EC2 tools to check that all instances really"
echo "have shut down."
echo "Code: ec2-describe-instances | grep running"
ec2-describe-instances | grep running

echo -e "\nNot tested: show, shutdown, login, ssh, ssh_all, scp, scp_all."
