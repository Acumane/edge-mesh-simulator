import * as THREE from "three"
import { scene, COL } from "./setup"
import { OFFSET } from "./factory"


export interface Signal {
    perc: number
    dBm: number
}

export interface Controller {
    name: string
    comm: string
    pos: { x: number; y: number; z: number }
    orient: { roll: number; pitch: number; yaw: number }
    ip: string
    hears: { [key: string]: Signal }
    bf: boolean
}
type Mesh = { [key: string]: Controller }
export let controllers: Mesh = {}
export let controllerMesh: THREE.InstancedMesh, controllerSphereMesh: THREE.InstancedMesh
let edgeMesh: THREE.LineSegments,
    edges: Array<[string, string]> = []

function sendControllers(data: any): Mesh {
    try {
        return data.reduce((acc: Mesh, item: any) => {
            acc[item.name] = {
                name: item.name,
                comm: item.comm,
                pos: item.pos,
                orient: item.orient,
                ip: item.ip,
                hears: item.hears,
                bf: item.bf
            }
            return acc
        }, {})
    } catch (error) {
        console.error("Error fetching data:", error)
        return {}
    }
}

export function loadControllers(data: any) {
    applyControllers(data)
    if (!controllerMesh) setupControllerMesh()
    if (!edgeMesh) setupEdgeMesh()
    updateControllers(data)
}

function applyControllers(data: any) {
    const stripped: Mesh = sendControllers(data)
    Object.values(stripped).forEach((item: Controller) => {
        controllers[item.name] = item
    })
}

function setupControllerMesh() {
    const res = 32,
        pointGeometry = new THREE.SphereGeometry(0.2, res / 2, res / 2),
        sphereGeometry = new THREE.SphereGeometry(1.25, res, res),
        pointMaterial = new THREE.MeshBasicMaterial({ color: COL.node }),
        sphereMaterial = new THREE.MeshBasicMaterial({
            color: COL.blue,
            transparent: true,
            opacity: 0.3
        })
    const controllerCount = Object.keys(controllers).length
    controllerMesh = new THREE.InstancedMesh(pointGeometry, pointMaterial, controllerCount)
    controllerSphereMesh = new THREE.InstancedMesh(sphereGeometry, sphereMaterial, controllerCount)

    let index = 0
    const tmpMatrix = new THREE.Matrix4()
    Object.values(controllers).forEach((item: Controller) => {
        tmpMatrix.setPosition(item.pos.x, item.pos.z, -item.pos.y)
        controllerMesh.setMatrixAt(index, tmpMatrix)
        controllerSphereMesh.setMatrixAt(index, tmpMatrix)
        index++
    })

    controllerMesh.position.set(...OFFSET)
    controllerSphereMesh.position.set(...OFFSET)
    controllerMesh.instanceMatrix.needsUpdate = controllerSphereMesh.instanceMatrix.needsUpdate = true
    scene.add(controllerMesh, controllerSphereMesh)
}

function setupEdgeMesh() {
    const edgeGeometry = new THREE.BufferGeometry()
    const positions: Array<number> = []
    edgeGeometry.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3))
    const edgeMaterial = new THREE.LineBasicMaterial({ color: COL.black })
    edgeMesh = new THREE.LineSegments(edgeGeometry, edgeMaterial)
    edgeMesh.position.set(...OFFSET)
    scene.add(edgeMesh)
}

export function updateControllers(data: Mesh) {
    updateControllerPos(data)
    updateEdges()
}

function updateControllerPos(data: Mesh) {
    if (!controllerMesh || !controllerSphereMesh) return
    const tmpMatrix = new THREE.Matrix4()

    // TODO: Handle issues when indexing becomes out of order when
    // changing controller order or adding/removing controllers
    // OR maybe abstract adding / removing to seperate feature

    Object.values(controllers).forEach((item: Controller, index: number) => {
        if (item.name in data) {
            tmpMatrix.setPosition(item.pos.x, item.pos.z, -item.pos.y)
            controllerMesh.setMatrixAt(index, tmpMatrix)
            controllerSphereMesh.setMatrixAt(index, tmpMatrix)
        }
    })
    controllerMesh.instanceMatrix.needsUpdate = true
    controllerSphereMesh.instanceMatrix.needsUpdate = true
}

function updateEdges() {
    const positions: Array<number> = []
    edges.forEach((edge) => {
        const [from, to] = edge,
            fromPos = controllers[from].pos,
            toPos = controllers[to].pos
        positions.push(fromPos.x, fromPos.z, -fromPos.y, toPos.x, toPos.z, -toPos.y)
    })
    if (edgeMesh && edgeMesh.geometry)
        edgeMesh.geometry.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3))
}
