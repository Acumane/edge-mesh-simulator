import axios from "axios"
import { Client } from "@stomp/stompjs"
import { initSplash, updateProgress } from "./components/Progress"
import { loadControllers } from "./controllers"
import { launch } from "./main"

export let ws_client = new Client({
    brokerURL: "ws://" + window.location.hostname + ":15674/ws",
    connectHeaders: {
        login: "guest",
        passcode: "guest"
    },
    onConnect: async () => {
        console.log("Connected to RabbitMQ WebSocket")

        // TODO: Publish rebound message here

        // try {
        //     // Fetch the routing key from the server
        //     const response = await axios.get("http://localhost:8001/connect")
        //     const mq_key = response.data

        initSplash()

        ws_client.subscribe(`/exchange/edge-mesh/*.loading`, async (message) => {
            const data = JSON.parse(message.body)
            console.log(data)
            const empty = () => void 0
            updateProgress(data.build, data.signal)
            if (data.build.value >= 1.0 && data.signal.value >= 1.0) {
                if (data.build.value < 1.0 || data.signal.value < 1.0) {
                    requestAnimationFrame(empty)
                } else await launch()
            }
        })

        // ws_client.subscribe(`/exchange/edge-mesh/*.data`, async (message) => {
        //     const data = JSON.parse(message.body)
        //     console.log(data)
        //     // await loadControllers(data)
        //     // update controllers here
        // })
        // } catch (error) {
        //     console.error("Error fetching routing key:", error)
        // }
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
