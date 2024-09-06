import * as THREE from "three"
import { controllers, Controller } from "./controllers"
import { OFFSET } from "./factory"
import { scene } from "./setup"

// TODO: Fix naming conflict issues with controllers.ts

const MAX_VERT = 10000
let lineMesh: THREE.LineSegments
export let edgeThreshold = 75

const strenCol: { [key: number]: THREE.Color } = {
    100: new THREE.Color(0x00ff00),
    90: new THREE.Color(0x00ff00),
    60: new THREE.Color(0xffff00),
    30: new THREE.Color(0xff8000),
    0: new THREE.Color(0xff0000)
}

export function initEdges() {
    const geometry = new THREE.BufferGeometry(),
        positions = new Float32Array(MAX_VERT * 6), // 3<x,y,z> * 2
        colors = new Float32Array(MAX_VERT * 8) // 4<r,g,b,a> * 2

    geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3))
    geometry.setAttribute("color", new THREE.BufferAttribute(colors, 4))

    const material = new THREE.LineBasicMaterial({ vertexColors: true, transparent: true })
    lineMesh = new THREE.LineSegments(geometry, material)
    lineMesh.position.set(...OFFSET)
    lineMesh.frustumCulled = false
    scene.add(lineMesh)
}

export function updateEdges() {
    const { position, color } = lineMesh.geometry.attributes,
        cVals = Object.values(controllers)
    let lines = 0

    position.array.fill(0)
    for (let a = 0; a < cVals.length && lines < MAX_VERT; a++) {
        for (let b = a + 1; b < cVals.length && lines < MAX_VERT; b++) {
            const stren = Math.max(cVals[a].hears[cVals[b].name].perc, cVals[b].hears[cVals[a].name].perc)
            if (stren > edgeThreshold) {
                updateLine(lines, cVals[a], cVals[b], stren)
                lines++
            }
        }
    }
    position.needsUpdate = color.needsUpdate = true
}

function updateLine(i: number, cA: Controller, cB: Controller, stren: number) {
    const { position, color } = lineMesh.geometry.attributes
    position.array.set([cA.pos.x, cA.pos.z, -cA.pos.y, cB.pos.x, cB.pos.z, -cB.pos.y], i * 6)
    const { r, g, b, a } = getLineColor(stren)
    color.array.set([r, g, b, a, r, g, b, a], i * 8)
}

function getLineColor(stren: number) {
    const levels = Object.keys(strenCol).map(Number),
        i = levels.findIndex((level) => stren <= level),
        lower = levels[Math.max(0, i - 1)],
        upper = levels[i]

    return {
        ...strenCol[lower].clone().lerp(strenCol[upper], (stren - lower) / (upper - lower)),
        a: stren > 50 ? 1.0 : 0.4 + (stren / 50) * 0.6
    }
}

export function threshold(step: number) {
    return (event: any) => {
        edgeThreshold = Math.min(Math.max(edgeThreshold + step, 0), 100)
        updateEdges()
    }
}
