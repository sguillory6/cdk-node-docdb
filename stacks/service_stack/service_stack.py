from typing import Dict

from aws_cdk import (
    core,
    aws_ec2 as ec2,
    aws_ecs as ecs
)
from utils.stack_util import add_tags_to_stack
from .ec2_service import Ec2Service


class ServiceStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str,
                 config: Dict,
                 vpc: ec2.IVpc,
                 cluster: ecs.Cluster,
                 bastion_sg_id: str,
                 ** kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Get bastion host security group created in tne network stack
        bastion_sg = ec2.SecurityGroup.from_security_group_id(
            self,
            "ElasticsearchSG",
            security_group_id=bastion_sg_id
        )

        # create the service
        Ec2Service(self, 'Ecs', config, vpc, cluster, bastion_sg)
