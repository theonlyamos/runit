try {
    if (process.argv.length > 2) {
        const filename = process.argv[2];
        const methods = require(filename);
        const functionParams = {};

        Object.keys(methods).forEach((funcName) => {
            const func = methods[funcName];
            if (typeof func === 'function') {
                const paramNames = getParamNames(func);
                functionParams[funcName] = paramNames;
            }
        });

        console.log(JSON.stringify(functionParams));
    }
} catch (error) {
    console.log(error.toString().split('\n')[0]);
}

function getParamNames(func) {
    const funcStr = func.toString();
    const result = funcStr.slice(funcStr.indexOf('(') + 1, funcStr.indexOf(')')).match(/([^\s,]+)/g);
    return result === null ? [] : result;
}