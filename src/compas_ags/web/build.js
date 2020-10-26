const packager = require('electron-packager')
const zipFolder = require('zip-folder')
const fs = require('fs')


let electron_app_path = "electron"
let temp_path = "temp"
let app_name = "frontpage"
let zip_path = 'electron.zip'


async function bundleElectronApp(options) {
  const appPaths = await packager(options)
  console.log(`Electron app bundles created:\n${appPaths.join("\n")}`)

  if (fs.existsSync(electron_app_path)) fs.rmdirSync(electron_app_path, { recursive: true })
  fs.renameSync(appPaths[0], electron_app_path)
  fs.rmdirSync(temp_path)
  console.log('moved to '+ electron_app_path)

  if (process.platform === "darwin") return
  
  if (fs.existsSync(zip_path)) fs.unlinkSync(zip_path)
  zipFolder(electron_app_path, zip_path, err => {
    if (err) {
      console.log('zip failed', err)
    } else {
      console.log('zipped at', zip_path)
    }
  })

}

bundleElectronApp({
  dir: ".",
  overwrite: true,
  out: temp_path,
  name: app_name,
  ignore: ["node_modules", "electron", "electron.zip", ".py", ".md"]
})