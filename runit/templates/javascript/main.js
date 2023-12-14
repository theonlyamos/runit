exports.index = ()=>{
    return 'Yay, Javascript works!!!'
}

exports.counter = ()=>{
    return '1,2,3,4,5'
}

exports.printout = (string)=>{
    return string
}

exports.time = ()=>{
    return new Date().toUTCString()
}