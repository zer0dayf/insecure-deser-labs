<?php
// Produces benign PHP data only; genuine Monolog chain comes from PHPGGC.
echo base64_encode(serialize(['message' => 'hello-from-php', 'count' => 1])) . PHP_EOL;
