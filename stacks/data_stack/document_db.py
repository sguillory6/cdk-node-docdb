from typing import Dict

from aws_cdk import (
    core,
    aws_docdb as docdb,
    aws_ec2 as ec2,
    aws_iam as iam,
)


class DocumentDB(core.Construct):

    # def __init__(self, scope: core.Construct, id: str,
    #              config: Dict,
    #              vpc: ec2.Vpc,
    #              es_sg: ec2.SecurityGroup) -> None:
    def __init__(self, scope: core.Construct, id: str,
                 config: Dict,
                 vpc: ec2.Vpc) -> None:
        super().__init__(scope, id)

        es_config = config['data']['documentdb']

        cluster = docdb.DatabaseCluster(self, "Database",
                                        master_user={
                                            "username": "stan_db"
                                        },
                                        instance_props={
                                            "instance_type": ec2.InstanceType.of(ec2.InstanceClass.MEMORY5,
                                                                                 ec2.InstanceSize.LARGE),
                                            "vpc_subnets": {
                                                "subnets": vpc.select_subnets(
                                                    subnet_group_name=es_config['subnetGroupName']).subnets
                                            },
                                            "vpc": vpc
                                        }
                                        )
