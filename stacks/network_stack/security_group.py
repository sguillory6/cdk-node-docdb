from aws_cdk import (
    core,
    aws_ec2 as ec2
)


class SecurityGroup(core.Construct):
    _vpc: ec2.Vpc
    bastion_sg: ec2.SecurityGroup

    def __init__(self, scope: core.Construct, id: str, vpc: ec2.Vpc) -> None:
        super().__init__(scope, id)

        self._vpc = vpc
        self.__create_bastion_sg()

    # Create elasticsearch security group
    def __create_bastion_sg(self) -> ec2.SecurityGroup:
        self.bastion_sg = ec2.SecurityGroup(
            self, 'BastionHost',
            security_group_name='BastionHostSG',
            vpc=self._vpc,
            description='Bastion Host security group',
        )
