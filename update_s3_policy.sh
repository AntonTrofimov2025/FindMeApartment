#!/bin/bash
set -e

echo -n "Enter AWS S3 Bucket Name [default: fma-server-bucket]: "
read bucket_name

if [ -z "$bucket_name" ]; then
    bucket_name="fma-server-bucket"
fi

echo "Deactivating Block Public Access constraints for '$bucket_name'..."
aws s3api put-public-access-block \
    --bucket "$bucket_name" \
    --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false"

sleep 2

echo "Generating and injecting secure Bucket Policy for '$bucket_name'..."

POLICY_JSON=$(cat <<FMA_EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": [
                "arn:aws:s3:::${bucket_name}/listings/*",
                "arn:aws:s3:::${bucket_name}/users/*"
            ]
        }
    ]
}
FMA_EOF
)

aws s3api put-bucket-policy \
    --bucket "$bucket_name" \
    --policy "$POLICY_JSON"

sleep 5
echo "DONE! AWS S3 Bucket Policy for '$bucket_name' has been successfully applied! 🎉"
