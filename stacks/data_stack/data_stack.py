from typing import Dict

from aws_cdk import (
    core,
    aws_ec2 as ec2,
)
from utils.stack_util import add_tags_to_stack
from .document_db import DocumentDB


class DataStack(core.Stack):
    vpc: ec2.IVpc

    def __init__(self, scope: core.Construct, id: str,
                 config: Dict,
                 vpc: ec2.Vpc,
                 docdb_sg_id: str,
                 ** kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Apply common tags to stack resources.
        add_tags_to_stack(self, config)

        # Get docdb security group created in tne network stack
        docdb_sg = ec2.SecurityGroup.from_security_group_id(
            self,
            "DocumentDBSG",
            security_group_id=docdb_sg_id
        )
        DocumentDB(self, 'Vpc', config, vpc, docdb_sg)
