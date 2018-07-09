import yaml

from charms.reactive import set_flag
from charms.reactive import when_not

from charms import layer
from charms.layer.basic import pod_spec_set


@when_not('charm.kubeflow-tf-job-operator.started')
def start_charm():
    layer.status.maintenance('configuring tf-job-operator container')

    conf_dir = '/etc/tf_operator'
    conf_file = 'controller_config_file.yaml'
    pod_spec_set(yaml.dump({
        'containers': [
            {
                'name': 'tf-job-operator',
                'image': ('gcr.io/kubeflow-images-public/'
                          'tf_operator:v20180329-a7511ff'),
                'command': [
                    '/opt/mlkube/tf-operator',
                    '--controller-config-file={}/{}'.format(conf_dir,
                                                            conf_file),
                    '--alsologtostderr',
                    '-v=1',
                ],
                'files': [
                    {
                        'name': 'configs',
                        'mountPath': conf_dir,
                        'files': {
                            conf_file: yaml.dump({
                                'grpcServerFilePath': (
                                    '/opt/mlkube/grpc_tensorflow_server/'
                                    'grpc_tensorflow_server.py'
                                ),
                            }),
                        },
                    },
                ],
            },
        ],
    }))

    layer.status.active('ready')
    set_flag('charm.kubeflow-tf-job-operator.started')
