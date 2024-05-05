const index = ()=>{
    return 'Yay, Javascript works!!!'
}

const counter = ()=>{
    return '1,2,3,4,5'
}

const printout = (string)=>{
    return string
}

const time = ()=>{
    return new Date().toUTCString()
}

module.exports = {
    index,
    counter,
    printout,
    time
}