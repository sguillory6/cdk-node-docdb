
from typing import Dict
from aws_cdk import (
    aws_ec2 as ec2,
    core,
)

from utils.stack_util import add_tags_to_stack
from .vpc import Vpc
from .bastion_host import BastionHost
from .security_group import SecurityGroup


class NetworkStack(core.Stack):
    vpc: ec2.IVpc
    bastion_sg_id: str

    def __init__(self, scope: core.Construct, id: str, config: Dict, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Apply common tags to stack resources.
        add_tags_to_stack(self, config)

        vpc_construct = Vpc(self, 'Vpc', config)
        self.vpc = vpc_construct.vpc

        sg = SecurityGroup(self, "SecurityGroups", self.vpc)
        self.bastion_sg_id = sg.bastion_sg.security_group_id
        self.docdb_sg_id = sg.docdb_sg.security_group_id

        BastionHost(self, "BastionHost", vpc=self.vpc, bastion_sg_id=self.bastion_sg_id)
