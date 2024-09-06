import { FC as Component } from "react"
import ReactDOM from "react-dom/client"
import { Controller } from "../controllers"
import { edgeThreshold } from "../edges"
import "./styles.sass"

interface Popup {
    cur: Controller | null
    pos: { x: number; y: number }
}

const Popup: Component<Popup> = ({ cur, pos }) => {
    if (!cur) return null

    const byStren = Object.entries(cur.hears)
        .filter(([, value]) => value.perc >= edgeThreshold)
        .sort(([, a], [, b]) => b.perc - a.perc)

    return (
        <div
            id="popup"
            style={{
                left: `${pos.x}px`,
                top: `${pos.y}px`
            }}
        >
            <h3 id="popup-title">{cur.name}</h3>
            <p id="popup-info">IP: {cur.ip}</p>
            <p id="popup-info">{cur.bf ? "Beamformed" : "Omnidirectional"}</p>
            <div id="stren">
                {byStren.map(([key, value]) => (
                    <div id="stren-item" key={key}>
                        <span>{key}: </span>
                        <div id="stren-bar">
                            <div
                                id="stren-bar-fill"
                                style={{
                                    width: `${Math.min(value.perc, 100)}%`
                                }}
                            />
                        </div>
                        <span> {value.dBm.toFixed(2)} dBm</span>
                    </div>
                ))}
            </div>
        </div>
    )
}

let popupRoot: ReactDOM.Root

export function initPopup() {
    const parent = document.body.appendChild(document.createElement("div"))
    popupRoot = ReactDOM.createRoot(parent)
}

export function updatePopup(props: Popup) {
    popupRoot.render(<Popup {...props} />)
}

export default Popup
