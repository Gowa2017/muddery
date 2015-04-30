/*
Muddery webclient (javascript component)
*/

var webclient = {
    enviroment : {  // player's current position
        room_name : "",
        room_desc : "",
        objects : [],
        players : [],
        exits : [],
    },

    login : false,  // Whether player is login or not.

    // display all kinds of data
    displayData : function(data) {
        for (var key in data) {
            try {
                if (key == "msg") {
                    this.displayMsg(data[key]);
                }
                else if (key == "out") {
                    this.displayOut(data[key]);
                }
                else if (key == "err") {
                    this.displayErr(data[key]);
                }
                else if (key == "sys") {
                    this.displaySystem(data[key]);
                }
                else if (key == "debug") {
                    this.displayDebug(data[key]);
                }
                else if (key == "prompt") {
                    this.displayPrompt(data[key]);
                }
                else if (key == "env") {
                    this.displayEnv(data[key]);
                }
                else {
                    this.displayMsg(data[key]);
                }
            }
            catch(error) {
                this.displayErr("Data error.");
            }
        }
    },

    displayMsg : function(data) {
        data = text2html.parseHtml(data);
        this.displayTextMsg("msg", data);
    },

    displayOut : function(data) {
        this.displayTextMsg("out", data);
    },

    displayErr : function(data) {
        this.displayTextMsg("err", data);
    },

    displaySystem : function(data) {
        this.displayTextMsg("sys", data);
    },

    displayDebug : function(data) {
        this.displayTextMsg("debug", data);
    },

    displayPrompt : function(data) {
        this.displayTextMsg("prompt", data);
    },

    displayTextMsg : function(type, msg) {
        $("#msg_wnd").stop(true);
        $("#msg_wnd").scrollTop($("#msg_wnd")[0].scrollHeight);
        $("#msg_wnd").append("<div class='msg "+ type +"'>"+ msg +"</div>");
        
        // remove old messages
        var max = 40;
        while ($("#msg_wnd div").size() > max) {
            $("#msg_wnd div:first").remove();
        }
        
        // scroll message window to bottom
        // $("#msg_wnd").scrollTop($("#msg_wnd")[0].scrollHeight);
        $("#msg_wnd").animate({scrollTop: $("#msg_wnd")[0].scrollHeight});
    },

    display_env : function(data) {
        $("#env_wnd").empty();
        
        if ("room_name" in data) {
            this.enviroment["room_name"] = data["room_name"];
        }
        if ("room_desc" in data) {
            this.enviroment["room_desc"] = data["room_desc"];
        }
        if ("objects" in data) {
            this.enviroment["objects"] = data["objects"];
        }
        if ("players" in data) {
            this.enviroment["players"] = data["players"];
        }
        if ("exits" in data) {
            this.enviroment["exits"] = data["exits"];
        }

        var split = "****************************************";
        var text = "<div class='msg out'>"+ split +"</div>";
        text += "<div class='msg out'>"+ this.enviroment["room_name"] +"</div>";
        text += "<div class='msg out'>"+ split +"</div>";
        text += "<div><br></div>";
        text += "<div class='msg out'>"+ this.enviroment["room_desc"] +"</div>";
        
        $("#env_wnd").append(text);
    },

    doSetSizes : function() {
        // Sets the size of the message window
        var win_h = $(window).innerHeight();
        var win_w = $(window).innerWidth();
        var close_h = $('#close_button').outerHeight(true);
        var prom_h = $('#input_prompt').outerHeight(true);
        var add_h = $('#input_additional').outerHeight(true);
        $('#input_box').height(close_h + prom_h + add_h);
        
        var inp_h = $('#input_box').outerHeight(true);
        var inp_w = $('#input_box').outerWidth(true);
        //$("#wrapper").css({'height': win_h - inp_h - 1});
        $('#input_box').css({'left': (win_w - inp_w) / 2, 'top': (win_h - inp_h) / 2});

        if (win_h > 480) {
            var head_h = $('#site-title').outerHeight(true);
            $('#header_bar').show();
            $('#wrapper').height(win_h - head_h - 6);
        }
        else {
            $('#header_bar').hide();
            $('#wrapper').height(win_h - 6);
        }
        
        var middle_h = $('#middlewindow').outerHeight(true);
        var total_h = middle_h - 2;
        var tab_bar_h = 30;
        var tab_content_max_h = 240;
        if (total_h + tab_bar_h > tab_content_max_h * 2) {
            $('#msg_wnd').height(middle_h - tab_bar_h - tab_content_max_h - 2);
            $('#tab_bar').height(tab_bar_h);
            $('#tab_content').height(tab_content_max_h);
        }
        else {
            $('#msg_wnd').height(total_h / 2 - tab_bar_h);
            $('#tab_bar').height(tab_bar_h);
            $('#tab_content').height(total_h / 2);
        }
        
        if (win_w > 960) {
            $('#middlewindow').width(960);
        }
        else {
            $('#middlewindow').width(win_w);
        }
    },

    doCancel : function() {
        this.doCloseInput();
    },

    doInputCommand : function() {
        var command = $("#input_box :text").val();
        $("#input_box :text").val("");
        
        history_add(command);
        HISTORY_POS = 0;
        
        sendCommand(command);
        this.doCloseInput();
    },

    // show boxes
    showInputCmdBox : function(prompt) {
        this.createInputBox();
        
        prompt = text2html.parseHtml(prompt);
        $('#input_prompt').html(prompt);
        
        var input = '<div><input type="text" class="input_text" value="" autocomplete="off"/></div>';
        var button = '<div>\
                        <input type="button" class="btn button_left" value="CANCEL" onClick="doCloseInput()"/>\
                        <input type="button" class="btn btn-primary button_right" value="  OK  " onClick="doInputCommand()"/>\
                      </div>'
        $('#input_additional').html(input + button);
        $('#input_box :text').focus();
        this.doSetSizes();
    },

    showAlert : function(msg) {
        this.createInputBox();
        
        prompt = text2html.parseHtml(msg);
        $('#input_prompt').html(msg);
        
        var button = '<div><br></div>\
                      <div>\
                        <center>\
                          <input type="button" id="button_center" value="  OK  " class="btn btn-primary" onClick="doCloseInput()"/>\
                        </center>\
                      </div>'
        $('#input_additional').html(button);
        this.doSetSizes();
    },
    
    createInputBox : function() {
        var dlg = '<div id="input_box">\
        <div id="close_button" class="clearfix">\
        <input type="image" id="button_close" class="close" src="/static/this/img/button_close.png" alt="close" onclick="doCloseInput()"/>\
        </div>\
        <div id="input_prompt">\
        </div>\
        <div id="input_additional">\
        </div>\
        </div>';
        
        var overlayer = '<div class="overlayer" id="overlayer"></div>';
        
        $("body").prepend(dlg + overlayer);
    },

    doCloseInput : function() {
        $('#input_box').remove();
        $('#overlayer').remove();
        this.doSetSizes();
    },
    
    // show tabs
    clearAllTabs : function() {
        $("li#tab_bar").css("display", "none");
    },
    
    unselectAllTabs : function() {
        $("#tab_login").removeClass("pill_active");
        $("#page_login").css("display", "none");
        $("#tab_command").removeClass("pill_active");
        $("#page_command").css("display", "none");
    },
    
    showLogin : function() {
        this.unselectAllTabs();
        $("#tab_login").addClass("pill_active");
        $("#page_login").css("display", "");
    },
    
    showCommand : function() {
        this.unselectAllTabs();
        $("#tab_command").addClass("pill_active");
        $("#page_command").css("display", "");
    },

    // commands
    doLogin : function() {
        var username = $("#page_login :text").val();
        var password = $("#page_login :password").val();
        $("#page_login :password").val("");
        
        sendCommand("connect " + username + " " + password);
    },

    doRegister : function() {
        var username = $("#page_login :text").val();
        var password = $("#page_login :password").val();
        $("#page_login :password").val("");
        
        sendCommand("create " + username + " " + password);
    },
    
    doSendCommand : function() {
        var command = $("#page_command :text").val();
        $("#page_command :text").val("");
        
        sendCommand(command);
    },
}


// Callback function - called when the browser window resizes
$(window).resize(webclient.doSetSizes);