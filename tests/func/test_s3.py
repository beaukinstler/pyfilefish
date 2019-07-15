from s3_integration.s3_tools import S3Connection
import pytest


@pytest.mark.s3
def test_get_buckets(test_env, s3conn):
    buckets = s3conn.get_buckets()
    assert test_env.ACTIVE_BUCKET_NAME in buckets


@pytest.mark.s3_slow
def test_fixture_fileobj(test_med_fileobj):
    assert test_med_fileobj.read() is not None


@pytest.mark.s3
def test_upload_sm_fileobj(test_sm_fileobj, test_env, s3conn: S3Connection):
    # GIVEN: a fileobj and a connection to and S3 bucket
    # WHEN: a fileobj is uploaded
    # THEN: no errors occur
    result = s3conn.upload_fileobj(
        test_sm_fileobj, test_env.SMALL_TEST_FILE_KEY
    )
    assert result is None


@pytest.mark.s3_slow
def test_upload_med_fileobj(test_med_fileobj, test_env, s3conn: S3Connection):
    # GIVEN: a fileobj and a connection to and S3 bucket
    # WHEN: a fileobj is uploaded
    # THEN: no errors occur
    with open(test_env.MED_TEST_FILE, "rb") as obj:
        s3conn.upload_fileobj(obj, test_env.MED_TEST_FILE_KEY)
