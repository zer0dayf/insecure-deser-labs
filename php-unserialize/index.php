<?php
// Real Monolog library classes loaded via Composer, not a lab-defined gadget.
require __DIR__ . '/vendor/autoload.php';

fwrite(STDOUT, "LOCAL LAB - paste Base64 PHP serialization:\n");
$b64 = trim(fgets(STDIN));
$data = base64_decode($b64, true);
if ($data === false) { throw new InvalidArgumentException('Invalid Base64'); }
// VULNERABLE SINK: do not unserialize untrusted input in real applications.
$value = unserialize($data);
fwrite(STDOUT, "Deserialized type: " . get_debug_type($value) . PHP_EOL);
// Avoid var_export() or implicit stringification of potentially hostile objects.
if (is_array($value) || is_scalar($value)) {
    fwrite(STDOUT, "Deserialized value: " . var_export($value, true) . PHP_EOL);
} else {
    fwrite(STDOUT, "Object reconstructed; side effects, if any, appear in output.\n");
}
unset($value); // destructor gadgets may trigger here; never label that as harmless
