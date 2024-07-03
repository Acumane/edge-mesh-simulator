import { FC as Component } from "react"
import ReactDOM from "react-dom/client"
import "./styles.sass"

interface Controller {
    name: string
    ip: string
    signal: number
}

interface Popup {
    cur: Controller | null
    pos: { x: number; y: number }
}

const Popup: Component<Popup> = ({ cur, pos }) => {
    if (!cur) return null

    return (
        <div id="popup" style={{
            left: `${pos.x}px`,
            top: `${pos.y}px`,
        }}>
            <h3 id="popup-title">{cur.name}</h3>
            <p id="popup-info">IP: {cur.ip}</p>
            <p id="popup-info">Signal: {cur.signal}</p>
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
