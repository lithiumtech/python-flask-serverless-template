#!/bin/bash
# Usage: ./deploy-serverless.sh <universe> <region>
set -ex

UNIVERSE="$1"
REGION="$2"

function deployServerless() {
    SLS_DEBUG="*" sls deploy --region ${REGION} -s ${UNIVERSE}
}

deployServerless
