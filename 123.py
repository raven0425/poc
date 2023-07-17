import boto3
from datetime import datetime, timedelta

# Create a session using your AWS credentials
session = boto3.Session(
    aws_access_key_id='YOUR_ACCESS_KEY',
    aws_secret_access_key='YOUR_SECRET_ACCESS_KEY',
    region_name='YOUR_REGION'
)

# Create an EC2 client using the session
ec2_client = session.client('ec2')

# Get the current date
current_date = datetime.now()

# Calculate the cutoff date (30 days ago)
cutoff_date = current_date - timedelta(days=30)

# Get a list of all EBS volumes in an available state
response = ec2_client.describe_volumes(Filters=[{'Name': 'status', 'Values': ['available']}])

# Iterate over the volumes and check their creation dates
for volume in response['Volumes']:
    volume_id = volume['VolumeId']
    creation_date = volume['CreateTime']
    
    # Convert the creation date string to a datetime object
    creation_date = datetime.strptime(creation_date, '%Y-%m-%dT%H:%M:%S.%fZ')
    
    # Check if the volume is older than 30 days
    if creation_date < cutoff_date:
        # Create a snapshot of the volume
        snapshot_response = ec2_client.create_snapshot(VolumeId=volume_id, Description='Snapshot of volume')
        snapshot_id = snapshot_response['SnapshotId']
        print(f"Snapshot {snapshot_id} created for volume {volume_id}")
        
        # Get the volume's tags
        volume_tags = volume.get('Tags', [])
        
        # Add tags to the snapshot
        snapshot_tags = [{'Key': tag['Key'], 'Value': tag['Value']} for tag in volume_tags]
        ec2_client.create_tags(Resources=[snapshot_id], Tags=snapshot_tags)
        print(f"Tags added to snapshot {snapshot_id}: {snapshot_tags}")
        
        # Delete the volume
        ec2_client.delete_volume(VolumeId=volume_id)
        print(f"Volume {volume_id} deleted.")
    else:
        print(f"Volume {volume_id} is not older than 30 days. Ignoring...")
