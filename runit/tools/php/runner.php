<?php
/**
 * Description
 * @authors Amos Amissah (theonlyamos@gmail.com)
 * @date    2022-05-09 09:58:31
 * @version 1.0.0
 */

 require_once __DIR__ . '/manager.php';
 use Runit\Controller\DotEnvEnvironment;
 

$functionArguments;

try {
    if ($argc > 1) {
        $filename = $argv[1];
        $functionname = $argv[2];
        $filepath = dirname($filename);
        (new DotEnvEnvironment)->load($filepath);
        
        include_once($filename);

        if ($argc > 3) {
            $functionArguments = $argv[3];
        }

        if (!isset($functionArguments)) {
            ($functionname)();
        } else {
            ($functionname)($functionArguments);
        }
    
    }
} catch (Exception $th) {
    echo $th;
}
