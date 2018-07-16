// utility part
const log = console.log.bind(console)
const sel = selector => document.querySelector(selector)

// let's  rock
const post_login = () => {
    username = sel("#username-id")
    passoword = sel("#passoword-id")
    data = new FormData()
    data.set('username', username.value)
    data.set('password', passoword.value)
    axios.post('/login_api',
        data
    ).then(
        (respnse) => {
            log(respnse)
        }
    ).catch(
        (error) => {
            log(error)
        }
    )
}
const login = () => {
    submit = sel("#login-submit-id")
    // data = new FormData() // data.set('username': username,)
    submit.addEventListener("click", post_login, false)
}


const show_chatrooms = () => {
    // const axios = require('axios');
    // chat_rooms = await axios.get('')
}

const chat = (room_name) => {
    const ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    try {
        const ws = new WebSocket(
            ws_scheme + '://' + window.location.host
            + "/ws/chat/" + room_name + "/"
        )
        ws.onmessage = (e) => {
            append_log(e)
        }
        // log if error
        ws.onclose = (e) => {
            leave_log(e)
        }
        // bind send message event
        bind_event(ws)
    } catch (error) {
        // window.location = window.location.protocol + window.location.host + "/login/";
        log(error)
    }
}

const append_log = (e) => {
    const data = JSON.parse(e.data)
    const message = data['message']
    sel('#chat-log-id').value += (message + '\n')
}

const leave_log = (e) => {
    const code = event.code
    const reason = event.reason
    const wasClean = event.wasClean
    log(`code:${code}\nreason:${reason}wasClean:${wasClean}`)
}

const bind_event = (ws) => {
    sel("#message-input-id").focus()
    sel("#message-input-id").onkeyup = (e) => {
        if (e.keyCode === 13) {
            document.querySelector('#message-submit-id').click()
        }
    }
    sel("#message-submit-id").click = (e) => {
        const ele = sel("#message-input-id")
        ws.send(JSON.stringify({ "message": ele.value }))
        ele.value = ""
    }

    // const axios = require('axios');
    sel("#room-input-id").onkeyup = (e) => {
        if (e.keyCode === 13) {
            document.querySelector('#room-submit-id').click()
        }
    }
    sel("#room-submit-id").click = (e) => {
        const ele = sel("#room-input-id")
        log('ff')
        var data = new FormData();
        data.set('name', ele.value);
        axios.post('rooms', data)
        ele.value = ""
    }
}

const main = () => {
    log("let's rock")
    login()
    show_chatrooms()
    // chat("test")
}
main()