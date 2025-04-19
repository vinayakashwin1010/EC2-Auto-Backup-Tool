import boto3
import datetime
import argparse
import logging

def create_snapshot(instance_id, description):
    ec2 = boto3.client('ec2')
    volumes = ec2.describe_instances(InstanceIds=[instance_id])

    for reservation in volumes['Reservations']:
        for instance in reservation['Instances']:
            for device in instance['BlockDeviceMappings']:
                volume_id = device['Ebs']['VolumeId']
                print(f"Creating snapshot for volume: {volume_id}")
                snapshot = ec2.create_snapshot(
                    VolumeId=volume_id,
                    Description=description
                )
                logging.info(f"Snapshot created: {snapshot['SnapshotId']}")

def delete_old_snapshots(retention_days=7):
    ec2 = boto3.client('ec2')
    snapshots = ec2.describe_snapshots(OwnerIds=['self'])['Snapshots']
    now = datetime.datetime.now(datetime.timezone.utc)
    for snap in snapshots:
        start_time = snap['StartTime']
        age = (now - start_time).days
        if age > retention_days:
            logging.info(f"Deleting snapshot {snap['SnapshotId']} (age: {age} days)")
            ec2.delete_snapshot(SnapshotId=snap['SnapshotId'])

def get_backup_instances(tag_key='backup', tag_value='true'):
    ec2 = boto3.client('ec2')
    response = ec2.describe_instances(
        Filters=[
            {'Name': f'tag:{tag_key}', 'Values': [tag_value]},
            {'Name': 'instance-state-name', 'Values': ['running']}
        ]
    )
    instances = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instances.append(instance['InstanceId'])
    return instances

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    parser = argparse.ArgumentParser(description="EC2 Auto Snapshot Tool")
    parser.add_argument('--desc', type=str, help="snapshot description", default="Automated backup")
    args = parser.parse_args()

    all_regions = [r['RegionName'] for r in boto3.client('ec2').describe_regions()['Regions']]

    for region in all_regions:
        logging.info(f"--- Region: {region} ---")
        ec2 = boto3.client('ec2', region_name=region)

        instance_ids = get_backup_instances(ec2)
        if not instance_ids:
            logging.info(f"No backup-tagged instances found in region {region}")
        else:
            logging.info(f"Instances found in {region}: {instance_ids}")
            for instance_id in instance_ids:
                create_snapshot(ec2, instance_id, desc)

        delete_old_snapshots(retention_days=7)