function fn() {
  var env = karate.env; // get system property 'karate.env'
  if (!env) {
    env = 'dev';
  }
  karate.log('karate.env system property was:', env);

  var config = {
    baseUrl: 'http://api:8000'
  };

  if (env == 'qa') {
    config.baseUrl = 'http://qa-environment:8000';
  }

  // Set timeouts
  karate.configure('connectTimeout', 5000);
  karate.configure('readTimeout', 10000);

  return config;
}
