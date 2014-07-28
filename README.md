labspion
========
A software to find currently logged in clients in a local network.
Active clients are retrieved from the router devices section.

Currently works with with the following devices:

 * Netgear WNR2000

To add your device, you must use your own router in the 'router' variable inside `main#main`.

## License
MIT. Full license in `LICENSE.md`.

## TODO
Currently there is no base class for all routers. In order to make this more
configurable, a common base class should be implemented. Configuration is then done
by overriding the `client.Router#recv_clients` method.
