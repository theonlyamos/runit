const dotenv = require('dotenv')
const path = require('node:path')

const args = process.argv

let functionArguments;

try {
    if (args.length >= 3) {
        const filename = args[2]
        const filepath = path.dirname(filename)
        dotenv.config({
            path: path.join(filepath, '.env')
        })
        const functionname = args[3]
        
        const method = require(filename)[functionname]

        if (args.length > 4) functionArguments = args[4]
    
        if (functionArguments !== undefined) {
            method(functionArguments)
        } else {
            method()
        }
    
    }
} catch (error) {
    console.log(error)
}