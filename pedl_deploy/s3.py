import boto3

s3 = boto3.resource('s3')


def empty_bucket(bucket_name):
    bucket = s3.Bucket(bucket_name)
    bucket.objects.all().delete()