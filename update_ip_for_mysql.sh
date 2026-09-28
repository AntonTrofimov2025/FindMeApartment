#!/bin/bash
set -e

MY_IP=$(curl -s https://ifconfig.me)

echo -n "Enter 'Security group ID' (Symbols after 'sg-'): "
read sg_full_id

echo -n "Enter 'Security group rule ID' responsible for 3306 port (Symbols after 'sgr-'): "
read sgr_full_id

aws ec2 modify-security-group-rules \
    --group-id "sg-$sg_full_id" \
    --security-group-rules "SecurityGroupRuleId=sgr-$sgr_full_id,SecurityGroupRule={IpProtocol=tcp,FromPort=3306,ToPort=3306,CidrIpv4=$MY_IP/32}"

sleep 5
echo "🎉DONE! '3306 port Security group' has been successfully updated for specified id :)"
