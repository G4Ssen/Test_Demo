function fn() {
  var env = karate.env || 'dev';

  var config = {
    baseUrl:          'http://localhost:8000/api/v1',
    uploadTimeoutMs:  10000,
    processTimeoutMs: 30000,
    classifyTimeoutMs: 15000
  };

  if (env === 'ci') {
    // Docker Compose service name used in GitHub Actions
    config.baseUrl = 'http://api-service:8000/api/v1';
  }

  if (env === 'docker') {
    config.baseUrl = 'http://host.docker.internal:8000/api/v1';
  }

  if (env === 'staging') {
    config.baseUrl = 'https://staging-api.example.com/api/v1';
  }

  karate.log('Karate env:', env, '| baseUrl:', config.baseUrl);
  return config;
}
