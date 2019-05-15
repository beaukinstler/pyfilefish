
from s3_integration.s3_tools import S3Connection
import pytest

@pytest.mark.s3
def test_get_buckets(test_env):
    s3conn = S3Connection()
    buckets = s3conn.get_buckets()
    assert test_env.ACTIVE_BUCKET_NAME in buckets
