# EC2-Auto-Backup-Tool

This script automates snapshot backups of EC2 volumes for instances tagged with backup:true

## Featrues

- Backs up running EC2 instances
- Create EBS Snapshots of attached volumes
- Auto description with timestamp

## How to use

python backup.py --desc "daily backup"