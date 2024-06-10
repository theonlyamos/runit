<?php
/**
 * Description
 * @date    2022-07-09 15:05:41
 * @version 1.0.0
 */
// require_once __DIR__ . '/manager.php';
// use Runit\Controller\DotEnvEnvironment;

try {
    if ($argc >= 2) {
        $filename = $argv[1];
        $filepath = dirname($filename);
        // (new DotEnvEnvironment)->load($filepath);
        include_once $filename;
        
        $userFunctions = get_defined_functions()['user'];
        $functionParams = [];
        
        foreach ($userFunctions as $function) {
            $reflection = new ReflectionFunction($function);
            $params = $reflection->getParameters();
            $paramNames = array_map(function($param) {
                return $param->getName();
            }, $params);
            $functionParams[$function] = $paramNames;
        }
        
        echo json_encode($functionParams);
    }
} catch (Exception $error) {
    echo $error->getMessage();
}