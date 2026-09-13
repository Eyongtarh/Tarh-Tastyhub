#!/usr/bin/env bash
#
# Creates a CloudFront distribution in front of the S3 bucket already used
# for static/media (custom_storages.py sets ACL='public-read' per object,
# so this script does NOT touch bucket policy/ACLs - it just points
# CloudFront at objects that are already public).
#
# Requires an IAM identity with cloudfront:CreateDistribution and
# cloudfront:GetDistribution - the tarh-tasty-hub-user IAM user did not
# have this as of 2026-09-13, so run with an identity that does (e.g. an
# admin profile), or attach a policy granting those actions first.
#
# Usage:
#   AWS_STORAGE_BUCKET_NAME=my-bucket AWS_S3_REGION_NAME=eu-north-1 \
#     ./scripts/setup_cloudfront.sh [--wait]
#
# On success, prints the distribution domain to set as CLOUDFRONT_DOMAIN
# in Heroku config vars (settings.py already reads it - see DEPLOYMENT.md).

set -euo pipefail

BUCKET_NAME="${AWS_STORAGE_BUCKET_NAME:?Set AWS_STORAGE_BUCKET_NAME}"
REGION="${AWS_S3_REGION_NAME:?Set AWS_S3_REGION_NAME}"
ORIGIN_DOMAIN="${BUCKET_NAME}.s3.${REGION}.amazonaws.com"
CALLER_REFERENCE="tarh-tastyhub-static-$(date +%s)"
WAIT_FOR_DEPLOY=false

if [[ "${1:-}" == "--wait" ]]; then
  WAIT_FOR_DEPLOY=true
fi

echo "Origin: ${ORIGIN_DOMAIN}"

DIST_CONFIG=$(cat <<EOF
{
  "CallerReference": "${CALLER_REFERENCE}",
  "Comment": "Tarh Tastyhub static/media - HTTP/2 in front of S3",
  "Enabled": true,
  "HttpVersion": "http2",
  "IsIPV6Enabled": true,
  "PriceClass": "PriceClass_100",
  "Origins": {
    "Quantity": 1,
    "Items": [
      {
        "Id": "s3-${BUCKET_NAME}",
        "DomainName": "${ORIGIN_DOMAIN}",
        "CustomOriginConfig": {
          "HTTPPort": 80,
          "HTTPSPort": 443,
          "OriginProtocolPolicy": "https-only",
          "OriginSslProtocols": {
            "Quantity": 1,
            "Items": ["TLSv1.2"]
          }
        }
      }
    ]
  },
  "DefaultCacheBehavior": {
    "TargetOriginId": "s3-${BUCKET_NAME}",
    "ViewerProtocolPolicy": "redirect-to-https",
    "AllowedMethods": {
      "Quantity": 2,
      "Items": ["GET", "HEAD"],
      "CachedMethods": {
        "Quantity": 2,
        "Items": ["GET", "HEAD"]
      }
    },
    "Compress": true,
    "CachePolicyId": "658327ea-f89d-4fab-a63d-7e88639e58f6"
  }
}
EOF
)

echo "Creating distribution..."
RESULT=$(aws cloudfront create-distribution --distribution-config "${DIST_CONFIG}")

DIST_ID=$(echo "${RESULT}" | python3 -c "import json,sys; print(json.load(sys.stdin)['Distribution']['Id'])")
DIST_DOMAIN=$(echo "${RESULT}" | python3 -c "import json,sys; print(json.load(sys.stdin)['Distribution']['DomainName'])")

echo "Distribution created: ${DIST_ID}"
echo "Domain: ${DIST_DOMAIN}"

if [[ "${WAIT_FOR_DEPLOY}" == "true" ]]; then
  echo "Waiting for deployment (typically 5-15 minutes)..."
  aws cloudfront wait distribution-deployed --id "${DIST_ID}"
  echo "Deployed."
fi

cat <<MSG

Next steps:
1. Set this in Heroku config vars:
     heroku config:set CLOUDFRONT_DOMAIN=${DIST_DOMAIN}
2. Confirm static/media load correctly from the new domain before
   relying on it (Cache-Control headers are read from the object, set
   in custom_storages.py - no extra CloudFront cache policy work needed
   beyond the managed policy already used above).
3. To roll back, unset CLOUDFRONT_DOMAIN - settings.py falls back to the
   raw S3 domain automatically.
MSG
