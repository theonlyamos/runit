<?php
/**
 * Description
 * @authors Amos Amissah (theonlyamos@gmail.com)
 * @date    2022-07-09 15:05:41
 * @version 1.0.0
 */
require_once __DIR__ . '/manager.php';
use Runit\Controller\DotEnvEnvironment;

try {
    if ($argc >= 2) {
        $filename = $argv[1];
        $filepath = dirname($filename);
        (new DotEnvEnvironment)->load($filepath);
        include_once $filename;
        echo join(',', get_defined_functions()['user']);
    }
} catch (Exception $error) {
    echo $error->getMessage();
}
