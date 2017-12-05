#!/bin/sh

HERMESROOT=/home/chris/src/hermes
PYTHONPATH=${HERMESROOT}

export PYTHONPATH

mv /home/chris/tmp/upload/sample_sftp_put3/* /home/chris/tmp/download/sample_sftp_get3


ls -lrt /home/chris/tmp/download/sample_sftp_get3

python ${HERMESROOT}/bin/hcmd.py ${HERMESROOT}/sample/sample_sftp_put3.hermes

ls -lrt /home/chris/tmp/upload/sample_sftp_put3
