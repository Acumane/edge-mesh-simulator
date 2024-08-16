import axios from "axios"
import { Client } from "@stomp/stompjs"
import { initSplash, updateProgress } from "./components/Progress"
import { loadControllers } from "./controllers"
import { launch } from "./main"

// add state mangagement library to pin all global export vals
export let isLaunched = false

export let ws_client = new Client({
    brokerURL: "ws://" + window.location.hostname + ":15674/ws",
    connectHeaders: {
        login: "guest",
        passcode: "guest"
    },
    onConnect: async () => {
        console.log("Connected to RabbitMQ WebSocket")

        initSplash()
        ws_client.subscribe(`/exchange/edge-mesh/*.loading`, async (message) => {
            const data = JSON.parse(message.body)
            console.log(data)
            const empty = () => void 0
            updateProgress(data.build, data.signal)
            if (data.build.value >= 1.0 && data.signal.value >= 1.0) {
                if (data.build.value < 1.0 || data.signal.value < 1.0) {
                    requestAnimationFrame(empty)
                } else if (!isLaunched) {
                    await launch()
                    isLaunched = true
                }
            }
        })

        ws_client.subscribe(`/exchange/edge-mesh/*.data`, async (message) => {
            const data = JSON.parse(message.body)
            console.log(data)
            loadControllers(data)
        })
        const reloadMessage = {
            type: "reload",
            content: "Triggering reload process."
        }
        ws_client.publish({
            destination: "/exchange/edge-mesh/reload",
            body: JSON.stringify(reloadMessage)
        })
        console.log("Sent reload message to queue")
    },
    onWebSocketError: (e) => {
        console.error(e)
    },
    onStompError: (frame) => {
        console.error(`Broker reported error: ${frame.headers["message"]}`)
        console.error(`Additional details: ${frame.body}`)
    }
})

export const activateClient = () => {
    ws_client.activate()
}

export const deactivateClient = () => {
    if (ws_client.active) {
        ws_client.deactivate()
    }
}
