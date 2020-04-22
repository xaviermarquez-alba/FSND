/* @TODO replace with your variables
 * ensure all variables on this page match your project
 */

export const environment = {
  production: false,
  apiServerUrl: 'http://127.0.0.1:5000', // the running FLASK api server url
  auth0: {
    url: 'xaviermm.auth0.com', // the auth0 domain prefix
    audience: 'choffe shop', // the audience set for the auth0 app
    clientId: 'jBEU9HBEoHIKgI0XRa1jwEgJdLKwDVoY', // the client id generated for the auth0 app
    callbackURL: 'http://127.0.0.1:8100', // the base url of the running ionic application. 
  }
};
