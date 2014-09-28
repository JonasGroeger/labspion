labspion
========

A software to find currently logged in clients in a local network.
Active clients are retrieved from the router.

Currently works with with the following devices:

 * All routers with DD-WRT firmware

To add your device, use your own router in the 'router' variable inside `main#main`.

## License

MIT. Full license in `LICENSE.md`.

## TODO

 * Implement more router / firmware configurations (done by by overriding the `client.Router#clients` method.
