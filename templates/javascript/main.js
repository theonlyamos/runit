exports.index = ()=>{
    console.log('Hello world')
}

exports.counter = ()=>{
    console.log(1,2,3,4,5)
}

exports.printout = (string)=>{
    console.log(string)
}

exports.gettime = ()=>{
    console.log(new Date().toUTCString())
}