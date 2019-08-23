from aws_cdk import (
  core,
  aws_s3 as s3,
  aws_ec2 as ec2,
  aws_ecs as ecs,
  aws_elasticloadbalancingv2 as elbv2,
  aws_autoscaling as autoscaling
)

class SynapseDockerRegistryStack(core.Stack):

  def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
    super().__init__(scope, id, **kwargs)

    STACK = scope.node.try_get_context("STACK")
    VPC_NAME = scope.node.try_get_context("VPC_NAME")
    KEY_NAME = scope.node.try_get_context("KEY_NAME")

    # VPC where the docker registry cluster will be deployed
    vpc = ec2.Vpc.from_lookup(scope=self, id="sdr-vpc", vpc_id=VPC_NAME)

    # Bucket to host the cert files that need to be provisioned on instances
    bucket_id = "synapse-docker-registry-certs.{}.sagebase.org".format(STACK)
    bucket = s3.Bucket(self, id=bucket_id)

    # Cluster
    cluster_id = "sdr-cluster"
    cluster = ecs.Cluster(self, id=cluster_id, vpc=vpc)

    # Autoscaling group
    asg = autoscaling.AutoScalingGroup(
      self,
      "docker-fleet",
      instance_type=ec2.InstanceType.of(
        ec2.InstanceClass.BURSTABLE3,
        ec2.InstanceSize.MICRO
      ),
      machine_image=ec2.AmazonLinuxImage(),
      min_capacity=2,
      desired_capacity=2,
      key_name=KEY_NAME,
      vpc=vpc
    )
    asg.add_user_data(
      "yum install python3 -y",
      "pip3 install awscli --upgrade",
      "export PATH=/usr/local/bin:\$PATH",
      "aws s3 cp s3://xschildw-test-userdata.dev.sagebase.org/test.txt /home/ec2-user/test.txt",
      "chown \"ec2-user:ec2-user\" /home/ec2-user/test.txt",
      "chmod 755 /home/ec2-user/test.txt"
    )

    # Task definition




