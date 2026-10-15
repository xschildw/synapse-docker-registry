import aws_cdk as core
import aws_cdk.assertions as assertions
import config

from common.vpc_stack import VpcStack
from docker_fargate.docker_fargate_stack import DockerFargateStack

def synth_template():
    app = core.App()
    app_config = {
        config.TAGS_CONTEXT: {"tagName": "tagValue"},
        config.STACK_NAME_PREFIX_CONTEXT: "registry-test",
        "AWS_DEFAULT_REGION": "us-east-1",
        "PORT": "443",
        "BUCKET_NAME": "test-bucket",
        "VPC_CIDR": "172.29.0.0/24",
        "ACM_CERT_ARN": "arn:aws:acm:us-east-1:111111111111:certificate/test",
    }

    vpc_stack = VpcStack(app, "dev", app_config)
    stack = DockerFargateStack(app, "dev", app_config, vpc=vpc_stack.vpc, vpc_endpoint=vpc_stack.vpc_endpoint)
    return assertions.Template.from_stack(stack)

NOTIFICATION_TOPIC = [{"Fn::ImportValue": "us-east-1-synapse-dev-global-resources-NotificationTopic"}]

def test_unhealthy_host_alarm_created():
    template = synth_template()

    template.resource_count_is("AWS::SNS::Topic", 0)
    template.has_resource_properties("AWS::CloudWatch::Alarm", {
        "MetricName": "UnHealthyHostCount",
        "Namespace": "AWS/ApplicationELB",
        "Statistic": "Maximum",
        "Period": 300,
        "Threshold": 1,
        "ComparisonOperator": "GreaterThanOrEqualToThreshold",
        "EvaluationPeriods": 3,
        "DatapointsToAlarm": 3,
        "TreatMissingData": "notBreaching",
        "AlarmActions": NOTIFICATION_TOPIC,
        "OKActions": NOTIFICATION_TOPIC,
    })

def test_no_healthy_host_alarm_created():
    template = synth_template()

    template.has_resource_properties("AWS::CloudWatch::Alarm", {
        "MetricName": "HealthyHostCount",
        "Namespace": "AWS/ApplicationELB",
        "Statistic": "Minimum",
        "Period": 60,
        "Threshold": 1,
        "ComparisonOperator": "LessThanThreshold",
        "EvaluationPeriods": 3,
        "DatapointsToAlarm": 3,
        "TreatMissingData": "breaching",
        "AlarmActions": NOTIFICATION_TOPIC,
        "OKActions": NOTIFICATION_TOPIC,
    })
