from .language import LanguagePlugin

loader = """
const dotenv = require('dotenv')
const path = require('node:path')

try {
    if (process.argv.length > 2) {
        const filename = process.argv[2]
        const filepath = path.dirname(filename)
        dotenv.config({
            path: path.join(filepath, '.env')
        })
        const methods = require(filename)

        console.log(Object.keys(methods))
    }
} catch (error) {
    console.log(error.toString().split('\n')[0])
}
"""

runner = """
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
            console.log(method(functionArguments))
        } else {
            console.log(method())
        }

    }
} catch (error) {
    console.log(error)
}
"""

Javascript = LanguagePlugin('javascript', 'language', 'node', loader=loader, runner=runner, author='admin')