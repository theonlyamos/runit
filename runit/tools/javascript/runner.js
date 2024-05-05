const args = process.argv;

if (args.length >= 3) {
    const filename = args[2];
    const functionname = args[3];
    const functionArguments = args.length > 4 ? args[4] : undefined;

    try {
        const module = require(filename);
        const method = module[functionname];

        if (typeof method === 'function') {
            // Check if functionArguments are provided and handle accordingly
            const result = functionArguments ? method(functionArguments) : method();

            // Check if the result is a Promise
            if (result instanceof Promise) {
                result.then(output => console.log(output))
                      .catch(error => console.error("Error executing async function:", error));
            } else {
                console.log(result);
            }
        } else {
            console.log('No function found by the name:', functionname);
        }
    } catch (error) {
        console.error("Error:", error);
    }
}