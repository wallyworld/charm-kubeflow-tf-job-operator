import os
import yaml

from charmhelpers.core import hookenv
from charms.reactive import set_flag
from charms.reactive import when, when_not

from charms import layer


@when_not('layer.docker-resource.tf-operator-image.fetched')
def fetch_image():
    layer.docker_resource.fetch('tf-operator-image')


@when('layer.docker-resource.tf-operator-image.fetched')
@when_not('charm.kubeflow-tf-job-operator.started')
def start_charm():
    layer.status.maintenance('configuring container')

    conf_dir = '/etc/tf_operator'
    conf_file = 'controller_config_file.yaml'
    image_info = layer.docker_resource.get_info('tf-operator-image')
    layer.caas_base.pod_spec_set({
        'containers': [
            {
                'name': 'tf-job-operator',
                'imageDetails': {
                    'imagePath': image_info.registry_path,
                    'username': image_info.username,
                    'password': image_info.password,
                },
                'command': [
                    '/opt/mlkube/tf-operator',
                    '--controller-config-file={}/{}'.format(conf_dir,
                                                            conf_file),
                    '--alsologtostderr',
                    '-v=1',
                ],
                'ports': [
                    {
                        'name': 'dummy',
                        'containerPort': 9999,
                    },
                ],
                'config': {
                    'MY_POD_NAMESPACE': os.environ['JUJU_MODEL_NAME'],
                    'MY_POD_NAME': hookenv.service_name(),
                },
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
    })

    layer.status.maintenance('creating container')
    set_flag('charm.kubeflow-tf-job-operator.started')
