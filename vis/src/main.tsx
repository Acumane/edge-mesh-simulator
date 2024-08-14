import React, { useEffect, useRef } from "react"
import ReactDOM from "react-dom/client"
import * as THREE from "three"
import Stats from "three/examples/jsm/libs/stats.module"
import { initCamera, initLights, initKeybinds, orientCamera } from "./setup"
import { scene, renderer, camera, cameraControls } from "./setup"
import { loadFactory } from "./factory"
import { updateControllers } from "./controllers"
import { removeSplash } from "./components/Progress"
import { initInteract, updateInteract } from "./interact"
import { initEdges, updateEdges } from "./edges"
import { activateClient } from "./socket"

const stats = new Stats(),
    clock = new THREE.Clock(),
    URL = "http://localhost:8001"

function animate() {
    requestAnimationFrame(animate)
    stats.update()
    const delta = clock.getDelta()
    // updateControllers()
    // updateEdges()
    updateInteract() // move popup with node
    cameraControls.update(delta)
    renderer.render(scene, camera)
}

async function init() {
    const canvas = document.getElementById("canvas")!
    canvas.append(stats.dom, renderer.domElement)

    initCamera()
    initKeybinds()
    initInteract()
    activateClient()
}

export async function launch() {
    await loadFactory()
    setTimeout(() => removeSplash(), 500)
    initLights()
    orientCamera({ view: "default" })
    initEdges()
    renderer.render(scene, camera)
    animate()
}

const App = () => {
    const ready = useRef(false)
    useEffect(() => {
        // TODO: timing?
        if (!ready.current) {
            init()
            ready.current = true
        }
        return () => {}
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
