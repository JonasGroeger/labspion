labspion
========
A software to find currently logged in clients in a local network.
Active clients are retrieved from the router.

Currently works with with the following devices:

 * Netgear WNR2000v3

To add your device, you must use your own router in the 'router' variable inside `main#main`.

## License
MIT. Full license in `LICENSE.md`.

## TODO

 * Implement more Router configurations (done by by overriding the `client.Router#clients` method.
