import boto3
import datetime
import argparse

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
                print(f"Snapshot created:{snapshot['SnapshotId']}")

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
    parser = argparse.ArgumentParser(description="EC2 Auto Snapshot Tool")
    parser.add_argument('--desc', type=str, help="snapshot description", default="Automated backup")
    args = parser.parse_args()

    today = datetime.datetime.now().strftime("%y-%m-%d")
    desc = f"{args.desc} - {today}"

    print("fetching instances with backup=true tag...")
    instance_ids = get_backup_instances()

    if not instance_ids:
        print("No backup tagged instances found")
    else:
        print(f"Instances found: {instance_ids}")
        for instance_id in instance_ids:
            create_snapshot(instance_id, desc)