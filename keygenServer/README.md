This is the code for API key Generation

## Client

This is the interface a user goes to for requesting an API key.

The client asks the server to generate a new API key. Only the client website 
can request new keys.

Login is handled through google auth. Keys are associated with email addresses.

## Server

Server handles requests for new keys. It also exposes and endpoint for verifying
that a key exists. Currently it doesn't do anything more can check existance of 
keys, but we will be fixing that soon.


