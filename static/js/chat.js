let input_message = $('.input-message')
let message_body = $('#chat-display-pannel')
let send_message_form = $('#send-message-form')
const USER = $('#logged-user').val()
const GAME = $('#game-chat').val()
console.log(USER);

let loc = window.location
let wsStart = 'ws://'
if (location.protocol === "https") {
    wsStart ='wss://'
}
let endPoint = wsStart + loc.host + loc.pathname + '?game_id=' + GAME

var socket = new WebSocket(endPoint)

socket.onopen = async function(e) {
    console.log('open' , e)
    send_message_form.on('submit' , function (e){
        e.preventDefault()
        let message = input_message.val()
        if (USER == 3) {
            send_to = 7
        }
        else{
            send_to = 3
        }
        let data = {
            'message' : message,
            'sent_by' : USER,
            'sent_to' : GAME,
        }
        data = JSON.stringify(data)
        socket.send(data)
        $(this)[0].reset()

    })
    scrollChatToBottom()
}

socket.onmessage = async function(e) {
    console.log('message' , e)
    let data = JSON.parse(e.data)
    let message = data['message']
    let sent_by_id = data['send_by']
    let sent_by_name = data['send_by_name']
    newMessage(message , sent_by_id , sent_by_name)
    scrollChatToBottom()
}

socket.onerror = async function(e) {
    console.log('error' , e)
}

socket.onclose = async function(e) {
    console.log('close' , e)
}




function newMessage(message , send_by_id, sent_by_name) {
    if($.trim(message) === ''){
        return false;
    }
    console.log(message)
    
    let message_element;

    
    if(send_by_id == USER){
        message_element = `
            <div class="chat-you  mt-2" >
                <img class="mt-2 rounded-circle" src="/static/images/profile-pic.webp" alt="">
                <div class="chat-contents">
                    <div class="chat-user rounded-top ps-2 pe-4 w-100">
                        <span>You</span>
                    </div>
                    <div class="chat-text px-2 rounded-bottom w-100">
                        ${message}
                        </div>                      
                        </div>
                        </div>         
                        `
    }else{
        message_element =  `
                        <div class="chat  mt-2" >
                        <img class="mt-2 rounded-circle" src="/static/images/profile-pic.webp" alt="">
                        <div class="chat-contents">
                        <div class="chat-user rounded-top ps-2 pe-4 w-100">
                        <span>${sent_by_name}</span>
                        </div>
                        <div class="chat-text px-2 rounded-bottom w-100">
                        ${message}
                    </div>                      
                </div>
            </div>
        `
    }


    message_body.append($(message_element))
    message_body.animate({
        scrollTop :$(document).height()
    },100)
    input_message.val(null);

}


function scrollChatToBottom() {
    var chatDisplayPanel = document.getElementById('chat-feild-inner')
    chatDisplayPanel.scrollTop = chatDisplayPanel.scrollHeight;
}