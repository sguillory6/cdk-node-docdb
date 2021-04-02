from typing import Dict
from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns,
    aws_servicediscovery,
    aws_iam as iam,
    core,
)


class Ecs(core.Construct):
    _config: Dict
    _cluster: ecs.Cluster

    def __init__(self, scope: core.Construct, id: str,
                 config: Dict,
                 vpc: ec2.Vpc,
                 # es_sg: ec2.ISecurityGroup,
                 ) -> None:
        super().__init__(scope, id)
        self._config = config

        # Create cluster control plane
        self.__create_ecs_control_plane(vpc)

        # Create cluster compute nodes
        self.__create_ec2_capacity()

    def __create_ecs_control_plane(self, vpc: ec2.Vpc) -> ecs.Cluster:
        # Creating ECS Cluster in the VPC created above
        self.ecs_cluster = ecs.Cluster(
            self, "ECSCluster",
            vpc=vpc,
            cluster_name=self._config['name']
        )

    def __create_ec2_capacity(self):
        # Adding EC2 capacity to the ECS Cluster
        ecs_config = self._config['compute']['ecs']
        self.asg = self.ecs_cluster.add_capacity(
            "ECSEC2Capacity",
            instance_type=ec2.InstanceType.of(
                                 ec2.InstanceClass.STANDARD5,
                                 ec2.InstanceSize.LARGE),
            key_name=ecs_config['keyName'],
            min_capacity=2,
            max_capacity=10,
            vpc_subnets=ec2.SubnetSelection(subnet_name=ecs_config['subnetGroupName'])
        )

