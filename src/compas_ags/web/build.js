const packager = require('electron-packager')
const fs = require('fs')
const { zip } = require('zip-a-folder')

let electron_app_path = "electron"
let temp_path = "temp"
let app_name = "frontpage"
let zip_path = 'electron.zip'
let version = process.argv[2]

async function bundleElectronApp(options) {
  const appPaths = await packager(options)
  console.log(`Electron app bundles created:\n${appPaths.join("\n")}`)

  if (fs.existsSync(electron_app_path)) fs.rmdirSync(electron_app_path, { recursive: true })
  fs.renameSync(appPaths[0], electron_app_path)
  fs.rmdirSync(temp_path)
  console.log('moved to '+ electron_app_path)

  if (version){
    console.log("Set version in index.html with", version)
    let html_path = electron_app_path+"/resources/app/src/index.html"
    let html = fs.readFileSync(html_path, "utf-8")
    html = html.replace("{{dev}}", version)
    fs.writeFileSync(html_path,html)
  }

  if (process.platform === "darwin") return
  
  if (fs.existsSync(zip_path)) fs.unlinkSync(zip_path)

  await zip(electron_app_path, zip_path)

  console.log('zipped at', zip_path)

}

bundleElectronApp({
  dir: ".",
  overwrite: true,
  out: temp_path,
  name: app_name,
  ignore: ["node_modules", "electron", "electron.zip", ".py", ".md"]
})