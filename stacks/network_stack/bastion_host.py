from aws_cdk import (
    aws_ec2 as ec2,
    aws_iam as iam,
    core
)


class BastionHost(core.Construct):

    def __init__(self, scope: core.Construct, id: str, vpc: ec2.Vpc, bastion_sg_id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Get elasticsearch security group created in the network stack
        bastion_sg = ec2.SecurityGroup.from_security_group_id(
            self,
            "BastionHostSG",
            security_group_id=bastion_sg_id
        )

        # AMI
        amzn_linux = ec2.MachineImage.latest_amazon_linux(
            generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
            edition=ec2.AmazonLinuxEdition.STANDARD,
            virtualization=ec2.AmazonLinuxVirt.HVM,
            storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE
        )

        # Instance Role and SSM Managed Policy
        role = iam.Role(self, "InstanceSSM", assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"))

        role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonEC2RoleforSSM"))

        # Instance
        instance = ec2.Instance(self, "Instance",
                                instance_type=ec2.InstanceType("t3.medium"),
                                machine_image=amzn_linux,
                                vpc=vpc,
                                role=role,
                                vpc_subnets=ec2.SubnetSelection(subnet_name="Public"),
                                security_group=bastion_sg
                                )

