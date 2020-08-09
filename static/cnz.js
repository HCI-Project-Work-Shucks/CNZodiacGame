$(document).ready(function() {
    if (!window.console) window.console = {}
    if (!window.console.log) window.console.log = function() {}

    cnz.start()

    $("#messageform").on("submit", function() {
        cnz.say($(this))
        return false
    })
    $("#messageform").on("keypress", function(e) {
        if (e.keycode == 13) {
            cnz.say($(this))
            return false
        }
    })

    $("#userinfo").on("submit", function() {
        cnz.login($(this))
        return false
    })
    $("#userinfo").on("keypress", function(e) {
        if (e.keycode == 13) {
            cnz.login($(this))
            return false
        }
    })

    $("#answer0, #answer1, #answer2, #answer3").on("click", cnz.reply)

    $("#fight").on("click", cnz.fight)
    $("#flip").on("click", cnz.flip)
})

var cnz = {
    ERROR: 0x0,
    LOGIN: 0x1,
    LOGOUT: 0x2,
    SAY: 0x3,
    FIGHT: 0x5,
    ROUND: 0x6,
    FLIP: 0x7,
    REPLY: 0x8,
    REVEAL: 0x9,
    WIN: 0xa,

    ws: null,
    playerID: 0,
    chessers: new Map(),
    stallCount: 36,
    lostScore: 0,

    start: function() {
        var url = "ws://" + location.host + "/ws"
        cnz.ws = new WebSocket(url)
        cnz.ws.onmessage = cnz.recv
    },

    recv: function(event) {
        message = JSON.parse(event.data)
        if (message.type == cnz.ERROR) alert(message.body)
        if (message.type == cnz.LOGIN) cnz.onLogin(message)
        if (message.type == cnz.WIN) cnz.win(message)
        if (message.type == cnz.LOGOUT) cnz.onLogout(message)
        if (message.type == cnz.SAY) cnz.onSay(message)
        if (message.type == cnz.FIGHT) cnz.onFight(message)
        if (message.type == cnz.ROUND) cnz.round(message)
        if (message.type == cnz.FLIP) cnz.onFlip(message)
        if (message.type == cnz.REVEAL) cnz.reveal(message)
    },

    round: function(message) {
        if (!cnz.ami(message.player_id)) {
            cnz.markRound(message.player_name)
            return
        }

        var btn = $("#flip")
        cnz.fadeOutIn(btn)
        btn.removeAttr("disabled")

        $("#round").html("轮到你了").fadeIn()
    },

    win: function(message) {
        window.location.href = "/?lastWin=" + message.player_name
    },

    onLogout: function(message) {
        cnz.onSay({html: "<div>" + message.message + "</div>"})
        cnz.removeChesser(message.player_id)

        if (message.new_round_chesser === undefined) {
            return
        }

        $("#topic").html("")
        $("#flip").fadeOut().attr("disable", true)
        $("#answer0, #answer1, #answer2, #answer3").fadeOut()

        cnz.round({
            player_id: message.new_round_chesser.player_id,
            player_name: message.new_round_chesser.player_name,
        })
    },

    removeChesser: function(chesserID) {
        var node = cnz.chessers.get(chesserID)
        if (!node) {
            return
        }
        node.remove()

        cnz.chessers.delete(chesserID)

        $("#score" + chesserID).remove()
    },

    login: function(form) {
        cnz.name = form.find("[id=username]").val()
        var message = {
            type: cnz.LOGIN,
            body: cnz.name,
        }
        cnz.ws.send(JSON.stringify(message))
    },
    onLogin: function(message) {
        $("#userinfodiv").remove()
        $("#messagediv").fadeIn()

        cnz.onSay({html: "<div>" + message.message + "</div>"})

        if (cnz.name == message.player_name) {
            cnz.playerID = message.player_id
        }

        message.chessers.forEach(function(chesser, index) {
            cnz.setChesser(chesser)
        })

        $("#winner").fadeOut()
    },

    fight: function() {
        var message = {type: cnz.FIGHT}
        cnz.ws.send(JSON.stringify(message))
    },
    onFight: function(message) {
        cnz.setChesser(message)

        if (cnz.ami(message.player_id)) {
            $("#fight").parent().remove()
        }

        
    },

    say: function(form) {
        var message = {
            type: cnz.SAY,
            body: form.find("[id=message]").val(),
        }
        cnz.ws.send(JSON.stringify(message))
        form.find("input[type=text]").val("").select()
    },
    onSay: function(message) {
        var node = $(message.html)
        node.hide()
        $("#inbox").prepend(node);
        node.slideDown()
    },

    flip: function() {
        var message = {type: cnz.FLIP}
        cnz.ws.send(JSON.stringify(message))
    },
    onFlip: function(message) {
        var btn = $("#flip")
        btn.attr("disabled", true)

        var dice = message.point
        var node = cnz.getChesser(message.player_id)
        var interval
        var animate = function(i) {
            if (cnz.ami(message.player_id)) {
                var v = "掷骰子 (" + dice.toString() + ")"
                btn.slideUp().val(v).slideDown()
            }

            if (dice == 0) {
                clearInterval(interval)
                btn.fadeOut()
                cnz.showQuiz(message.quiz, message.player_id)
                return
            }

            var idx = parseInt(node.parent().attr("id").slice(4))
            next = (idx+1) % cnz.stallCount

            node.detach().appendTo($("#cell" + next))
            node.fadeOut().fadeIn()

            dice--
        }

        interval = setInterval(animate, 1000)
    },

    showQuiz: function(quiz, playerID) {
        $("#animal").html(quiz.animal).fadeOut()
        $("#topic").html(quiz.topic).fadeIn()
        quiz.answers.forEach(function(answer, index) {
            var btn = $("#answer" + index.toString(16))
            btn.html(answer).fadeIn()

            if (cnz.ami(playerID))
                btn.removeAttr("disabled")
            else
                btn.attr("disabled", true)
        })
    },

    reply: function() {
        var message = {
            type: cnz.REPLY,
            animal: $("#animal").html(),
            topic: $("#topic").html(),
            answer: $(this).html(),
        }
        cnz.ws.send(JSON.stringify(message))
    },
    reveal: function(message) {
        $("#answer0, #answer1, #answer2, #answer3").fadeOut()

        var node = $("#topic")
        if (message.correct) {
            node.text("答对了").css({"color": "green"})
        } else {
            node.text("答错了").css({"color": "red"})
        }
        cnz.fadeOutIn(node).fadeOut()

        if (message.next_chesser !== undefined) {
            cnz.round({
                player_id: message.next_chesser.player_id,
                player_name: message.next_chesser.player_name,
            })
        }

        cnz.setChesserScore(message)
    },

    markRound: function(name) {
        var node = $("#round").html("轮到 " + name + " 了")
        cnz.fadeOutIn(node)
    },

    ami: function(playerID) {
        return playerID == cnz.playerID
    },

    getChesser: function(playerID) {
        return cnz.chessers.get(playerID)
    },
    setChesser: function(chesser) {
        if (cnz.getChesser(chesser.player_id) !== undefined) {
            return
        }

        var node = $("<span class='dot'></span>")
        node.css("background-color", "#" + chesser.rgb.toString(16))
        node.hide()

        $("#cell" + chesser.stall).html(node)
        cnz.fadeOutIn(node)

        cnz.chessers.set(chesser.player_id, node)

        cnz.insertChesserScore(chesser)
    },

    insertChesserScore: function(chesser) {
        var node = $("<span class='chesser_score' id='score" + chesser.player_id + "'>" + chesser.player_name + ": " + chesser.player_score +"</span>")
        node.css({"color": "#" + chesser.rgb.toString(16)}).appendTo($("#score")).fadeOut().fadeIn()
    },
    setChesserScore: function(chesser) {
        var node = $("#score" + chesser.player_id)

        if (chesser.player_score <= cnz.lostScore) {
            node.html("<s>" + chesser.player_name + ": lost</s>")
            return
        }

        node.text(chesser.player_name + ": " + chesser.player_score)
    },

    fadeOutIn: function(node) {
        for (var i = 0; i < 5; i++) {
            node.fadeOut().fadeIn()
        }
        return node
    },

    randint: function(min, max) {
        return Math.floor(Math.random() * (max - min) + min)
    },
}
