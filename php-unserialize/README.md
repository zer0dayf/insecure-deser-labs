# PHP / Monolog 2.3.0 (8083)

The app uses real Composer-installed `monolog/monolog:2.3.0` classes and PHP's native `unserialize()`. No custom `LaunchCalculator` gadget exists. The image also contains PHPGGC at `/opt/phpggc` for generating an appropriate Monolog chain. Some Monolog gadgets activate on object destruction rather than at the initial `unserialize` call.

For benign/exploit generation commands and observed output interpretation, see `../payloads.md`. The `Monolog/RCE1` chain depends on specific versions and environments. Confirm results from actual process output; tool compatibility is not guaranteed.
