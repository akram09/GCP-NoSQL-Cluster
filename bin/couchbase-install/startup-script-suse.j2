#!/bin/bash

# This script is used to run a startup script on Debian/SUSE/RHEL based systems.

# Check if the script is being run as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root"
   exit 1
fi

NEW_HOSTNAME="new-hostname"

# Set the new hostname
hostname $NEW_HOSTNAME

# Update the /etc/hosts file
sed -i "s/^127.0.1.1.*$/127.0.1.1\t$NEW_HOSTNAME/g" /etc/hosts

# Update the /etc/hostname file
echo $NEW_HOSTNAME > /etc/hostname

# Reboot the system to apply the changes
echo "The hostname has been changed. The system will now reboot."
reboot
