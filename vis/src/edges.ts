import * as THREE from "three"
import { controllers, Controller } from "./controllers"
import { OFFSET } from "./factory"
import { scene } from "./setup"
import { graphPath } from "./socket"

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

const isValidHex = (hex: string) => /^#([A-Fa-f0-9]{3,4}){1,2}$/.test(hex)

const getChunksFromString = (st: any, chunkSize: number) => st.match(new RegExp(`.{${chunkSize}}`, "g"))

const convertHexUnitTo256 = (hexStr: string) => parseInt(hexStr.repeat(2 / hexStr.length), 16)

const getAlphafloat = (a: any, alpha: any) => {
    if (typeof a !== "undefined") {
        return a / 255
    }
    if (typeof alpha != "number" || alpha < 0 || alpha > 1) {
        return 1
    }
    return alpha
}

export const hexToRGBA = (hex: string, alpha: any = -1) => {
    if (!isValidHex(hex)) {
        throw new Error("Invalid HEX")
    }
    const chunkSize = Math.floor((hex.length - 1) / 3)
    const hexArr = getChunksFromString(hex.slice(1), chunkSize)
    const [r, g, b, a] = hexArr.map(convertHexUnitTo256)
    const n_a = getAlphafloat(a, alpha)
    return { r, g, b, n_a }
}

export function updateEdges() {
    const { position, color } = lineMesh.geometry.attributes,
        cVals = Object.values(controllers)
    let lines = 0
    const edges = new Set(graphPath.get("edges"))
    console.log(edges)

    position.array.fill(0)
    for (let a = 0; a < cVals.length && lines < MAX_VERT; a++) {
        for (let b = a + 1; b < cVals.length && lines < MAX_VERT; b++) {
            if (edges.has(cVals[a].name + " " + cVals[b].name) || edges.has(cVals[b].name + " " + cVals[a].name)) {
                updateLine(lines, cVals[a], cVals[b], hexToRGBA("#000000"))
                lines++
                continue
            }
            const stren = Math.min(cVals[a].hears[cVals[b].name], cVals[b].hears[cVals[a].name])
            if (stren > edgeThreshold) {
                updateLine(lines, cVals[a], cVals[b], getLineColor(stren))
                lines++
            }
        }
    }
    position.needsUpdate = color.needsUpdate = true
}

function updateLine(i: number, cA: Controller, cB: Controller, lineColor: any) {
    const { position, color } = lineMesh.geometry.attributes
    position.array.set([cA.pos.x, cA.pos.z, -cA.pos.y, cB.pos.x, cB.pos.z, -cB.pos.y], i * 6)
    const { r, g, b, a } = lineColor
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
