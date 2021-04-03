from typing import Dict

from aws_cdk import (
    core,
    aws_docdb as docdb,
    aws_ec2 as ec2,
    aws_iam as iam,
)


class DocumentDB(core.Construct):

    def __init__(self, scope: core.Construct, id: str,
                 config: Dict,
                 vpc: ec2.Vpc,
                 docdb_sg: ec2.SecurityGroup) -> None:
        super().__init__(scope, id)

        docdb_config = config['data']['documentdb']

        docdb_sg.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(27017),
            description='Accept traffic from the ecs cluster'
        )

        param_vars = {
            "tls": "disabled"
        }
        param_group = docdb.ClusterParameterGroup(self,
                                                  "DocDbParameterGroup",
                                                  family="docdb4.0",
                                                  parameters=param_vars,
                                                  db_cluster_parameter_group_name="nodeAPI-docdb4-0")

        login = docdb.Login(username="stan_db",
                            password=core.SecretValue.plain_text("stan_db_pw"))
        cluster = docdb.DatabaseCluster(self, "Database",
                                        master_user=login,
                                        engine_version="4.0.0",
                                        parameter_group=param_group,
                                        instance_props={
                                            "vpc": vpc,
                                            "security_group": docdb_sg,
                                            "instance_type": ec2.InstanceType.of(ec2.InstanceClass.MEMORY5,
                                                                                 ec2.InstanceSize.LARGE),
                                            "vpc_subnets": ec2.SubnetSelection(
                                                subnet_group_name=docdb_config['subnetGroupName'])
                                        }
                                        )
