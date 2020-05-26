# (jwt_bearer_token.py) JWT bearer token generator for kube-arangodb

## General information

Previously, ArangoDB cloud installations were relying on arangodb-exporter for exposing Prometheus metrics.
Starting from 3.6.0, there's a built-in endpoint /_admin/metrics.
The sad part is that kube-arangodb operator does not generate a secret with a jwt bearer token, thus leaving the endpoint inaccessible for Prometheus. It's possible to use basic auth with credentials stored in an automatically generated secret with root password, which doesn't seem to be safe. Moreover, basic auth-based access is disabled in cluster deployments.
To summarize, you need to manually generate a secret with jwt-token for further usage in ServiceMonitor.
The script does just that - it retrieves a jwt-secret generated by operator, creates a jwt bearer token and saves it in a new secret.
Note: kube-arangodb is likely to introduce its own automation, and its current lack of the feature served like an excuse to finally try Kubernetes API client. The script can be bundled in a container to be run trough a Kubernetes job.

## Settings

### Mandatory

* KUBERNETES_SERVICE_PORT_HTTPS (e.g. 6443);
* KUBERNETES_SERVICE_HOST (e.g. 10.156.0.37);
* JWT_SECRET_NAME (e.g. kube-arangodb-deployment-jwt; the name of the secret created by kube-arangodb);
* JWT_BEARER_TOKEN_SECRET_NAME (e.g. kube-arangodb-deployment-jwt-bearer-token; the secret which will contain the newly generated token).

### Optional

* TOKEN (if it's not passed through the env, it will be read from /var/run/secrets/kubernetes.io/serviceaccount/token);
* NAMESPACE (if it's not passed through the env, it will be read from /var/run/secrets/kubernetes.io/serviceaccount/namespace);
* VERIFY_SSL=False (if it's set to True, a CA certificate will be read from: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt);
* REPLACE_SECRET=False (if it's set to True, a pre-existing secret with a name specified in JWT_BEARER_TOKEN_SECRET_NAME will be replaced).