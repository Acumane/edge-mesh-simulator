import * as THREE from "three"
import { camera, cameraControls, factoryVis } from "./setup"
import { controllerSphereMesh, controllers } from "./controllers"
import { initPopup, updatePopup } from "./components/Popup"
import { factoryOpacity, factoryGroup } from "./factory"

let ray: THREE.Raycaster, mouse: THREE.Vector2
export let onController: string | null = null,
    overPopup: boolean = false

const RAD = Math.PI / 180

export function initInteract() {
    initPopup()
    ray = new THREE.Raycaster()
    mouse = new THREE.Vector2()

    window.addEventListener("click", (event: MouseEvent) => {
        const obj = checkIntersect(event)
        if (obj) {
            const name = Object.keys(controllers)[obj.instanceId!]
            if (!onController) cameraControls.saveState()
            showPopup(name)
        } else if (!overPopup) hidePopup({ restore: true })
    })
    window.addEventListener("keydown", (event: KeyboardEvent) => {
        if (event.key == "Escape") hidePopup({ restore: true })
    })

    window.addEventListener("mousemove", onPopupMouse)
}

function onPopupMouse(event: MouseEvent) {
    if (!onController) return
    const cur = controllers[onController]
    const x = event.clientX / (window.innerWidth / 2) - 1,
        y = -event.clientY / (window.innerHeight / 2) + 1
    const target = new THREE.Vector3(cur.pos.x - 20, cur.pos.z, -cur.pos.y + 10)

    const spherical = orientOffset!.clone()
    spherical.theta -= x * 1.5 * RAD
    spherical.phi += y * RAD

    const adjustCam = target.clone().add(new THREE.Vector3().setFromSpherical(spherical))

    cameraControls.setPosition(...adjustCam.toArray(), true)
    cameraControls.setTarget(...target.toArray(), true)

    onPopupHover(event)
}

function onPopupHover(event: MouseEvent) { // TODO: effects
    const popup = document.getElementById("popup")
    if (popup) {
        const rect = popup.getBoundingClientRect()
        overPopup = event.clientX >= rect.left && event.clientX <= rect.right &&
                       event.clientY >= rect.top && event.clientY <= rect.bottom
    }
}

function checkIntersect(event: MouseEvent) {
    mouse.x = event.clientX / (window.innerWidth / 2) - 1
    mouse.y = -event.clientY / (window.innerHeight / 2) + 1
    ray.setFromCamera(mouse, camera)
    let occluded = ray.intersectObject(factoryGroup, true),
        intersects = ray.intersectObject(controllerSphereMesh)
    if (intersects.length > 0) {
        if (occluded.length > 0 && occluded[0].distance < intersects[0].distance) factoryOpacity(0.2)
        return intersects.length > 0 ? intersects[0] : false
    } else return false
}

let orientOffset: THREE.Spherical | null = null

function showPopup(name: string) {
    if (onController == name) return
    const cur = controllers[name],
        target = new THREE.Vector3(cur.pos.x - 20, cur.pos.z, -cur.pos.y + 10)

    cameraControls.truck(target.x, target.y, true)
    if (!onController) cameraControls.zoom(camera.zoom * 1.5, true)

    // Use spherical cordinates to better capture rotation about target
    orientOffset = new THREE.Spherical().setFromVector3(camera.position.clone().sub(target))
    const adjustCam = target.clone().add(new THREE.Vector3().setFromSpherical(orientOffset)) 

    cameraControls.setPosition(...adjustCam.toArray(), true)
    cameraControls.setTarget(...target.toArray(), true)

    onController = name
}

export function hidePopup({ restore = false } = {}) {
    updatePopup({ cur: null, pos: { x: 0, y: 0 } })
    if (onController) {
        onController = orientOffset = null
        if (restore) cameraControls.reset(true)
        factoryOpacity(factoryVis)
    }
}

export function updateInteract() {
    if (onController) {
        const cur = controllers[onController],
            pos = new THREE.Vector3(cur.pos.x - 20, cur.pos.z, -cur.pos.y + 10)
        //  (in-place) convert vector from world space -> camera's NDC space. 
        pos.project(camera)

        // NDC space [-1, 1] -> normalize [0, 1] -> window space
        const x = (pos.x / 2 + 0.5) * window.innerWidth,
            y = -(pos.y / 2 - 0.5) * window.innerHeight

        updatePopup({ cur, pos: { x: x + 10, y: y + 10 } })
    }
}
