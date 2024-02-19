// index.js
const tf = require('@tensorflow/tfjs');
const os = require('os'); // Node.js module is used for accessing system information
const say = require('say'); // Importing the 'say' module

// Function to pull system information
function getSystemInfo() {
    const platform = os.platform();
    const arch = os.arch();
    const cpus = os.cpus();
    const totalMemory = os.totalmem();
    const freeMemory = os.freemem();

    return {
        platform,
        arch,
        cpus,
        totalMemory,
        freeMemory,
    };
}

// Converting System Information Function to text
function systemInfoToText(systemInfo) {
  return
        SystemInformation:
        Platform: {systemInfo.platform}
        Architecture: {systemInfo.acrch}
        CPUs: {systemInfo.cpus.length}
        totalMemory: {Math.round(systemInfo.totalMemory / (1024 * 1024))} MB
        freeMemoryMemory: {Math.round(systemInfo.freememory / (1024 * 1024))} MB
        
     };

// Main function
async function main () {
    // Pulling system information
    const systemInfo = getSystemInfo();
    console.log('System Information:', systemInfo);
    
    //Convert system information to text
    const systemInfoText = systemInfoToText(systemInfo);
    console.log(systemInfoToText);

// trying to figure out how to get it to read off the system results from the scan. 

    //Speak the system information
    say.speak(systemInfoToText);
    
    //Speaking the system information
    //say.speak(systemInfoToText, 'Microsoft Zira Desktop', 1.0);
    
    //Can add more code here
}
//Running the main code here

main();
