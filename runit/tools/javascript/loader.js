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