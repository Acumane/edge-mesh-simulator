import React, { useEffect, useRef } from "react"
import ReactDOM from "react-dom/client"
import * as THREE from "three"
import Stats from "three/examples/jsm/libs/stats.module"
import { initCamera, initLights, initKeybinds, orientCamera } from "./setup"
import { scene, renderer, camera, cameraControls } from "./setup"
import { loadFactory } from "./factory"
import { loadControllers, updateControllers } from "./controllers"
import { initSplash, updateProgress, removeSplash } from "./components/Progress"
import { initInteract, updateInteract } from "./interact"
import { initEdges, updateEdges } from "./edges"

const stats = new Stats(),
    clock = new THREE.Clock(),
    URL = "http://localhost:8001"

function animate() {
    requestAnimationFrame(animate)
    stats.update()
    const delta = clock.getDelta()
    updateControllers()
    updateEdges()
    updateInteract() // move popup with node
    cameraControls.update(delta)
    renderer.render(scene, camera)
}

async function buildProgress(): Promise<void> {
    const getData = () => { return fetch(`${URL}/progress`).then((res) => res.json()) }
    let check = await getData()
    if (check.build.value == 1.0) return
    return new Promise((resolve) => {
        initSplash()
        function getProgress() {
            getData().then((data) => {
                updateProgress(data.build, data.signal)

                if (data.build.value < 1.0 || data.signal.value < 1.0) {
                    requestAnimationFrame(getProgress)
                } else resolve()
            })
        }
        getProgress()
    })
}

async function init() {
    const canvas = document.getElementById("canvas")!
    canvas.append(stats.dom, renderer.domElement)

    initCamera()
    initKeybinds()
    initInteract()
    await buildProgress() // block on build step
    await loadFactory()
    setTimeout(() => removeSplash(), 500)
    initLights()
    orientCamera({ view: "default" })
    await loadControllers()
    initEdges()
    renderer.render(scene, camera)
    animate()
}

const App = () => {
    const ready = useRef(false)
    useEffect(() => { // TODO: timing?
        if (!ready.current) { init(); ready.current = true }
    }, [])
    return <div id="canvas"></div>
}

const Provider = ({ children }: { children: React.ReactNode }) => children // WIP 
ReactDOM.createRoot(document.getElementById("root")!).render(
    <React.StrictMode>
        <Provider>
            <App />
        </Provider>
    </React.StrictMode>
)
