import * as THREE from "three"
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js"
import { scene, COL } from "./setup"

export let factoryGroup: THREE.Group

let floor: THREE.Mesh
export const OFFSET: THREE.Vector3Tuple = [-20, 0, 10]
export let factorySize: THREE.Vector3 = new THREE.Vector3(),
    center: THREE.Vector3 = new THREE.Vector3(),
    boundingBox: THREE.Box3

const sceneUrl = "./assets/scene.glb",
    gltfLoader = new GLTFLoader()

export function loadFactory(): Promise<void> {
    return new Promise((resolve, reject) => {
        gltfLoader.load(
            sceneUrl,
            (gltf: any) => {
                factoryGroup = gltf.scene
                factoryGroup.traverse((node) => {
                    if (node instanceof THREE.Mesh) {
                        node.material = new THREE.MeshStandardMaterial({ vertexColors: true })
                        node.material.needsUpdate = true
                        node.receiveShadow = true

                        if (node.name === "bounds") node.visible = false
                    }
                })

                updateFactoryGroup()
                makeBoundingBox()
                scene.add(factoryGroup)
                scene.add(makeFloor())
                resolve()
            },
            undefined,
            (error: any) => {
                console.error("Failed to load GLTF model:", error)
                reject(error)
            }
        )
    })
}

function updateFactoryGroup() {
    factoryGroup.traverse((child: any) => {
        if (child instanceof THREE.Mesh) {
            child.material.transparent = true
            child.castShadow = true
        }
    })
    factoryGroup.position.set(...OFFSET)
    factoryGroup.rotation.x = -Math.PI / 2
}

export function factoryOpacity(opacity: number) {
    ;(floor.material as THREE.Material).opacity = opacity
    factoryGroup.traverse((child: THREE.Object3D) => {
        if (child instanceof THREE.Mesh) {
            child.material.transparent = opacity < 1
            child.material.opacity = opacity
        }
    })
}

function makeBoundingBox() {
    boundingBox = new THREE.Box3().setFromObject(factoryGroup)
    boundingBox.getSize(factorySize)
    boundingBox.getCenter(center)
}

function makeFloor(border = 4) {
    const width = factorySize.z + border,
        height = factorySize.x + border
    const floorGeom = new THREE.PlaneGeometry(width, height, width, height)
    const floorMat = new THREE.MeshStandardMaterial({ color: COL.floor, side: THREE.DoubleSide })
    floor = new THREE.Mesh(floorGeom, floorMat)
    floor.position.set(center.x, -0.001, center.z)
    floor.rotation.x = -(floor.rotation.z = Math.PI / 2)
    ;(floor.material as THREE.Material).transparent = true
    floor.receiveShadow = true
    return floor
}