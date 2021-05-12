from typing import Dict
from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_elasticloadbalancingv2 as elbv2,
    aws_iam as iam,
    aws_servicediscovery,
    core,
)


class Ec2Service(core.Construct):

    def __init__(self, scope: core.Construct, id: str,
                 config: Dict,
                 vpc: ec2.Vpc,
                 cluster: ecs.Cluster,
                 bastion_sg: ec2.ISecurityGroup,
                 ) -> None:
        super().__init__(scope, id)
        ecs_config = config['compute']['ecs']
        mongodb_config = config['mongodb']
        app_config =  config['app']

        # Create Task Definition
        task_definition = ecs.Ec2TaskDefinition(
            self, "NodeApiTaskDefinition",
            network_mode=ecs.NetworkMode.AWS_VPC,
            execution_role=iam.Role.from_role_arn(self, "NodeApiTaskRole",
                                                  role_arn="arn:aws:iam::750353892954:role/ecsTaskExecutionRole"
                                                  )
        )
        container = task_definition.add_container(
            "web",
            image=ecs.ContainerImage.from_registry("sguillory6/react-node-backend:2.1"),
            cpu=256,
            memory_limit_mib=256,
            environment={
                "NODE_ENV": app_config['node_env'],
                "APP_PORT": app_config['port'],
                "MONGODB_HOST": mongodb_config['host'],
                "MONGODB_PORT": mongodb_config['port'],
                "MONGODB_DATABASE": mongodb_config['database'],
                "MONGODB_USERNAME": mongodb_config['username'],
                "MONGODB_PASSWORD": mongodb_config['password']
            },
            logging=ecs.LogDrivers.aws_logs(stream_prefix="NodeAPI-DocDB")
        )
        port_mapping = ecs.PortMapping(
            container_port=3080,
            host_port=3080,
            protocol=ecs.Protocol.TCP
        )
        container.add_port_mappings(port_mapping)

        # Create security group for service
        service_sg = ec2.SecurityGroup(
            self, 'NodeApiServiceSG',
            security_group_name='NodeApiServiceSG',
            vpc=vpc,
            description='Node API Service security group',
        )
        service_sg.add_ingress_rule(
            peer=bastion_sg,
            connection=ec2.Port.tcp(3080),
            description='Accept traffic from the eks cluster in https'
        )

        # Create Service
        service = ecs.Ec2Service(
            self, "NodeApiService",
            cluster=cluster,
            task_definition=task_definition,
            daemon=False,
            desired_count=3,
            min_healthy_percent=100,
            max_healthy_percent=200,
            vpc_subnets=ec2.SubnetSelection(subnet_group_name=ecs_config['subnetGroupName']),
            security_group=service_sg
        )

        # Create ALB
        lb = elbv2.ApplicationLoadBalancer(
            self, "LB",
            vpc=vpc,
            internet_facing=True,
            vpc_subnets=ec2.SubnetSelection(subnet_group_name=ecs_config['publicSubnetGroupName'])
        )
        listener = lb.add_listener(
            "PublicListener",
            port=80,
            open=True
        )

        health_check = elbv2.HealthCheck(
            interval=core.Duration.seconds(60),
            path="/api/users",
            timeout=core.Duration.seconds(5)
        )

        # Attach ALB to ECS Service
        listener.add_targets(
            "ECS",
            port=3080,
            protocol=elbv2.ApplicationProtocol.HTTP,
            targets=[service],
            health_check=health_check,
        )
